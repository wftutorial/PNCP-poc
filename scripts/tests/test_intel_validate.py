#!/usr/bin/env python3
"""Tests for intel-validate.py — Gates 2, 4, 5 + --fix mode + CLI."""
import copy
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

# Import the module under test by executing its path
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "intel_validate", SCRIPTS_DIR / "intel-validate.py"
)
intel_validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intel_validate)

# Aliases for key functions/constants
gate2_semantic = intel_validate.gate2_semantic
gate4_completeness = intel_validate.gate4_completeness
gate5_coherence = intel_validate.gate5_coherence
validate_v4_fields = intel_validate.validate_v4_fields
_normalize_text = intel_validate._normalize_text
_extract_cnae_prefixes = intel_validate._extract_cnae_prefixes
_check_enum_field = intel_validate._check_enum_field
_is_valid_date = intel_validate._is_valid_date
FORBIDDEN_WORDS_PATTERNS = intel_validate.FORBIDDEN_WORDS_PATTERNS
CRITERIO_JULGAMENTO_ENUM = intel_validate.CRITERIO_JULGAMENTO_ENUM
REGIME_EXECUCAO_ENUM = intel_validate.REGIME_EXECUCAO_ENUM
CONSORCIO_ENUM = intel_validate.CONSORCIO_ENUM
RECOMENDACAO_ENUM = intel_validate.RECOMENDACAO_ENUM


# ============================================================
# HELPERS — _normalize_text, _extract_cnae_prefixes
# ============================================================


class TestNormalizeText:
    def test_lowercases(self):
        assert _normalize_text("ABC") == "abc"

    def test_strips_accents(self):
        assert _normalize_text("construção") == "construcao"
        assert _normalize_text("licitação") == "licitacao"

    def test_empty(self):
        assert _normalize_text("") == ""


class TestExtractCnaePrefixes:
    def test_extracts_principal(self):
        empresa = {"cnae_principal": "4120400"}
        assert _extract_cnae_prefixes(empresa) == {"41"}

    def test_extracts_secundarios_list(self):
        empresa = {
            "cnae_principal": "4120400",
            "cnaes_secundarios": ["4211101", "7112000"],
        }
        assert _extract_cnae_prefixes(empresa) == {"41", "42", "71"}

    def test_extracts_secundarios_string(self):
        empresa = {"cnae_principal": "4120400", "cnaes_secundarios": "4211101, 7112000"}
        assert _extract_cnae_prefixes(empresa) == {"41", "42", "71"}

    def test_empty_empresa(self):
        assert _extract_cnae_prefixes({}) == set()

    def test_short_cnae_ignored(self):
        empresa = {"cnae_principal": "4"}
        assert _extract_cnae_prefixes(empresa) == set()


class TestCheckEnumField:
    def test_exact_match(self):
        assert _check_enum_field("menor preco", CRITERIO_JULGAMENTO_ENUM)

    def test_prefix_match(self):
        assert _check_enum_field(
            "Menor Preco Global, modo de disputa Aberto", CRITERIO_JULGAMENTO_ENUM
        )

    def test_no_match(self):
        assert not _check_enum_field("qualidade total", CRITERIO_JULGAMENTO_ENUM)

    def test_empty_string(self):
        assert not _check_enum_field("", CRITERIO_JULGAMENTO_ENUM)


class TestIsValidDate:
    def test_valid_dd_mm_yyyy(self):
        assert _is_valid_date("15/04/2026")

    def test_valid_iso(self):
        assert _is_valid_date("2026-04-15")

    def test_nao_consta(self):
        assert _is_valid_date("Nao consta no edital disponivel")

    def test_invalid(self):
        assert not _is_valid_date("amanha")

    def test_nao_informado(self):
        assert _is_valid_date("Nao informado")


# ============================================================
# GATE 2 — SEMANTIC COMPATIBILITY
# ============================================================


