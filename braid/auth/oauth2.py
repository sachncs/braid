"""OAuth2 authentication."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.error import validationerror


@registry.register(category="auth", name="oauth2")
class oauth2:
    """OAuth2 token-introspection authentication."""

    name: str = "oauth2"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, introspectionurl: str, clientid: str, clientsecret: str) -> None:
        self.introspectionurl = introspectionurl
        self.clientid = clientid
        self.clientsecret = clientsecret

    async def authenticate(self, token: str) -> dict[str, Any]:
        """Async OAuth2 token introspection."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.introspectionurl,
                    data={"token": token},
                    auth=aiohttp.BasicAuth(self.clientid, self.clientsecret),
                ) as resp:
                    data = await resp.json()
            if not data.get("active"):
                raise validationerror("oauth2 token inactive", retryable=False)
            return {"principal": data.get("username", "anon"), "claims": data, "kind": "oauth2"}
        except Exception as exc:  # noqa: BLE001
            raise validationerror(f"oauth2 introspection failed: {exc}", retryable=True) from exc

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
