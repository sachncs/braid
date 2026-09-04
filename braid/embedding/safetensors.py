"""Safetensors embedding save/load."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="embedding", name="safetensors")
class safetensors:
    """Safetensors-backed save/load for catalog embeddings.

    Real implementation requires ``safetensors`` (pip install safetensors).
    """

    name: str = "safetensors"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "persistable", "observable"})

    def save(self, embeddings: np.ndarray, path: str) -> None:
        """Persist ``embeddings`` to ``path`` in safetensors format.

        Args:
            embeddings: ``[numitems, dim]`` float array.
            path: output path.

        Raises:
            requiresenvironment: if ``safetensors`` is not installed.
        """
        try:
            from safetensors.numpy import save_file
        except ImportError as exc:
            raise requiresenvironment(
                "safetensors is required for embedding:safetensors",
                hint="pip install safetensors",
            ) from exc
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        save_file({"embeddings": embeddings}, path)

    def load(self, path: str) -> np.ndarray:
        """Load ``embeddings`` from ``path``.

        Args:
            path: file path.

        Returns:
            ``[numitems, dim]`` array.

        Raises:
            requiresenvironment: if ``safetensors`` is not installed.
        """
        try:
            from safetensors.numpy import load_file
        except ImportError as exc:
            raise requiresenvironment(
                "safetensors is required for embedding:safetensors",
                hint="pip install safetensors",
            ) from exc
        return load_file(path)["embeddings"]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
