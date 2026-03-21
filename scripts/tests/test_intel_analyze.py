#!/usr/bin/env python3
"""Tests for intel-analyze.py — LLM-driven edital analysis."""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from types import SimpleNamespace

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "intel_analyze", SCRIPTS_DIR / "intel-analyze.py"
)
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
prepare_mode = intel_analyze.prepare_mode
save_analysis_mode = intel_analyze.save_analysis_mode


# ============================================================
# HELPERS
# ============================================================


class TestSafeFloat:
    def test_none(self):
        assert _safe_float(None) == 0.0

    def test_int(self):
        assert _safe_float(1000) == 1000.0

    def test_float(self):
        assert _safe_float(1500.5) == 1500.5

    def test_string_br_format(self):
        # "1.500.000,50" -> 1500000.50
        assert _safe_float("1.500.000,50") == 1500000.50

    def test_invalid_string(self):
        assert _safe_float("abc") == 0.0

    def test_empty_string(self):
        assert _safe_float("") == 0.0


class TestFmtBrl:
    def test_millions(self):
        assert "M" in _fmt_brl(5_000_000)

    def test_thousands(self):
        assert "mil" in _fmt_brl(50_000)

    def test_small(self):
        assert "R$" in _fmt_brl(500)

    def test_zero(self):
        assert _fmt_brl(0) == "Nao informado"

    def test_negative(self):
        assert _fmt_brl(-100) == "Nao informado"


# ============================================================
# ANALYSIS SCHEMA VALIDATION
# ============================================================


class TestValidateAnalysis:
    def test_fills_missing_fields(self):
        raw = {"recomendacao_acao": "PARTICIPAR"}
        result = _validate_analysis(raw)
        for field in ANALYSIS_FIELDS:
            assert field in result

    def test_missing_list_fields_get_default(self):
        raw = {}
        result = _validate_analysis(raw)
        assert isinstance(result["requisitos_tecnicos"], list)
        assert isinstance(result["requisitos_habilitacao"], list)

    def test_string_list_field_converted(self):
        raw = {"requisitos_tecnicos": "Acervo tecnico"}
        result = _validate_analysis(raw)
        assert result["requisitos_tecnicos"] == ["Acervo tecnico"]

    def test_nivel_dificuldade_normalized(self):
        raw = {"nivel_dificuldade": "medio"}
        result = _validate_analysis(raw)
        assert result["nivel_dificuldade"] == "MEDIO"

    def test_invalid_nivel_defaults_medio(self):
        raw = {"nivel_dificuldade": "EXTREMO"}
        result = _validate_analysis(raw)
        assert result["nivel_dificuldade"] == "MEDIO"

    def test_recomendacao_nao_participar(self):
        raw = {"recomendacao_acao": "nao participar"}
        result = _validate_analysis(raw)
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"

    def test_recomendacao_participar(self):
        raw = {"recomendacao_acao": "participar"}
        result = _validate_analysis(raw)
        assert result["recomendacao_acao"] == "PARTICIPAR"

    def test_recomendacao_unclear_defaults_nao(self):
        """Unclear recommendation defaults to NAO PARTICIPAR (zero noise)."""
        raw = {"recomendacao_acao": "avaliar com cautela"}
        result = _validate_analysis(raw)
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"

    def test_recomendacao_with_accent(self):
        raw = {"recomendacao_acao": "NÃO PARTICIPAR"}
        result = _validate_analysis(raw)
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"

    def test_all_16_fields_present(self):
        assert len(ANALYSIS_FIELDS) == 17  # custo_logistico_nota is the 17th
        raw = {}
        result = _validate_analysis(raw)
        for field in ANALYSIS_FIELDS:
            assert field in result


# ============================================================
# FALLBACK ANALYSIS
# ============================================================