class TestGate2Semantic:
    """Gate 2: Reject tenders semantically incompatible with company CNAEs."""

    def test_rejects_software_for_construction(self, make_edital, sample_empresa):
        """Software/TI edital must be flagged for a construction company (CNAE 41/42/43)."""
        empresa = {**sample_empresa, "cnae_principal": "4120400", "cnaes_secundarios": []}
        top20 = [make_edital(objeto="Aquisicao de software ERP para gestao municipal")]
        result, decisions, removed = gate2_semantic(top20, empresa)
        assert not result["passed"]
        assert len(result["issues"]) >= 1
        assert "software_for_construction" in result["issues"][0]

    def test_rejects_food_for_engineering(self, make_edital, sample_empresa):
        """Food/meal edital must be flagged for engineering company (CNAE 71)."""
        empresa = {**sample_empresa, "cnae_principal": "7112000", "cnaes_secundarios": []}
        top20 = [make_edital(objeto="Fornecimento de alimentacao e refeicao para escola")]
        result, decisions, removed = gate2_semantic(top20, empresa)
        assert not result["passed"]
        assert any("food_for_engineering" in i for i in result["issues"])

    def test_rejects_cleaning_for_construction(self, make_edital, sample_empresa):
        """Cleaning services flagged for construction company."""
        empresa = {**sample_empresa, "cnae_principal": "4211100", "cnaes_secundarios": []}
        top20 = [make_edital(objeto="Servicos de limpeza e conservacao predial")]
        result, decisions, removed = gate2_semantic(top20, empresa)
        assert not result["passed"]

    def test_rejects_concession_for_construction(self, make_edital, sample_empresa):
        """Concession edital flagged for construction."""
        empresa = {**sample_empresa, "cnae_principal": "4211100", "cnaes_secundarios": []}
        top20 = [make_edital(objeto="Concessao de iluminacao publica municipal")]
        result, decisions, removed = gate2_semantic(top20, empresa)
        assert not result["passed"]

    def test_accepts_legitimate_construction(self, make_edital, sample_empresa):
        """Legitimate construction edital passes gate 2."""
        top20 = [make_edital(objeto="Pavimentacao asfaltica em vias urbanas do centro")]
        result, decisions, removed = gate2_semantic(top20, sample_empresa)
        assert result["passed"]
        assert len(result["issues"]) == 0

    def test_mixed_cnaes_not_all_in_trigger_set(self, make_edital, sample_empresa):
        """If company has CNAEs outside the trigger set, pattern should not trigger."""
        empresa = {
            **sample_empresa,
            "cnae_principal": "4120400",
            "cnaes_secundarios": ["6201501"],  # CNAE 62 = software
        }
        top20 = [make_edital(objeto="Aquisicao de software de gestao")]
        result, decisions, removed = gate2_semantic(top20, empresa)
        # cnae_prefixes = {41, 62} — NOT a subset of {42, 43, 41} because 62 is outside
        assert result["passed"]

    def test_no_cnaes_skips_gate(self, make_edital):
        """If empresa has no CNAEs, gate 2 returns early with just a dict (not a tuple)."""
        empresa = {"razao_social": "Empresa Sem CNAE"}
        top20 = [make_edital(objeto="Software ERP")]
        # Early return is just the result dict, not (result, decisions, removed)
        ret = gate2_semantic(top20, empresa)
        if isinstance(ret, tuple):
            result = ret[0]
        else:
            result = ret
        issues_text = " ".join(result["issues"])
        assert "ignorado" in issues_text.lower()

    def test_fix_removes_incompatible(self, make_edital, sample_empresa):
        """--fix mode removes incompatible editais from top20."""
        empresa = {**sample_empresa, "cnae_principal": "4120400", "cnaes_secundarios": []}
        top20 = [
            make_edital(objeto="Software ERP para prefeitura"),
            make_edital(objeto="Construcao de escola municipal"),
        ]
        assert len(top20) == 2
        result, decisions, removed = gate2_semantic(top20, empresa, do_fix=True)
        assert len(top20) == 1  # incompatible removed in-place
        assert len(removed) == 1
        assert "Software" in removed[0]["objeto"]

    def test_fix_preserves_compatible(self, make_edital, sample_empresa):
        """--fix mode preserves compatible editais."""
        top20 = [
            make_edital(objeto="Reforma de edificio publico"),
            make_edital(objeto="Pavimentacao de ruas"),
        ]
        original_len = len(top20)
        result, decisions, removed = gate2_semantic(top20, sample_empresa, do_fix=True)
        assert len(top20) == original_len
        assert len(removed) == 0


# ============================================================
# GATE 4 — ANALYSIS COMPLETENESS
# ============================================================


