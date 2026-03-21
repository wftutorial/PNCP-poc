"""Shared fixtures for scripts/tests/."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Ensure scripts/ is importable
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# COMMON FIXTURES
# ============================================================


@pytest.fixture
def sample_empresa():
    """A realistic construction company."""
    return {
        "cnpj": "01721078000168",
        "razao_social": "LCM Construcoes LTDA",
        "cnae_principal": "4120400",
        "cnaes_secundarios": ["4211101", "4321500"],
        "cidade_sede": "Florianopolis",
        "uf_sede": "SC",
        "sancionada": False,
        "sancoes": {},
    }


@pytest.fixture
def sample_empresa_sancionada(sample_empresa):
    """A sanctioned company."""
    return {**sample_empresa, "sancionada": True}


@pytest.fixture
def make_edital():
    """Factory to create an edital dict with sensible defaults."""

    def _make(
        objeto="Pavimentacao asfaltica em vias urbanas",
        uf="SC",
        municipio="Joinville",
        valor_estimado=1_500_000.0,
        status_temporal="PLANEJAVEL",
        analise=None,
        **kwargs,
    ):
        ed = {
            "objeto": objeto,
            "uf": uf,
            "municipio": municipio,
            "municipio_nome": municipio,
            "valor_estimado": valor_estimado,
            "status_temporal": status_temporal,
            "cnae_compatible": True,
            "data_abertura": "2026-04-15",
        }
        if analise is not None:
            ed["analise"] = analise
        ed.update(kwargs)
        return ed

    return _make


@pytest.fixture
def valid_analise():
    """A fully valid analysis dict that passes all gates."""
    return {
        "resumo_objeto": "Pavimentacao asfaltica em vias urbanas do municipio.",
        "requisitos_tecnicos": ["Acervo tecnico em pavimentacao asfaltica"],
        "requisitos_habilitacao": ["CND federal, estadual e municipal"],
        "qualificacao_economica": "Capital social minimo de R$ 150.000,00",
        "prazo_execucao": "180 dias corridos",
        "garantias": "5% do valor do contrato",
        "criterio_julgamento": "Menor Preco",
        "data_sessao": "15/04/2026",
        "prazo_proposta": "10/04/2026",
        "visita_tecnica": "Facultativa",
        "exclusividade_me_epp": "Nao",
        "regime_execucao": "Empreitada por preco global",
        "consorcio": "Vedado",
        "observacoes_criticas": "Edital compativel com perfil da empresa.",
        "nivel_dificuldade": "MEDIO",
        "recomendacao_acao": "PARTICIPAR",
        "custo_logistico_nota": "180 km da sede — custo moderado",
    }


@pytest.fixture
def make_top20(make_edital, valid_analise):
    """Create a list of N editais with valid analysis."""

    def _make(n=5, **edital_kwargs):
        editais = []
        for i in range(n):
            ed = make_edital(
                objeto=f"Obra de construcao #{i+1} no municipio",
                analise=dict(valid_analise),
                **edital_kwargs,
            )
            editais.append(ed)
        return editais

    return _make


@pytest.fixture
def write_json(tmp_path):
    """Write a dict to a temp JSON file and return the path."""

    def _write(data, filename="input.json"):
        p = tmp_path / filename
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    return _write


# ============================================================
# CNPJ FIXTURES
# ============================================================

@pytest.fixture
def valid_cnpj_raw() -> str:
    """Valid CNPJ with formatting."""
    return "01.721.078/0001-68"


@pytest.fixture
def valid_cnpj_clean() -> str:
    """Valid CNPJ digits only (14 chars)."""
    return "01721078000168"


@pytest.fixture
def invalid_cnpj_short() -> str:
    """Invalid CNPJ (too short)."""
    return "1234567890"


# ============================================================
# UF FIXTURES
# ============================================================

@pytest.fixture
def sample_ufs() -> list[str]:
    """Standard UF list for tests."""
    return ["SC", "PR", "RS"]


# ============================================================
# OPENCNPJ RESPONSE FIXTURES
# ============================================================

@pytest.fixture
def sample_opencnpj_response() -> dict:
    """Realistic OpenCNPJ API response for a construction company."""
    return {
        "cnpj": "01721078000168",
        "razao_social": "LCM CONSTRUCOES E SERVICOS LTDA",
        "nome_fantasia": "LCM CONSTRUCOES",
        "capital_social": "1232000,00",
        "porte": "EMPRESA DE PEQUENO PORTE",
        "cnae_fiscal": 4120400,
        "cnae_fiscal_descricao": "Construcao de edificios",
        "cnaes_secundarios": ["4211101", "4213800", "4291000"],
        "uf": "SC",
        "municipio": "FLORIANOPOLIS",
    }


# ============================================================
# PNCP API RESPONSE FIXTURES
# ============================================================

@pytest.fixture
def sample_pncp_item() -> dict:
    """Single realistic PNCP API item (contratacao)."""
    now = datetime.now(timezone.utc)
    future_date = (now + timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%S")
    pub_date = (now - timedelta(days=5)).strftime("%Y-%m-%d")
    return {
        "orgaoEntidade": {
            "cnpj": "83.102.459/0001-52",
            "razaoSocial": "PREFEITURA MUNICIPAL DE CHAPECO",
        },
        "unidadeOrgao": {
            "ufSigla": "SC",
            "municipioNome": "Chapeco",
            "nomeUnidade": "Secretaria de Obras",
        },
        "anoCompra": "2026",
        "sequencialCompra": "42",
        "objetoCompra": "Construcao de unidades habitacionais no bairro Efapi",
        "valorTotalEstimado": 2500000.00,
        "modalidadeNome": "Concorrencia - Eletronica",
        "dataPublicacaoPncp": pub_date,
        "dataAberturaProposta": future_date,
        "dataEncerramentoProposta": (now + timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%S"),
        "linkSistemaOrigem": "",
    }


@pytest.fixture
def sample_pncp_response(sample_pncp_item) -> list[dict]:
    """PNCP API response: list of items."""
    return [sample_pncp_item]


@pytest.fixture
def sample_pncp_empty_response() -> list[dict]:
    """Empty PNCP API response."""
    return []


# ============================================================
# EDITAL FIXTURES (for intel-collect tests)
# ============================================================

@pytest.fixture
def sample_editais_intel() -> list[dict]:
    """5 realistic edital dicts as they appear after PNCP parsing in intel-collect."""
    now = datetime.now(timezone.utc)
    return [
        {
            "_id": "83102459000152/2026/42",
            "objeto": "Construcao de unidades habitacionais no bairro Efapi",
            "orgao": "PREFEITURA MUNICIPAL DE CHAPECO",
            "cnpj_orgao": "83102459000152",
            "uf": "SC",
            "municipio": "Chapeco",
            "valor_estimado": 2500000.00,
            "modalidade_code": 4,
            "modalidade_nome": "Concorrencia - Eletronica",
            "data_publicacao": (now - timedelta(days=5)).strftime("%Y-%m-%d"),
            "data_abertura_proposta": (now + timedelta(days=15)).isoformat(),
            "data_encerramento_proposta": (now + timedelta(days=20)).isoformat(),
            "link_pncp": "https://pncp.gov.br/app/editais/83102459000152/2026/42",
            "ano_compra": "2026",
            "sequencial_compra": "42",
            "_dedup_key": "83102459000152/2026/42",
            "status_temporal": "PLANEJAVEL",
            "dias_restantes": 20,
        },
        {
            "_id": "79373767000148/2026/15",
            "objeto": "Pavimentacao asfaltica em CBUQ de vias urbanas no municipio",
            "orgao": "PREFEITURA MUNICIPAL DE JOINVILLE",
            "cnpj_orgao": "79373767000148",
            "uf": "SC",
            "municipio": "Joinville",
            "valor_estimado": 1800000.00,
            "modalidade_code": 5,
            "modalidade_nome": "Pregao Eletronico",
            "data_publicacao": (now - timedelta(days=3)).strftime("%Y-%m-%d"),
            "data_abertura_proposta": (now + timedelta(days=10)).isoformat(),
            "data_encerramento_proposta": (now + timedelta(days=12)).isoformat(),
            "link_pncp": "https://pncp.gov.br/app/editais/79373767000148/2026/15",
            "ano_compra": "2026",
            "sequencial_compra": "15",
            "_dedup_key": "79373767000148/2026/15",
            "status_temporal": "IMINENTE",
            "dias_restantes": 12,
        },
        {
            "_id": "76535764000143/2026/8",
            "objeto": "Reforma e ampliacao da escola municipal Professor Anisio Teixeira",
            "orgao": "PREFEITURA MUNICIPAL DE CURITIBA",
            "cnpj_orgao": "76535764000143",
            "uf": "PR",
            "municipio": "Curitiba",
            "valor_estimado": 5200000.00,
            "modalidade_code": 4,
            "modalidade_nome": "Concorrencia - Eletronica",
            "data_publicacao": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
            "data_abertura_proposta": (now + timedelta(days=25)).isoformat(),
            "data_encerramento_proposta": (now + timedelta(days=30)).isoformat(),
            "link_pncp": "https://pncp.gov.br/app/editais/76535764000143/2026/8",
            "ano_compra": "2026",
            "sequencial_compra": "8",
            "_dedup_key": "76535764000143/2026/8",
            "status_temporal": "PLANEJAVEL",
            "dias_restantes": 30,
        },
        {
            "_id": "92963560000160/2026/3",
            "objeto": "Aquisicao de medicamentos para a rede municipal de saude",
            "orgao": "PREFEITURA MUNICIPAL DE PORTO ALEGRE",
            "cnpj_orgao": "92963560000160",
            "uf": "RS",
            "municipio": "Porto Alegre",
            "valor_estimado": 800000.00,
            "modalidade_code": 5,
            "modalidade_nome": "Pregao Eletronico",
            "data_publicacao": (now - timedelta(days=2)).strftime("%Y-%m-%d"),
            "data_abertura_proposta": (now + timedelta(days=5)).isoformat(),
            "data_encerramento_proposta": (now + timedelta(days=7)).isoformat(),
            "link_pncp": "https://pncp.gov.br/app/editais/92963560000160/2026/3",
            "ano_compra": "2026",
            "sequencial_compra": "3",
            "_dedup_key": "92963560000160/2026/3",
            "status_temporal": "URGENTE",
            "dias_restantes": 7,
        },
        {
            "_id": "11111111000100/2026/99",
            "objeto": "Contratacao de servicos de limpeza e conservacao predial",
            "orgao": "SECRETARIA DE ADMINISTRACAO",
            "cnpj_orgao": "11111111000100",
            "uf": "PR",
            "municipio": "Londrina",
            "valor_estimado": 300000.00,
            "modalidade_code": 5,
            "modalidade_nome": "Pregao Eletronico",
            "data_publicacao": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
            "data_abertura_proposta": (now + timedelta(days=8)).isoformat(),
            "data_encerramento_proposta": (now + timedelta(days=10)).isoformat(),
            "link_pncp": "https://pncp.gov.br/app/editais/11111111000100/2026/99",
            "ano_compra": "2026",
            "sequencial_compra": "99",
            "_dedup_key": "11111111000100/2026/99",
            "status_temporal": "URGENTE",
            "dias_restantes": 10,
        },
    ]


# ============================================================
# INTEL JSON STRUCTURE FIXTURE
# ============================================================

@pytest.fixture
def sample_intel_json(sample_editais_intel) -> dict:
    """Minimal valid intel JSON structure (as saved by intel-collect.py)."""
    return {
        "empresa": {
            "razao_social": "LCM CONSTRUCOES E SERVICOS LTDA",
            "cnpj": "01721078000168",
            "cnae_principal": "4120400",
            "capital_social": "1232000,00",
            "uf_sede": "SC",
            "sancionada": False,
            "sicaf": {"status": "OK"},
            "_source": {"status": "API"},
        },
        "busca": {
            "cnpj": "01.721.078/0001-68",
            "ufs": ["SC", "PR", "RS"],
            "dias": 30,
            "data_inicio": "2026-02-18",
            "data_fim": "2026-03-20",
            "modalidades": [4, 5, 6],
            "setor": "Engenharia e Obras",
            "sector_key": "engenharia_obras",
            "keywords_count": 150,
            "keywords_sample": ["construcao", "obra", "reforma"],
        },
        "estatisticas": {
            "total_bruto": 500,
            "total_expirados_removidos": 100,
            "total_apos_filtro_temporal": 400,
            "total_cnae_compativel": 50,
            "total_cnae_incompativel": 350,
            "total_needs_llm_review": 0,
            "valor_total_compativel": 150000000.00,
            "pncp_pages_fetched": 200,
            "pncp_errors": 2,
            "pncp_pagination_exhausted": [],
            "status_temporal": {"PLANEJAVEL": 30, "IMINENTE": 10, "URGENTE": 10},
        },
        "editais": sample_editais_intel,
        "_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "script": "intel-collect.py",
            "version": "1.2.0",
        },
    }


# ============================================================
# HTTPX MOCK HELPERS
# ============================================================

class MockHttpxResponse:
    """Lightweight mock for httpx.Response."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: Any = None,
        text: str = "",
        headers: dict | None = None,
    ):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text or (json.dumps(json_data, ensure_ascii=False) if json_data else "")
        self.headers = headers or {}

    def json(self) -> Any:
        if self._json_data is not None:
            return self._json_data
        return json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


