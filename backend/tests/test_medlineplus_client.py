import time

import pytest

from app.services.medlineplus_client import (
    CODE_SYSTEM_OIDS,
    MedlinePlusClient,
    MedlinePlusResult,
    _parse_atom_feed,
)

# -- Sample Atom XML --------------------------------------------------------

SAMPLE_ATOM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>MedlinePlus Connect</title>
  <entry>
    <title>Metformin</title>
    <link href="https://medlineplus.gov/druginfo/meds/a696005.html"/>
    <summary>Metformin is used to treat type 2 diabetes.</summary>
  </entry>
  <entry>
    <title>Diabetes Medicines</title>
    <link href="https://medlineplus.gov/diabetesmedicines.html"/>
    <summary>Several types of diabetes medicines are available.</summary>
  </entry>
</feed>
"""

EMPTY_ATOM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>MedlinePlus Connect</title>
</feed>
"""

INVALID_XML = "<not valid xml><<>>"


# -- XML parsing tests -------------------------------------------------------


def test_parse_atom_feed_two_entries():
    results = _parse_atom_feed(SAMPLE_ATOM_XML)
    assert len(results) == 2
    assert results[0].title == "Metformin"
    assert "a696005" in results[0].url
    assert "type 2 diabetes" in results[0].summary


def test_parse_atom_feed_empty():
    results = _parse_atom_feed(EMPTY_ATOM_XML)
    assert results == []


def test_parse_atom_feed_invalid_xml():
    results = _parse_atom_feed(INVALID_XML)
    assert results == []


# -- OID coverage -------------------------------------------------------------


def test_oid_mapping_covers_required_systems():
    assert "SNOMED CT" in CODE_SYSTEM_OIDS
    assert "RxNorm" in CODE_SYSTEM_OIDS
    assert "LOINC" in CODE_SYSTEM_OIDS


# -- Client behavior ----------------------------------------------------------


@pytest.mark.asyncio
async def test_unknown_code_system_returns_empty():
    client = MedlinePlusClient()
    results = await client.lookup("12345", "FAKE_SYSTEM")
    assert results == []


@pytest.mark.asyncio
async def test_cache_hit_returns_cached_data():
    client = MedlinePlusClient()
    cached = [MedlinePlusResult(title="Cached", url="http://example.com", summary="test")]
    client._cache["RxNorm:860975"] = (time.monotonic(), cached)

    results = await client.lookup("860975", "RxNorm")
    assert len(results) == 1
    assert results[0].title == "Cached"


@pytest.mark.asyncio
async def test_cache_expired_is_not_returned():
    client = MedlinePlusClient()
    # Set cache entry with timestamp far in the past
    cached = [MedlinePlusResult(title="Stale", url="", summary="")]
    client._cache["RxNorm:000000"] = (time.monotonic() - 100000, cached)

    # This will try to hit the real API (which may fail), but the key point
    # is that we DON'T get the stale cached data back.
    results = await client.lookup("000000", "RxNorm")
    # Either empty (API error for bogus code) or fresh results -- not "Stale"
    stale_found = any(r.title == "Stale" for r in results)
    assert not stale_found
