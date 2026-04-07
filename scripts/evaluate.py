#!/usr/bin/env python3
"""Evaluation framework: compare LLM outputs across providers and reading levels.

Generates the same prompts for multiple patients, sends them to multiple LLM
providers, scores readability, and writes a comparison report.

Usage:
    # From medlit/backend directory with venv activated:
    cd backend && source .venv/bin/activate
    python ../scripts/evaluate.py --providers groq-llama8b,groq-llama70b

    # Include Claude (requires ANTHROPIC_API_KEY env var):
    ANTHROPIC_API_KEY=sk-... python ../scripts/evaluate.py --providers groq-llama8b,claude-haiku

    # Specific patients and levels:
    python ../scripts/evaluate.py --patients maria_garcia,david_thompson --levels simple,detailed
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

# Add backend to path so we can reuse its modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.fhir_parser import FHIRParser
from app.services.medlineplus_client import MedlinePlusClient
from app.services.prompt_builder import (
    build_condition_prompt,
    build_medication_prompt,
    build_summary_prompt,
)
from app.services.readability import score_readability

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("evaluate")

FHIR_DATA = str(Path(__file__).resolve().parent.parent / "data" / "fhir")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "evaluation"


# ── Provider definitions ─────────────────────────────────────────────

@dataclass
class ProviderConfig:
    name: str
    api_url: str
    model: str
    api_key_env: str
    headers_fn: object = None  # callable


PROVIDER_REGISTRY: dict[str, ProviderConfig] = {
    "groq-llama8b": ProviderConfig(
        name="Groq Llama 3.1 8B",
        api_url="https://api.groq.com/openai/v1/chat/completions",
        model="llama-3.1-8b-instant",
        api_key_env="GROQ_API_KEY",
    ),
    "groq-llama70b": ProviderConfig(
        name="Groq Llama 3.1 70B",
        api_url="https://api.groq.com/openai/v1/chat/completions",
        model="llama-3.1-70b-versatile",
        api_key_env="GROQ_API_KEY",
    ),
    "claude-haiku": ProviderConfig(
        name="Claude Haiku 4.5",
        api_url="https://api.anthropic.com/v1/messages",
        model="claude-haiku-4-5-20251001",
        api_key_env="ANTHROPIC_API_KEY",
    ),
    "claude-sonnet": ProviderConfig(
        name="Claude Sonnet 4.6",
        api_url="https://api.anthropic.com/v1/messages",
        model="claude-sonnet-4-6-20250514",
        api_key_env="ANTHROPIC_API_KEY",
    ),
}


async def call_provider(config: ProviderConfig, prompt: str) -> tuple[str, float]:
    """Send prompt to provider, return (response_text, latency_seconds)."""
    api_key = os.environ.get(config.api_key_env, "")
    if not api_key:
        return f"[SKIPPED: {config.api_key_env} not set]", 0.0

    start = time.monotonic()

    if "anthropic" in config.api_url:
        headers = {
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": config.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
        }

    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(3):
            resp = await client.post(config.api_url, json=payload, headers=headers)
            if resp.status_code == 429 and attempt < 2:
                wait = int(resp.headers.get("retry-after", "10"))
                logger.warning("%s rate limited, waiting %ds", config.name, wait)
                await asyncio.sleep(wait)
                continue
            break

    elapsed = time.monotonic() - start

    if resp.status_code != 200:
        return f"[ERROR {resp.status_code}: {resp.text[:200]}]", elapsed

    data = resp.json()
    if "anthropic" in config.api_url:
        text = data["content"][0]["text"]
    else:
        text = data["choices"][0]["message"]["content"]

    return text, elapsed


# ── Evaluation logic ─────────────────────────────────────────────────

@dataclass
class EvalResult:
    patient_id: str
    patient_name: str
    prompt_type: str  # "summary", "condition", "medication"
    subject: str
    reading_level: str
    provider: str
    model: str
    explanation: str
    flesch_kincaid: float
    gunning_fog: float
    latency_s: float
    char_count: int


async def evaluate_patient_summary(
    parser: FHIRParser,
    medline: MedlinePlusClient,
    patient_id: str,
    levels: list[str],
    providers: list[ProviderConfig],
) -> list[EvalResult]:
    """Generate summary prompts and evaluate across providers and levels."""
    detail = parser.get_patient(patient_id)
    if detail is None:
        print(f"  Skipping {patient_id}: not found")
        return []

    # Fetch MedlinePlus for all conditions + meds
    lookup_tasks = []
    for c in detail.conditions:
        lookup_tasks.append((c.display, c.code, c.system))
    for m in detail.medications:
        lookup_tasks.append((m.display, m.code, m.system))

    medline_results_list = await asyncio.gather(
        *[medline.lookup(code, sys) for _, code, sys in lookup_tasks]
    )

    medline_by_subject = {}
    for (subject, _, _), results in zip(lookup_tasks, medline_results_list):
        medline_by_subject[subject] = results

    conditions = [c.display for c in detail.conditions]
    medications = [m.display for m in detail.medications]
    observations = [
        f"{o.display}: {o.value} {o.unit or ''}".strip()
        for o in detail.observations
    ]

    results: list[EvalResult] = []

    for level in levels:
        prompt = build_summary_prompt(
            patient_name=detail.name,
            patient_age=detail.age,
            conditions=conditions,
            medications=medications,
            observations=observations,
            medline_results=medline_by_subject,
            reading_level=level,
        )

        for prov in providers:
            print(f"    {prov.name} @ {level}...", end=" ", flush=True)
            text, latency = await call_provider(prov, prompt)
            scores = score_readability(text) if not text.startswith("[") else {"flesch_kincaid_grade": 0, "gunning_fog": 0}
            print(f"FK={scores['flesch_kincaid_grade']:.1f} ({latency:.1f}s)")

            results.append(EvalResult(
                patient_id=patient_id,
                patient_name=detail.name,
                prompt_type="summary",
                subject=f"Health Summary",
                reading_level=level,
                provider=prov.name,
                model=prov.model,
                explanation=text,
                flesch_kincaid=scores["flesch_kincaid_grade"],
                gunning_fog=scores["gunning_fog"],
                latency_s=round(latency, 2),
                char_count=len(text),
            ))

            # Rate limit courtesy between calls
            await asyncio.sleep(1)

    return results


async def run_evaluation(
    patient_ids: list[str],
    levels: list[str],
    provider_keys: list[str],
) -> list[EvalResult]:
    parser = FHIRParser(FHIR_DATA)
    medline = MedlinePlusClient()

    providers = []
    for key in provider_keys:
        if key not in PROVIDER_REGISTRY:
            print(f"Unknown provider: {key}. Available: {list(PROVIDER_REGISTRY.keys())}")
            sys.exit(1)
        providers.append(PROVIDER_REGISTRY[key])

    all_results: list[EvalResult] = []

    for pid in patient_ids:
        print(f"\n  Patient: {pid}")
        results = await evaluate_patient_summary(parser, medline, pid, levels, providers)
        all_results.extend(results)

    return all_results


def write_csv(results: list[EvalResult], path: Path) -> None:
    fields = [
        "patient_id", "patient_name", "prompt_type", "subject",
        "reading_level", "provider", "model", "flesch_kincaid",
        "gunning_fog", "latency_s", "char_count",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow({k: getattr(r, k) for k in fields})


def write_full_json(results: list[EvalResult], path: Path) -> None:
    data = []
    for r in results:
        data.append({
            "patient_id": r.patient_id,
            "patient_name": r.patient_name,
            "prompt_type": r.prompt_type,
            "subject": r.subject,
            "reading_level": r.reading_level,
            "provider": r.provider,
            "model": r.model,
            "explanation": r.explanation,
            "flesch_kincaid": r.flesch_kincaid,
            "gunning_fog": r.gunning_fog,
            "latency_s": r.latency_s,
            "char_count": r.char_count,
        })
    path.write_text(json.dumps(data, indent=2))


def print_summary_table(results: list[EvalResult]) -> None:
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"{'Provider':<28} {'Level':<10} {'FK Grade':<10} {'GF Index':<10} {'Latency':<10} {'Chars':<8}")
    print("-" * 80)
    for r in results:
        if r.explanation.startswith("["):
            continue
        print(
            f"{r.provider:<28} {r.reading_level:<10} "
            f"{r.flesch_kincaid:<10.1f} {r.gunning_fog:<10.1f} "
            f"{r.latency_s:<10.2f} {r.char_count:<8}"
        )
    print("=" * 80)

    # Averages by provider
    from collections import defaultdict
    by_provider: dict[str, list[EvalResult]] = defaultdict(list)
    for r in results:
        if not r.explanation.startswith("["):
            by_provider[r.provider].append(r)

    print(f"\n{'Provider':<28} {'Avg FK':<10} {'Avg GF':<10} {'Avg Latency':<12} {'Samples':<8}")
    print("-" * 70)
    for prov, rs in by_provider.items():
        avg_fk = sum(r.flesch_kincaid for r in rs) / len(rs)
        avg_gf = sum(r.gunning_fog for r in rs) / len(rs)
        avg_lat = sum(r.latency_s for r in rs) / len(rs)
        print(f"{prov:<28} {avg_fk:<10.1f} {avg_gf:<10.1f} {avg_lat:<12.2f} {len(rs):<8}")


def main():
    ap = argparse.ArgumentParser(description="Evaluate LLM outputs across providers")
    ap.add_argument(
        "--providers",
        default="groq-llama8b",
        help="Comma-separated provider keys: " + ", ".join(PROVIDER_REGISTRY.keys()),
    )
    ap.add_argument(
        "--patients",
        default="maria_garcia,david_thompson,sarah_johnson",
        help="Comma-separated patient IDs",
    )
    ap.add_argument(
        "--levels",
        default="simple,standard,detailed",
        help="Comma-separated reading levels",
    )
    args = ap.parse_args()

    provider_keys = [p.strip() for p in args.providers.split(",")]
    patient_ids = [p.strip() for p in args.patients.split(",")]
    levels = [l.strip() for l in args.levels.split(",")]

    print(f"Providers: {provider_keys}")
    print(f"Patients: {patient_ids}")
    print(f"Levels: {levels}")
    print(f"Total evaluations: {len(patient_ids) * len(levels) * len(provider_keys)}")

    results = asyncio.run(run_evaluation(patient_ids, levels, provider_keys))

    # Write outputs
    OUTPUT_DIR.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    csv_path = OUTPUT_DIR / f"eval_{ts}.csv"
    json_path = OUTPUT_DIR / f"eval_{ts}.json"

    write_csv(results, csv_path)
    write_full_json(results, json_path)
    print_summary_table(results)

    print(f"\nResults written to:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")


if __name__ == "__main__":
    main()
