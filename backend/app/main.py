import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import activity, auth, explain, health, patients

logger = logging.getLogger("medlit")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("MedLit backend starting — LLM provider: %s", settings.llm_provider)
    logger.info("FHIR data path: %s", settings.fhir_data_path)
    yield


app = FastAPI(
    title="MedLit API",
    description="Patient health literacy via FHIR + MedlinePlus + LLM",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(explain.router, prefix="/api")
