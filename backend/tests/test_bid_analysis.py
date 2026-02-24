"""Tests for STORY-259 AC22: Batch and deep bid analysis.

Covers:
- batch_analyze_bids: 0, 1, 50 bids
- LLM fallback behavior
- deep_analyze_bid with full/partial/empty profile
- POST /v1/bid-analysis/{bid_id} endpoint
- Rate limit enforcement
- Cache hit returns cached result
- Prompt includes/omits profile fields based on presence
"""

import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from main import app
from auth import require_auth
from bid_analyzer import (
    batch_analyze_bids,
    deep_analyze_bid,
    BidAnalysis,
    DeepBidAnalysis,
    _build_profile_section,
)


# ============================================================================
# Auth fixture
# ============================================================================

@pytest.fixture(autouse=True)
def setup_auth():
    """Override auth dependency for all tests in this module."""
    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user-id",
        "email": "test@example.com",
    }
    yield
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# Helper builders
# ============================================================================

def _make_bid(idx: int = 0, valor: float = 100_000.0) -> dict:
    """Create a minimal bid dict for testing."""
    return {
        "id": f"bid-{idx}",
        "objetoCompra": f"Fornecimento de materiais {idx}",
        "valorTotalEstimado": valor,
        "uf": "SP",
        "modalidade": "Pregão Eletrônico",
        "dataEncerramentoProposta": "2026-12-31",
    }


def _make_profile(**overrides) -> dict:
    """Create a profile dict with sensible defaults."""
    base = {
        "setor_id": "vestuario",
        "porte_empresa": "ME",
        "ufs_atuacao": ["SP", "RJ"],
        "faixa_valor_min": 50_000.0,
        "faixa_valor_max": 500_000.0,
        "experiencia_licitacoes": "experiente",
        "capacidade_funcionarios": 20,
        "faturamento_anual": 2_000_000.0,
        "atestados": ["iso_9001"],
    }
    base.update(overrides)
    return base


# ============================================================================
# batch_analyze_bids — unit tests
# ============================================================================