class TestFallbackAnalysis:
    def test_basic_fallback(self):
        edital = {
            "objeto": "Pavimentacao de ruas",
            "municipio": "Joinville",
            "uf": "SC",
            "valor_estimado": 1000000,
        }
        empresa = {"sancionada": False}
        result = _fallback_analysis(edital, empresa, "timeout error")
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"
        assert result["_source"] == "fallback"
        assert "timeout error" in result["_error"]

    def test_sancionada_fallback(self):
        edital = {"objeto": "Obra", "municipio": "X", "uf": "SC"}
        empresa = {"sancionada": True}
        result = _fallback_analysis(edital, empresa, "api down")
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"
        assert "sancionada" in result["observacoes_criticas"].lower()

    def test_expirado_fallback(self):
        edital = {
            "objeto": "Obra",
            "municipio": "X",
            "uf": "SC",
            "status_temporal": "EXPIRADO",
        }
        empresa = {"sancionada": False}
        result = _fallback_analysis(edital, empresa, "error")
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"
        assert "encerrado" in result["observacoes_criticas"].lower()

    def test_fallback_has_all_fields(self):
        edital = {"objeto": "X", "municipio": "Y", "uf": "Z"}
        empresa = {}
        result = _fallback_analysis(edital, empresa, "err")
        for field in ANALYSIS_FIELDS:
            assert field in result


# ============================================================
# LLM CALL (mocked)
# ============================================================


def _mock_llm_response(content_json):
    """Create a mock OpenAI response object."""
    message = SimpleNamespace(content=json.dumps(content_json))
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


class TestCallLlm:
    def test_valid_json_response(self):
        expected = {"resumo_objeto": "Teste", "recomendacao_acao": "PARTICIPAR"}
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_llm_response(expected)
        result = _call_llm(client, "gpt-4.1-nano", "system", "user")
        assert result["resumo_objeto"] == "Teste"

    def test_malformed_json_in_code_block(self):
        """LLM sometimes wraps JSON in markdown code block."""
        raw_json = '{"resumo_objeto": "Test"}'
        content = f"```json\n{raw_json}\n```"
        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message)
        response = SimpleNamespace(choices=[choice])
        client = MagicMock()
        client.chat.completions.create.return_value = response
        result = _call_llm(client, "gpt-4.1-nano", "system", "user")
        assert result["resumo_objeto"] == "Test"

    def test_empty_response_returns_empty_dict(self):
        message = SimpleNamespace(content=None)
        choice = SimpleNamespace(message=message)
        response = SimpleNamespace(choices=[choice])
        client = MagicMock()
        client.chat.completions.create.return_value = response
        result = _call_llm(client, "gpt-4.1-nano", "system", "user")
        assert result == {}

    def test_non_json_raises(self):
        message = SimpleNamespace(content="This is not JSON at all")
        choice = SimpleNamespace(message=message)
        response = SimpleNamespace(choices=[choice])
        client = MagicMock()
        client.chat.completions.create.return_value = response
        with pytest.raises(ValueError, match="nao-JSON"):
            _call_llm(client, "gpt-4.1-nano", "system", "user")


# ============================================================
# analyze_edital (integration with mocked LLM)
# ============================================================


