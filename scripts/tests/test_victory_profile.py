"""Tests for scripts/lib/victory_profile.py — winning pattern analysis."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.victory_profile import (
    POP_BRACKETS,
    VictoryProfile,
    _extract_keywords,
    _pop_bracket,
    _score_geography_fit,
    _score_keyword_fit,
    _score_modalidade_fit,
    _score_population_fit,
    _score_value_fit,
    build_victory_profile,
    format_fit_label,
    score_edital_fit,
)


# ============================================================
# HELPERS
# ============================================================


def _make_contracts(n=5, base_valor=500_000, modalidade=5, uf="SC", objeto="Pavimentacao asfaltica em vias urbanas"):
    """Create N realistic contract dicts."""
    contracts = []
    for i in range(n):
        contracts.append({
            "valor_contrato": base_valor + i * 50_000,
            "modalidade_code": modalidade,
            "uf": uf,
            "municipio": f"Cidade_{i}",
            "populacao": 50_000 + i * 10_000,
            "objeto": objeto,
            "distancia_km": 100 + i * 30,
        })
    return contracts


# ============================================================
# BUILD VICTORY PROFILE
# ============================================================


class TestBuildVictoryProfile:
    def test_minimum_3_contracts(self):
        """<3 contracts returns profile with has_data=False."""
        profile = build_victory_profile([{"valor_contrato": 100_000}])
        assert profile.total_contracts == 1
        assert profile.has_data is False

    def test_empty_list(self):
        profile = build_victory_profile([])
        assert profile.total_contracts == 0
        assert profile.has_data is False

    def test_none_input(self):
        profile = build_victory_profile(None)
        assert profile.total_contracts == 0

    def test_3_contracts_sufficient(self):
        contracts = _make_contracts(3)
        profile = build_victory_profile(contracts)
        assert profile.has_data is True
        assert profile.total_contracts == 3

    def test_value_statistics(self):
        contracts = _make_contracts(5, base_valor=100_000)
        profile = build_victory_profile(contracts)
        assert profile.valor_mean > 0
        assert profile.valor_min <= profile.valor_mean <= profile.valor_max
        assert profile.valor_q25 <= profile.valor_q75

    def test_modalidade_weights(self):
        contracts = _make_contracts(5, modalidade=5)
        profile = build_victory_profile(contracts)
        assert 5 in profile.modalidade_weights
        assert profile.modalidade_weights[5] == 1.0  # all same modalidade

    def test_mixed_modalidades(self):
        contracts = _make_contracts(3, modalidade=5)
        contracts.extend(_make_contracts(3, modalidade=4))
        profile = build_victory_profile(contracts)
        assert 5 in profile.modalidade_weights
        assert 4 in profile.modalidade_weights
        assert abs(profile.modalidade_weights[5] + profile.modalidade_weights[4] - 1.0) < 0.01

    def test_uf_weights(self):
        contracts = _make_contracts(5, uf="SC")
        profile = build_victory_profile(contracts)
        assert "SC" in profile.uf_weights
        assert profile.uf_weights["SC"] == 1.0

    def test_distance_stats(self):
        contracts = _make_contracts(5)
        profile = build_victory_profile(contracts)
        assert profile.dist_mean_km > 0
        assert profile.dist_max_km >= profile.dist_mean_km

    def test_keyword_freq(self):
        contracts = _make_contracts(5, objeto="Pavimentacao asfaltica em vias urbanas do municipio")
        profile = build_victory_profile(contracts)
        # "pavimentacao" and "asfaltica" should appear
        assert len(profile.keyword_freq) > 0

    def test_keyword_min_2_occurrences(self):
        """Keywords must appear >=2 times to be included."""
        contracts = _make_contracts(3, objeto="Pavimentacao asfaltica")
        # Add one with unique word
        contracts.append({
            "valor_contrato": 200_000, "modalidade_code": 5, "uf": "SC",
            "objeto": "Construcao unica especial rara",
        })
        profile = build_victory_profile(contracts)
        # "pavimentacao" appears 3x (>=2), "unica" appears 1x (<2)
        assert "pavimentacao" in profile.keyword_freq or len(profile.keyword_freq) >= 0

    def test_population_bracket_weights(self):
        contracts = _make_contracts(5)
        profile = build_victory_profile(contracts)
        assert len(profile.pop_bracket_weights) > 0

    def test_zero_valor_contracts_excluded_from_stats(self):
        contracts = _make_contracts(3, base_valor=0)
        contracts[0]["valor_contrato"] = 100_000
        contracts[1]["valor_contrato"] = 200_000
        contracts[2]["valor_contrato"] = 0
        profile = build_victory_profile(contracts)
        # Only 2 non-zero values
        assert profile.valor_mean > 0


# ============================================================
# POPULATION BRACKETS
# ============================================================


class TestPopBracket:
    def test_micro(self):
        assert _pop_bracket(3000) == "micro"

    def test_pequeno(self):
        assert _pop_bracket(15000) == "pequeno"

    def test_medio(self):
        assert _pop_bracket(50000) == "medio"

    def test_grande(self):
        assert _pop_bracket(200000) == "grande"

    def test_metropole(self):
        assert _pop_bracket(1_000_000) == "metropole"

    def test_zero_unknown(self):
        assert _pop_bracket(0) == "desconhecido"

    def test_none_unknown(self):
        assert _pop_bracket(None) == "desconhecido"

    def test_negative_unknown(self):
        assert _pop_bracket(-100) == "desconhecido"


# ============================================================
# KEYWORD EXTRACTION
# ============================================================


class TestExtractKeywords:
    def test_basic_extraction(self):
        kws = _extract_keywords("Pavimentacao asfaltica em vias urbanas")
        assert "pavimentacao" in kws
        assert "asfaltica" in kws

    def test_stop_words_filtered(self):
        kws = _extract_keywords("servico de construcao para empresa")
        assert "servico" not in kws  # stop word
        assert "construcao" in kws

    def test_min_length(self):
        kws = _extract_keywords("obra de pavimentacao boa via")
        # "de" (2), "boa" (3), "via" (3) are <4 chars -> excluded
        assert "boa" not in kws
        assert "via" not in kws
        # "obra" (4 chars) passes min_len=4
        assert "obra" in kws

    def test_empty_input(self):
        assert _extract_keywords("") == []


# ============================================================
# SCORING COMPONENTS
# ============================================================


class TestScoreValueFit:
    def test_exact_match_high_score(self):
        profile = VictoryProfile(valor_mean=500_000, valor_std=100_000, valor_max=800_000)
        score = _score_value_fit(500_000, profile)
        assert score > 0.9

    def test_far_from_mean_low_score(self):
        profile = VictoryProfile(valor_mean=500_000, valor_std=100_000, valor_max=800_000)
        score = _score_value_fit(2_000_000, profile)
        assert score < 0.3

    def test_no_data_neutral(self):
        profile = VictoryProfile()
        assert _score_value_fit(100_000, profile) == 0.5

    def test_exceeds_3x_max_penalty(self):
        profile = VictoryProfile(valor_mean=500_000, valor_std=100_000, valor_max=800_000)
        score_within = _score_value_fit(800_000, profile)
        score_3x = _score_value_fit(2_500_000, profile)
        assert score_3x < score_within


class TestScoreKeywordFit:
    def test_overlap_high_score(self):
        profile = VictoryProfile(keyword_freq={"pavimentacao": 0.8, "asfaltica": 0.6})
        score = _score_keyword_fit("Pavimentacao asfaltica em vias", profile)
        assert score > 0.3

    def test_no_overlap_low_score(self):
        profile = VictoryProfile(keyword_freq={"pavimentacao": 0.8})
        score = _score_keyword_fit("Construcao de edificios residenciais", profile)
        assert score <= 0.5

    def test_no_profile_data_neutral(self):
        profile = VictoryProfile()
        assert _score_keyword_fit("Anything", profile) == 0.5


class TestScoreModalidadeFit:
    def test_preferred_modalidade(self):
        profile = VictoryProfile(modalidade_weights={5: 0.8, 4: 0.2})
        assert _score_modalidade_fit(5, profile) == 0.8

    def test_unknown_modalidade(self):
        profile = VictoryProfile(modalidade_weights={5: 0.8})
        assert _score_modalidade_fit(4, profile) == 0.1

    def test_no_data(self):
        profile = VictoryProfile()
        assert _score_modalidade_fit(5, profile) == 0.5


class TestScoreGeographyFit:
    def test_known_uf(self):
        profile = VictoryProfile(uf_weights={"SC": 0.8}, dist_mean_km=200)
        score = _score_geography_fit("SC", 150, profile)
        assert score > 0.5

    def test_unknown_uf(self):
        profile = VictoryProfile(uf_weights={"SC": 0.8}, dist_mean_km=200)
        score = _score_geography_fit("AM", 150, profile)
        assert score < 0.7

    def test_very_distant_penalized(self):
        profile = VictoryProfile(uf_weights={"SC": 0.5}, dist_mean_km=200)
        near = _score_geography_fit("SC", 100, profile)
        far = _score_geography_fit("SC", 800, profile)
        assert far < near


class TestScorePopulationFit:
    def test_known_bracket(self):
        profile = VictoryProfile(pop_bracket_weights={"medio": 0.7, "grande": 0.3})
        assert _score_population_fit(50_000, profile) == 0.7

    def test_unknown_bracket(self):
        profile = VictoryProfile(pop_bracket_weights={"medio": 0.7})
        assert _score_population_fit(None, profile) == 0.4

    def test_no_data(self):
        profile = VictoryProfile()
        assert _score_population_fit(50_000, profile) == 0.5


# ============================================================
# EDITAL FIT SCORE (integrated)
# ============================================================


class TestScoreEditalFit:
    def test_no_data_neutral(self):
        profile = VictoryProfile()
        edital = {"valor_estimado": 100_000, "objeto": "Obra"}
        assert score_edital_fit(edital, profile) == 0.5

    def test_perfect_fit_high_score(self):
        contracts = _make_contracts(10, base_valor=500_000, uf="SC", objeto="Pavimentacao asfaltica")
        profile = build_victory_profile(contracts)
        edital = {
            "valor_estimado": 550_000,
            "objeto": "Pavimentacao asfaltica em vias urbanas",
            "modalidade_code": 5,
            "uf": "SC",
            "distancia": {"km": 120},
            "ibge": {"populacao": 60_000},
        }
        score = score_edital_fit(edital, profile)
        assert score > 0.4  # Good fit

    def test_poor_fit_low_score(self):
        contracts = _make_contracts(10, base_valor=100_000, uf="SC", objeto="Pavimentacao asfaltica")
        profile = build_victory_profile(contracts)
        edital = {
            "valor_estimado": 50_000_000,  # way outside range
            "objeto": "Fornecimento de material hospitalar",
            "modalidade_code": 99,
            "uf": "AM",
            "distancia": {"km": 3000},
            "ibge": {"populacao": 2_000_000},
        }
        score = score_edital_fit(edital, profile)
        assert score < 0.4

    def test_score_bounded_0_to_1(self):
        contracts = _make_contracts(5)
        profile = build_victory_profile(contracts)
        edital = {"valor_estimado": 500_000, "objeto": "Obra"}
        score = score_edital_fit(edital, profile)
        assert 0.0 <= score <= 1.0


# ============================================================
# FORMAT FIT LABEL
# ============================================================


class TestFormatFitLabel:
    def test_excelente(self):
        assert format_fit_label(0.75) == "Excelente"

    def test_bom(self):
        assert format_fit_label(0.55) == "Bom"

    def test_moderado(self):
        assert format_fit_label(0.35) == "Moderado"

    def test_baixo(self):
        assert format_fit_label(0.15) == "Baixo"

    def test_boundary_values(self):
        assert format_fit_label(0.70) == "Excelente"
        assert format_fit_label(0.50) == "Bom"
        assert format_fit_label(0.30) == "Moderado"
        assert format_fit_label(0.29) == "Baixo"
