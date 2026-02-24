from __future__ import annotations

import enum
import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import Settings, get_settings
from app.models.schemas import (
    APIResponse,
    ExplanationResponse,
    MedlinePlusSource,
    ReadabilityScores,
)
from app.services.fhir_parser import FHIRParser
from app.services.llm_provider import get_llm_provider
from app.services.medlineplus_client import MedlinePlusClient
from app.services.prompt_builder import build_medication_prompt
from app.services.readability import score_readability

logger = logging.getLogger(__name__)

router = APIRouter()

# Module-level singleton so the cache persists across requests
_medline_client = MedlinePlusClient()


class ReadingLevel(str, enum.Enum):
    simple = "simple"
    standard = "standard"
    detailed = "detailed"


def _get_parser(settings: Settings = Depends(get_settings)) -> FHIRParser:
    return FHIRParser(settings.fhir_data_path)


@router.get(
    "/explain/medication/{patient_id}/{med_index}",
    response_model=APIResponse,
)
async def explain_medication(
    patient_id: str,
    med_index: int,
    level: ReadingLevel = Query(ReadingLevel.standard),
    parser: FHIRParser = Depends(_get_parser),
):
    # Load patient
    detail = parser.get_patient(patient_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")

    # Validate medication index
    if med_index < 0 or med_index >= len(detail.medications):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Medication index {med_index} out of range — "
                f"patient has {len(detail.medications)} medication(s)"
            ),
        )

    med = detail.medications[med_index]

    # Query MedlinePlus
    medline_results = await _medline_client.lookup(med.code, med.system)

    # Build prompt
    conditions = [c.display for c in detail.conditions]
    observations = [
        f"{o.display}: {o.value} {o.unit or ''}".strip() for o in detail.observations
    ]
    prompt = build_medication_prompt(
        patient_name=detail.name,
        patient_age=detail.age,
        conditions=conditions,
        observations=observations,
        medication=med.display,
        medline_results=medline_results,
        reading_level=level.value,
    )

    # Call LLM
    provider = get_llm_provider()
    try:
        explanation = await provider.generate(prompt)
    except Exception:
        logger.exception("LLM generation failed")
        raise HTTPException(status_code=503, detail="LLM service is unavailable")

    # Score readability
    scores = score_readability(explanation)

    # Build response
    sources = [
        MedlinePlusSource(title=r.title, url=r.url) for r in medline_results
    ]
    result = ExplanationResponse(
        medication=med.display,
        reading_level=level.value,
        explanation=explanation,
        readability=ReadabilityScores(**scores),
        sources=sources,
    )

    return APIResponse(success=True, data=result.model_dump())
