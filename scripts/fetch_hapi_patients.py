#!/usr/bin/env python3
"""One-time script to fetch patients from the public HAPI FHIR R4 server.

Finds patients with linked Conditions, fetches their $everything bundle,
filters for ones with at least 1 Condition + 1 other resource, tags them
with a medlit source marker, and saves to data/fhir/.

Usage:
    python scripts/fetch_hapi_patients.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import httpx

BASE_URL = "https://hapi.fhir.org/baseR4"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "fhir"
TARGET_COUNT = 3
TIMEOUT = 30.0


def search_candidates(client: httpx.Client) -> list[dict]:
    """Find patients that have at least one Condition linked to them."""
    resp = client.get(
        f"{BASE_URL}/Patient",
        params={
            "_has:Condition:patient:_id": "",
            "_count": "100",
        },
    )
    resp.raise_for_status()
    bundle = resp.json()
    entries = bundle.get("entry", [])
    print(f"  Found {len(entries)} candidate patients with Conditions")
    return entries


def fetch_everything(client: httpx.Client, patient_id: str) -> dict | None:
    """Fetch Patient/$everything and return the bundle dict, or None on error."""
    try:
        resp = client.get(
            f"{BASE_URL}/Patient/{patient_id}/$everything",
            params={"_count": "100"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except (httpx.HTTPStatusError, httpx.ReadTimeout) as exc:
        print(f"    Skipping {patient_id}: {exc}")
        return None


def score_bundle(bundle: dict) -> dict:
    """Count resource types in a bundle and return a summary."""
    counts: dict[str, int] = {}
    for entry in bundle.get("entry", []):
        rt = entry.get("resource", {}).get("resourceType", "Unknown")
        counts[rt] = counts.get(rt, 0) + 1
    return counts


def extract_patient_name(bundle: dict) -> str | None:
    """Pull the first human-readable name from the Patient resource."""
    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        if res.get("resourceType") != "Patient":
            continue
        names = res.get("name", [])
        if not names:
            return None
        n = names[0]
        given = " ".join(n.get("given", []))
        family = n.get("family", "")
        full = f"{given} {family}".strip()
        return full if full else None
    return None


def fix_datetimes(obj: dict | list | str) -> dict | list | str:
    """Recursively fix FHIR DateTime values missing timezone offsets.

    The FHIR spec requires timezone offsets on dateTime values, but many
    real-world servers return naive timestamps like '2018-06-01T09:00:00'.
    This appends '+00:00' (UTC) to any ISO-ish datetime string that has a
    time component but no offset.
    """
    if isinstance(obj, dict):
        return {k: fix_datetimes(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_datetimes(item) for item in obj]
    if isinstance(obj, str):
        # Match datetime-like strings with time but no offset/Z
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", obj):
            return obj + "+00:00"
    return obj


def tag_bundle(bundle: dict) -> dict:
    """Inject medlit source tag into the bundle's meta."""
    if "meta" not in bundle:
        bundle["meta"] = {}
    if "tag" not in bundle["meta"]:
        bundle["meta"]["tag"] = []
    bundle["meta"]["tag"].append(
        {"system": "medlit", "code": "hapi-fhir"}
    )
    return bundle


def extract_birth_year(bundle: dict) -> int | None:
    """Pull birth year from the Patient resource, or None."""
    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        if res.get("resourceType") != "Patient":
            continue
        bd = res.get("birthDate", "")
        if bd and len(bd) >= 4:
            try:
                return int(bd[:4])
            except ValueError:
                return None
    return None


def safe_filename(name: str) -> str:
    """Convert a patient name to a filesystem-safe filename prefix."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main() -> None:
    print("Fetching patients from HAPI FHIR R4 server...")
    saved: list[str] = []

    with httpx.Client(timeout=TIMEOUT) as client:
        candidates = search_candidates(client)

        for entry in candidates:
            if len(saved) >= TARGET_COUNT:
                break

            patient_res = entry.get("resource", {})
            patient_id = patient_res.get("id")
            if not patient_id:
                continue

            print(f"\n  Checking Patient/{patient_id}...")
            bundle = fetch_everything(client, patient_id)
            if bundle is None:
                continue

            counts = score_bundle(bundle)
            conditions = counts.get("Condition", 0)
            meds = counts.get("MedicationRequest", 0) + counts.get(
                "MedicationStatement", 0
            )
            obs = counts.get("Observation", 0)
            print(f"    Resources: {counts}")

            # Require at least 2 conditions + 1 other clinical resource
            if conditions < 2 or (meds + obs) < 1:
                print("    Skipping: not enough clinical data")
                continue

            # Require adult patients (18+)
            birth_year = extract_birth_year(bundle)
            if birth_year is not None and (2026 - birth_year) < 18:
                print(f"    Skipping: pediatric patient (born {birth_year})")
                continue

            name = extract_patient_name(bundle)
            if not name:
                print("    Skipping: no usable name")
                continue

            # Skip names that match existing local patients
            existing_names = {
                "robert chen", "david thompson", "maria garcia",
                "sarah johnson", "james wilson", "aisha martinez",
                "priya patel",
            }
            if name.lower() in existing_names:
                print(f"    Skipping: name collision with local patient")
                continue

            bundle = fix_datetimes(bundle)
            bundle = tag_bundle(bundle)

            filename = f"hapi_{safe_filename(name)}.json"
            out_path = OUTPUT_DIR / filename
            out_path.write_text(json.dumps(bundle, indent=2))
            print(f"    Saved: {out_path.name}")
            print(
                f"    -> {name}: {conditions} conditions, {meds} meds, {obs} observations"
            )
            saved.append(filename)

    print(f"\nDone. Saved {len(saved)} HAPI patients to {OUTPUT_DIR}/")
    for f in saved:
        print(f"  - {f}")

    if len(saved) < TARGET_COUNT:
        print(
            f"\nWarning: Only found {len(saved)}/{TARGET_COUNT} suitable patients."
        )
        print("HAPI's public test server has mostly low-quality data.")
        print("Re-run later or adjust the filtering criteria.")
        sys.exit(1 if len(saved) == 0 else 0)


if __name__ == "__main__":
    main()
