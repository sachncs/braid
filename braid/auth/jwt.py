"""JWT authentication."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.error import validationerror


@registry.register(category="auth", name="jwt")
class jwt:
    """HS256 JWT authentication."""

    name: str = "jwt"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, secret: str, algorithm: str = "HS256") -> None:
        self.secret = secret
        self.algorithm = algorithm

    def authenticate(self, token: str) -> dict[str, Any]:
        """Decode and verify a JWT; return the principal claims."""
        try:
            import jwt as pyjwt

            claims = pyjwt.decode(token, self.secret, algorithms=[self.algorithm])
            return {"principal": claims.get("sub", "anon"), "claims": claims, "kind": "jwt"}
        except Exception as exc:  # noqa: BLE001
            raise validationerror(f"invalid jwt: {exc}", retryable=False) from exc

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
