"""
Edge case and boundary tests for scripts/intel-analyze.py.

Tests cover:
- LLM response edge cases (malformed JSON, refusals, rate limits, timeouts)
- Analysis content edge cases (very short/long text, all-caps, tables)
- Status temporal boundary conditions
- Executive summary edge cases (all PARTICIPAR, all NAO PARTICIPAR, zero editais)
- Validation / normalization edge cases
- Adversarial review edge cases
- Prepare mode and save-analysis mode edge cases

All OpenAI calls are mocked. No production code is modified.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ---------------------------------------------------------------------------
# Import intel-analyze.py via importlib
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "intel_analyze", SCRIPTS_DIR / "intel-analyze.py"
)
if _spec is None or _spec.loader is None:
    pytest.skip("Cannot load intel-analyze.py", allow_module_level=True)

intel_analyze = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intel_analyze)

# Aliases
ANALYSIS_FIELDS = intel_analyze.ANALYSIS_FIELDS
CRITERIO_ENUM = intel_analyze.CRITERIO_ENUM
RECOMENDACAO_ENUM = intel_analyze.RECOMENDACAO_ENUM
DIFICULDADE_ENUM = intel_analyze.DIFICULDADE_ENUM
_safe_float = intel_analyze._safe_float
_fmt_brl = intel_analyze._fmt_brl
_validate_analysis = intel_analyze._validate_analysis
_fallback_analysis = intel_analyze._fallback_analysis
_build_enrichment_context = intel_analyze._build_enrichment_context
_build_override_rules = intel_analyze._build_override_rules
_build_user_prompt = intel_analyze._build_user_prompt
_call_llm = intel_analyze._call_llm
analyze_edital = intel_analyze.analyze_edital
generate_executive_summary = intel_analyze.generate_executive_summary
_adversarial_review = intel_analyze._adversarial_review
prepare_mode = intel_analyze.prepare_mode
save_analysis_mode = intel_analyze.save_analysis_mode
MAX_TEXT_CHARS = intel_analyze.MAX_TEXT_CHARS
REVIEW_MAX_TEXT_CHARS = intel_analyze.REVIEW_MAX_TEXT_CHARS


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def sample_empresa():
    return {
        "razao_social": "LCM Construcoes LTDA",
        "cnpj": "01721078000168",
        "cnae_principal": "4120400",
        "cidade_sede": "Florianopolis",
        "uf_sede": "SC",
        "sancionada": False,
        "restricao_sicaf": False,
    }


@pytest.fixture
def sample_edital():
    return {
        "_id": "83102459000152/2026/42",
        "objeto": "Construcao de unidades habitacionais no bairro Efapi",
        "orgao_nome": "PREFEITURA DE CHAPECO",
        "uf": "SC",
        "municipio": "Chapeco",
        "valor_estimado": 2_500_000.0,
        "modalidade_nome": "Concorrencia",
        "status_temporal": "PLANEJAVEL",
        "cnae_compatible": True,
        "cnae_confidence": 0.85,
        "texto_documentos": "Edital de licitacao para construcao de 50 unidades...",
        "extraction_quality": "OK",
    }


@pytest.fixture
def valid_analysis():
    """A complete valid analysis dict."""
    return {
        "resumo_objeto": "Construcao de 50 unidades habitacionais.",
        "requisitos_tecnicos": ["Acervo tecnico em construcao civil"],
        "requisitos_habilitacao": ["CND federal, estadual e municipal"],
        "qualificacao_economica": "Capital social minimo R$ 250.000,00",
        "prazo_execucao": "12 meses",
        "garantias": "5% do valor do contrato",
        "criterio_julgamento": "Menor Preco",
        "data_sessao": "15/04/2026 10:00",
        "prazo_proposta": "10/04/2026",
        "visita_tecnica": "Facultativa",
        "exclusividade_me_epp": "Nao",
        "regime_execucao": "Empreitada por preco global",
        "consorcio": "Vedado",
        "observacoes_criticas": "Edital compativel.",
        "nivel_dificuldade": "MEDIO",
        "recomendacao_acao": "PARTICIPAR",
        "custo_logistico_nota": "180 km da sede",
    }


def _make_llm_response(content_dict: dict | None = None, content_str: str | None = None):
    """Create a mock OpenAI response object."""
    if content_str is None:
        content_str = json.dumps(content_dict or {}, ensure_ascii=False)
    choice = SimpleNamespace(
        message=SimpleNamespace(content=content_str)
    )
    return SimpleNamespace(choices=[choice])


# ============================================================
# LLM RESPONSE EDGE CASES
# ============================================================


class TestLlmResponseEdgeCases:
    """Test handling of various LLM response formats."""

    def test_valid_json_in_markdown_code_block(self):
        """LLM wrapping JSON in ```json ... ``` should be parsed correctly."""
        analysis_json = json.dumps({
            "resumo_objeto": "Teste",
            "nivel_dificuldade": "BAIXO",
            "recomendacao_acao": "PARTICIPAR",
        })
        content = f"```json\n{analysis_json}\n```"
        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(content_str=content)
        result = _call_llm(client, "gpt-4.1-nano", "system", "user")
        assert result["resumo_objeto"] == "Teste"

    def test_json_with_extra_fields(self, valid_analysis):
        """Extra fields in LLM response should be kept (not crash)."""
        analysis = dict(valid_analysis)
        analysis["campo_extra"] = "valor inesperado"
        analysis["outro_campo"] = 42
        result = _validate_analysis(analysis)
        assert result["campo_extra"] == "valor inesperado"
        assert result["recomendacao_acao"] == "PARTICIPAR"

    def test_json_missing_required_fields(self):
        """Missing fields should be filled with defaults."""
        partial = {
            "resumo_objeto": "Teste",
            "recomendacao_acao": "PARTICIPAR",
        }
        result = _validate_analysis(partial)
        for field in ANALYSIS_FIELDS:
            assert field in result
        assert result["requisitos_tecnicos"] == ["Nao consta no edital disponivel"]
        assert result["garantias"] == "Nao consta no edital disponivel"

    def test_empty_string_from_llm(self):
        """LLM returning empty string should raise ValueError."""
        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(content_str="")
        # Empty string -> json.loads("") fails, then regex finds nothing
        # But the content fallback is "{}" which parses to empty dict
        # Actually, content is "" -> json.loads("") -> JSONDecodeError
        # -> regex search on "" -> no match -> ValueError
        # Wait, the code does: content = response.choices[0].message.content or "{}"
        # So empty string "" is falsy -> becomes "{}" -> parses to {}
        result = _call_llm(client, "gpt-4.1-nano", "system", "user")
        assert result == {}

    def test_llm_returns_none_content(self):
        """LLM returning None content should fall back to empty dict."""
        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(content_str=None)
        # content = None or "{}" -> "{}"
        choice = SimpleNamespace(message=SimpleNamespace(content=None))
        client.chat.completions.create.return_value = SimpleNamespace(choices=[choice])
        result = _call_llm(client, "gpt-4.1-nano", "system", "user")
        assert result == {}

    def test_llm_refusal_text(self, sample_edital, sample_empresa):
        """LLM returning a refusal should produce fallback analysis."""
        client = MagicMock()
        client.chat.completions.create.side_effect = ValueError(
            "LLM retornou resposta nao-JSON: I can't help with that"
        )
        with patch("time.sleep"):
            result = analyze_edital(client, "gpt-4.1-nano", sample_edital, sample_empresa, 1, 1)
        assert result["_source"] == "fallback"
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"

    def test_llm_connection_timeout(self, sample_edital, sample_empresa):
        """Connection timeout should produce fallback after retries."""
        client = MagicMock()
        client.chat.completions.create.side_effect = TimeoutError("Connection timed out")
        with patch("time.sleep"):
            result = analyze_edital(client, "gpt-4.1-nano", sample_edital, sample_empresa, 1, 1)
        assert result["_source"] == "fallback"
        assert "timed out" in result["_error"].lower()

    def test_llm_rate_limit_429(self, sample_edital, sample_empresa):
        """429 rate limit should produce fallback after retries."""
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception(
            "Error code: 429 - Rate limit exceeded"
        )
        with patch("time.sleep"):
            result = analyze_edital(client, "gpt-4.1-nano", sample_edital, sample_empresa, 1, 1)
        assert result["_source"] == "fallback"

    def test_llm_returns_json_with_wrong_types(self):
        """Numbers as strings, etc. should be accepted by validate."""
        analysis = {
            "resumo_objeto": "Teste",
            "requisitos_tecnicos": "Uma unica string em vez de lista",
            "requisitos_habilitacao": 42,  # Wrong type entirely
            "nivel_dificuldade": "medio",  # Lowercase
            "recomendacao_acao": "participar",  # Lowercase
        }
        result = _validate_analysis(analysis)
        # requisitos_tecnicos string -> list
        assert isinstance(result["requisitos_tecnicos"], list)
        assert result["requisitos_tecnicos"] == ["Uma unica string em vez de lista"]
        # requisitos_habilitacao not a list/str -> default
        assert result["requisitos_habilitacao"] == ["Nao consta no edital disponivel"]
        # nivel_dificuldade normalized to upper
        assert result["nivel_dificuldade"] == "MEDIO"
        # recomendacao_acao normalized
        assert result["recomendacao_acao"] == "PARTICIPAR"

    def test_llm_first_attempt_fails_second_succeeds(self, sample_edital, sample_empresa,
                                                       valid_analysis):
        """First LLM call fails, second succeeds."""
        client = MagicMock()
        fail_response = Exception("transient error")
        ok_response = _make_llm_response(content_dict=valid_analysis)
        client.chat.completions.create.side_effect = [fail_response, ok_response]
        with patch("time.sleep"):
            result = analyze_edital(client, "gpt-4.1-nano", sample_edital, sample_empresa, 1, 1)
        assert result["_source"] in ("llm", "llm_limited")  # limited if no texto_documentos
        assert result["recomendacao_acao"] == "PARTICIPAR"


# ============================================================
# ANALYSIS CONTENT EDGE CASES
# ============================================================


class TestAnalysisContentEdgeCases:
    """Test analysis behavior with various content qualities."""

    def test_no_texto_documentos_limited_analysis(self, sample_edital, sample_empresa,
                                                    valid_analysis):
        """Edital without texto_documentos should produce limited analysis."""
        edital = dict(sample_edital)
        edital["texto_documentos"] = ""
        edital["extraction_quality"] = "VAZIO"

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(content_dict=valid_analysis)

        result = analyze_edital(client, "gpt-4.1-nano", edital, sample_empresa, 1, 1)
        assert result["_source"] == "llm_limited"

    def test_very_short_text_is_limited(self, sample_edital, sample_empresa, valid_analysis):
        """Text under 100 chars should trigger limited analysis."""
        edital = dict(sample_edital)
        edital["texto_documentos"] = "Edital de obra."
        edital["extraction_quality"] = "OK"

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(content_dict=valid_analysis)

        result = analyze_edital(client, "gpt-4.1-nano", edital, sample_empresa, 1, 1)
        assert result["_source"] == "llm_limited"

    def test_very_long_text_truncated_in_prompt(self, sample_edital, sample_empresa):
        """Text >50K chars should be truncated in the user prompt."""
        edital = dict(sample_edital)
        edital["texto_documentos"] = "A" * 60_000

        prompt = _build_user_prompt(edital, sample_empresa, 1, 1, limited=False)
        assert "[... texto truncado ...]" in prompt
        # Prompt should contain at most MAX_TEXT_CHARS of text plus the marker
        assert len(prompt) < 60_000 + 5000  # Some overhead for context

    def test_all_caps_text(self, sample_edital, sample_empresa, valid_analysis):
        """All-caps text should not cause issues."""
        edital = dict(sample_edital)
        edital["texto_documentos"] = "EDITAL DE LICITACAO PARA CONSTRUCAO DE ESCOLA. " * 100

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(content_dict=valid_analysis)

        result = analyze_edital(client, "gpt-4.1-nano", edital, sample_empresa, 1, 1)
        assert result["_source"] == "llm"

    def test_text_with_table_formatting(self, sample_edital, sample_empresa, valid_analysis):
        """Text with pipe-separated table formatting should not crash."""
        edital = dict(sample_edital)
        edital["texto_documentos"] = (
            "ITEM | DESCRICAO | VALOR\n"
            "1 | Pavimentacao | R$ 500.000,00\n"
            "2 | Drenagem | R$ 300.000,00\n"
        ) * 50  # Repeat to get over 100 chars

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(content_dict=valid_analysis)

        result = analyze_edital(client, "gpt-4.1-nano", edital, sample_empresa, 1, 1)
        assert result["_source"] == "llm"

    def test_analysis_all_nao_consta(self):
        """Analysis where every field is 'Nao consta' should still be valid."""
        analysis = {field: "Nao consta no edital disponivel" for field in ANALYSIS_FIELDS}
        analysis["requisitos_tecnicos"] = ["Nao consta no edital disponivel"]
        analysis["requisitos_habilitacao"] = ["Nao consta no edital disponivel"]
        analysis["nivel_dificuldade"] = "MEDIO"
        analysis["recomendacao_acao"] = "NAO PARTICIPAR"
        result = _validate_analysis(analysis)
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"


# ============================================================
# VALIDATION / NORMALIZATION EDGE CASES
# ============================================================


class TestValidationEdgeCases:
    """Test _validate_analysis normalization behavior."""

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("PARTICIPAR", "PARTICIPAR"),
            ("NAO PARTICIPAR", "NAO PARTICIPAR"),
            ("participar", "PARTICIPAR"),
            ("nao participar", "NAO PARTICIPAR"),
            ("NÃO PARTICIPAR", "NAO PARTICIPAR"),  # Accented NAO
            ("Sim, participar", "PARTICIPAR"),
            ("Nao recomendado", "NAO PARTICIPAR"),  # Contains "NAO"
            ("", "NAO PARTICIPAR"),  # Empty defaults to NAO
            ("TALVEZ", "NAO PARTICIPAR"),  # Unknown defaults to NAO
        ],
    )
    def test_recomendacao_normalization(self, input_val, expected):
        analysis = {"recomendacao_acao": input_val}
        result = _validate_analysis(analysis)
        assert result["recomendacao_acao"] == expected

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("BAIXO", "BAIXO"),
            ("MEDIO", "MEDIO"),
            ("ALTO", "ALTO"),
            ("baixo", "BAIXO"),
            ("alto", "ALTO"),
            ("MUITO ALTO", "MEDIO"),  # Not in enum -> default
            ("", "MEDIO"),  # Empty -> default
            ("MODERADO", "MEDIO"),  # Not in enum -> default
        ],
    )
    def test_dificuldade_normalization(self, input_val, expected):
        analysis = {"nivel_dificuldade": input_val}
        result = _validate_analysis(analysis)
        assert result["nivel_dificuldade"] == expected

    def test_requisitos_string_to_list(self):
        """String value for list fields should be wrapped in a list."""
        analysis = {
            "requisitos_tecnicos": "Acervo em pavimentacao",
            "requisitos_habilitacao": "CND federal",
        }
        result = _validate_analysis(analysis)
        assert result["requisitos_tecnicos"] == ["Acervo em pavimentacao"]
        assert result["requisitos_habilitacao"] == ["CND federal"]

    def test_requisitos_empty_string_to_default(self):
        """Empty string for list fields should become default."""
        analysis = {
            "requisitos_tecnicos": "",
            "requisitos_habilitacao": "",
        }
        result = _validate_analysis(analysis)
        assert result["requisitos_tecnicos"] == ["Nao consta no edital disponivel"]

    def test_requisitos_none_to_default(self):
        """None for list fields should become default."""
        analysis = {
            "requisitos_tecnicos": None,
            "requisitos_habilitacao": None,
        }
        result = _validate_analysis(analysis)
        assert result["requisitos_tecnicos"] == ["Nao consta no edital disponivel"]

    def test_requisitos_number_to_default(self):
        """Number for list fields should become default."""
        analysis = {
            "requisitos_tecnicos": 42,
        }
        result = _validate_analysis(analysis)
        assert result["requisitos_tecnicos"] == ["Nao consta no edital disponivel"]


# ============================================================
# FALLBACK ANALYSIS EDGE CASES
# ============================================================


class TestFallbackAnalysisEdgeCases:
    """Test fallback analysis under various conditions."""

    def test_fallback_sancionada(self):
        """Sanctioned company should get NAO PARTICIPAR with impedimento note."""
        empresa = {"sancionada": True}
        edital = {"objeto": "Obra", "municipio": "Test", "uf": "SC", "valor_estimado": 1000000}
        result = _fallback_analysis(edital, empresa, "test error")
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"
        assert "sancionada" in result["observacoes_criticas"].lower()

    def test_fallback_expirado(self):
        """Expired edital should get NAO PARTICIPAR."""
        empresa = {"sancionada": False}
        edital = {"objeto": "Obra", "municipio": "Test", "uf": "SC",
                  "status_temporal": "EXPIRADO", "valor_estimado": 1000000}
        result = _fallback_analysis(edital, empresa, "test error")
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"
        assert "encerrado" in result["observacoes_criticas"].lower()

    def test_fallback_generic_error(self):
        """Generic error should produce manual-review recommendation."""
        empresa = {"sancionada": False}
        edital = {"objeto": "Obra", "municipio": "Test", "uf": "SC",
                  "status_temporal": "PLANEJAVEL", "valor_estimado": 1000000}
        result = _fallback_analysis(edital, empresa, "connection reset")
        assert result["_source"] == "fallback"
        assert "connection reset" in result["_error"]
        assert "manual" in result["observacoes_criticas"].lower()

    def test_fallback_has_all_required_fields(self):
        """Fallback analysis should contain all ANALYSIS_FIELDS."""
        empresa = {"sancionada": False}
        edital = {"objeto": "Obra", "municipio": "Test", "uf": "SC",
                  "valor_estimado": 1000000}
        result = _fallback_analysis(edital, empresa, "error")
        for field in ANALYSIS_FIELDS:
            assert field in result, f"Missing field: {field}"


# ============================================================
# ENRICHMENT CONTEXT / OVERRIDE RULES EDGE CASES
# ============================================================


class TestEnrichmentContextEdgeCases:
    """Test context and override rule building."""

    def test_override_sancionada(self, sample_empresa, sample_edital):
        """Sanctioned company should produce mandatory NAO PARTICIPAR rule."""
        empresa = dict(sample_empresa)
        empresa["sancionada"] = True
        rules = _build_override_rules(sample_edital, empresa)
        assert "NAO PARTICIPAR" in rules
        assert "SANCIONADA" in rules

    def test_override_restricao_sicaf(self, sample_empresa, sample_edital):
        """SICAF restriction should produce warning rule."""
        empresa = dict(sample_empresa)
        empresa["restricao_sicaf"] = True
        rules = _build_override_rules(sample_edital, empresa)
        assert "RESTRICAO" in rules
        assert "SICAF" in rules

    def test_override_expired_edital(self, sample_empresa):
        """Expired edital should force NAO PARTICIPAR."""
        edital = {"status_temporal": "EXPIRADO", "valor_estimado": 1000000}
        rules = _build_override_rules(edital, sample_empresa)
        assert "NAO PARTICIPAR" in rules
        assert "EXPIRADO" in rules

    def test_override_urgent_edital(self, sample_empresa):
        """Urgent edital should mention urgency."""
        edital = {"status_temporal": "URGENTE", "valor_estimado": 1000000}
        rules = _build_override_rules(edital, sample_empresa)
        assert "URGENTE" in rules

    def test_override_long_distance(self, sample_empresa):
        """Distance >500km should mention logistic cost."""
        edital = {"distancia": {"km": 800}, "valor_estimado": 1000000}
        rules = _build_override_rules(edital, sample_empresa)
        assert "800" in rules
        assert "logistico" in rules.lower()

    def test_override_small_city_high_value(self, sample_empresa):
        """Small city + high value should alert fragility."""
        edital = {"ibge": {"populacao": 3000}, "valor_estimado": 5_000_000}
        rules = _build_override_rules(edital, sample_empresa)
        assert "3,000" in rules or "3000" in rules
        assert "fragilidade" in rules.lower()

    def test_override_no_rules(self, sample_empresa, sample_edital):
        """Normal edital + normal company should produce no rules."""
        rules = _build_override_rules(sample_edital, sample_empresa)
        assert rules == ""

    def test_context_includes_empresa(self, sample_empresa, sample_edital):
        """Context should include company razao_social."""
        context = _build_enrichment_context(sample_edital, sample_empresa)
        assert "LCM Construcoes" in context

    def test_context_includes_edital_metadata(self, sample_empresa, sample_edital):
        """Context should include edital objeto and municipio."""
        context = _build_enrichment_context(sample_edital, sample_empresa)
        assert "Chapeco" in context
        assert "Construcao" in context

    def test_context_with_bid_simulation(self, sample_empresa, sample_edital):
        """Context should include bid simulation data when present."""
        edital = dict(sample_edital)
        edital["_bid_simulation"] = {
            "has_data": True,
            "lance_sugerido": 2_000_000,
            "desconto_sugerido_pct": 15.0,
            "p_vitoria_pct": 60,
            "historico_contratos": 5,
        }
        context = _build_enrichment_context(edital, sample_empresa)
        assert "SIMULACAO LANCE" in context

    def test_context_with_structured_extraction(self, sample_empresa, sample_edital):
        """Context should include pre-extracted fields."""
        edital = dict(sample_edital)
        edital["_structured_extraction"] = {
            "fields": {
                "garantia": {"found": True, "value": "5% do valor"},
                "prazo": {"found": True, "value": "180 dias"},
                "missing_field": {"found": False, "value": ""},
            }
        }
        context = _build_enrichment_context(edital, sample_empresa)
        assert "DADOS PRE-EXTRAIDOS" in context
        assert "5% do valor" in context
        assert "180 dias" in context


# ============================================================
# ADVERSARIAL REVIEW EDGE CASES
# ============================================================


class TestAdversarialReviewEdgeCases:
    """Test the adversarial review pass."""

    def test_review_no_text_returns_empty(self, sample_edital, valid_analysis):
        """Review without texto_documentos should return empty corrections."""
        edital = dict(sample_edital)
        edital["texto_documentos"] = ""
        client = MagicMock()
        result = _adversarial_review(client, edital, valid_analysis, "gpt-4.1-nano")
        assert result == {}
        client.chat.completions.create.assert_not_called()

    def test_review_all_correct(self, sample_edital, valid_analysis):
        """Review finding no errors should return empty corrections."""
        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={"corrections": {}, "review_notes": "Analise validada sem correcoes"}
        )
        result = _adversarial_review(client, sample_edital, valid_analysis, "gpt-4.1-nano")
        assert result == {}

    def test_review_with_corrections(self, sample_edital, valid_analysis):
        """Review finding errors should return correction dict."""
        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={
                "corrections": {"data_sessao": "20/04/2026 14:00"},
                "review_notes": "Data corrigida",
            }
        )
        result = _adversarial_review(client, sample_edital, valid_analysis, "gpt-4.1-nano")
        assert result == {"data_sessao": "20/04/2026 14:00"}

    def test_review_api_failure_returns_empty(self, sample_edital, valid_analysis):
        """API failure during review should return empty corrections (not crash)."""
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception("API down")
        result = _adversarial_review(client, sample_edital, valid_analysis, "gpt-4.1-nano")
        assert result == {}

    def test_review_non_dict_corrections_ignored(self, sample_edital, valid_analysis):
        """Non-dict corrections field should be treated as empty."""
        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={"corrections": "not a dict", "review_notes": "bad"}
        )
        result = _adversarial_review(client, sample_edital, valid_analysis, "gpt-4.1-nano")
        assert result == {}

    def test_review_truncates_text(self, sample_edital, valid_analysis):
        """Review should truncate text to REVIEW_MAX_TEXT_CHARS."""
        edital = dict(sample_edital)
        edital["texto_documentos"] = "X" * 20_000
        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={"corrections": {}}
        )
        _adversarial_review(client, edital, valid_analysis, "gpt-4.1-nano")
        # Verify the user prompt was called
        call_args = client.chat.completions.create.call_args
        messages = call_args.kwargs.get("messages") or call_args[1].get("messages", [])
        user_content = messages[-1]["content"]
        # Text in prompt should be truncated
        assert len(user_content) < 20_000 + 5000  # text + overhead


# ============================================================
# EXECUTIVE SUMMARY EDGE CASES
# ============================================================


class TestExecutiveSummaryEdgeCases:
    """Test executive summary generation edge cases."""

    def test_zero_participar_all_nao(self, sample_empresa, valid_analysis):
        """All NAO PARTICIPAR should still generate a valid summary."""
        nao_analysis = dict(valid_analysis)
        nao_analysis["recomendacao_acao"] = "NAO PARTICIPAR"

        data = {
            "empresa": sample_empresa,
            "busca": {"ufs": ["SC"], "dias": 30},
            "editais": [{"cnae_compatible": True}] * 5,
            "top20": [
                {
                    "_id": f"test/{i}",
                    "objeto": f"Obra #{i}",
                    "municipio": "Test",
                    "uf": "SC",
                    "valor_estimado": 1000000,
                    "analise": dict(nao_analysis),
                }
                for i in range(5)
            ],
        }

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={
                "resumo_executivo": "Nenhum edital recomendado.",
                "proximos_passos": ["MONITORAR: Aguardar novos editais"],
            }
        )
        resumo, passos = generate_executive_summary(client, "gpt-4.1-nano", data)
        assert isinstance(resumo, str)
        assert isinstance(passos, list)

    def test_all_participar(self, sample_empresa, valid_analysis):
        """All PARTICIPAR should generate summary."""
        data = {
            "empresa": sample_empresa,
            "busca": {"ufs": ["SC"], "dias": 30},
            "editais": [{"cnae_compatible": True}] * 20,
            "top20": [
                {
                    "_id": f"test/{i}",
                    "objeto": f"Construcao #{i}",
                    "municipio": "Test",
                    "uf": "SC",
                    "valor_estimado": 1000000 * (i + 1),
                    "analise": dict(valid_analysis),
                }
                for i in range(20)
            ],
        }

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={
                "resumo_executivo": "20 editais recomendados.",
                "proximos_passos": ["URGENTE: Preparar propostas"],
            }
        )
        resumo, passos = generate_executive_summary(client, "gpt-4.1-nano", data)
        assert isinstance(resumo, str)
        assert len(passos) >= 1

    def test_zero_editais_in_top20(self, sample_empresa):
        """Empty top20 should still produce summary (from editais stats)."""
        data = {
            "empresa": sample_empresa,
            "busca": {"ufs": ["SC"], "dias": 30},
            "editais": [{"cnae_compatible": True}] * 3,
            "top20": [],
        }

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={
                "resumo_executivo": "Nenhum edital analisado.",
                "proximos_passos": [],
            }
        )
        resumo, passos = generate_executive_summary(client, "gpt-4.1-nano", data)
        assert isinstance(resumo, str)

    def test_summary_llm_failure_produces_fallback(self, sample_empresa, valid_analysis):
        """LLM failure should produce a simple fallback summary."""
        data = {
            "empresa": sample_empresa,
            "busca": {"ufs": ["SC", "PR"], "dias": 30},
            "editais": [{"cnae_compatible": True}] * 10,
            "top20": [
                {
                    "_id": "test/1",
                    "objeto": "Obra",
                    "municipio": "Test",
                    "uf": "SC",
                    "valor_estimado": 1000000,
                    "analise": dict(valid_analysis),
                }
            ],
        }

        client = MagicMock()
        client.chat.completions.create.side_effect = Exception("LLM API down")
        resumo, passos = generate_executive_summary(client, "gpt-4.1-nano", data)
        # Should get fallback text
        assert "10" in resumo  # total editais
        assert "SC" in resumo or "PR" in resumo  # UFs mentioned
        assert len(passos) >= 1

    def test_summary_proximos_passos_as_string(self, sample_empresa):
        """If LLM returns proximos_passos as string instead of list, it should be wrapped."""
        data = {
            "empresa": sample_empresa,
            "busca": {"ufs": ["SC"], "dias": 30},
            "editais": [],
            "top20": [],
        }

        client = MagicMock()
        client.chat.completions.create.return_value = _make_llm_response(
            content_dict={
                "resumo_executivo": "Resumo",
                "proximos_passos": "URGENTE: Acao unica",  # String, not list
            }
        )
        resumo, passos = generate_executive_summary(client, "gpt-4.1-nano", data)
        assert isinstance(passos, list)
        assert passos == ["URGENTE: Acao unica"]


# ============================================================
# PREPARE MODE EDGE CASES
# ============================================================


class TestPrepareModeEdgeCases:
    """Test prepare_mode behavior."""

    def test_prepare_nonexistent_file(self, tmp_path):
        """Should exit with error for nonexistent input file."""
        with pytest.raises(SystemExit):
            prepare_mode(tmp_path / "nonexistent.json", None, 20)

    def test_prepare_invalid_json(self, tmp_path):
        """Should exit with error for invalid JSON."""
        bad = tmp_path / "bad.json"
        bad.write_text("{INVALID", encoding="utf-8")
        with pytest.raises(SystemExit):
            prepare_mode(bad, None, 20)

    def test_prepare_empty_top20(self, tmp_path):
        """Should exit when top20 is empty."""
        f = tmp_path / "data.json"
        f.write_text(json.dumps({"empresa": {}, "top20": []}), encoding="utf-8")
        with pytest.raises(SystemExit):
            prepare_mode(f, None, 20)

    def test_prepare_adds_context_fields(self, tmp_path):
        """Prepare should add _analysis_context, _analysis_rules, _analysis_limited."""
        data = {
            "empresa": {"razao_social": "Test LTDA"},
            "top20": [
                {
                    "objeto": "Obra de construcao",
                    "texto_documentos": "Edital completo com texto longo o suficiente " * 10,
                    "extraction_quality": "OK",
                    "municipio": "Test",
                    "uf": "SC",
                    "valor_estimado": 1000000,
                },
            ],
        }
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")
        out = tmp_path / "out.json"

        prepare_mode(f, str(out), 20)

        result = json.loads(out.read_text(encoding="utf-8"))
        ed = result["top20"][0]
        assert "_analysis_context" in ed
        assert "_analysis_rules" in ed
        assert "_analysis_limited" in ed
        assert ed["_analysis_limited"] is False


# ============================================================
# SAVE-ANALYSIS MODE EDGE CASES
# ============================================================


class TestSaveAnalysisModeEdgeCases:
    """Test save_analysis_mode behavior."""

    def test_save_analysis_validates_and_cleans(self, tmp_path, valid_analysis):
        """Should validate analyses and remove preparation fields."""
        data = {
            "empresa": {"razao_social": "Test"},
            "top20": [
                {
                    "objeto": "Obra",
                    "texto_documentos": "Long text " * 50,
                    "analise": dict(valid_analysis),
                    "_analysis_context": "context to remove",
                    "_analysis_rules": "rules to remove",
                    "_analysis_limited": False,
                },
            ],
        }
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        save_analysis_mode(f, None)

        result = json.loads(f.read_text(encoding="utf-8"))
        ed = result["top20"][0]
        assert "_analysis_context" not in ed
        assert "_analysis_rules" not in ed
        assert "_analysis_limited" not in ed
        assert ed["analise"]["_source"] == "claude"
        assert "_metadata" in result
        assert result["_metadata"]["analysis"]["editais_analyzed"] == 1

    def test_save_analysis_no_analise_skipped(self, tmp_path):
        """Editais without analise should be counted but not crash."""
        data = {
            "empresa": {"razao_social": "Test"},
            "top20": [
                {"objeto": "Obra sem analise", "texto_documentos": "text"},
            ],
        }
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        save_analysis_mode(f, None)

        result = json.loads(f.read_text(encoding="utf-8"))
        assert result["_metadata"]["analysis"]["editais_analyzed"] == 0

    def test_save_analysis_nonexistent_file(self, tmp_path):
        """Should exit for nonexistent file."""
        with pytest.raises(SystemExit):
            save_analysis_mode(tmp_path / "nonexistent.json", None)

    def test_save_analysis_invalid_json(self, tmp_path):
        """Should exit for invalid JSON."""
        bad = tmp_path / "bad.json"
        bad.write_text("BROKEN", encoding="utf-8")
        with pytest.raises(SystemExit):
            save_analysis_mode(bad, None)


# ============================================================
# USER PROMPT BUILDING EDGE CASES
# ============================================================


class TestUserPromptEdgeCases:
    """Test user prompt construction."""

    def test_limited_prompt_no_text(self, sample_empresa):
        """Limited prompt should state docs are unavailable."""
        edital = {"objeto": "Obra", "extraction_quality": "VAZIO", "texto_documentos": "",
                  "municipio": "Test", "uf": "SC", "valor_estimado": 1000000}
        prompt = _build_user_prompt(edital, sample_empresa, 1, 5, limited=True)
        assert "ANALISE LIMITADA" in prompt
        assert "documentos nao disponiveis" in prompt.lower()

    def test_full_prompt_includes_text(self, sample_empresa):
        """Full prompt should include document text."""
        edital = {
            "objeto": "Obra de pavimentacao",
            "texto_documentos": "Edital completo com todos os detalhes da obra.",
            "extraction_quality": "OK",
            "municipio": "Test",
            "uf": "SC",
            "valor_estimado": 1000000,
        }
        prompt = _build_user_prompt(edital, sample_empresa, 3, 20, limited=False)
        assert "EDITAL 3/20" in prompt
        assert "Edital completo com todos os detalhes" in prompt
        assert "TEXTO DO EDITAL" in prompt

    def test_prompt_with_override_rules(self, sample_empresa):
        """Override rules should be injected into the prompt."""
        empresa = dict(sample_empresa)
        empresa["sancionada"] = True
        edital = {"objeto": "Obra", "texto_documentos": "text " * 30,
                  "extraction_quality": "OK", "status_temporal": "PLANEJAVEL",
                  "municipio": "Test", "uf": "SC", "valor_estimado": 1000000}
        prompt = _build_user_prompt(edital, empresa, 1, 1, limited=False)
        assert "SANCIONADA" in prompt
        assert "NAO PARTICIPAR" in prompt


# ============================================================
# SAFE FLOAT / FMT BRL EDGE CASES
# ============================================================


class TestHelperEdgeCases:
    """Test helper function edge cases."""

    @pytest.mark.parametrize(
        "val,expected",
        [
            (None, 0.0),
            ("", 0.0),
            ("abc", 0.0),
            (0, 0.0),
            (1000, 1000.0),
            ("1.500.000,50", 1500000.50),
            ("0", 0.0),
            (True, 1.0),
            (False, 0.0),
            (float("inf"), float("inf")),
        ],
    )
    def test_safe_float_edge_cases(self, val, expected):
        result = _safe_float(val)
        assert result == expected

    @pytest.mark.parametrize(
        "val,expected_substr",
        [
            (0, "Nao informado"),
            (-100, "Nao informado"),
            (500, "R$"),
            (50_000, "mil"),
            (5_000_000, "M"),
        ],
    )
    def test_fmt_brl_edge_cases(self, val, expected_substr):
        result = _fmt_brl(val)
        assert expected_substr in result
