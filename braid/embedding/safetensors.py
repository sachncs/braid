"""Safetensors embedding save/load."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="embedding", name="safetensors")
class safetensors:
    """Safetensors-backed save/load for catalog embeddings."""

    name: str = "safetensors"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "persistable", "observable"})

    def save(self, embeddings: np.ndarray, path: str) -> None:
        try:
            from safetensors.numpy import save_file
        except ImportError:
            np.save(path, embeddings)
            return
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        save_file({"embeddings": embeddings}, path)

    def load(self, path: str) -> np.ndarray:
        try:
            from safetensors.numpy import load_file
        except ImportError:
            return np.load(path)
        return load_file(path)["embeddings"]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
