from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "stub"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.1:8b"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"

    # FHIR
    fhir_data_path: str = "/app/data/fhir"

    # Auth
    auth_disabled: bool = True
    session_secret: str = "medlit-dev-secret-change-in-prod"
    admin_password: str = "changeme-admin"
    demo_password: str = "changeme-demo"
    demo_login_enabled: bool = True

    # Server
    backend_port: int = 8000
    log_level: str = "info"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
