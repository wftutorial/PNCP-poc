"""Tests for SYS-036: OpenAPI Documentation Access Control.

Tests that /docs, /redoc, and /openapi.json are:
- Accessible when DOCS_ACCESS_TOKEN is not set (development)
- Protected by bearer token when DOCS_ACCESS_TOKEN is set (production)
- Accessible via query param ?token= as browser-friendly alternative

Uses a standalone FastAPI app to avoid lifespan signal issues in tests.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


def _make_app(docs_access_token: str = "") -> FastAPI:
    """Create a minimal FastAPI app with the docs guard middleware."""
    app = FastAPI(
        title="SmartLic API",
        description="API para busca e analise de licitacoes em fontes oficiais brasileiras.",
        version="test",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {"name": "admin", "description": "Admin endpoints"},
            {"name": "feature-flags", "description": "Feature flag management"},
        ],
    )

    _docs_paths = frozenset({"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"})

    @app.middleware("http")
    async def docs_access_guard(request: Request, call_next):
        """SYS-036: Gate OpenAPI docs behind DOCS_ACCESS_TOKEN bearer."""
        path = request.url.path
        if path in _docs_paths and docs_access_token:
            auth_header = request.headers.get("Authorization", "")
            query_token = request.query_params.get("token", "")
            if auth_header == f"Bearer {docs_access_token}" or query_token == docs_access_token:
                return await call_next(request)
            return JSONResponse(
                status_code=401,
                content={"detail": "API docs access requires DOCS_ACCESS_TOKEN."},
            )
        return await call_next(request)

    @app.get("/")
    async def root():
        return {"status": "ok"}

    @app.get("/health/live")
    async def health_live():
        return {"status": "ok"}

    return app


@pytest.fixture
def client_no_token():
    """Client with DOCS_ACCESS_TOKEN unset (development mode)."""
    app = _make_app(docs_access_token="")
    return TestClient(app)


@pytest.fixture
def client_with_token():
    """Client with DOCS_ACCESS_TOKEN set (production mode)."""
    app = _make_app(docs_access_token="test-docs-secret-123")
    return TestClient(app)


class TestDocsAccessOpen:
    """When DOCS_ACCESS_TOKEN is not set, docs should be open."""

    def test_docs_accessible(self, client_no_token):
        resp = client_no_token.get("/docs")
        assert resp.status_code == 200

    def test_redoc_accessible(self, client_no_token):
        resp = client_no_token.get("/redoc")
        assert resp.status_code == 200

    def test_openapi_json_accessible(self, client_no_token):
        resp = client_no_token.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["info"]["title"] == "SmartLic API"


class TestDocsAccessProtected:
    """When DOCS_ACCESS_TOKEN is set, docs require authentication."""

    def test_docs_blocked_without_token(self, client_with_token):
        resp = client_with_token.get("/docs")
        assert resp.status_code == 401

    def test_redoc_blocked_without_token(self, client_with_token):
        resp = client_with_token.get("/redoc")
        assert resp.status_code == 401

    def test_openapi_json_blocked_without_token(self, client_with_token):
        resp = client_with_token.get("/openapi.json")
        assert resp.status_code == 401

    def test_docs_accessible_with_bearer(self, client_with_token):
        resp = client_with_token.get(
            "/docs",
            headers={"Authorization": "Bearer test-docs-secret-123"},
        )
        assert resp.status_code == 200

    def test_redoc_accessible_with_bearer(self, client_with_token):
        resp = client_with_token.get(
            "/redoc",
            headers={"Authorization": "Bearer test-docs-secret-123"},
        )
        assert resp.status_code == 200

    def test_openapi_json_accessible_with_bearer(self, client_with_token):
        resp = client_with_token.get(
            "/openapi.json",
            headers={"Authorization": "Bearer test-docs-secret-123"},
        )
        assert resp.status_code == 200

    def test_docs_accessible_with_query_param(self, client_with_token):
        resp = client_with_token.get("/docs?token=test-docs-secret-123")
        assert resp.status_code == 200

    def test_openapi_json_accessible_with_query_param(self, client_with_token):
        resp = client_with_token.get("/openapi.json?token=test-docs-secret-123")
        assert resp.status_code == 200

    def test_docs_rejected_with_wrong_token(self, client_with_token):
        resp = client_with_token.get(
            "/docs",
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert resp.status_code == 401

    def test_docs_rejected_with_wrong_query_param(self, client_with_token):
        resp = client_with_token.get("/docs?token=wrong-token")
        assert resp.status_code == 401


class TestOpenAPIMetadata:
    """Verify OpenAPI schema has proper metadata."""

    def test_schema_has_title(self, client_no_token):
        resp = client_no_token.get("/openapi.json")
        data = resp.json()
        assert data["info"]["title"] == "SmartLic API"

    def test_schema_has_description(self, client_no_token):
        resp = client_no_token.get("/openapi.json")
        data = resp.json()
        assert "licitacoes" in data["info"]["description"].lower()

    def test_schema_has_version(self, client_no_token):
        resp = client_no_token.get("/openapi.json")
        data = resp.json()
        assert "version" in data["info"]

    def test_schema_has_tags(self, client_no_token):
        resp = client_no_token.get("/openapi.json")
        data = resp.json()
        assert "tags" in data
        tag_names = [t["name"] for t in data["tags"]]
        assert "admin" in tag_names
        assert "feature-flags" in tag_names

    def test_non_docs_paths_unaffected(self, client_with_token):
        """Other endpoints should not be blocked by docs guard."""
        resp = client_with_token.get("/")
        assert resp.status_code == 200

    def test_health_unaffected(self, client_with_token):
        """Health endpoints should not be affected by docs guard."""
        resp = client_with_token.get("/health/live")
        assert resp.status_code == 200
