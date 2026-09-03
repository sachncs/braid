"""Request/response Pydantic schemas for serving."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class rankrequest(BaseModel):
    """Rank request payload."""

    userid: str
    context: dict = Field(default_factory=dict)
    history: list[dict] = Field(default_factory=list)
    candidates: list[int] = Field(default_factory=list)
    topk: int = 50
    mode: Optional[str] = None  # catalog_matmul or semantic_id_ar


class rankresponse(BaseModel):
    """Rank response payload."""

    ids: list[int]
    scores: list[float]
    fallback: bool = False
    extras: dict = Field(default_factory=dict)
