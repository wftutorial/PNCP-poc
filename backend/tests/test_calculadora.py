"""Tests for P2 SEO: /v1/calculadora/dados and P3 SEO: /v1/empresa/{cnpj}/perfil-b2g."""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from routes.calculadora import _calc_cache
from routes.empresa_publica import _perfil_cache


@pytest.fixture(autouse=True)
def _clear_caches():
    _calc_cache.clear()
    _perfil_cache.clear()
    yield
    _calc_cache.clear()
    _perfil_cache.clear()


@pytest.fixture
def client():
    from startup.app_factory import create_app
    app = create_app()
    return TestClient(app)


# Patch target: datalake_query module (imported locally in route functions)
DL_PATCH = "datalake_query.query_datalake"


class TestCalculadoraDados:
    def test_valid_request(self, client):
        mock_results = [
            {"valorTotalEstimado": 100_000},
            {"valorTotalEstimado": 200_000},
            {"valorTotalEstimado": 300_000},
            {"valorTotalEstimado": 400_000},
            {"valorTotalEstimado": 500_000},
        ]

        with patch(DL_PATCH, new_callable=AsyncMock, return_value=mock_results):
            resp = client.get("/v1/calculadora/dados?setor=vestuario&uf=SP")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_editais_mes"] == 5
        assert data["avg_value"] == 300_000.0
        assert data["uf"] == "SP"
        assert "setor_name" in data
        assert "p25_value" in data
        assert "p75_value" in data

    def test_invalid_setor(self, client):
        resp = client.get("/v1/calculadora/dados?setor=inexistente&uf=SP")
        assert resp.status_code == 400

    def test_invalid_uf(self, client):
        resp = client.get("/v1/calculadora/dados?setor=vestuario&uf=XX")
        assert resp.status_code == 400

    def test_missing_params(self, client):
        resp = client.get("/v1/calculadora/dados")
        assert resp.status_code == 422

    def test_empty_datalake(self, client):
        with patch(DL_PATCH, new_callable=AsyncMock, return_value=[]):
            resp = client.get("/v1/calculadora/dados?setor=vestuario&uf=AC")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_editais_mes"] == 0
        assert data["avg_value"] == 0.0

    def test_cache_hit(self, client):
        mock_results = [{"valorTotalEstimado": 50_000}]

        with patch(DL_PATCH, new_callable=AsyncMock, return_value=mock_results) as mock_dl:
            client.get("/v1/calculadora/dados?setor=vestuario&uf=SP")
            client.get("/v1/calculadora/dados?setor=vestuario&uf=SP")

        assert mock_dl.call_count == 1

    def test_datalake_failure_graceful(self, client):
        with patch(DL_PATCH, new_callable=AsyncMock, side_effect=Exception("DB down")):
            resp = client.get("/v1/calculadora/dados?setor=vestuario&uf=SP")

        assert resp.status_code == 200
        assert resp.json()["total_editais_mes"] == 0

    def test_uf_case_insensitive(self, client):
        with patch(DL_PATCH, new_callable=AsyncMock, return_value=[]):
            resp = client.get("/v1/calculadora/dados?setor=vestuario&uf=sp")

        assert resp.status_code == 200
        assert resp.json()["uf"] == "SP"