class TestGate4Completeness:
    """Gate 4: Validate analysis fields, forbidden words, enums."""

    def test_valid_analysis_passes(self, make_edital, valid_analise, sample_empresa):
        top20 = [make_edital(analise=dict(valid_analise))]
        result = gate4_completeness(top20, sample_empresa)
        assert result["passed"]
        assert len(result["issues"]) == 0

    def test_detects_verificar(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["garantias"] = "Verificar no edital completo"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]
        assert any("verificar" in fw["word"] for fw in result["forbidden_words_found"])

    def test_detects_possivelmente(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["prazo_execucao"] = "Possivelmente 180 dias"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_detects_a_confirmar(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["criterio_julgamento"] = "A confirmar"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_detects_buscar_edital(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["observacoes_criticas"] = "Necessario buscar edital completo"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_detects_nao_detalhado(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["qualificacao_economica"] = "Nao detalhado no documento"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_invalid_criterio_julgamento(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["criterio_julgamento"] = "Qualidade Total"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]
        assert any("criterio_julgamento" in mf["field"] for mf in result["missing_fields"])

    def test_invalid_regime_execucao(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["regime_execucao"] = "Alguma coisa invalida"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_invalid_consorcio(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["consorcio"] = "Talvez"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_recomendacao_verificar_is_invalid(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "VERIFICAR"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_recomendacao_participar_valid(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "PARTICIPAR"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        # Should pass on recomendacao (may fail on other fields if any)
        rec_issues = [i for i in result["issues"] if "recomendacao_acao" in i]
        assert len(rec_issues) == 0

    def test_recomendacao_nao_participar_valid(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "NAO PARTICIPAR"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        rec_issues = [i for i in result["issues"] if "recomendacao_acao" in i]
        assert len(rec_issues) == 0

    def test_expirado_must_be_nao_participar(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "PARTICIPAR"
        top20 = [make_edital(analise=analise, status_temporal="EXPIRADO")]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]
        assert any("EXPIRADO" in i for i in result["issues"])

    def test_sancionada_must_be_nao_participar(self, make_edital, valid_analise):
        empresa = {"sancionada": True, "sancoes": {}, "cnae_principal": "4120400"}
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "PARTICIPAR"
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, empresa)
        assert not result["passed"]
        assert any("sancionada" in i for i in result["issues"])

    def test_missing_analise_handled(self, make_edital, sample_empresa):
        """Edital without analysis dict should not crash."""
        top20 = [make_edital()]  # no analise key
        result = gate4_completeness(top20, sample_empresa)
        # Should flag missing required fields
        assert not result["passed"]

    def test_forbidden_word_in_list_field(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["requisitos_tecnicos"] = [
            "Acervo tecnico",
            "Verificar documentacao junto ao orgao",
        ]
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]

    def test_fix_replaces_verificar(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["garantias"] = "Verificar no edital"
        top20 = [make_edital(analise=analise)]
        gate4_completeness(top20, sample_empresa, do_fix=True)
        # After fix, the field should no longer contain "verificar"
        assert "verificar" not in top20[0]["analise"]["garantias"].lower()

    def test_fix_replaces_invalid_recomendacao(self, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "VERIFICAR"
        top20 = [make_edital(analise=analise)]
        gate4_completeness(top20, sample_empresa, do_fix=True)
        assert top20[0]["analise"]["recomendacao_acao"] == "NAO PARTICIPAR"

    def test_nao_consta_embedded_in_long_text(self, make_edital, valid_analise, sample_empresa):
        """'Nao consta' embedded in a sentence > 50 chars should be flagged."""
        analise = dict(valid_analise)
        analise["qualificacao_economica"] = (
            "A empresa deve apresentar balanco patrimonial. "
            "Nao consta no edital disponivel informacao sobre indice de liquidez."
        )
        top20 = [make_edital(analise=analise)]
        result = gate4_completeness(top20, sample_empresa)
        assert not result["passed"]
        assert any("Nao consta" in i for i in result["issues"])


# ============================================================
# GATE 5 — REPORT COHERENCE
# ============================================================


class TestGate5Coherence:
    """Gate 5: No expired in top20, completeness threshold, proximos_passos coherence."""

    def test_no_expired_passes(self, make_top20):
        top20 = make_top20(5, status_temporal="PLANEJAVEL")
        result, removed = gate5_coherence(top20)
        # Should have no expired-related issues
        expired_issues = [i for i in result["issues"] if "EXPIRADO" in i]
        assert len(expired_issues) == 0

    def test_expired_in_top20_fails(self, make_edital, valid_analise):
        top20 = [
            make_edital(analise=dict(valid_analise), status_temporal="PLANEJAVEL"),
            make_edital(analise=dict(valid_analise), status_temporal="EXPIRADO"),
        ]
        result, removed = gate5_coherence(top20)
        assert not result["passed"]
        assert any("EXPIRADO" in i for i in result["issues"])

    def test_fix_removes_expired(self, make_edital, valid_analise):
        top20 = [
            make_edital(analise=dict(valid_analise), status_temporal="PLANEJAVEL"),
            make_edital(analise=dict(valid_analise), status_temporal="EXPIRADO"),
            make_edital(analise=dict(valid_analise), status_temporal="PLANEJAVEL"),
        ]
        assert len(top20) == 3
        result, removed = gate5_coherence(top20, do_fix=True)
        assert len(top20) == 2
        assert len(removed) == 1

    def test_campos_completos_pct_calculation(self, make_top20):
        top20 = make_top20(3)
        result, removed = gate5_coherence(top20)
        assert result["campos_completos_pct"] == 100

    def test_campos_completos_below_threshold(self, make_edital):
        """Empty analysis fields lower the completeness percentage."""
        analise_empty = {
            "data_sessao": "",
            "criterio_julgamento": "",
            "regime_execucao": "",
            "consorcio": "",
            "recomendacao_acao": "",
        }
        top20 = [make_edital(analise=analise_empty, status_temporal="PLANEJAVEL")]
        result, removed = gate5_coherence(top20)
        assert result["campos_completos_pct"] == 0
        assert not result["passed"]

    def test_proximos_passos_no_nao_participar_municipio(self, make_edital, valid_analise):
        """proximos_passos must not reference NAO PARTICIPAR municipalities."""
        analise_np = dict(valid_analise)
        analise_np["recomendacao_acao"] = "NAO PARTICIPAR"
        top20 = [
            make_edital(
                analise=analise_np,
                municipio="Joinville",
                municipio_nome="Joinville",
                status_temporal="PLANEJAVEL",
            ),
        ]
        data_root = {
            "proximos_passos": [
                "URGENTE: Preparar proposta para edital de Joinville",
                "MONITORAR: Acompanhar editais em Florianopolis",
            ]
        }
        result, removed = gate5_coherence(top20, data_root=data_root)
        assert not result["passed"]
        assert any("municipio" in i.lower() for i in result["issues"])

    def test_fix_removes_nao_participar_proximos_passos(self, make_edital, valid_analise):
        """--fix removes proximos_passos that reference NAO PARTICIPAR municipalities."""
        analise_np = dict(valid_analise)
        analise_np["recomendacao_acao"] = "NAO PARTICIPAR"
        top20 = [
            make_edital(
                analise=analise_np,
                municipio="Joinville",
                municipio_nome="Joinville",
                status_temporal="PLANEJAVEL",
            ),
        ]
        data_root = {
            "proximos_passos": [
                "URGENTE: Proposta para Joinville",
                "MONITORAR: Novos editais em Florianopolis",
            ]
        }
        result, removed = gate5_coherence(top20, do_fix=True, data_root=data_root)
        assert len(data_root["proximos_passos"]) == 1
        assert "Florianopolis" in data_root["proximos_passos"][0]

    def test_missing_analise_flagged(self, make_edital):
        """Edital without analise in top20 should be flagged."""
        top20 = [make_edital(status_temporal="PLANEJAVEL")]  # no analise
        result, removed = gate5_coherence(top20)
        assert not result["passed"]
        assert any("sem analise" in i for i in result["issues"])

    def test_missing_data_sessao_and_status(self, make_edital, valid_analise):
        """Edital without data_sessao AND status_temporal should fail."""
        analise = dict(valid_analise)
        analise["data_sessao"] = ""
        top20 = [make_edital(analise=analise, status_temporal="")]
        result, removed = gate5_coherence(top20)
        assert not result["passed"]


# ============================================================
# V4 FIELDS VALIDATION
# ============================================================


class TestValidateV4Fields:
    def test_valid_v4(self, make_edital, sample_empresa):
        top20 = [
            make_edital(
                cnae_confidence=0.85,
                _victory_fit=0.7,
                _bid_simulation={"has_data": True, "lance_sugerido": 1000000},
                _delta_status="NOVO",
                _structured_extraction={"fields": {}},
            )
        ]
        result = validate_v4_fields(top20, sample_empresa)
        assert result["passed"]
        assert result["stats"]["with_confidence"] == 1

    def test_invalid_cnae_confidence_out_of_range(self, make_edital, sample_empresa):
        top20 = [make_edital(cnae_confidence=1.5)]
        result = validate_v4_fields(top20, sample_empresa)
        assert not result["passed"]

    def test_invalid_delta_status(self, make_edital, sample_empresa):
        top20 = [make_edital(_delta_status="INVALIDO")]
        result = validate_v4_fields(top20, sample_empresa)
        assert not result["passed"]

    def test_bid_has_data_but_zero_lance(self, make_edital, sample_empresa):
        top20 = [
            make_edital(_bid_simulation={"has_data": True, "lance_sugerido": 0})
        ]
        result = validate_v4_fields(top20, sample_empresa)
        assert not result["passed"]


# ============================================================
# --fix MODE IDEMPOTENCY
# ============================================================


class TestFixIdempotency:
    def test_fix_is_idempotent(self, make_edital, valid_analise, sample_empresa):
        """Running fix twice produces the same result."""
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "VERIFICAR"
        analise["garantias"] = "Verificar no edital"
        top20 = [make_edital(analise=analise, status_temporal="PLANEJAVEL")]
        data = {"top20": top20, "empresa": sample_empresa}

        # First fix pass
        gate4_completeness(data["top20"], data["empresa"], do_fix=True)
        state_after_first = json.dumps(data, sort_keys=True)

        # Second fix pass
        gate4_completeness(data["top20"], data["empresa"], do_fix=True)
        state_after_second = json.dumps(data, sort_keys=True)

        assert state_after_first == state_after_second

    def test_fix_preserves_valid_data(self, make_edital, valid_analise, sample_empresa):
        """Fix should not modify already-valid data."""
        top20 = [make_edital(analise=dict(valid_analise), status_temporal="PLANEJAVEL")]
        original = json.dumps(top20[0]["analise"], sort_keys=True)
        gate4_completeness(top20, sample_empresa, do_fix=True)
        after = json.dumps(top20[0]["analise"], sort_keys=True)
        assert original == after


# ============================================================
# CLI INTEGRATION
# ============================================================


class TestCLI:
    def test_missing_input_exits(self, tmp_path):
        """Missing --input should cause non-zero exit."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "intel-validate.py")],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0

    def test_nonexistent_file_exits(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-validate.py"),
                "--input", str(tmp_path / "nonexistent.json"),
            ],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0

    def test_empty_top20_exits(self, write_json):
        path = write_json({"top20": [], "empresa": {}})
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-validate.py"),
                "--input", str(path),
            ],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0

    def test_valid_input_runs(self, write_json, make_edital, valid_analise, sample_empresa):
        top20 = [make_edital(analise=dict(valid_analise), status_temporal="PLANEJAVEL")]
        data = {"top20": top20, "empresa": sample_empresa}
        path = write_json(data)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-validate.py"),
                "--input", str(path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0

    def test_strict_fails_on_issues(self, write_json, make_edital, sample_empresa):
        analise = {"recomendacao_acao": "VERIFICAR"}
        top20 = [make_edital(analise=analise, status_temporal="PLANEJAVEL")]
        data = {"top20": top20, "empresa": sample_empresa}
        path = write_json(data)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-validate.py"),
                "--input", str(path),
                "--strict",
            ],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 1

    def test_fix_writes_json(self, write_json, make_edital, valid_analise, sample_empresa):
        analise = dict(valid_analise)
        analise["recomendacao_acao"] = "VERIFICAR"
        top20 = [make_edital(analise=analise, status_temporal="PLANEJAVEL")]
        data = {"top20": top20, "empresa": sample_empresa}
        path = write_json(data)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-validate.py"),
                "--input", str(path),
                "--fix",
            ],
            capture_output=True, text=True, timeout=15,
        )
        # After fix, recomendacao should be NAO PARTICIPAR
        fixed = json.loads(path.read_text(encoding="utf-8"))
        assert fixed["top20"][0]["analise"]["recomendacao_acao"] == "NAO PARTICIPAR"
