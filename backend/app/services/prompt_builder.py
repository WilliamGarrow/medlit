from __future__ import annotations

from app.services.medlineplus_client import MedlinePlusResult

READING_LEVEL_INSTRUCTIONS = {
    "simple": (
        "Write at a 5th-6th grade reading level. Use short sentences and "
        "everyday words. Avoid medical jargon entirely."
    ),
    "standard": (
        "Write at a 7th-8th grade reading level. You may use common medical "
        "terms but explain each one briefly."
    ),
    "detailed": (
        "Write at a 10th-12th grade reading level. You may use medical "
        "terminology and provide more in-depth explanations."
    ),
}

MAX_MEDLINE_REFS = 3


def build_medication_prompt(
    patient_name: str,
    patient_age: int,
    conditions: list[str],
    observations: list[str],
    medication: str,
    medline_results: list[MedlinePlusResult],
    reading_level: str,
) -> str:
    """Construct a RAG prompt for medication explanation."""
    level_instruction = READING_LEVEL_INSTRUCTIONS.get(
        reading_level, READING_LEVEL_INSTRUCTIONS["standard"]
    )

    conditions_text = ", ".join(conditions) if conditions else "None listed"
    observations_text = "; ".join(observations) if observations else "None available"

    # Build MedlinePlus reference section
    refs = medline_results[:MAX_MEDLINE_REFS]
    if refs:
        ref_lines = []
        for r in refs:
            ref_lines.append(f"- {r.title}: {r.summary}" if r.summary else f"- {r.title}")
        medline_section = "MedlinePlus references:\n" + "\n".join(ref_lines)
    else:
        medline_section = "MedlinePlus references: No references available"

    return f"""You are a health literacy assistant helping patients understand their medications.

Patient context:
- Name: {patient_name}
- Age: {patient_age}
- Conditions: {conditions_text}
- Recent lab results: {observations_text}

Medication to explain: {medication}

{medline_section}

Reading level: {level_instruction}

Please explain what this medication is, why it was likely prescribed given the patient's conditions, common side effects to watch for, and any important instructions. Ground your explanation in the MedlinePlus references when available."""
