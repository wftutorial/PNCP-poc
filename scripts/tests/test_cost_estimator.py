"""Tests for scripts/lib/cost_estimator.py — proposal cost estimation."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cost_estimator import (
    CostParams,
    DEFAULT_PARAMS,
    SECTOR_COST_PROFILES,
    estimate_proposal_cost,
    estimate_roi_simple,
    get_sector_params,
    _build_nota,
)


# ============================================================
# PRESENCIAL SESSION COST
# ============================================================


class TestPresencialCost:
    def test_local_no_lodging(self):
        """Distance <=200km: no lodging."""
        result = estimate_proposal_cost(distancia_km=150, duracao_horas=2.5)
        assert result["total"] is not None
        assert result["modalidade_tipo"] == "presencial"
        assert result["breakdown"]["hospedagem"] == 0.0

    def test_regional_one_night(self):
        """Distance 200-500km: 1 night lodging."""
        result = estimate_proposal_cost(distancia_km=350, duracao_horas=4.5)
        assert result["breakdown"]["hospedagem"] > 0
        assert result["premissas"]["diarias_hospedagem"] == 1

    def test_long_distance_two_nights(self):
        """Distance >500km: 2 nights lodging."""
        result = estimate_proposal_cost(distancia_km=700, duracao_horas=9.0)
        assert result["premissas"]["diarias_hospedagem"] == 2

    def test_capital_higher_lodging(self):
        """Capital destination = higher lodging cost."""
        interior = estimate_proposal_cost(distancia_km=350, duracao_horas=4.5, is_capital=False)
        capital = estimate_proposal_cost(distancia_km=350, duracao_horas=4.5, is_capital=True)
        assert capital["breakdown"]["hospedagem"] > interior["breakdown"]["hospedagem"]

    def test_travel_cost_proportional_to_distance(self):
        """Travel cost = distance * 2 * custo_km."""
        result = estimate_proposal_cost(distancia_km=100, duracao_horas=1.5)
        expected_travel = 100 * 2 * DEFAULT_PARAMS.custo_km
        assert result["breakdown"]["deslocamento"] == expected_travel

    def test_toll_by_range(self):
        """Toll follows the pedagio_por_faixa table."""
        # 0-100km: 0 toll
        r1 = estimate_proposal_cost(distancia_km=80, duracao_horas=1.0)
        assert r1["breakdown"]["pedagio"] == 0.0

        # 100-300km: R$30 * 2
        r2 = estimate_proposal_cost(distancia_km=200, duracao_horas=3.0)
        assert r2["breakdown"]["pedagio"] == 60.0  # 30 * 2

    def test_per_diem_with_lodging(self):
        """With lodging: per_diem = (diarias + 1) * per_diem_alimentacao."""
        result = estimate_proposal_cost(distancia_km=350, duracao_horas=4.5)
        # 1 night -> (1+1) * 80 = 160
        assert result["breakdown"]["alimentacao"] == 160.0

    def test_per_diem_no_lodging_far(self):
        """Distance 50-200km: 1 meal."""
        result = estimate_proposal_cost(distancia_km=100, duracao_horas=1.5)
        assert result["breakdown"]["alimentacao"] == DEFAULT_PARAMS.per_diem_alimentacao

    def test_per_diem_very_close(self):
        """Distance <=50km: no food cost."""
        result = estimate_proposal_cost(distancia_km=30, duracao_horas=0.5)
        assert result["breakdown"]["alimentacao"] == 0.0


# ============================================================
# ELETRONICO SESSION COST
# ============================================================


class TestEletronicoCost:
    def test_basic_eletronico(self):
        """Eletronico = prep time cost only (minimum R$600)."""
        result = estimate_proposal_cost(distancia_km=350, duracao_horas=4.5, is_eletronico=True)
        assert result["modalidade_tipo"] == "eletronica"
        assert result["breakdown"]["deslocamento"] == 0.0
        assert result["breakdown"]["hospedagem"] == 0.0
        assert result["total"] >= 600.0

    def test_eletronico_much_cheaper_than_presencial(self):
        """Eletronico should cost significantly less than presencial."""
        presencial = estimate_proposal_cost(distancia_km=500, duracao_horas=6.0, is_eletronico=False)
        eletronico = estimate_proposal_cost(distancia_km=500, duracao_horas=6.0, is_eletronico=True)
        assert eletronico["total"] < presencial["total"]

    def test_eletronico_site_visit_surcharge(self):
        """Eletronico >200km adds visita tecnica surcharge."""
        near = estimate_proposal_cost(distancia_km=100, duracao_horas=1.5, is_eletronico=True)
        far = estimate_proposal_cost(distancia_km=500, duracao_horas=6.0, is_eletronico=True)
        assert far["breakdown"]["visita_tecnica"] > 0
        assert near["breakdown"]["visita_tecnica"] == 0.0


# ============================================================
# EDGE CASES
# ============================================================


class TestEdgeCases:
    def test_zero_distance(self):
        """distancia_km=0 should return 'indisponivel'."""
        result = estimate_proposal_cost(distancia_km=0, duracao_horas=0)
        assert result["total"] is None
        assert "indisponivel" in result["nota"].lower()

    def test_none_distance(self):
        result = estimate_proposal_cost(distancia_km=None, duracao_horas=None)
        assert result["total"] is None

    def test_very_large_distance(self):
        """>1000km should still compute with max toll bracket."""
        result = estimate_proposal_cost(distancia_km=1500, duracao_horas=20.0)
        assert result["total"] is not None
        assert result["total"] > 0
        assert result["breakdown"]["pedagio"] == 500.0  # 250 * 2

    def test_missing_duration_fallback(self):
        """None duracao_horas falls back to distancia/60."""
        result = estimate_proposal_cost(distancia_km=300, duracao_horas=None)
        assert result["premissas"]["duracao_horas_via"] == 5.0  # 300/60

    def test_negative_distance(self):
        result = estimate_proposal_cost(distancia_km=-50, duracao_horas=1.0)
        assert result["total"] is None


# ============================================================
# ROI CALCULATION
# ============================================================


class TestROICalculation:
    def test_excellent_roi(self):
        result = estimate_roi_simple(valor_edital=10_000_000, custo_proposta=5_000)
        assert result is not None
        assert result["classificacao"] == "EXCELENTE"
        assert result["ratio_valor_custo"] == 2000

    def test_good_roi(self):
        result = estimate_roi_simple(valor_edital=500_000, custo_proposta=2_000)
        assert result["classificacao"] == "BOM"

    def test_moderate_roi(self):
        result = estimate_roi_simple(valor_edital=150_000, custo_proposta=2_000)
        assert result["classificacao"] == "MODERADO"

    def test_marginal_roi(self):
        result = estimate_roi_simple(valor_edital=50_000, custo_proposta=2_000)
        assert result["classificacao"] == "MARGINAL"

    def test_desfavoravel_roi(self):
        result = estimate_roi_simple(valor_edital=5_000, custo_proposta=2_000)
        assert result["classificacao"] == "DESFAVORAVEL"

    def test_zero_valor_returns_none(self):
        assert estimate_roi_simple(valor_edital=0, custo_proposta=1000) is None

    def test_zero_custo_returns_none(self):
        assert estimate_roi_simple(valor_edital=100_000, custo_proposta=0) is None

    def test_none_values_returns_none(self):
        assert estimate_roi_simple(valor_edital=None, custo_proposta=None) is None

    def test_custo_percentual(self):
        result = estimate_roi_simple(valor_edital=1_000_000, custo_proposta=10_000)
        assert result["custo_percentual_valor"] == 1.0


# ============================================================
# SECTOR COST PROFILES
# ============================================================


class TestSectorProfiles:
    def test_engenharia_profile(self):
        params = get_sector_params("4120400")
        assert params.custo_hora_tecnico == 180.0
        assert params.custo_fixo_proposta == 2500.0

    def test_ti_profile(self):
        params = get_sector_params("6201501")
        assert params.custo_hora_tecnico == 120.0

    def test_unknown_cnae_gets_default(self):
        params = get_sector_params("99999")
        assert params == SECTOR_COST_PROFILES["default"]

    def test_sector_params_affect_total(self):
        """Different sectors produce different totals for same distance."""
        eng = estimate_proposal_cost(300, 4.0, params=SECTOR_COST_PROFILES["engenharia_obras"])
        ti = estimate_proposal_cost(300, 4.0, params=SECTOR_COST_PROFILES["ti_software"])
        assert eng["total"] != ti["total"]


# ============================================================
# NOTA (explanation text)
# ============================================================


class TestBuildNota:
    def test_local(self):
        assert "local" in _build_nota(30, 0, False).lower()

    def test_regional(self):
        nota = _build_nota(150, 0, False)
        assert "regional" in nota.lower()

    def test_interestadual(self):
        nota = _build_nota(350, 1, False)
        assert "interestadual" in nota.lower()

    def test_capital_note(self):
        nota = _build_nota(350, 1, True)
        assert "capital" in nota.lower()
