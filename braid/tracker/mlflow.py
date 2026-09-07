"""MLflow tracker integration. Requires ``mlflow``."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="tracker", name="mlflow")
class mlflow:
    """MLflow tracker integration."""

    name: str = "mlflow"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, runname: str = "default") -> None:
        try:
            import mlflow

            self.runname = runname
            self.runobj: Any = mlflow.start_run(run_name=self.runname)
        except ImportError as exc:
            raise requiresenvironment(
                "mlflow is required for tracker:mlflow", hint="pip install mlflow"
            ) from exc

    def log(self, key: str, value: float, step: int | None = None) -> None:
        try:
            import mlflow

            mlflow.log_metric(key, value, step=step or 0)
        except Exception:
            pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
