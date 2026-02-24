from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.models.schemas import APIResponse
from app.services.fhir_parser import FHIRParser

router = APIRouter()


def _get_parser(settings: Settings = Depends(get_settings)) -> FHIRParser:
    return FHIRParser(settings.fhir_data_path)


@router.get("/patients", response_model=APIResponse)
async def list_patients(parser: FHIRParser = Depends(_get_parser)):
    summaries = parser.list_patients()
    return APIResponse(success=True, data=[s.model_dump() for s in summaries])


@router.get("/patients/{patient_id}", response_model=APIResponse)
async def get_patient(patient_id: str, parser: FHIRParser = Depends(_get_parser)):
    detail = parser.get_patient(patient_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")
    return APIResponse(success=True, data=detail.model_dump())
