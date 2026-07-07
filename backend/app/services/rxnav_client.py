"""RxNav client for fetching brand names by RxNorm code.

Queries NLM's RxNav `/REST/rxcui/{cui}/related.json?tty=BN` endpoint to map
a generic RxNorm Semantic Clinical Drug (SCD) code to its commercial brand
names. Used to render "Tiotropium ... (Spiriva)" on patient medication
cards and to provide brand context to the LLM.

API docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
No authentication required.
"""

from __future__ import annotations

import logging
import time

import httpx

logger = logging.getLogger(__name__)

RXNAV_URL_TEMPLATE = "https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/related.json"
CACHE_TTL_SECONDS = 86_400  # 24 hours


class RxNavClient:
    """Fetches brand names for an RxNorm code from RxNav."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, list[str]]] = {}

    async def lookup_brands(self, rxcui: str) -> list[str]:
        """Return brand names for a given RxNorm code.

        Returns an empty list if the code is not RxNorm, the lookup fails,
        or the drug has no associated brand names.
        """
        if not rxcui or not rxcui.isdigit():
            return []

        if rxcui in self._cache:
            ts, brands = self._cache[rxcui]
            if time.monotonic() - ts < CACHE_TTL_SECONDS:
                return brands

        url = RXNAV_URL_TEMPLATE.format(rxcui=rxcui)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, params={"tty": "BN"})
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("RxNav request failed for %s: %s", rxcui, exc)
            return []

        try:
            payload = resp.json()
        except ValueError:
            logger.warning("RxNav returned non-JSON for %s", rxcui)
            return []

        brands = _extract_brand_names(payload)
        self._cache[rxcui] = (time.monotonic(), brands)
        return brands


def _extract_brand_names(payload: dict) -> list[str]:
    """Pull brand-name strings out of an RxNav /related.json?tty=BN response.

    Deduplicates while preserving first-seen order so the most-canonical
    brand (RxNav usually lists it first) wins.
    """
    groups = payload.get("relatedGroup", {}).get("conceptGroup") or []
    seen: set[str] = set()
    brands: list[str] = []
    for group in groups:
        for cp in group.get("conceptProperties") or []:
            name = (cp.get("name") or "").strip()
            if name and name not in seen:
                seen.add(name)
                brands.append(name)
    return brands
