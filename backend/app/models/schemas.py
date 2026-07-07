from __future__ import annotations

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None


class HealthStatus(BaseModel):
    status: str
    fhir_data: str
    fhir_patients: int
    ollama: str


class ConditionDetail(BaseModel):
    display: str
    code: str
    system: str
    onset: str | None = None


class MedicationDetail(BaseModel):
    display: str
    code: str
    system: str
    status: str | None = None
    dosage: str | None = None
    brand_names: list[str] = []


class ObservationDetail(BaseModel):
    display: str
    code: str
    system: str
    value: float | str | None = None
    unit: str | None = None
    date: str | None = None


class PatientSummary(BaseModel):
    id: str
    name: str
    gender: str
    birth_date: str
    age: int
    condition_count: int
    medication_count: int
    observation_count: int
    source: str = "local"


class PatientDetail(BaseModel):
    id: str
    name: str
    gender: str
    birth_date: str
    age: int
    conditions: list[ConditionDetail]
    medications: list[MedicationDetail]
    observations: list[ObservationDetail]
    source: str = "local"


class MedlinePlusSource(BaseModel):
    title: str
    url: str


class ReadabilityScores(BaseModel):
    flesch_kincaid_grade: float
    gunning_fog: float


class SummarySection(BaseModel):
    heading: str
    icon: str = ""
    body: str


class ExplanationResponse(BaseModel):
    subject: str
    reading_level: str
    explanation: str
    readability: ReadabilityScores
    sources: list[MedlinePlusSource]
    sections: list[SummarySection] | None = None
    disclaimer: str = (
        "This explanation is for educational purposes only and does not "
        "constitute medical advice. Always consult your healthcare provider."
    )
