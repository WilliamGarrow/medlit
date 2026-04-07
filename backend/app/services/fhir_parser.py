from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

from fhir.resources.R4B.bundle import Bundle

from app.models.schemas import (
    ConditionDetail,
    MedicationDetail,
    ObservationDetail,
    PatientDetail,
    PatientSummary,
)

logger = logging.getLogger(__name__)


class FHIRParser:
    """Loads FHIR JSON bundles from disk and extracts clinical data."""

    def __init__(self, data_dir: str) -> None:
        self._data_dir = Path(data_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_patients(self) -> list[PatientSummary]:
        summaries: list[PatientSummary] = []
        for path in sorted(self._data_dir.glob("*.json")):
            try:
                detail = self._parse_bundle(path)
                if detail is None:
                    continue
                summaries.append(
                    PatientSummary(
                        id=detail.id,
                        name=detail.name,
                        gender=detail.gender,
                        birth_date=detail.birth_date,
                        age=detail.age,
                        condition_count=len(detail.conditions),
                        medication_count=len(detail.medications),
                        observation_count=len(detail.observations),
                        source=detail.source,
                    )
                )
            except Exception:
                logger.exception("Failed to parse %s", path.name)
        return summaries

    def get_patient(self, patient_id: str) -> PatientDetail | None:
        path = self._data_dir / f"{patient_id}.json"
        if not path.exists():
            return None
        return self._parse_bundle(path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_bundle(self, path: Path) -> PatientDetail | None:
        raw = json.loads(path.read_text())
        bundle = Bundle.parse_obj(raw)

        # Detect medlit source tag (injected by fetch_hapi_patients.py)
        source = "local"
        if bundle.meta and bundle.meta.tag:
            for tag in bundle.meta.tag:
                if str(tag.system) == "medlit" and tag.code == "hapi-fhir":
                    source = "hapi-fhir"
                    break

        patient_id = path.stem
        name = gender = birth_date = None
        age = 0
        conditions: list[ConditionDetail] = []
        medications: list[MedicationDetail] = []
        observations: list[ObservationDetail] = []

        for entry in bundle.entry or []:
            res = entry.resource
            rtype = res.get_resource_type()

            if rtype == "Patient":
                name, gender, birth_date, age = self._extract_patient(res)
            elif rtype == "Condition":
                detail = self._extract_condition(res)
                if detail:
                    conditions.append(detail)
            elif rtype in ("MedicationRequest", "MedicationStatement"):
                detail = self._extract_medication(res, rtype)
                if detail:
                    medications.append(detail)
            elif rtype == "Observation":
                detail = self._extract_observation(res)
                if detail:
                    observations.append(detail)

        if name is None:
            return None

        return PatientDetail(
            id=patient_id,
            name=name,
            gender=gender or "unknown",
            birth_date=birth_date or "unknown",
            age=age,
            conditions=conditions,
            medications=medications,
            observations=observations,
            source=source,
        )

    @staticmethod
    def _extract_patient(res) -> tuple[str | None, str | None, str | None, int]:
        try:
            hn = res.name[0]
            given = " ".join(hn.given) if hn.given else ""
            name = f"{given} {hn.family}".strip()
        except (IndexError, AttributeError):
            name = None

        gender = res.gender
        birth_date = str(res.birthDate) if res.birthDate else None
        age = 0
        if res.birthDate:
            today = date.today()
            bd = res.birthDate
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

        return name, gender, birth_date, age

    @staticmethod
    def _extract_condition(res) -> ConditionDetail | None:
        coding = _first_coding(res.code)
        if coding is None:
            return None
        onset = None
        if res.onsetDateTime:
            onset = str(res.onsetDateTime)
        return ConditionDetail(
            display=coding.get("display", "Unknown"),
            code=coding["code"],
            system=coding["system_label"],
            onset=onset,
        )

    @staticmethod
    def _extract_medication(res, rtype: str) -> MedicationDetail | None:
        if rtype == "MedicationRequest":
            concept = getattr(res, "medicationCodeableConcept", None)
        else:
            concept = getattr(res, "medicationCodeableConcept", None)

        coding = _first_coding(concept)
        if coding is None:
            return None

        dosage_text = None
        dosage_list = getattr(res, "dosageInstruction", None) or getattr(res, "dosage", None)
        if dosage_list:
            dosage_text = getattr(dosage_list[0], "text", None)

        return MedicationDetail(
            display=coding.get("display", "Unknown"),
            code=coding["code"],
            system=coding["system_label"],
            status=getattr(res, "status", None),
            dosage=dosage_text,
        )

    @staticmethod
    def _extract_observation(res) -> ObservationDetail | None:
        coding = _first_coding(res.code)
        if coding is None:
            return None

        value = None
        unit = None
        vq = getattr(res, "valueQuantity", None)
        if vq:
            value = vq.value
            unit = vq.unit

        obs_date = None
        if res.effectiveDateTime:
            obs_date = str(res.effectiveDateTime)

        return ObservationDetail(
            display=coding.get("display", "Unknown"),
            code=coding["code"],
            system=coding["system_label"],
            value=value,
            unit=unit,
            date=obs_date,
        )


def _first_coding(codeable_concept) -> dict | None:
    """Return the first coding from a CodeableConcept as a plain dict."""
    if codeable_concept is None:
        return None
    codings = getattr(codeable_concept, "coding", None)
    if not codings:
        return None
    c = codings[0]
    if not c.code:
        return None
    system_raw = str(c.system) if c.system else ""
    if "snomed" in system_raw:
        label = "SNOMED CT"
    elif "rxnorm" in system_raw:
        label = "RxNorm"
    elif "loinc" in system_raw:
        label = "LOINC"
    else:
        label = system_raw
    return {
        "code": c.code,
        "display": getattr(c, "display", None) or "Unknown",
        "system_label": label,
    }
