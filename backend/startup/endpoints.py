"""startup/endpoints.py — Root-level endpoint definitions (DEBT-107).

Endpoints that live directly on the app (not inside a router):
  GET /             — API root / navigation
  GET /v1/setores   — Sector list for frontend dropdown

NOTE: GET /debug/pncp-test is registered directly in main.py so that
test monkeypatching of ``main.PNCPClient`` continues to work (DEBT-015).
"""

import os

from fastapi import FastAPI

from schemas import RootResponse, SetoresResponse
from sectors import list_sectors

APP_VERSION = os.getenv("APP_VERSION", "dev")


def register_endpoints(app: FastAPI) -> None:
    """Attach root endpoints to *app* (excluding /debug/pncp-test, see module docstring)."""

    @app.get("/", response_model=RootResponse)
    async def root():
        """API root — navigation and version info."""
        return {
            "name": "SmartLic API",
            "version": APP_VERSION,
            "api_version": "v1",
            "description": "API para busca e análise de licitações em fontes oficiais",
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "health": "/health",
                "openapi": "/openapi.json",
                "v1_api": "/v1",
            },
            "versioning": {
                "current": "v1",
                "supported": ["v1"],
                "deprecated": [],
                "note": "All endpoints at /v1/<endpoint>. Legacy root paths removed (TD-004).",
            },
            "status": "operational",
        }

    @app.get("/v1/setores", response_model=SetoresResponse)
    async def listar_setores():
        """Return available procurement sectors for frontend dropdown."""
        return {"setores": list_sectors()}
