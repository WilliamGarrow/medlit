#!/usr/bin/env python3
"""Validate FHIR sample data: check that every coded value's display string
matches the canonical name returned by an authoritative source.

- RxNorm codes -> RxNav /REST/rxcui/{cui}/properties.json
- SNOMED CT codes -> MedlinePlus Connect (the same path the live app uses,
  so coverage gaps surface here too)
- LOINC and other systems are skipped for now.

Exits 1 if any errors are found. Warnings are reported but don't fail.

Usage:
    python -m scripts.validate_fhir_data            # validate all
    python -m scripts.validate_fhir_data <file.json>  # validate one
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

import httpx

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "fhir"

RXNAV_URL = "https://rxnav.nlm.nih.gov/REST/rxcui/{code}/properties.json"
MEDLINEPLUS_URL = "https://connect.medlineplus.gov/service"
ATOM_NS = "http://www.w3.org/2005/Atom"

CODE_SYSTEM_OIDS = {
    "snomed": "2.16.840.1.113883.6.96",
    "rxnorm": "2.16.840.1.113883.6.88",
    "loinc": "2.16.840.1.113883.6.1",
}

# Tokens that appear in nearly every drug name and add no validation signal.
STOPWORDS = {
    "oral", "tablet", "capsule", "capsules", "powder", "solution", "spray",
    "inhalation", "injectable", "injection", "delayed", "release", "extended",
    "actuat", "for", "the", "with", "and", "syrup", "suspension",
    "mg", "mcg", "ml", "unt", "unit", "units", "iu",
}

JUNK_DISPLAYS = {"test", "xy", "n/a", "na", "unknown", ""}


def _tokens(text: str) -> set[str]:
    """Lower-case alphabetic tokens >=3 chars, minus stopwords."""
    return {t for t in re.findall(r"[a-z]+", text.lower()) if len(t) >= 3 and t not in STOPWORDS}


def _detect_system(uri: str) -> str:
    u = (uri or "").lower()
    if "snomed" in u:
        return "snomed"
    if "rxnorm" in u:
        return "rxnorm"
    if "loinc" in u:
        return "loinc"
    return "unknown"


@dataclass(frozen=True)
class Finding:
    file: str
    rtype: str
    system: str
    code: str
    display: str
    severity: str  # "error" | "warn"
    detail: str


def _lookup_rxnav(client: httpx.Client, code: str) -> str | None:
    try:
        r = client.get(RXNAV_URL.format(code=code), timeout=10.0)
        if r.status_code != 200:
            return None
        props = (r.json() or {}).get("properties")
        if not props:
            return None
        # Combine name + synonym so display alternatives are accepted
        name = props.get("name") or ""
        synonym = props.get("synonym") or ""
        return f"{name} {synonym}".strip()
    except (httpx.HTTPError, ValueError):
        return None


def _lookup_medlineplus(client: httpx.Client, code: str, system: str) -> str | None:
    oid = CODE_SYSTEM_OIDS.get(system)
    if not oid:
        return None
    try:
        r = client.get(
            MEDLINEPLUS_URL,
            params={
                "mainSearchCriteria.v.cs": oid,
                "mainSearchCriteria.v.c": code,
                "knowledgeResponseType": "application/xml",
            },
            timeout=10.0,
        )
        if r.status_code != 200:
            return None
        root = ElementTree.fromstring(r.text)
        # Concatenate all entry titles - any one that overlaps the display is fine
        titles: list[str] = []
        for entry in root.findall(f"{{{ATOM_NS}}}entry"):
            t = entry.find(f"{{{ATOM_NS}}}title")
            if t is not None and t.text:
                titles.append(t.text)
        return " ".join(titles) if titles else None
    except (httpx.HTTPError, ElementTree.ParseError):
        return None


def _iter_coded_values(bundle: dict):
    """Yield (resource_type, system_uri, code, display) for every coded value
    we care about validating."""
    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        rtype = res.get("resourceType")
        codeable = None
        if rtype == "Condition":
            codeable = res.get("code")
        elif rtype in ("MedicationRequest", "MedicationStatement"):
            codeable = res.get("medicationCodeableConcept")
        elif rtype == "Observation":
            codeable = res.get("code")
        if not codeable:
            continue
        for c in codeable.get("coding", []):
            yield rtype, c.get("system", ""), c.get("code", ""), c.get("display", "")


def validate_file(client: httpx.Client, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    bundle = json.loads(path.read_text())

    for rtype, sys_uri, code, display in _iter_coded_values(bundle):
        system = _detect_system(sys_uri)

        if not code:
            findings.append(Finding(path.name, rtype, system, code, display,
                                    "error", "missing code"))
            continue

        if (display or "").strip().lower() in JUNK_DISPLAYS:
            findings.append(Finding(path.name, rtype, system, code, display,
                                    "error", f"junk display {display!r}"))
            continue

        # token-mismatch severity differs by source:
        # - RxNav is authoritative for RxNorm; mismatch == real data error
        # - MedlinePlus topic titles are patient-friendly synonyms (e.g.
        #   "Cholesterol" for SNOMED "Hyperlipidemia"), so token mismatch
        #   on SNOMED conditions is informational only
        mismatch_severity = "error"
        if system == "rxnorm":
            canonical = _lookup_rxnav(client, code)
            if canonical is None:
                findings.append(Finding(path.name, rtype, system, code, display,
                                        "error", "RxCUI not found in RxNav"))
                continue
        elif system == "snomed":
            if rtype in ("MedicationRequest", "MedicationStatement"):
                # SNOMED-coded meds don't flow through our RxNorm-driven
                # MedlinePlus path - flag rather than silently accept.
                findings.append(Finding(path.name, rtype, system, code, display,
                                        "warn", "medication coded in SNOMED (not RxNorm); won't resolve via app's MedlinePlus path"))
                continue
            canonical = _lookup_medlineplus(client, code, system)
            if canonical is None:
                findings.append(Finding(path.name, rtype, system, code, display,
                                        "warn", "no MedlinePlus topic for this SNOMED code"))
                continue
            mismatch_severity = "warn"
        else:
            # Skip LOINC and unknown systems for now
            continue

        d_tokens = _tokens(display)
        c_tokens = _tokens(canonical)
        if not d_tokens:
            findings.append(Finding(path.name, rtype, system, code, display,
                                    "warn", "display has no validatable tokens after stopword removal"))
            continue
        if not d_tokens & c_tokens:
            findings.append(Finding(path.name, rtype, system, code, display,
                                    mismatch_severity,
                                    f"display tokens {sorted(d_tokens)} disjoint from canonical "
                                    f"{canonical!r} tokens {sorted(c_tokens)}"))

    return findings


def run(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    with httpx.Client() as client:
        for p in paths:
            findings.extend(validate_file(client, p))
    return findings


def main() -> int:
    if len(sys.argv) > 1:
        paths = [Path(a) for a in sys.argv[1:]]
    else:
        paths = sorted(DATA_DIR.glob("*.json"))

    print(f"Validating {len(paths)} file(s)...", file=sys.stderr)
    findings = run(paths)

    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]

    for sev, items in (("ERROR", errors), ("WARN", warns)):
        if not items:
            continue
        print(f"\n=== {sev} ({len(items)}) ===")
        for f in items:
            print(f"  [{f.file}] {f.rtype} {f.system}:{f.code or '<empty>'} "
                  f"display={f.display!r}\n    -> {f.detail}")

    print(f"\nSummary: {len(errors)} error(s), {len(warns)} warning(s) "
          f"across {len(paths)} file(s).")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
