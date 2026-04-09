"""Tests for GET /v1/blog/daily/* (Wave 3.2 — Daily Digest)."""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.fixture
def client():
    from main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    from routes.daily_digest import _daily_cache
    _daily_cache.clear()
    yield
    _daily_cache.clear()


MOCK_RESULTS = [
    {
        "objeto": "Pregao eletronico para aquisicao de computadores",
        "objetoCompra": "Pregao eletronico para aquisicao de computadores",
        "valorTotalEstimado": 500000.0,
        "uf": "SP",
        "codigoModalidadeContratacao": 5,
        "orgaoEntidade": {"razaoSocial": "Min Educacao"},
    },
    {
        "objeto": "Servico de limpeza e conservacao predial",
        "objetoCompra": "Servico de limpeza e conservacao predial",
        "valorTotalEstimado": 120000.0,
        "uf": "RJ",
        "codigoModalidadeContratacao": 5,
        "orgaoEntidade": {"razaoSocial": "Sec Fazenda"},
    },
    {
        "objeto": "Fornecimento de alimentos para merenda escolar",
        "objetoCompra": "Fornecimento de alimentos para merenda escolar",
        "valorTotalEstimado": 80000.0,
        "uf": "MG",
        "codigoModalidadeContratacao": 12,
        "orgaoEntidade": {"razaoSocial": "Pref Municipal"},
    },
]


class TestDailyDigestLatest:
    def test_latest_returns_200(self, client):
        with patch("datalake_query.query_datalake", new_callable=AsyncMock, return_value=MOCK_RESULTS):
            resp = client.get("/v1/blog/daily/latest")
        assert resp.status_code == 200
        data = resp.json()
        assert "date" in data
        assert data["total_bids"] == 3
        assert data["total_value"] == 700000.0
        assert len(data["by_sector"]) > 0
        assert len(data["by_uf"]) > 0
        assert len(data["by_modalidade"]) > 0
        assert "highlights" in data

    def test_latest_empty_results(self, client):
        with patch("datalake_query.query_datalake", new_callable=AsyncMock, return_value=[]):
            resp = client.get("/v1/blog/daily/latest")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_bids"] == 0
        assert data["total_value"] == 0.0


class TestDailyDigestByDate:
    def test_valid_date_returns_200(self, client):
        with patch("datalake_query.query_datalake", new_callable=AsyncMock, return_value=MOCK_RESULTS):
            resp = client.get("/v1/blog/daily/2026-04-07")
        assert resp.status_code == 200
        data = resp.json()
        assert data["date"] == "2026-04-07"
        assert data["total_bids"] == 3

    def test_invalid_date_format_returns_400(self, client):
        resp = client.get("/v1/blog/daily/not-a-date")
        assert resp.status_code == 400

    def test_invalid_date_month_returns_400(self, client):
        resp = client.get("/v1/blog/daily/2026-13-01")
        assert resp.status_code == 400

    def test_highlights_sorted_by_value(self, client):
        with patch("datalake_query.query_datalake", new_callable=AsyncMock, return_value=MOCK_RESULTS):
            resp = client.get("/v1/blog/daily/2026-04-07")
        data = resp.json()
        highlights = data["highlights"]
        if len(highlights) >= 2:
            assert highlights[0]["valor"] >= highlights[1]["valor"]

    def test_modalidade_pct_sum(self, client):
        with patch("datalake_query.query_datalake", new_callable=AsyncMock, return_value=MOCK_RESULTS):
            resp = client.get("/v1/blog/daily/2026-04-06")
        data = resp.json()
        total_pct = sum(m["pct"] for m in data["by_modalidade"])
        assert 99.0 <= total_pct <= 101.0 or data["total_bids"] == 0
