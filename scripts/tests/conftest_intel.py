"""
Shared fixtures for intel-excel, intel-report, and intel-enrich tests.

Provides sample data structures matching the JSON format produced by
intel-collect.py and consumed by the three scripts.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure scripts/ and scripts/lib/ are importable
_scripts_dir = str(Path(__file__).resolve().parent.parent)
_lib_dir = str(Path(__file__).resolve().parent.parent / "lib")
for d in (_scripts_dir, _lib_dir):
    if d not in sys.path:
        sys.path.insert(0, d)


# ── Minimal valid empresa dict ──────────────────────────────────


def make_empresa(**overrides: Any) -> dict:
    base = {
        "cnpj": "12345678000199",
        "razao_social": "Empresa Teste LTDA",
        "nome_fantasia": "Empresa Teste",
        "cnae_principal": "4120400",
        "cnae_descricao": "Construcao de edificios",
        "cnae_principal_descricao": "Construcao de edificios",
        "capital_social": 500000.0,
        "cidade_sede": "Florianopolis",
        "municipio": "Florianopolis",
        "uf_sede": "SC",
        "uf": "SC",
        "cnaes_secundarios": "4211101,4313400",
        "sicaf": {"status": "ATIVO", "crc_status": "REGULAR"},
        "sancoes": {"sancionada": False},
        "sancionada": False,
        "restricao_sicaf": False,
    }
    base.update(overrides)
    return base


# ── Minimal valid edital dict ────────────────────────────────────


def make_edital(idx: int = 1, **overrides: Any) -> dict:
    base = {
        "_id": f"ed-{idx:04d}",
        "objeto": f"Construcao de escola municipal fase {idx}",
        "objetoCompra": f"Construcao de escola municipal fase {idx}",
        "orgao": f"Prefeitura Municipal de Cidade {idx}",
        "nomeOrgao": f"Prefeitura Municipal de Cidade {idx}",
        "uf": "SC",
        "municipio": f"Cidade{idx}",
        "valor_estimado": 1_000_000.0 + idx * 100_000,
        "modalidade_nome": "Concorrencia Eletronica",
        "modalidadeNome": "Concorrencia Eletronica",
        "data_publicacao": "2026-03-01",
        "dataPublicacaoPncp": "2026-03-01",
        "data_abertura_proposta": "2026-03-20T10:00:00",
        "dataAberturaProposta": "2026-03-20T10:00:00",
        "data_encerramento_proposta": "2026-03-25T18:00:00",
        "dataEncerramentoProposta": "2026-03-25T18:00:00",
        "cnae_compatible": True,
        "cnae_confidence": 0.85,
        "keyword_density": 0.12,
        "status_temporal": "PLANEJAVEL",
        "dias_restantes": 15,
        "link_pncp": f"https://pncp.gov.br/app/editais/12345678000199/2026/{idx}",
        "link": f"https://pncp.gov.br/app/editais/12345678000199/2026/{idx}",
        "sector_name": "Engenharia e Obras Publicas",
        "setor": "Engenharia e Obras Publicas",
        "match_keywords": ["construcao", "obra"],
        "distancia": {"km": 150.0, "duracao_horas": 2.5},
        "custo_proposta": {"total": 2500.0, "modalidade_tipo": "presencial"},
        "roi_proposta": {"classificacao": "BOM", "ratio_valor_custo": 400},
        "ibge": {"populacao": 50000, "pib_mil_reais": 1200000},
        "competitive_intel": {
            "competition_level": "MEDIA",
            "unique_suppliers": 8,
            "top_suppliers": [{"nome": "Construtora ABC", "share": 0.25}],
            "hhi": 0.15,
        },
        "price_benchmark": {
            "contratos_analisados": 5,
            "valor_sugerido_min": 900000,
            "valor_sugerido_max": 1100000,
            "desconto_mediano_orgao": 0.12,
        },
        "_delta_status": "",
        "_victory_fit_label": "Bom",
    }
    base.update(overrides)
    return base


def make_edital_with_analise(idx: int = 1, **overrides: Any) -> dict:
    ed = make_edital(idx, **overrides)
    ed["analise"] = {
        "resumo_objeto": f"Construcao de escola com {idx} salas de aula",
        "requisitos_tecnicos": ["Acervo tecnico em construcao civil", "RT de engenheiro"],
        "requisitos_habilitacao": ["CND FGTS", "CND Trabalhista", "Balanco patrimonial"],
        "qualificacao_economica": "Capital social minimo 10% do valor",
        "garantias": "5% do valor do contrato",
        "prazo_execucao": "12 meses",
        "criterio_julgamento": "Menor preco",
        "regime_execucao": "Empreitada por preco global",
        "visita_tecnica": "Facultativa",
        "consorcio": "Permitido",
        "observacoes_criticas": "",
        "recomendacao_acao": "PARTICIPAR",
        "nivel_dificuldade": "MEDIO",
        "data_sessao": "25/03/2026 as 10:00h",
        "prazo_proposta": "25/03/2026",
    }
    return ed


# ── Full JSON data structure ─────────────────────────────────────


def make_intel_data(
    n_editais: int = 5,
    n_top20: int = 3,
    with_analise: bool = True,
    **overrides: Any,
) -> dict:
    editais = [make_edital(i) for i in range(1, n_editais + 1)]
    top20 = []
    for i in range(1, min(n_top20, n_editais) + 1):
        if with_analise:
            top20.append(make_edital_with_analise(i))
        else:
            top20.append(make_edital(i))

    data = {
        "empresa": make_empresa(),
        "busca": {
            "ufs": ["SC", "PR", "RS"],
            "setor": "engenharia_obras",
            "setor_mapeado": "Engenharia e Obras Publicas",
            "data_inicio": "2026-03-01",
            "data_fim": "2026-03-20",
            "dias": 20,
        },
        "editais": editais,
        "top20": top20,
        "estatisticas": {
            "total_bruto": n_editais * 10,
            "total_expirados_removidos": n_editais * 2,
            "total_apos_filtro_temporal": n_editais * 8,
            "total_cnae_compativel": n_editais,
            "total_dentro_capacidade": n_editais - 1,
            "total_analisados_profundidade": min(20, n_editais),
        },
        "stats": {
            "total_bruto": n_editais * 10,
            "total_pncp": n_editais * 10,
        },
        "_metadata": {
            "version": "1.0.0",
            "collected_at": "2026-03-20T10:00:00Z",
        },
        "meta": {},
    }
    data.update(overrides)
    return data


# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def sample_data() -> dict:
    """Standard test data with 5 editais and 3 top20 with analysis."""
    return make_intel_data(n_editais=5, n_top20=3, with_analise=True)


@pytest.fixture
def sample_json_file(tmp_path: Path, sample_data: dict) -> Path:
    """Write sample data to a JSON file and return the path."""
    path = tmp_path / "test-input.json"
    path.write_text(json.dumps(sample_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


@pytest.fixture
def empty_data() -> dict:
    """Data structure with zero editais."""
    return make_intel_data(n_editais=0, n_top20=0)


@pytest.fixture
def large_data() -> dict:
    """Data structure with 120 editais for large dataset tests."""
    return make_intel_data(n_editais=120, n_top20=20, with_analise=True)
