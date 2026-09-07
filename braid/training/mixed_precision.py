"""Mixed-precision helpers."""

from __future__ import annotations

from typing import Any


def autocastcontext(dtype: str = "bf16") -> Any:
    """Yield a torch autocast context if torch is available."""
    try:
        import torch

        if dtype == "bf16":
            return torch.autocast(device_type="cuda", dtype=torch.bfloat16)
        if dtype == "fp16":
            return torch.autocast(device_type="cuda", dtype=torch.float16)
        return __import__("contextlib").nullcontext()
    except Exception:  # noqa: BLE001
        return __import__("contextlib").nullcontext()
