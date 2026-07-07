import pytest

from app.services.fhir_parser import FHIRParser

FHIR_DATA_PATH = "data/fhir"


@pytest.fixture()
def parser():
    return FHIRParser(FHIR_DATA_PATH)


def test_list_patients_returns_all(parser):
    patients = parser.list_patients()
    assert len(patients) == 8


def test_list_patients_fields(parser):
    patients = parser.list_patients()
    p = next(p for p in patients if p.id == "maria_garcia")
    assert p.name == "Maria Garcia"
    assert p.gender == "female"
    assert p.condition_count == 2
    assert p.medication_count == 2
    assert p.observation_count == 1


def test_get_patient_detail(parser):
    detail = parser.get_patient("maria_garcia")
    assert detail is not None
    assert detail.name == "Maria Garcia"
    assert len(detail.conditions) == 2
    assert len(detail.medications) == 2
    assert len(detail.observations) == 1


def test_get_patient_conditions(parser):
    detail = parser.get_patient("maria_garcia")
    codes = {c.code for c in detail.conditions}
    assert "44054006" in codes  # Type 2 diabetes
    assert "59621000" in codes  # Hypertension


def test_get_patient_medications(parser):
    detail = parser.get_patient("maria_garcia")
    codes = {m.code for m in detail.medications}
    assert "860975" in codes  # Metformin
    assert "314076" in codes  # Lisinopril


def test_get_patient_observations(parser):
    detail = parser.get_patient("maria_garcia")
    obs = detail.observations[0]
    assert obs.code == "4548-4"  # A1c
    assert obs.value == 7.2
    assert obs.unit == "%"


def test_get_patient_not_found(parser):
    assert parser.get_patient("nobody") is None


def test_medication_request_parsed(parser):
    """Verify MedicationRequest (not MedicationStatement) is handled."""
    detail = parser.get_patient("james_wilson")
    assert detail is not None
    assert len(detail.medications) == 2
    med_codes = {m.code for m in detail.medications}
    assert "259255" in med_codes  # Atorvastatin


def test_kenneth_liu_complex_patient(parser):
    detail = parser.get_patient("kenneth_liu")
    assert detail is not None
    assert len(detail.conditions) == 3
    assert len(detail.medications) == 3
    assert len(detail.observations) == 3


def test_local_patient_source(parser):
    detail = parser.get_patient("maria_garcia")
    assert detail.source == "local"


def test_hapi_patient_source(parser):
    detail = parser.get_patient("hapi_robert_chen")
    assert detail is not None
    assert detail.source == "hapi-fhir"
