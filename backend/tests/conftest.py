from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app

FHIR_DATA_PATH = str(Path(__file__).resolve().parents[2] / "data" / "fhir")


def _test_settings() -> Settings:
    return Settings(
        fhir_data_path=FHIR_DATA_PATH,
        llm_provider="stub",
    )


@pytest.fixture()
def client():
    app.dependency_overrides[get_settings] = _test_settings
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
