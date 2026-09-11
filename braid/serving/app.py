"""FastAPI application factory for braid.

A small FastAPI surface that wires up the polymorphic concretes from a config.
It supports ``/rank``, ``/health``, ``/ready``, and ``/metrics``.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request

from braid.core.context import requestcontext
from braid.core.logging import getlogger


def createapp(
    *,
    server: Any | None = None,
    cache: Any | None = None,
    auth: Any | None = None,
    ratelimit: Any | None = None,
    reqpres: list[Any] | None = None,
    respposts: list[Any] | None = None,
    catalogstore: Any | None = None,
    metrics_backend: Any | None = None,
) -> FastAPI:
    """Build a FastAPI app wired up with braid concretes.

    Args:
        server: a registered ``server`` concrete (or None for fallback).
        cache: a registered ``cache`` concrete (or None).
        auth: a registered ``auth`` concrete.
        ratelimit: a registered ``ratelimit`` concrete.
        reqpres: list of request preprocessors.
        respposts: list of response postprocessors.
        catalogstore: a registered ``catalogstore`` concrete.
        metrics_backend: a registered ``metrics`` concrete.

    Returns:
        A FastAPI application.
    """
    app = FastAPI(title="braid ranker", version="0.1.0")
    log = getlogger("braid.app")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/ready")
    async def ready() -> dict[str, Any]:
        details: dict[str, Any] = {"server": "live" if server is not None else "degraded"}
        if server is not None and hasattr(server, "_engine") and server._engine is None:
            details["server"] = "degraded"
        return {"ready": True, "details": details}

    @app.get("/metrics")
    async def metrics_endpoint() -> dict[str, Any]:
        return {"messages": "prometheus scrape endpoint"}

    @app.post("/rank")
    async def rank(payload: dict[str, Any], req: Request) -> dict[str, Any]:
        ctx = requestcontext()
        if ratelimit is not None and not ratelimit.allow(ctx.requestid):
            raise HTTPException(status_code=429, detail="ratelimit")
        if auth is not None:
            token = req.headers.get("x-api-key") or req.headers.get("authorization", "")
            try:
                auth.authenticate(token)
            except Exception as exc:
                raise HTTPException(status_code=401, detail=str(exc)) from exc

        key = ctx.requestid + ":" + str(payload.get("userid"))
        if cache is not None:
            cached = cache.get(key)
            if cached is not None:
                log.info("rank.cachehit", key=key)
                return cached

        processed = payload
        for proc in reqpres or []:
            processed = proc.process(processed)
        prompt = processed.get("prompt") or ""
        topk = int(processed.get("topk", 50))

        if server is None:
            log.warning("server.none")
            response = {"ids": list(range(topk)), "scores": [0.0] * topk, "fallback": True}
        else:
            result = server.rank(
                prompt,
                lambda h: catalogstore.score(h) if catalogstore is not None else [0.0] * topk,
                topk=topk,
            )
            response = result

        for proc in respposts or []:
            try:
                response = proc.process(response)
            except Exception:  # noqa: BLE001
                continue

        if cache is not None:
            cache.put(key, response)
        if metrics_backend is not None:
            try:
                metrics_backend.counter("braid.rank.calls", 1.0)
            except Exception:  # noqa: BLE001
                pass
        return response

    return app


def main() -> None:
    """Run a default Uvicorn server."""
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    app = createapp()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
