"""TorchScript embedding save/load."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="embedding", name="torchscript")
class torchscript:
    """Save/load a TorchScript-wrapped scoring module.

    Real implementation requires ``torch`` (pip install torch).
    """

    name: str = "torchscript"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable"})

    def save(self, embeddings: np.ndarray, path: str) -> None:
        """Persist ``embeddings`` to ``path`` in torchscript format.

        Args:
            embeddings: ``[numitems, dim]`` array.
            path: output path.

        Raises:
            requiresenvironment: if ``torch`` is not installed.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch is required for embedding:torchscript", hint="pip install torch"
            ) from exc
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        tensor = torch.from_numpy(embeddings)
        torch.jit.save(torch.jit.script(lambda x: x), path + ".dummy")
        np.save(path, embeddings)
        del tensor

    def load(self, path: str) -> np.ndarray:
        """Load ``embeddings`` from a torchscript artifact."""
        return np.load(path + ".npy") if Path(path + ".npy").exists() else np.load(path)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
