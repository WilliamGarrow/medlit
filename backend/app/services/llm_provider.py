from __future__ import annotations

import logging
from typing import Protocol

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Interface for LLM providers."""

    async def generate(self, prompt: str) -> str: ...


class StubProvider:
    """Returns a placeholder response. Used when LLM_PROVIDER=stub."""

    async def generate(self, prompt: str) -> str:
        return (
            "LLM explanations will be available in a future update. "
            "This is a placeholder response from the stub provider."
        )


class OllamaProvider:
    """Generates text via a local Ollama instance."""

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url
        self.model = model

    async def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json=payload)
        except httpx.ConnectError:
            logger.error(
                "Cannot connect to Ollama at %s — is the service running?",
                self.base_url,
            )
            raise RuntimeError("LLM service is unavailable")

        if resp.status_code == 404:
            logger.error(
                "Ollama model '%s' not found. Run: "
                "docker compose exec ollama ollama pull %s",
                self.model,
                self.model,
            )
            raise RuntimeError("LLM service is unavailable")

        resp.raise_for_status()
        return resp.json().get("response", "")


class GroqProvider:
    """Generates text via the Groq cloud API."""

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("GROQ_API_KEY is required for GroqProvider")
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
        except httpx.ConnectError:
            logger.error("Cannot connect to Groq API")
            raise RuntimeError("LLM service is unavailable")

        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def get_llm_provider() -> LLMProvider:
    """Factory that returns the configured LLM provider."""
    settings = get_settings()
    provider = settings.llm_provider

    if provider == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.ollama_model)
    elif provider == "groq":
        return GroqProvider(settings.groq_api_key, settings.groq_model)
    elif provider == "stub":
        return StubProvider()
    else:
        logger.warning("Unknown LLM_PROVIDER '%s', falling back to stub", provider)
        return StubProvider()
