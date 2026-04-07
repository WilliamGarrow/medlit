"""Disk-backed explanation cache.

Stores LLM-generated explanations and summaries in a JSON file so they
survive container restarts.  The in-memory dict is the primary store;
the JSON file is written after every new entry.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path("/app/data/cache/explanation_cache.json")


class ExplanationCache:
    def __init__(self, path: Path | str = _DEFAULT_PATH) -> None:
        self._path = Path(path)
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
                logger.info(
                    "Loaded %d cached explanations from %s",
                    len(self._data),
                    self._path,
                )
            except (json.JSONDecodeError, OSError):
                logger.warning("Failed to load cache file, starting fresh")
                self._data = {}
        else:
            logger.info("No cache file at %s, starting fresh", self._path)

    def _persist(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(self._data))
        except OSError:
            logger.warning("Failed to write cache file %s", self._path)

    def get(self, key: str) -> dict | None:
        return self._data.get(key)

    def set(self, key: str, value: dict) -> None:
        self._data[key] = value
        self._persist()

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)
