import httpx
from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models.schemas import APIResponse, HealthStatus
from app.services.fhir_parser import FHIRParser

router = APIRouter()


@router.get("/health", response_model=APIResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    parser = FHIRParser(settings.fhir_data_path)
    patient_count = len(parser.list_patients())

    fhir_status = "Loaded" if patient_count > 0 else "No Data"

    llm_status = "Not Configured"
    if settings.llm_provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                llm_status = "Connected (Ollama)" if resp.status_code == 200 else "Error"
        except httpx.ConnectError:
            llm_status = "Unreachable"
    elif settings.llm_provider == "groq":
        llm_status = "Connected (Groq)"
    elif settings.llm_provider == "stub":
        llm_status = "Stub Mode"

    status = HealthStatus(
        status="Healthy",
        fhir_data=fhir_status,
        fhir_patients=patient_count,
        ollama=llm_status,
    )

    return APIResponse(success=True, data=status.model_dump())
