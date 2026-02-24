from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from xml.etree import ElementTree

import httpx

logger = logging.getLogger(__name__)

# MedlinePlus Connect uses OIDs for code systems
CODE_SYSTEM_OIDS = {
    "SNOMED CT": "2.16.840.1.113883.6.96",
    "RxNorm": "2.16.840.1.113883.6.88",
    "LOINC": "2.16.840.1.113883.6.1",
}

MEDLINEPLUS_URL = "https://connect.medlineplus.gov/service"
CACHE_TTL_SECONDS = 86400  # 24 hours

# Atom feed namespace
ATOM_NS = "http://www.w3.org/2005/Atom"


@dataclass
class MedlinePlusResult:
    title: str
    url: str
    summary: str


class MedlinePlusClient:
    """Queries MedlinePlus Connect API and caches results."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, list[MedlinePlusResult]]] = {}

    async def lookup(
        self, code: str, code_system: str
    ) -> list[MedlinePlusResult]:
        oid = CODE_SYSTEM_OIDS.get(code_system)
        if oid is None:
            logger.warning("Unknown code system: %s", code_system)
            return []

        cache_key = f"{code_system}:{code}"

        # Check cache
        if cache_key in self._cache:
            ts, results = self._cache[cache_key]
            if time.monotonic() - ts < CACHE_TTL_SECONDS:
                return results

        # Query MedlinePlus Connect
        params = {
            "mainSearchCriteria.v.cs": oid,
            "mainSearchCriteria.v.c": code,
            "knowledgeResponseType": "application/xml",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(MEDLINEPLUS_URL, params=params)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("MedlinePlus request failed: %s", exc)
            return []

        results = _parse_atom_feed(resp.text)
        self._cache[cache_key] = (time.monotonic(), results)
        return results


def _parse_atom_feed(xml_text: str) -> list[MedlinePlusResult]:
    """Parse MedlinePlus Atom feed XML into result objects."""
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        logger.error("Failed to parse MedlinePlus XML response")
        return []

    results: list[MedlinePlusResult] = []
    for entry in root.findall(f"{{{ATOM_NS}}}entry"):
        title_el = entry.find(f"{{{ATOM_NS}}}title")
        link_el = entry.find(f"{{{ATOM_NS}}}link")
        summary_el = entry.find(f"{{{ATOM_NS}}}summary")

        title = title_el.text if title_el is not None and title_el.text else ""
        url = link_el.get("href", "") if link_el is not None else ""
        summary = summary_el.text if summary_el is not None and summary_el.text else ""

        if title:
            results.append(MedlinePlusResult(title=title, url=url, summary=summary))

    return results
