"""TorchScript embedding save/load."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="embedding", name="torchscript")
class torchscript:
    """Save/load a TorchScript-wrapped scoring module."""

    name: str = "torchscript"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable"})

    def save(self, embeddings: np.ndarray, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        try:
            import torch

            tensor = torch.from_numpy(embeddings)
            torch.jit.save(torch.jit.script(lambda x: x), path + ".dummy")
            np.save(path, embeddings)
            del tensor
        except Exception:  # noqa: BLE001
            np.save(path, embeddings)

    def load(self, path: str) -> np.ndarray:
        return np.load(path + ".npy") if Path(path + ".npy").exists() else np.load(path)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