class TestEmpresaPublica:
    BAPI_PATCH = "routes.empresa_publica._fetch_brasilapi"
    PT_PATCH = "routes.empresa_publica._fetch_contratos_pt"
    COUNT_PATCH = "routes.empresa_publica._fetch_editais_abertos"

    def test_invalid_cnpj_format(self, client):
        resp = client.get("/v1/empresa/123/perfil-b2g")
        assert resp.status_code == 400

    def test_sem_historico_profile(self, client):
        mock_bapi = {
            "razao_social": "Test Empresa",
            "cnae_fiscal": "4781",
            "porte": "ME",
            "uf": "SP",
            "descricao_situacao_cadastral": "ATIVA",
        }

        with patch(self.BAPI_PATCH, new_callable=AsyncMock, return_value=mock_bapi):
            with patch(self.PT_PATCH, new_callable=AsyncMock, return_value=[]):
                with patch(self.COUNT_PATCH, new_callable=AsyncMock, return_value=(42, [])):
                    resp = client.get("/v1/empresa/09225035000101/perfil-b2g")

        assert resp.status_code == 200
        data = resp.json()
        assert data["empresa"]["razao_social"] == "Test Empresa"
        assert data["score"] == "SEM_HISTORICO"
        assert data["editais_abertos_setor"] == 42

    def test_full_profile_ativo(self, client):
        mock_bapi = {
            "razao_social": "GJS Construções",
            "cnae_fiscal": "4120",
            "porte": "EPP",
            "uf": "SC",
            "descricao_situacao_cadastral": "ATIVA",
        }
        mock_contratos = [
            {
                "unidadeGestora": {"nome": "Prefeitura X", "uf": "SC"},
                "valorFinalCompra": 150_000,
                "dataInicioVigencia": "2025-06-01",
                "objeto": "Construção de escola",
            }
        ] * 6

        with patch(self.BAPI_PATCH, new_callable=AsyncMock, return_value=mock_bapi):
            with patch(self.PT_PATCH, new_callable=AsyncMock, return_value=mock_contratos):
                with patch(self.COUNT_PATCH, new_callable=AsyncMock, return_value=(15, [])):
                    resp = client.get("/v1/empresa/09225035000101/perfil-b2g")

        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == "ATIVO"
        assert data["total_contratos_24m"] == 6
        assert data["editais_abertos_setor"] == 15
        assert "SC" in data["ufs_atuacao"]

    def test_iniciante_profile(self, client):
        mock_bapi = {
            "razao_social": "Startup ABC",
            "cnae_fiscal": "6201",
            "porte": "ME",
            "uf": "RJ",
            "descricao_situacao_cadastral": "ATIVA",
        }
        mock_contratos = [
            {
                "unidadeGestora": {"nome": "Orgão Y", "uf": "RJ"},
                "valorFinalCompra": 50_000,
                "dataInicioVigencia": "2025-09-01",
                "objeto": "Desenvolvimento de sistema",
            }
        ] * 3

        with patch(self.BAPI_PATCH, new_callable=AsyncMock, return_value=mock_bapi):
            with patch(self.PT_PATCH, new_callable=AsyncMock, return_value=mock_contratos):
                with patch(self.COUNT_PATCH, new_callable=AsyncMock, return_value=(28, [])):
                    resp = client.get("/v1/empresa/12345678000199/perfil-b2g")

        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == "INICIANTE"
        assert data["setor_detectado"] == "informatica"

    def test_sem_historico_with_editais_amostra(self, client):
        mock_bapi = {
            "razao_social": "Empresa Teste",
            "cnae_fiscal": "4781",
            "porte": "ME",
            "uf": "SP",
            "descricao_situacao_cadastral": "ATIVA",
        }
        sample_bid = {
            "nomeOrgao": "PREFEITURA DE CAMPINAS",
            "objetoCompra": "Aquisição de uniformes escolares para rede municipal",
            "valorTotalEstimado": 85000.0,
            "dataEncerramentoProposta": "2026-05-15T23:59:00",
            "uf": "SP",
            "modalidadeNome": "Pregão Eletrônico",
        }

        with patch(self.BAPI_PATCH, new_callable=AsyncMock, return_value=mock_bapi):
            with patch(self.PT_PATCH, new_callable=AsyncMock, return_value=[]):
                with patch(self.COUNT_PATCH, new_callable=AsyncMock, return_value=(3, [sample_bid])):
                    resp = client.get("/v1/empresa/09225035000101/perfil-b2g")

        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == "SEM_HISTORICO"
        assert data["editais_abertos_setor"] == 3
        assert len(data["editais_amostra"]) == 1
        amostra = data["editais_amostra"][0]
        assert amostra["orgao"] == "PREFEITURA DE CAMPINAS"
        assert amostra["descricao"] == "Aquisição de uniformes escolares para rede municipal"
        assert amostra["valor_estimado"] == 85000.0
        assert amostra["data_encerramento"] == "2026-05-15"
        assert amostra["uf"] == "SP"
        assert amostra["modalidade"] == "Pregão Eletrônico"

    def test_editais_amostra_empty_for_ativo(self, client):
        mock_bapi = {
            "razao_social": "Empresa Ativa",
            "cnae_fiscal": "4120",
            "porte": "EPP",
            "uf": "MG",
            "descricao_situacao_cadastral": "ATIVA",
        }
        mock_contratos = [
            {
                "unidadeGestora": {"nome": "Orgão MG", "uf": "MG"},
                "valorFinalCompra": 200_000,
                "dataInicioVigencia": "2025-01-01",
                "objeto": "Obras diversas",
            }
        ] * 5

        with patch(self.BAPI_PATCH, new_callable=AsyncMock, return_value=mock_bapi):
            with patch(self.PT_PATCH, new_callable=AsyncMock, return_value=mock_contratos):
                with patch(self.COUNT_PATCH, new_callable=AsyncMock, return_value=(10, [])):
                    resp = client.get("/v1/empresa/09225035000101/perfil-b2g")

        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == "ATIVO"
        assert data["editais_amostra"] == []

    def test_editais_amostra_max_five(self, client):
        mock_bapi = {
            "razao_social": "Empresa Sem Hist",
            "cnae_fiscal": "4781",
            "porte": "ME",
            "uf": "SP",
            "descricao_situacao_cadastral": "ATIVA",
        }
        sample_bid = {
            "nomeOrgao": "ORGAO X",
            "objetoCompra": "Objeto qualquer",
            "valorTotalEstimado": 10000.0,
            "dataEncerramentoProposta": "2026-06-01",
            "uf": "SP",
            "modalidadeNome": "Dispensa",
        }
        # Simulate datalake returning 10 bids — backend should cap at 5
        ten_bids = [sample_bid] * 10

        with patch(self.BAPI_PATCH, new_callable=AsyncMock, return_value=mock_bapi):
            with patch(self.PT_PATCH, new_callable=AsyncMock, return_value=[]):
                with patch(self.COUNT_PATCH, new_callable=AsyncMock, return_value=(10, ten_bids)):
                    resp = client.get("/v1/empresa/09225035000101/perfil-b2g")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["editais_amostra"]) == 5
