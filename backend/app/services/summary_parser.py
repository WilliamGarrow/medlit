"""Parse the LLM's structured summary response into sections.

The model is instructed to return a JSON array of {heading, body} objects,
but real generations arrive imperfect: wrapped in markdown fences, prefixed
with prose, with trailing commas, or with literal newlines inside string
values (invalid JSON, but tolerated by json.loads(strict=False)). This
module absorbs those variations; the caller falls back to plain text only
when nothing here succeeds.
"""

from __future__ import annotations

import json
import re

SECTION_ICONS = {
    "Your Conditions": "conditions",
    "Your Medications": "medications",
    "Important Interactions": "interactions",
    "Lab Results": "labs",
    "Key Takeaways": "takeaways",
}


def parse_summary_sections(raw_response: str) -> tuple[list[dict] | None, str]:
    """Return (sections, explanation_text).

    sections is a list of {heading, icon, body} dicts, or None if the
    response could not be parsed; explanation_text is the joined section
    bodies, or the raw response when parsing fails.
    """
    try:
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
        # Extract the JSON array if surrounded by extra prose
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]
        try:
            # strict=False tolerates literal control characters (newlines,
            # tabs) inside string values, the most common malformation.
            parsed = json.loads(cleaned, strict=False)
        except json.JSONDecodeError:
            repaired = re.sub(r",\s*]", "]", cleaned)  # trailing commas
            repaired = re.sub(r",\s*}", "}", repaired)
            parsed = json.loads(repaired, strict=False)
        if not isinstance(parsed, list):
            return None, raw_response
        sections: list[dict] = []
        body_parts: list[str] = []
        for item in parsed:
            heading = item.get("heading", "")
            body = item.get("body", "")
            sections.append({
                "heading": heading,
                "icon": SECTION_ICONS.get(heading, ""),
                "body": body,
            })
            body_parts.append(body)
        return sections, "\n\n".join(body_parts)
    except (json.JSONDecodeError, AttributeError, TypeError, IndexError):
        return None, raw_response
