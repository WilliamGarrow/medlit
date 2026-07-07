"""Validate FHIR sample data against authoritative external sources.

Catches the class of bug where a CodeableConcept's display string and code
disagree (e.g. RxCUI 1116634 labeled 'Tiotropium' but actually mapping to
ticagrelor in RxNorm).

Marked `network` because it hits RxNav and MedlinePlus Connect; skip locally
with `pytest -m 'not network'`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the repo's scripts/ importable
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_fhir_data import DATA_DIR, run  # noqa: E402


@pytest.mark.network
def test_no_code_display_mismatches():
    paths = sorted(DATA_DIR.glob("*.json"))
    assert paths, "no FHIR data files found"
    findings = run(paths)
    errors = [f for f in findings if f.severity == "error"]
    assert not errors, "FHIR data validation errors:\n" + "\n".join(
        f"  [{f.file}] {f.rtype} {f.system}:{f.code or '<empty>'} "
        f"display={f.display!r} -> {f.detail}"
        for f in errors
    )
