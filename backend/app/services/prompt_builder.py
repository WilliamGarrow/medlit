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

NO_MARKDOWN = (
    "IMPORTANT: Do not use any markdown formatting — no bold (**), no "
    "headers (#), no bullet points (-). Write in plain flowing paragraphs "
    "with natural sentence structure. This text is displayed directly to patients."
)

MAX_MEDLINE_REFS = 3
# For summaries we use shorter excerpts to keep the prompt within LLM token limits
MAX_SUMMARY_REFS_PER_SUBJECT = 1
MAX_SUMMARY_EXCERPT_CHARS = 500


def _strip_html(text: str) -> str:
    """Remove HTML tags from MedlinePlus summary text."""
    import re

    clean = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", clean).strip()


def _build_medline_section(medline_results: list[MedlinePlusResult]) -> str:
    refs = medline_results[:MAX_MEDLINE_REFS]
    if refs:
        ref_lines = []
        for r in refs:
            ref_lines.append(f"- {r.title}: {r.summary}" if r.summary else f"- {r.title}")
        return "MedlinePlus references:\n" + "\n".join(ref_lines)
    return "MedlinePlus references: No references available"


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
    medline_section = _build_medline_section(medline_results)

    return f"""You are a health literacy assistant helping patients understand their medications.

Patient context:
- Name: {patient_name}
- Age: {patient_age}
- Conditions: {conditions_text}
- Recent lab results: {observations_text}

Medication to explain: {medication}

{medline_section}

Reading level: {level_instruction}

Please explain what this medication is, why it was likely prescribed given the patient's conditions, common side effects to watch for, and any important instructions. Ground your explanation in the MedlinePlus references when available.

{NO_MARKDOWN}"""


def build_condition_prompt(
    patient_name: str,
    patient_age: int,
    medications: list[str],
    observations: list[str],
    condition: str,
    medline_results: list[MedlinePlusResult],
    reading_level: str,
) -> str:
    """Construct a RAG prompt for condition explanation."""
    level_instruction = READING_LEVEL_INSTRUCTIONS.get(
        reading_level, READING_LEVEL_INSTRUCTIONS["standard"]
    )

    medications_text = ", ".join(medications) if medications else "None listed"
    observations_text = "; ".join(observations) if observations else "None available"
    medline_section = _build_medline_section(medline_results)

    return f"""You are a health literacy assistant helping patients understand their medical conditions.

Patient context:
- Name: {patient_name}
- Age: {patient_age}
- Current medications: {medications_text}
- Recent lab results: {observations_text}

Condition to explain: {condition}

{medline_section}

Reading level: {level_instruction}

Please explain what this condition is in plain language, what causes it, how it might affect the patient's daily life, what treatments are commonly used, and any warning signs to watch for. Ground your explanation in the MedlinePlus references when available.

{NO_MARKDOWN}"""


def build_summary_prompt(
    patient_name: str,
    patient_age: int,
    conditions: list[str],
    medications: list[str],
    observations: list[str],
    medline_results: dict[str, list[MedlinePlusResult]],
    reading_level: str,
    drug_interactions: dict[str, str] | None = None,
) -> str:
    """Construct a RAG prompt for a holistic patient health summary.

    ``medline_results`` maps subject names (condition or medication display
    names) to the MedlinePlus results fetched for that subject.

    ``drug_interactions`` maps medication display names to FDA-approved
    drug interaction text from the openFDA Drug Label API.
    """
    level_instruction = READING_LEVEL_INSTRUCTIONS.get(
        reading_level, READING_LEVEL_INSTRUCTIONS["standard"]
    )

    conditions_text = ", ".join(conditions) if conditions else "None listed"
    medications_text = ", ".join(medications) if medications else "None listed"
    observations_text = "; ".join(observations) if observations else "None available"

    # Build combined MedlinePlus reference section (compact to fit token limits)
    ref_sections: list[str] = []
    for subject, results in medline_results.items():
        refs = results[:MAX_SUMMARY_REFS_PER_SUBJECT]
        if refs:
            for r in refs:
                excerpt = _strip_html(r.summary)[:MAX_SUMMARY_EXCERPT_CHARS] if r.summary else ""
                line = f"  - {r.title}: {excerpt}" if excerpt else f"  - {r.title}"
                ref_sections.append(f"[{subject}]\n{line}")
    medline_block = "\n\n".join(ref_sections) if ref_sections else "No references available"

    # Build FDA drug interactions section
    fda_block = ""
    if drug_interactions:
        fda_lines = []
        for med_name, text in drug_interactions.items():
            if text:
                fda_lines.append(f"[{med_name}]\n  {text}")
        if fda_lines:
            fda_block = "\n\nFDA drug interaction references (from openFDA drug labels):\n" + "\n\n".join(fda_lines)

    return f"""You are a health literacy assistant helping a patient understand their overall health picture.

Patient context:
- Name: {patient_name}
- Age: {patient_age}
- Conditions: {conditions_text}
- Current medications: {medications_text}
- Recent lab results: {observations_text}

MedlinePlus references (by subject):
{medline_block}
{fda_block}

Reading level: {level_instruction}

Respond with a JSON array of sections. Each section has a "heading" and "body" field. Write plain text in the body (no markdown, no bullet points, no bold). Use these sections in order:

1. heading: "Your Conditions" — Explain what their conditions are, what they mean, and how they may relate to each other.
2. heading: "Your Medications" — Explain why each medication was likely prescribed and how it connects to their conditions.
3. heading: "Important Interactions" — If any medications have known interactions with each other or with their conditions (based on the FDA references), explain the most important ones. If there are no notable interactions, say so briefly.
4. heading: "Lab Results" — If lab results are available, explain what the values suggest in plain language. If no labs are available, omit this section entirely.
5. heading: "Key Takeaways" — One or two practical things the patient should keep in mind.

Ground your explanation in the MedlinePlus and FDA references. Only mention interactions supported by the FDA references. Do not speculate beyond what the references support.

Respond ONLY with the JSON array, no other text. Example format:
[{{"heading": "Your Conditions", "body": "..."}}, {{"heading": "Your Medications", "body": "..."}}]"""