@pytest.fixture
def mock_httpx_response():
    """Factory fixture for creating mock httpx responses."""
    def _factory(status_code=200, json_data=None, text="", headers=None):
        return MockHttpxResponse(
            status_code=status_code,
            json_data=json_data,
            text=text,
            headers=headers,
        )
    return _factory


# ============================================================
# MOCK API CLIENT
# ============================================================

@pytest.fixture
def mock_api_client():
    """Mock ApiClient that returns configurable responses.

    Usage:
        client = mock_api_client
        client.responses[url_substring] = (data, status_string)
    """
    client = MagicMock()
    client.responses = {}
    client._call_count = 0

    def _mock_get(url, params=None, label=""):
        client._call_count += 1
        for url_substr, (data, status) in client.responses.items():
            if url_substr in url:
                return data, status
        return None, "API_FAILED"

    client.get = MagicMock(side_effect=_mock_get)
    client.close = MagicMock()
    client.print_stats = MagicMock()
    return client


# ============================================================
# TEMP FILE FIXTURES
# ============================================================

@pytest.fixture
def output_dir(tmp_path) -> Path:
    """Temp directory for test output files."""
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture
def intel_json_file(tmp_path, sample_intel_json) -> Path:
    """Write sample intel JSON to a temp file and return its path."""
    p = tmp_path / "intel-01721078000168-test-2026-03-20.json"
    p.write_text(json.dumps(sample_intel_json, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