class TestAnalyzeEdital:
    def test_successful_analysis(self):
        llm_result = {
            "resumo_objeto": "Pavimentacao de vias",
            "requisitos_tecnicos": ["Acervo tecnico"],
            "requisitos_habilitacao": ["CND"],
            "qualificacao_economica": "R$ 100.000",
            "prazo_execucao": "180 dias",
            "garantias": "5%",
            "criterio_julgamento": "Menor Preco",
            "data_sessao": "15/04/2026",
            "prazo_proposta": "10/04/2026",
            "visita_tecnica": "Facultativa",
            "exclusividade_me_epp": "Nao",
            "regime_execucao": "Empreitada por preco global",
            "consorcio": "Vedado",
            "observacoes_criticas": "Compativel com perfil",
            "nivel_dificuldade": "MEDIO",
            "recomendacao_acao": "PARTICIPAR",
            "custo_logistico_nota": "180 km",
        }
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_llm_response(llm_result)

        edital = {
            "objeto": "Pavimentacao asfaltica",
            "uf": "SC",
            "municipio": "Joinville",
            "valor_estimado": 1500000,
            "texto_documentos": "Texto longo do edital. " * 20,  # >100 chars to avoid "limited"
        }
        empresa = {"razao_social": "LCM", "sancionada": False}

        result = analyze_edital(client, "gpt-4.1-nano", edital, empresa, 1, 1)
        assert result["recomendacao_acao"] == "PARTICIPAR"
        assert result["_source"] == "llm"

    def test_llm_failure_produces_fallback(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception("API timeout")

        edital = {
            "objeto": "Obra de drenagem",
            "uf": "SC",
            "municipio": "Blumenau",
            "valor_estimado": 500000,
            "texto_documentos": "Texto",
        }
        empresa = {"razao_social": "LCM", "sancionada": False}

        result = analyze_edital(client, "gpt-4.1-nano", edital, empresa, 1, 1)
        assert result["_source"] == "fallback"
        assert result["recomendacao_acao"] == "NAO PARTICIPAR"

    def test_limited_analysis_when_no_text(self):
        llm_result = {"recomendacao_acao": "NAO PARTICIPAR", "nivel_dificuldade": "ALTO"}
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_llm_response(llm_result)

        edital = {
            "objeto": "Obra",
            "uf": "SC",
            "municipio": "X",
            "texto_documentos": "",
            "extraction_quality": "VAZIO",
        }
        empresa = {"razao_social": "LCM"}

        result = analyze_edital(client, "gpt-4.1-nano", edital, empresa, 1, 1)
        assert result["_source"] == "llm_limited"


# ============================================================
# ENRICHMENT CONTEXT & OVERRIDE RULES
# ============================================================


class TestBuildEnrichmentContext:
    def test_basic_context(self):
        edital = {
            "objeto": "Obra de pavimentacao",
            "municipio": "Joinville",
            "uf": "SC",
            "valor_estimado": 1500000,
            "modalidade_nome": "Pregao Eletronico",
            "orgao_nome": "Prefeitura Municipal",
        }
        empresa = {"razao_social": "LCM", "cidade_sede": "Florianopolis", "uf_sede": "SC"}
        ctx = _build_enrichment_context(edital, empresa)
        assert "LCM" in ctx
        assert "Joinville" in ctx

    def test_distance_included(self):
        edital = {"distancia": {"km": 300}}
        empresa = {"razao_social": "X"}
        ctx = _build_enrichment_context(edital, empresa)
        assert "300" in ctx

    def test_sancionada_warning(self):
        edital = {}
        empresa = {"razao_social": "X", "sancionada": True}
        ctx = _build_enrichment_context(edital, empresa)
        assert "SANCIONADA" in ctx


class TestBuildOverrideRules:
    def test_sancionada_rule(self):
        edital = {}
        empresa = {"sancionada": True}
        rules = _build_override_rules(edital, empresa)
        assert "NAO PARTICIPAR" in rules

    def test_expirado_rule(self):
        edital = {"status_temporal": "EXPIRADO"}
        empresa = {}
        rules = _build_override_rules(edital, empresa)
        assert "NAO PARTICIPAR" in rules

    def test_urgente_rule(self):
        edital = {"status_temporal": "URGENTE"}
        empresa = {}
        rules = _build_override_rules(edital, empresa)
        assert "urgencia" in rules.lower()

    def test_high_distance_rule(self):
        edital = {"distancia": {"km": 600}}
        empresa = {}
        rules = _build_override_rules(edital, empresa)
        assert "600" in rules

    def test_desfavoravel_roi_rule(self):
        edital = {"roi_proposta": {"classificacao": "DESFAVORAVEL"}}
        empresa = {}
        rules = _build_override_rules(edital, empresa)
        assert "DESFAVORAVEL" in rules

    def test_small_pop_high_value(self):
        edital = {
            "ibge": {"populacao": 3000},
            "valor_estimado": 2000000,
        }
        empresa = {}
        rules = _build_override_rules(edital, empresa)
        assert "3,000" in rules or "3000" in rules

    def test_no_rules_returns_empty(self):
        edital = {}
        empresa = {}
        rules = _build_override_rules(edital, empresa)
        assert rules == ""


# ============================================================
# PREPARE MODE
# ============================================================


class TestPrepareMode:
    def test_prepare_adds_context(self, tmp_path):
        data = {
            "empresa": {"razao_social": "LCM", "cidade_sede": "Floripa", "uf_sede": "SC"},
            "top20": [
                {
                    "objeto": "Obra de pavimentacao",
                    "texto_documentos": "Texto longo " * 50,
                    "uf": "SC",
                    "municipio": "X",
                },
            ],
        }
        input_path = tmp_path / "input.json"
        input_path.write_text(json.dumps(data), encoding="utf-8")

        prepare_mode(input_path, str(input_path), top_n=20)

        result = json.loads(input_path.read_text(encoding="utf-8"))
        ed = result["top20"][0]
        assert "_analysis_context" in ed
        assert "_analysis_rules" in ed
        assert "_analysis_limited" in ed
        assert ed["_analysis_limited"] is False

    def test_prepare_limited_when_no_text(self, tmp_path):
        data = {
            "empresa": {"razao_social": "X"},
            "top20": [
                {"objeto": "Obra", "texto_documentos": "", "extraction_quality": "VAZIO"},
            ],
        }
        input_path = tmp_path / "input.json"
        input_path.write_text(json.dumps(data), encoding="utf-8")

        prepare_mode(input_path, str(input_path), top_n=20)

        result = json.loads(input_path.read_text(encoding="utf-8"))
        assert result["top20"][0]["_analysis_limited"] is True


# ============================================================
# SAVE-ANALYSIS MODE
# ============================================================


class TestSaveAnalysisMode:
    def test_validates_and_cleans(self, tmp_path):
        data = {
            "top20": [
                {
                    "objeto": "Obra",
                    "texto_documentos": "Texto",
                    "_analysis_context": "ctx",
                    "_analysis_rules": "rules",
                    "_analysis_limited": False,
                    "analise": {
                        "recomendacao_acao": "participar",
                        "nivel_dificuldade": "medio",
                    },
                },
            ],
        }
        input_path = tmp_path / "input.json"
        input_path.write_text(json.dumps(data), encoding="utf-8")

        save_analysis_mode(input_path, str(input_path))

        result = json.loads(input_path.read_text(encoding="utf-8"))
        ed = result["top20"][0]
        # Preparation fields removed
        assert "_analysis_context" not in ed
        assert "_analysis_rules" not in ed
        # Analysis validated
        assert ed["analise"]["recomendacao_acao"] == "PARTICIPAR"
        assert ed["analise"]["nivel_dificuldade"] == "MEDIO"
        # Metadata added
        assert "_metadata" in result
        assert result["_metadata"]["analysis"]["participar"] == 1


# ============================================================
# STATUS TEMPORAL HANDLING
# ============================================================


class TestStatusTemporal:
    def test_urgente_triggers_override(self):
        edital = {"status_temporal": "URGENTE"}
        rules = _build_override_rules(edital, {})
        assert "urgencia" in rules.lower()

    def test_expirado_triggers_nao_participar(self):
        edital = {"status_temporal": "EXPIRADO"}
        rules = _build_override_rules(edital, {})
        assert "NAO PARTICIPAR" in rules

    def test_planejavel_no_override(self):
        edital = {"status_temporal": "PLANEJAVEL"}
        rules = _build_override_rules(edital, {})
        assert rules == ""


# ============================================================
# CLI INTEGRATION
# ============================================================


class TestCLI:
    def test_missing_input_exits(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "intel-analyze.py")],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0

    def test_nonexistent_file_exits(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-analyze.py"),
                "--input", str(tmp_path / "nope.json"),
                "--prepare",
            ],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0

    def test_prepare_mode_cli(self, tmp_path):
        data = {
            "empresa": {"razao_social": "Test"},
            "top20": [{"objeto": "Obra", "texto_documentos": "X" * 200}],
        }
        path = tmp_path / "input.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-analyze.py"),
                "--input", str(path),
                "--prepare",
            ],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0

    def test_api_mode_no_key_exits(self, tmp_path):
        """API mode without OPENAI_API_KEY should exit with error."""
        data = {
            "empresa": {"razao_social": "Test"},
            "top20": [{"objeto": "Obra", "texto_documentos": "X" * 200}],
        }
        path = tmp_path / "input.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        env = {k: v for k, v in __import__("os").environ.items()}
        env.pop("OPENAI_API_KEY", None)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-analyze.py"),
                "--input", str(path),
            ],
            capture_output=True, text=True, timeout=15,
            env=env,
        )
        assert result.returncode != 0
        assert "OPENAI_API_KEY" in result.stderr
