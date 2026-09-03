"""ONNX embedding save/load."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="embedding", name="onnx")
class onnx:
    """ONNX save/load for catalog scoring modules."""

    name: str = "onnx"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable"})

    def save(self, embeddings: np.ndarray, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        try:
            import onnx
            from onnx import numpy_helper, helper, TensorProto

            tensor = numpy_helper.from_array(embeddings)
            graph = helper.make_graph([tensor], "embeddings", [], [])
            model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
            onnx.save(model, path)
        except Exception:  # noqa: BLE001
            np.save(path.replace(".onnx", ".npy"), embeddings)

    def load(self, path: str) -> np.ndarray:
        if not path.endswith(".onnx"):
            return np.load(path)
        try:
            import onnx
            from onnx import numpy_helper

            model = onnx.load(path)
            init = model.graph.initializer[0]
            return numpy_helper.to_array(init)
        except Exception:  # noqa: BLE001
            return np.load(path.replace(".onnx", ".npy"))

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
