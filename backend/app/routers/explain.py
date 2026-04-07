from __future__ import annotations

import asyncio
import enum
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import Settings, get_settings
from app.models.schemas import (
    APIResponse,
    ExplanationResponse,
    MedlinePlusSource,
    ReadabilityScores,
    SummarySection,
)
from app.services.fhir_parser import FHIRParser
from app.services.llm_provider import get_llm_provider
from app.services.medlineplus_client import MedlinePlusClient
from app.services.prompt_builder import (
    build_condition_prompt,
    build_medication_prompt,
    build_summary_prompt,
)
from app.services.cache import ExplanationCache
from app.services.openfda_client import OpenFDAClient
from app.services.readability import score_readability

logger = logging.getLogger(__name__)

router = APIRouter()

# Module-level singletons so caches persist across requests
_medline_client = MedlinePlusClient()
_openfda_client = OpenFDAClient()
_explanation_cache = ExplanationCache()


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
    # Check cache
    cache_key = f"med:{patient_id}:{med_index}:{level.value}"
    cached = _explanation_cache.get(cache_key)
    if cached is not None:
        return APIResponse(success=True, data=cached)

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
        subject=med.display,
        reading_level=level.value,
        explanation=explanation,
        readability=ReadabilityScores(**scores),
        sources=sources,
    )

    data = result.model_dump()
    _explanation_cache.set(cache_key, data)
    return APIResponse(success=True, data=data)


@router.get(
    "/patients/{patient_id}/summary",
    response_model=APIResponse,
)
async def patient_summary(
    patient_id: str,
    level: ReadingLevel = Query(ReadingLevel.standard),
    parser: FHIRParser = Depends(_get_parser),
):
    # Check cache
    cache_key = f"summary:{patient_id}:{level.value}"
    cached = _explanation_cache.get(cache_key)
    if cached is not None:
        return APIResponse(success=True, data=cached)

    # Load patient
    detail = parser.get_patient(patient_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")

    # Query MedlinePlus + openFDA for all conditions/medications in parallel
    lookup_tasks: list[tuple[str, str, str]] = []
    for c in detail.conditions:
        lookup_tasks.append((c.display, c.code, c.system))
    for m in detail.medications:
        lookup_tasks.append((m.display, m.code, m.system))

    # MedlinePlus lookups
    medline_coros = [
        _medline_client.lookup(code, system) for _, code, system in lookup_tasks
    ]
    # openFDA drug interaction lookups (medications only)
    fda_coros = [
        _openfda_client.lookup_interactions(m.code, m.display)
        for m in detail.medications
    ]

    all_coros = medline_coros + fda_coros
    all_results = await asyncio.gather(*all_coros)

    medline_results_list = all_results[: len(medline_coros)]
    fda_results_list = all_results[len(medline_coros) :]

    medline_by_subject: dict[str, list] = {}
    all_sources: list[MedlinePlusSource] = []
    seen_urls: set[str] = set()
    for (subject, _, _), medline_results in zip(lookup_tasks, medline_results_list):
        medline_by_subject[subject] = medline_results
        for r in medline_results:
            if r.url not in seen_urls:
                all_sources.append(MedlinePlusSource(title=r.title, url=r.url))
                seen_urls.add(r.url)

    # Collect FDA drug interaction text
    drug_interactions: dict[str, str] = {}
    for med, fda_result in zip(detail.medications, fda_results_list):
        if fda_result is not None:
            drug_interactions[med.display] = fda_result.interactions_text

    # Add openFDA as a source if we got any results
    if drug_interactions:
        all_sources.append(
            MedlinePlusSource(title="openFDA Drug Labels", url="https://open.fda.gov/apis/drug/label/")
        )

    # Build prompt
    conditions = [c.display for c in detail.conditions]
    medications = [m.display for m in detail.medications]
    observations = [
        f"{o.display}: {o.value} {o.unit or ''}".strip() for o in detail.observations
    ]
    prompt = build_summary_prompt(
        patient_name=detail.name,
        patient_age=detail.age,
        conditions=conditions,
        medications=medications,
        observations=observations,
        medline_results=medline_by_subject,
        reading_level=level.value,
        drug_interactions=drug_interactions or None,
    )

    # Call LLM
    provider = get_llm_provider()
    try:
        raw_response = await provider.generate(prompt)
    except Exception:
        logger.exception("LLM generation failed for patient summary")
        raise HTTPException(status_code=503, detail="LLM service is unavailable")

    # Parse structured sections from LLM JSON response
    SECTION_ICONS = {
        "Your Conditions": "conditions",
        "Your Medications": "medications",
        "Important Interactions": "interactions",
        "Lab Results": "labs",
        "Key Takeaways": "takeaways",
    }

    sections: list[SummarySection] | None = None
    explanation_text = raw_response
    try:
        # Strip any markdown code fences the LLM might add
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
        # Extract JSON array if surrounded by extra text
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            # LLM sometimes produces slightly malformed JSON — try to repair
            # common issues: trailing commas, unescaped newlines in strings
            import re

            repaired = re.sub(r",\s*]", "]", cleaned)  # trailing comma
            repaired = re.sub(r",\s*}", "}", repaired)
            parsed = json.loads(repaired)
        if isinstance(parsed, list):
            sections = []
            body_parts = []
            for item in parsed:
                heading = item.get("heading", "")
                body = item.get("body", "")
                icon = SECTION_ICONS.get(heading, "")
                sections.append(SummarySection(heading=heading, icon=icon, body=body))
                body_parts.append(body)
            explanation_text = "\n\n".join(body_parts)
    except (json.JSONDecodeError, AttributeError, TypeError):
        logger.warning("Failed to parse structured summary, using raw text")

    # Score readability on the combined plain text
    scores = score_readability(explanation_text)

    result = ExplanationResponse(
        subject=f"Health Summary for {detail.name}",
        reading_level=level.value,
        explanation=explanation_text,
        readability=ReadabilityScores(**scores),
        sources=all_sources,
        sections=sections,
    )

    data = result.model_dump()
    _explanation_cache.set(cache_key, data)
    return APIResponse(success=True, data=data)

@router.get(
    "/explain/condition/{patient_id}/{condition_index}",
    response_model=APIResponse,
)
async def explain_condition(
    patient_id: str,
    condition_index: int,
    level: ReadingLevel = Query(ReadingLevel.standard),
    parser: FHIRParser = Depends(_get_parser),
):
    # Check cache
    cache_key = f"cond:{patient_id}:{condition_index}:{level.value}"
    cached = _explanation_cache.get(cache_key)
    if cached is not None:
        return APIResponse(success=True, data=cached)

    # Load patient
    detail = parser.get_patient(patient_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")

    # Validate condition index
    if condition_index < 0 or condition_index >= len(detail.conditions):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Condition index {condition_index} out of range — "
                f"patient has {len(detail.conditions)} condition(s)"
            ),
        )

    cond = detail.conditions[condition_index]

    # Query MedlinePlus
    medline_results = await _medline_client.lookup(cond.code, cond.system)

    # Build prompt
    medications = [m.display for m in detail.medications]
    observations = [
        f"{o.display}: {o.value} {o.unit or ''}".strip() for o in detail.observations
    ]
    prompt = build_condition_prompt(
        patient_name=detail.name,
        patient_age=detail.age,
        medications=medications,
        observations=observations,
        condition=cond.display,
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
        subject=cond.display,
        reading_level=level.value,
        explanation=explanation,
        readability=ReadabilityScores(**scores),
        sources=sources,
    )

    data = result.model_dump()
    _explanation_cache.set(cache_key, data)
    return APIResponse(success=True, data=data)
