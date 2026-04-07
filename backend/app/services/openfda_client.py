"""OpenFDA Drug Label client for fetching drug interaction text.

Queries the openFDA Drug Label API by RxNorm code to retrieve the
``drug_interactions`` section from FDA-approved drug labeling (SPL).

API docs: https://open.fda.gov/apis/drug/label/
No authentication required.  Free tier: 240 req/min, 1 000 req/day.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

OPENFDA_URL = "https://api.fda.gov/drug/label.json"
CACHE_TTL_SECONDS = 86_400  # 24 hours (same as MedlinePlus cache)
MAX_INTERACTION_CHARS = 800  # Truncate to keep prompts within token limits


@dataclass
class DrugInteractionResult:
    drug_name: str
    rxnorm_code: str
    interactions_text: str  # Plain text, HTML stripped


def _strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", clean).strip()


class OpenFDAClient:
    """Fetches drug interaction text from the openFDA Drug Label API."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, DrugInteractionResult | None]] = {}

    async def lookup_interactions(
        self, rxnorm_code: str, drug_name: str = ""
    ) -> DrugInteractionResult | None:
        """Fetch the drug_interactions section for a medication by RxNorm code.

        Returns None if no label is found or if the label has no
        drug_interactions section.
        """
        # Check cache
        if rxnorm_code in self._cache:
            ts, result = self._cache[rxnorm_code]
            if time.monotonic() - ts < CACHE_TTL_SECONDS:
                return result

        result = await self._fetch(rxnorm_code, drug_name)
        self._cache[rxnorm_code] = (time.monotonic(), result)
        return result

    @staticmethod
    def _extract_generic_name(display: str) -> str | None:
        """Extract the first word (generic drug name) from a display string.

        E.g. 'Metformin 500 MG Oral Tablet' → 'metformin'
        """
        if not display:
            return None
        first_word = display.split()[0].lower()
        # Skip if it looks like a number or code
        if first_word[0].isdigit():
            return None
        return first_word

    async def _try_search(
        self, client: httpx.AsyncClient, search_query: str
    ) -> dict | None:
        """Execute an openFDA search and return the first result, or None."""
        try:
            resp = await client.get(
                OPENFDA_URL, params={"search": search_query, "limit": "1"}
            )
        except httpx.HTTPError as exc:
            logger.warning("openFDA request failed: %s", exc)
            return None

        if resp.status_code != 200:
            return None

        results = resp.json().get("results", [])
        if not results:
            return None

        label = results[0]
        if label.get("drug_interactions"):
            return label
        return None

    async def _fetch(
        self, rxnorm_code: str, drug_name: str
    ) -> DrugInteractionResult | None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try RxNorm code first
            label = await self._try_search(client, f"openfda.rxcui:{rxnorm_code}")

            # Fallback: search by generic name extracted from display string
            if label is None:
                generic = self._extract_generic_name(drug_name)
                if generic:
                    label = await self._try_search(
                        client, f"openfda.generic_name:{generic}"
                    )

        if label is None:
            return None

        interactions_raw = label.get("drug_interactions")
        if not interactions_raw:
            return None

        # drug_interactions is an array of strings (FDA label sections)
        full_text = " ".join(interactions_raw)
        clean_text = _strip_html(full_text)

        # Truncate to keep prompt size manageable
        if len(clean_text) > MAX_INTERACTION_CHARS:
            clean_text = clean_text[:MAX_INTERACTION_CHARS].rsplit(" ", 1)[0] + "..."

        return DrugInteractionResult(
            drug_name=drug_name or f"RxNorm:{rxnorm_code}",
            rxnorm_code=rxnorm_code,
            interactions_text=clean_text,
        )
