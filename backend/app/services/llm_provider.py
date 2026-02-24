from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    """Interface for LLM providers (implemented in Sprint 2)."""

    async def generate(self, prompt: str) -> str: ...


class StubProvider:
    """Returns a placeholder response. Used when LLM_PROVIDER=stub."""

    async def generate(self, prompt: str) -> str:
        return (
            "LLM explanations will be available in a future update. "
            "This is a placeholder response from the stub provider."
        )
