from __future__ import annotations

import textstat


def score_readability(text: str) -> dict[str, float]:
    """Return Flesch-Kincaid and Gunning Fog scores for the given text."""
    return {
        "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(text), 1),
        "gunning_fog": round(textstat.gunning_fog(text), 1),
    }
