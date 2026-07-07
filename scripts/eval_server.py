"""Run evaluation on the server where Groq API is accessible."""
import asyncio
import json
import sys
import time

sys.path.insert(0, "/app")

from app.services.fhir_parser import FHIRParser
from app.services.medlineplus_client import MedlinePlusClient
from app.services.prompt_builder import build_summary_prompt
from app.services.llm_provider import get_llm_provider
from app.services.readability import score_readability

PATIENTS = ["maria_garcia", "david_thompson", "hapi_eugene_morales"]
LEVELS = ["simple", "standard", "detailed"]


async def run():
    parser = FHIRParser("/app/data/fhir")
    medline = MedlinePlusClient()
    provider = get_llm_provider()
    results = []

    for pid in PATIENTS:
        d = parser.get_patient(pid)
        if not d:
            print(f"SKIP {pid}")
            continue

        conditions = [c.display for c in d.conditions]
        medications = [m.display for m in d.medications]
        observations = []
        for o in d.observations:
            unit = o.unit or ""
            observations.append(f"{o.display}: {o.value} {unit}".strip())

        tasks = []
        for c in d.conditions:
            tasks.append((c.display, c.code, c.system))
        for m in d.medications:
            tasks.append((m.display, m.code, m.system))

        ml_results = await asyncio.gather(
            *[medline.lookup(code, sys) for _, code, sys in tasks]
        )
        ml_by_subject = {}
        for (subj, _, _), r in zip(tasks, ml_results):
            ml_by_subject[subj] = r

        for level in LEVELS:
            prompt = build_summary_prompt(
                d.name, d.age, conditions, medications,
                observations, ml_by_subject, level,
            )
            start = time.monotonic()
            try:
                text = await provider.generate(prompt)
                elapsed = time.monotonic() - start

                # Parse JSON sections to get plain text for scoring
                plain = text
                try:
                    cleaned = text.strip()
                    si = cleaned.find("[")
                    ei = cleaned.rfind("]")
                    if si >= 0 and ei > si:
                        parsed = json.loads(cleaned[si:ei+1])
                        if isinstance(parsed, list):
                            plain = " ".join(
                                item.get("body", "") for item in parsed
                            )
                except (json.JSONDecodeError, AttributeError):
                    pass

                scores = score_readability(plain)
                fk = scores["flesch_kincaid_grade"]
                gf = scores["gunning_fog"]
                results.append({
                    "patient": d.name,
                    "patient_id": pid,
                    "level": level,
                    "fk": fk,
                    "gf": gf,
                    "latency": round(elapsed, 2),
                    "chars": len(plain),
                })
                print(f"  {d.name} @ {level}: FK={fk} GF={gf} ({elapsed:.1f}s)")
            except Exception as e:
                print(f"  {d.name} @ {level}: ERROR {e}")

            await asyncio.sleep(1)

    # Print table
    print()
    header = f"{'Patient':<25} {'Level':<10} {'FK':<8} {'GF':<8} {'Secs':<8} {'Chars':<8}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['patient']:<25} {r['level']:<10} "
            f"{r['fk']:<8} {r['gf']:<8} "
            f"{r['latency']:<8} {r['chars']:<8}"
        )

    # Averages by level
    print()
    print(f"{'Level':<12} {'Avg FK':<10} {'Avg GF':<10} {'Avg Secs':<10}")
    print("-" * 42)
    for level in LEVELS:
        level_results = [r for r in results if r["level"] == level]
        if level_results:
            avg_fk = sum(r["fk"] for r in level_results) / len(level_results)
            avg_gf = sum(r["gf"] for r in level_results) / len(level_results)
            avg_lat = sum(r["latency"] for r in level_results) / len(level_results)
            print(f"{level:<12} {avg_fk:<10.1f} {avg_gf:<10.1f} {avg_lat:<10.2f}")

    # Write JSON
    with open("/app/data/cache/eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to /app/data/cache/eval_results.json")


asyncio.run(run())
