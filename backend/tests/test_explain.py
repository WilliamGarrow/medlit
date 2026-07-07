import pytest

from app.services.medlineplus_client import MedlinePlusResult
from app.services.prompt_builder import build_medication_prompt
from app.services.readability import score_readability


# -- Readability tests --------------------------------------------------------


def test_readability_returns_both_metrics():
    scores = score_readability("The cat sat on the mat.")
    assert "flesch_kincaid_grade" in scores
    assert "gunning_fog" in scores


def test_simple_text_scores_low():
    scores = score_readability("The cat sat on the mat. The dog ran fast.")
    assert scores["flesch_kincaid_grade"] < 5


def test_complex_text_scores_higher():
    text = (
        "Pharmacokinetic considerations necessitate careful titration of "
        "antihypertensive medications in patients with concurrent renal "
        "insufficiency and hepatic dysfunction to avoid adverse outcomes."
    )
    simple_text = "The cat sat on the mat. The dog ran fast."
    complex_scores = score_readability(text)
    simple_scores = score_readability(simple_text)
    assert complex_scores["flesch_kincaid_grade"] > simple_scores["flesch_kincaid_grade"]


# -- Prompt builder tests -----------------------------------------------------


def test_prompt_contains_patient_context():
    prompt = build_medication_prompt(
        patient_name="Maria Garcia",
        patient_age=60,
        conditions=["Type 2 diabetes"],
        observations=["A1c: 7.2%"],
        medication="Metformin 500mg",
        medline_results=[],
        reading_level="standard",
    )
    assert "Maria Garcia" in prompt
    assert "60" in prompt
    assert "Type 2 diabetes" in prompt
    assert "A1c: 7.2%" in prompt
    assert "Metformin 500mg" in prompt


def test_prompt_reading_level_simple():
    prompt = build_medication_prompt(
        "Test", 30, [], [], "Aspirin", [], "simple"
    )
    assert "5th-6th grade" in prompt


def test_prompt_reading_level_standard():
    prompt = build_medication_prompt(
        "Test", 30, [], [], "Aspirin", [], "standard"
    )
    assert "7th-8th grade" in prompt


def test_prompt_reading_level_detailed():
    prompt = build_medication_prompt(
        "Test", 30, [], [], "Aspirin", [], "detailed"
    )
    assert "10th-12th grade" in prompt


def test_prompt_includes_medline_refs():
    refs = [
        MedlinePlusResult(title="Metformin", url="http://example.com", summary="Treats diabetes"),
        MedlinePlusResult(title="Diabetes Meds", url="http://example.com/2", summary="Overview"),
    ]
    prompt = build_medication_prompt(
        "Test", 30, [], [], "Metformin", refs, "standard"
    )
    assert "Metformin: Treats diabetes" in prompt
    assert "Diabetes Meds: Overview" in prompt


def test_prompt_handles_empty_conditions_and_observations():
    prompt = build_medication_prompt(
        "Test", 30, [], [], "Aspirin", [], "standard"
    )
    assert "None listed" in prompt
    assert "None available" in prompt


def test_prompt_caps_medline_refs_at_three():
    refs = [
        MedlinePlusResult(title=f"Ref {i}", url="", summary=f"Summary {i}")
        for i in range(5)
    ]
    prompt = build_medication_prompt(
        "Test", 30, [], [], "Drug", refs, "standard"
    )
    assert "Ref 0" in prompt
    assert "Ref 2" in prompt
    assert "Ref 3" not in prompt


# -- Endpoint tests -----------------------------------------------------------


def test_explain_medication_200(client):
    resp = client.get("/api/explain/medication/maria_garcia/0")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "Metformin" in data["subject"]
    assert data["reading_level"] == "standard"


def test_explain_medication_simple_level(client):
    resp = client.get("/api/explain/medication/maria_garcia/0?level=simple")
    assert resp.status_code == 200
    assert resp.json()["data"]["reading_level"] == "simple"


def test_explain_medication_detailed_level(client):
    resp = client.get("/api/explain/medication/maria_garcia/0?level=detailed")
    assert resp.status_code == 200
    assert resp.json()["data"]["reading_level"] == "detailed"


def test_explain_medication_invalid_level(client):
    resp = client.get("/api/explain/medication/maria_garcia/0?level=bogus")
    assert resp.status_code == 422


def test_explain_medication_patient_not_found(client):
    resp = client.get("/api/explain/medication/nobody/0")
    assert resp.status_code == 404


def test_explain_medication_index_out_of_range(client):
    resp = client.get("/api/explain/medication/maria_garcia/99")
    assert resp.status_code == 404
    assert "out of range" in resp.json()["detail"]


def test_explain_medication_has_disclaimer(client):
    resp = client.get("/api/explain/medication/maria_garcia/0")
    data = resp.json()["data"]
    assert "educational purposes" in data["disclaimer"]


def test_explain_medication_has_readability_scores(client):
    resp = client.get("/api/explain/medication/maria_garcia/0")
    data = resp.json()["data"]
    readability = data["readability"]
    assert isinstance(readability["flesch_kincaid_grade"], (int, float))
    assert isinstance(readability["gunning_fog"], (int, float))
