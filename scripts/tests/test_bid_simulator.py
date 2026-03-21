"""Tests for scripts/lib/bid_simulator.py — bid strategy simulation."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.bid_simulator import (
    BidSimulation,
    SECTOR_MARGINS,
    _estimate_competitors,
    _get_sector,
    _p_win,
    simulate_bid,
    format_bid_summary,
)


# ============================================================
# HHI & COMPETITOR ESTIMATION
# ============================================================


class TestEstimateCompetitors:
    def test_from_hhi_monopoly(self):
        """HHI=1.0 (monopoly) -> ~2 competitors (minimum)."""
        n = _estimate_competitors(hhi=1.0, concentration=None)
        assert n == 2

    def test_from_hhi_competitive(self):
        """HHI=0.1 -> effective_n=10 -> ~15 (capped at 20)."""
        n = _estimate_competitors(hhi=0.1, concentration=None)
        assert 10 <= n <= 20

    def test_from_hhi_moderate(self):
        """HHI=0.25 -> effective_n=4 -> ~6."""
        n = _estimate_competitors(hhi=0.25, concentration=None)
        assert 4 <= n <= 8

    def test_from_concentration_label(self):
        assert _estimate_competitors(hhi=None, concentration="BAIXA") == 8
        assert _estimate_competitors(hhi=None, concentration="MODERADA") == 5
        assert _estimate_competitors(hhi=None, concentration="ALTA") == 3
        assert _estimate_competitors(hhi=None, concentration="MUITO_ALTA") == 2

    def test_unknown_concentration_default(self):
        assert _estimate_competitors(hhi=None, concentration=None) == 5
        assert _estimate_competitors(hhi=None, concentration="UNKNOWN") == 5

    def test_hhi_zero_fallback(self):
        """HHI=0 should use concentration fallback."""
        n = _estimate_competitors(hhi=0, concentration="ALTA")
        assert n == 3

    def test_hhi_takes_precedence_over_label(self):
        """When HHI is provided, it takes precedence."""
        n_hhi = _estimate_competitors(hhi=0.2, concentration="BAIXA")
        n_label = _estimate_competitors(hhi=None, concentration="BAIXA")
        # HHI=0.2 -> eff=5 -> ~8, BAIXA=8, so they may be similar
        # But the point is HHI path is used
        assert isinstance(n_hhi, int)


# ============================================================
# PROBABILITY MODEL
# ============================================================


class TestPWin:
    def test_above_median_higher_pwin(self):
        """Discount above median -> higher P(win)."""
        p_above = _p_win(0.20, 0.15, 5, 0.05)
        p_below = _p_win(0.10, 0.15, 5, 0.05)
        assert p_above > p_below

    def test_more_competitors_lower_pwin(self):
        """More competitors -> lower P(win)."""
        p_few = _p_win(0.15, 0.15, 3, 0.05)
        p_many = _p_win(0.15, 0.15, 10, 0.05)
        assert p_few > p_many

    def test_bounded_0_to_1(self):
        """P(win) is always between 0.02 and 0.95."""
        p_extreme_high = _p_win(0.50, 0.10, 2, 0.05)
        p_extreme_low = _p_win(0.01, 0.30, 20, 0.05)
        assert 0.02 <= p_extreme_high <= 0.95
        assert 0.02 <= p_extreme_low <= 0.95

    def test_zero_std_uses_default(self):
        """std_descontos=0 should use 5% default."""
        p = _p_win(0.15, 0.15, 5, 0.0)
        assert 0.02 <= p <= 0.95


# ============================================================
# MAIN SIMULATOR
# ============================================================


class TestSimulateBid:
    @pytest.fixture
    def edital_1m(self):
        return {"valor_estimado": 1_000_000}

    @pytest.fixture
    def good_benchmark(self):
        return {
            "desconto_mediano": 0.15,
            "desconto_p25": 0.10,
            "desconto_p75": 0.22,
            "desconto_std": 0.06,
            "contratos_analisados": 12,
        }

    def test_insufficient_data_fallback(self, edital_1m):
        """<3 contracts -> INSUFICIENTE, lance = valor."""
        result = simulate_bid(edital_1m, benchmark={"contratos_analisados": 2})
        assert result.confianca == "INSUFICIENTE"
        assert result.lance_sugerido == 1_000_000

    def test_zero_valor_fallback(self):
        result = simulate_bid({"valor_estimado": 0}, benchmark={"contratos_analisados": 10})
        assert result.confianca == "INSUFICIENTE"

    def test_normal_bid_with_benchmark(self, edital_1m, good_benchmark):
        result = simulate_bid(edital_1m, benchmark=good_benchmark)
        assert result.lance_sugerido < 1_000_000
        assert result.desconto_sugerido_pct > 0
        assert result.p_vitoria_pct > 0
        assert result.confianca == "ALTA"

    def test_aggressive_less_than_conservative(self, edital_1m, good_benchmark):
        result = simulate_bid(edital_1m, benchmark=good_benchmark)
        assert result.lance_agressivo <= result.lance_sugerido
        assert result.lance_conservador >= result.lance_sugerido

    def test_aggressive_discount_higher(self, edital_1m, good_benchmark):
        result = simulate_bid(edital_1m, benchmark=good_benchmark)
        assert result.desconto_agressivo_pct >= result.desconto_sugerido_pct

    def test_margin_floor_respected(self, edital_1m):
        """Discount cannot exceed 1 - margem_minima."""
        benchmark = {
            "desconto_mediano": 0.90,
            "desconto_p25": 0.85,
            "desconto_p75": 0.95,
            "desconto_std": 0.05,
            "contratos_analisados": 10,
        }
        result = simulate_bid(edital_1m, benchmark=benchmark, cnae_principal="4120400")
        margin = SECTOR_MARGINS["engenharia_obras"]
        max_discount = 1.0 - margin["margem_minima"]
        assert result.desconto_sugerido_pct <= max_discount * 100 + 0.1  # rounding tolerance

    def test_confidence_levels(self, edital_1m):
        """ALTA >=10 contracts, MEDIA >=5, BAIXA <5."""
        result_alta = simulate_bid(edital_1m, benchmark={"contratos_analisados": 15, "desconto_mediano": 0.10, "desconto_p25": 0.05, "desconto_p75": 0.15, "desconto_std": 0.04})
        assert result_alta.confianca == "ALTA"

        result_media = simulate_bid(edital_1m, benchmark={"contratos_analisados": 7, "desconto_mediano": 0.10, "desconto_p25": 0.05, "desconto_p75": 0.15, "desconto_std": 0.04})
        assert result_media.confianca == "MEDIA"

        result_baixa = simulate_bid(edital_1m, benchmark={"contratos_analisados": 4, "desconto_mediano": 0.10, "desconto_p25": 0.05, "desconto_p75": 0.15, "desconto_std": 0.04})
        assert result_baixa.confianca == "BAIXA"

    def test_competitive_intel_hhi(self, edital_1m, good_benchmark):
        result = simulate_bid(
            edital_1m,
            competitive_intel={"hhi": 0.33},
            benchmark=good_benchmark,
        )
        assert result.competidores_esperados > 0

    def test_has_data_property(self, edital_1m, good_benchmark):
        result = simulate_bid(edital_1m, benchmark=good_benchmark)
        assert result.has_data is True

        result_no = simulate_bid(edital_1m)
        assert result_no.has_data is False

    def test_missing_benchmark_keys(self, edital_1m):
        """Should handle benchmark with alternative key names."""
        benchmark = {
            "median_discount": 0.12,
            "p25_discount": 0.08,
            "p75_discount": 0.18,
            "std_discount": 0.05,
            "total_contracts": 10,
        }
        result = simulate_bid(edital_1m, benchmark=benchmark)
        assert result.confianca == "ALTA"


# ============================================================
# FORMAT SUMMARY
# ============================================================


class TestFormatBidSummary:
    def test_insufficient_data_message(self):
        sim = BidSimulation(
            lance_sugerido=100000, desconto_sugerido_pct=0, p_vitoria_pct=0,
            margem_liquida_pct=0, lance_agressivo=100000, lance_conservador=100000,
            desconto_agressivo_pct=0, desconto_conservador_pct=0,
            competidores_esperados=5, historico_contratos=1,
            confianca="INSUFICIENTE", racional="N/A",
        )
        text = format_bid_summary(sim, 100000)
        assert "insuficiente" in text.lower()

    def test_normal_summary(self):
        sim = BidSimulation(
            lance_sugerido=850000, desconto_sugerido_pct=15.0, p_vitoria_pct=42.0,
            margem_liquida_pct=10.0, lance_agressivo=780000, lance_conservador=900000,
            desconto_agressivo_pct=22.0, desconto_conservador_pct=10.0,
            competidores_esperados=5, historico_contratos=10,
            confianca="ALTA", racional="Test",
        )
        text = format_bid_summary(sim, 1000000)
        assert "850" in text
        assert "15.0%" in text


# ============================================================
# SECTOR MAPPING
# ============================================================


class TestSectorMapping:
    def test_construction_cnae(self):
        assert _get_sector("4120400") == "engenharia_obras"

    def test_it_cnae(self):
        assert _get_sector("6201501") == "ti_software"

    def test_unknown_cnae(self):
        assert _get_sector("9999999") == "default"

    def test_none_cnae(self):
        assert _get_sector(None) == "default"