class TestBatchAnalyzeBids:
    """Unit tests for batch_analyze_bids function."""

    def test_empty_list_returns_empty(self):
        """0 bids → empty list (no LLM call)."""
        result = batch_analyze_bids([], user_profile=None, sector_name="vestuario")
        assert result == []

    def test_single_bid_returns_one_result(self):
        """1 bid → 1 BidAnalysis result using fallback (no real LLM)."""
        with patch("llm_arbiter._get_client", return_value=None):
            result = batch_analyze_bids(
                [_make_bid(0)], user_profile=None, sector_name="Vestuário"
            )
        assert len(result) == 1
        assert isinstance(result[0], BidAnalysis)
        assert result[0].bid_id == "bid-0"

    def test_fifty_bids_returns_fifty_results(self):
        """50 bids → 50 results when LLM is unavailable (uses fallback)."""
        bids = [_make_bid(i) for i in range(50)]
        with patch("llm_arbiter._get_client", return_value=None):
            result = batch_analyze_bids(bids, user_profile=None, sector_name="vestuario")
        assert len(result) == 50
        for r in result:
            assert isinstance(r, BidAnalysis)

    def test_truncated_to_50_bids(self):
        """More than 50 bids are truncated to first 50."""
        bids = [_make_bid(i) for i in range(70)]
        with patch("llm_arbiter._get_client", return_value=None):
            result = batch_analyze_bids(bids, user_profile=None, sector_name="vestuario")
        assert len(result) == 50

    def test_fallback_when_llm_returns_none(self):
        """Returns fallback results when LLM client returns None."""
        with patch("llm_arbiter._get_client", return_value=None):
            result = batch_analyze_bids(
                [_make_bid(0)], user_profile=_make_profile(), sector_name="Vestuário"
            )
        assert len(result) == 1
        assert isinstance(result[0], BidAnalysis)
        assert result[0].compatibilidade_pct >= 0
        assert result[0].compatibilidade_pct <= 100

    def test_fallback_when_llm_raises_exception(self):
        """Returns fallback results when LLM call raises exception."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("LLM error")
        with patch("llm_arbiter._get_client", return_value=mock_client):
            result = batch_analyze_bids(
                [_make_bid(0)], user_profile=None, sector_name="vestuario"
            )
        assert len(result) == 1
        assert isinstance(result[0], BidAnalysis)

    def test_llm_response_parsed_correctly(self):
        """Valid LLM JSON response is parsed into BidAnalysis objects."""
        llm_response_data = [
            {
                "bid_id": "bid-0",
                "justificativas": ["Setor compatível", "Valor adequado"],
                "acao_recomendada": "PARTICIPAR",
                "compatibilidade_pct": 85,
            }
        ]
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(llm_response_data)

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("llm_arbiter._get_client", return_value=mock_client):
            with patch("config.LLM_ARBITER_MODEL", "gpt-4.1-nano"):
                result = batch_analyze_bids(
                    [_make_bid(0)], user_profile=None, sector_name="vestuario"
                )

        assert len(result) >= 1
        match = next((r for r in result if r.bid_id == "bid-0"), None)
        assert match is not None
        assert match.acao_recomendada == "PARTICIPAR"
        assert match.compatibilidade_pct == 85

    def test_acao_recomendada_values(self):
        """All action values are in the expected set."""
        bids = [_make_bid(i) for i in range(3)]
        with patch("llm_arbiter._get_client", return_value=None):
            result = batch_analyze_bids(bids, user_profile=_make_profile(), sector_name="vestuario")

        valid_actions = {"PARTICIPAR", "AVALIAR COM CAUTELA", "NÃO PARTICIPAR"}
        for r in result:
            assert r.acao_recomendada in valid_actions

    def test_compatibilidade_pct_in_range(self):
        """compatibilidade_pct is always 0-100."""
        bids = [_make_bid(i, valor=float(i * 100_000)) for i in range(5)]
        with patch("llm_arbiter._get_client", return_value=None):
            result = batch_analyze_bids(bids, user_profile=_make_profile(), sector_name="vestuario")

        for r in result:
            assert 0 <= r.compatibilidade_pct <= 100


# ============================================================================
# deep_analyze_bid — unit tests
# ============================================================================

class TestDeepAnalyzeBid:
    """Unit tests for deep_analyze_bid function."""

    def test_full_profile_returns_deep_analysis(self):
        """deep_analyze_bid with full profile uses LLM (mocked)."""
        bid = _make_bid(0, valor=200_000.0)
        profile = _make_profile()

        with patch("llm_arbiter._get_client", return_value=None):
            result = deep_analyze_bid(bid=bid, user_profile=profile, sector_name="Vestuário")

        assert isinstance(result, DeepBidAnalysis)
        assert 0.0 <= result.score <= 10.0
        assert 0 <= result.compatibilidade_pct <= 100

    def test_partial_profile_returns_fallback(self):
        """deep_analyze_bid with partial profile (some fields None) uses fallback gracefully."""
        bid = _make_bid(0)
        partial_profile = {
            "setor_id": "vestuario",
            "porte_empresa": "ME",
            "ufs_atuacao": ["SP"],
            # faixa_valor_min/max absent
            # capacidade_funcionarios absent
            # faturamento_anual absent
        }

        with patch("llm_arbiter._get_client", return_value=None):
            result = deep_analyze_bid(bid=bid, user_profile=partial_profile, sector_name="Vestuário")

        assert isinstance(result, DeepBidAnalysis)
        assert result.bid_id == "bid-0"

    def test_empty_profile_uses_fallback(self):
        """deep_analyze_bid with empty dict profile returns fallback."""
        bid = _make_bid(0)

        with patch("llm_arbiter._get_client", return_value=None):
            result = deep_analyze_bid(bid=bid, user_profile={}, sector_name="")

        assert isinstance(result, DeepBidAnalysis)
        assert result.score >= 0.0

    def test_none_profile_uses_fallback(self):
        """deep_analyze_bid with None profile returns fallback."""
        bid = _make_bid(0)

        with patch("llm_arbiter._get_client", return_value=None):
            result = deep_analyze_bid(bid=bid, user_profile=None, sector_name="vestuario")

        assert isinstance(result, DeepBidAnalysis)
        assert isinstance(result.riscos, list)
        assert isinstance(result.justificativas_favoraveis, list)

    def test_llm_response_parsed_into_deep_analysis(self):
        """Valid LLM JSON response populates DeepBidAnalysis correctly."""
        llm_data = {
            "score": 8.5,
            "decisao_sugerida": "PARTICIPAR",
            "compatibilidade_pct": 85,
            "analise_prazo": "30 dias — prazo adequado",
            "analise_requisitos": ["Atestado CREA", "Certidão negativa"],
            "analise_competitividade": "Mercado competitivo — 5-10 concorrentes esperados",
            "riscos": ["Prazo curto"],
            "justificativas_favoraveis": ["Setor compatível", "Valor dentro da faixa"],
            "justificativas_contra": ["Alta concorrência"],
            "recomendacao_final": "Participar com proposta competitiva.",
        }
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(llm_data)

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("llm_arbiter._get_client", return_value=mock_client):
            with patch("config.LLM_ARBITER_MODEL", "gpt-4.1-nano"):
                result = deep_analyze_bid(
                    bid=_make_bid(0), user_profile=_make_profile(), sector_name="Vestuário"
                )

        assert result.score == 8.5
        assert result.decisao_sugerida == "PARTICIPAR"
        assert result.compatibilidade_pct == 85
        assert "Atestado CREA" in result.analise_requisitos

    def test_score_clamped_to_range(self):
        """Score is clamped to [0.0, 10.0] even if LLM returns out-of-range."""
        llm_data = {"score": 999.0, "decisao_sugerida": "PARTICIPAR", "compatibilidade_pct": 50}
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(llm_data)
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("llm_arbiter._get_client", return_value=mock_client):
            with patch("config.LLM_ARBITER_MODEL", "gpt-4.1-nano"):
                result = deep_analyze_bid(bid=_make_bid(0), user_profile=None, sector_name="")

        assert result.score <= 10.0


# ============================================================================
# _build_profile_section — prompt content tests
# ============================================================================

class TestBuildProfileSection:
    """Test that prompt includes/omits profile fields based on presence."""

    def test_prompt_includes_present_fields(self):
        """Profile section includes fields that have values."""
        profile = {
            "setor_id": "vestuario",
            "porte_empresa": "ME",
            "atestados": ["iso_9001"],
            "capacidade_funcionarios": 10,
            "faturamento_anual": 1_000_000.0,
        }
        section = _build_profile_section(profile)
        assert "ME" in section
        assert "iso_9001" in section
        assert "10" in section
        assert "1.000.000" in section or "1000000" in section

    def test_prompt_omits_none_fields(self):
        """Profile section omits fields that are None."""
        profile = {
            "setor_id": "vestuario",
            "porte_empresa": None,
            "capacidade_funcionarios": None,
            "faturamento_anual": None,
        }
        section = _build_profile_section(profile)
        # Fields with None should not appear in the section
        assert "Porte" not in section
        assert "Funcionários" not in section
        assert "Faturamento" not in section

    def test_prompt_omits_empty_list_fields(self):
        """Fields with empty lists are omitted."""
        profile = {
            "ufs_atuacao": [],
            "atestados": [],
        }
        section = _build_profile_section(profile)
        assert "atestados" not in section.lower() or "[]" not in section

    def test_empty_profile_returns_empty_string(self):
        """Empty profile dict returns empty string."""
        assert _build_profile_section({}) == ""

    def test_none_profile_returns_empty_string(self):
        """None profile returns empty string."""
        assert _build_profile_section(None) == ""

    def test_value_range_included_when_present(self):
        """Value range appears in prompt when both min and max are set."""
        profile = {"faixa_valor_min": 50_000.0, "faixa_valor_max": 200_000.0}
        section = _build_profile_section(profile)
        assert "50" in section
        assert "200" in section


# ============================================================================
# POST /v1/bid-analysis/{bid_id} endpoint tests
# ============================================================================

class TestBidAnalysisEndpoint:
    """Integration tests for POST /v1/bid-analysis/{bid_id}."""

    @pytest.fixture(autouse=True)
    def clear_rate_limits(self):
        """Clear rate limits between endpoint tests."""
        import routes.bid_analysis as bid_analysis_module
        bid_analysis_module._rate_limits.clear()
        yield
        bid_analysis_module._rate_limits.clear()

    def test_endpoint_returns_200_with_valid_bid(self, client):
        """Valid request with bid_data in body returns 200 + DeepBidAnalysis."""
        bid_data = _make_bid(0)

        with patch("routes.bid_analysis._get_cached_analysis", new=AsyncMock(return_value=None)):
            with patch("routes.bid_analysis._cache_analysis", new=AsyncMock()):
                with patch("routes.bid_analysis._get_user_profile", new=AsyncMock(return_value={})):
                    with patch("llm_arbiter._get_client", return_value=None):
                        response = client.post(
                            "/v1/bid-analysis/bid-0",
                            json={"search_id": "search-abc", "bid_data": bid_data},
                        )

        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "decisao_sugerida" in data
        assert "compatibilidade_pct" in data

    def test_endpoint_404_when_bid_not_found(self, client):
        """Returns 404 when bid_data is None and session cache has no data."""
        with patch("routes.bid_analysis._get_cached_analysis", new=AsyncMock(return_value=None)):
            with patch("routes.bid_analysis._get_bid_from_session", new=AsyncMock(return_value=None)):
                with patch("routes.bid_analysis._get_user_profile", new=AsyncMock(return_value={})):
                    response = client.post(
                        "/v1/bid-analysis/nonexistent-bid",
                        json={"search_id": "search-xyz", "bid_data": None},
                    )

        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()

    def test_cache_hit_returns_cached_result(self, client):
        """Cache hit returns cached DeepBidAnalysis without calling LLM."""
        cached = {
            "bid_id": "bid-0",
            "score": 9.0,
            "decisao_sugerida": "PARTICIPAR",
            "compatibilidade_pct": 90,
            "analise_prazo": "Cached",
            "analise_requisitos": [],
            "analise_competitividade": "Cached",
            "riscos": [],
            "justificativas_favoraveis": [],
            "justificativas_contra": [],
            "recomendacao_final": "Cached result",
        }

        with patch("routes.bid_analysis._get_cached_analysis", new=AsyncMock(return_value=cached)):
            with patch("llm_arbiter._get_client") as mock_llm:
                response = client.post(
                    "/v1/bid-analysis/bid-0",
                    json={"search_id": "search-abc", "bid_data": _make_bid(0)},
                )

                # LLM should NOT be called on cache hit
                mock_llm.assert_not_called()

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 9.0
        assert data["decisao_sugerida"] == "PARTICIPAR"

    def test_rate_limit_429_after_20_requests(self, client):
        """Rate limit: 21st request in 1 hour returns 429."""
        import routes.bid_analysis as bid_analysis_module
        import time

        now = time.time()
        bid_analysis_module._rate_limits["test-user-id"] = [now] * 20

        with patch("routes.bid_analysis._get_cached_analysis", new=AsyncMock(return_value=None)):
            response = client.post(
                "/v1/bid-analysis/bid-0",
                json={"search_id": "search-abc", "bid_data": _make_bid(0)},
            )

        assert response.status_code == 429
        assert "Limite" in response.json()["detail"]

    def test_endpoint_uses_sector_name_from_profile(self, client):
        """Endpoint resolves sector name from user profile's setor_id."""
        bid_data = _make_bid(0)
        profile = {"setor_id": "vestuario", "porte_empresa": "ME"}

        with patch("routes.bid_analysis._get_cached_analysis", new=AsyncMock(return_value=None)):
            with patch("routes.bid_analysis._cache_analysis", new=AsyncMock()):
                with patch("routes.bid_analysis._get_user_profile", new=AsyncMock(return_value=profile)):
                    with patch("llm_arbiter._get_client", return_value=None):
                        response = client.post(
                            "/v1/bid-analysis/bid-0",
                            json={"search_id": "search-abc", "bid_data": bid_data},
                        )

        # Should not crash when resolving sector name
        assert response.status_code == 200

    def test_endpoint_requires_auth(self):
        """Endpoint is protected — without auth override it would return 401/403."""
        # Our fixture provides auth. Just verify the endpoint exists and auth works.
        client_no_override = TestClient(app)
        app.dependency_overrides.pop(require_auth, None)

        try:
            response = client_no_override.post(
                "/v1/bid-analysis/bid-0",
                json={"search_id": "search-abc", "bid_data": _make_bid(0)},
            )
            # Without valid auth token, should be 401 or 403
            assert response.status_code in (401, 403)
        finally:
            # Restore auth override for subsequent tests
            app.dependency_overrides[require_auth] = lambda: {
                "id": "test-user-id",
                "email": "test@example.com",
            }
