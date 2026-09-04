"""MLflow tracker integration."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="tracker", name="mlflow")
class mlflow:
    """MLflow tracker integration."""

    name: str = "mlflow"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, runname: str = "default") -> None:
        self.runname = runname
        self.run: Any | None = None

    def init(self) -> None:
        try:
            import mlflow

            self.run = mlflow.start_run(run_name=self.runname)
        except Exception:  # noqa: BLE001
            self.run = None

    def log(self, key: str, value: float, step: int | None = None) -> None:
        if self.run is None:
            self.init()
        if self.run is not None:
            try:
                import mlflow

                mlflow.log_metric(key, value, step=step or 0)
            except Exception:  # noqa: BLE001
                pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
