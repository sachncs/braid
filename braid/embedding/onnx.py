"""ONNX embedding save/load."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="embedding", name="onnx")
class onnx:
    """ONNX save/load for catalog scoring modules.

    Real implementation requires ``onnx`` (pip install onnx).
    """

    name: str = "onnx"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable"})

    def save(self, embeddings: np.ndarray, path: str) -> None:
        """Save ``embeddings`` as an ONNX init tensor.

        Args:
            embeddings: ``[numitems, dim]`` array.
            path: output path.

        Raises:
            requiresenvironment: if ``onnx`` is not installed.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        try:
            import onnx
            from onnx import numpy_helper, helper
        except ImportError as exc:
            raise requiresenvironment(
                "onnx is required for embedding:onnx", hint="pip install onnx"
            ) from exc
        tensor = numpy_helper.from_array(embeddings)
        graph = helper.make_graph([tensor], "embeddings", [], [])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        onnx.save(model, path)

    def load(self, path: str) -> np.ndarray:
        """Load ``embeddings`` from an ONNX model.

        Args:
            path: file path.

        Raises:
            requiresenvironment: if ``onnx`` is not installed.
        """
        try:
            import onnx
            from onnx import numpy_helper
        except ImportError as exc:
            raise requiresenvironment(
                "onnx is required for embedding:onnx", hint="pip install onnx"
            ) from exc
        model = onnx.load(path)
        init = model.graph.initializer[0]
        return numpy_helper.to_array(init)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
