"""
Tests for scripts/intel-pipeline.py — orchestrator with quality gates.

All subprocess calls are mocked. Tests cover:
- Helper functions (_slug, _clean_cnpj, _fmt_duration, _find_latest_json)
- Quality gates (gate1 through gate5)
- Step sequencing and --from-step
- CLI argument parsing
- Error propagation
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Import intel-pipeline.py via importlib (hyphen-free module name)
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util
import os

_ip_path = str(SCRIPTS_DIR / "intel-pipeline.py")
_ip_spec = importlib.util.spec_from_file_location("intel_pipeline", _ip_path)
if _ip_spec is None or _ip_spec.loader is None:
    pytest.skip(f"Cannot load {_ip_path}", allow_module_level=True)

_ip = importlib.util.module_from_spec(_ip_spec)
# Prevent Windows encoding fix from destroying pytest's capture FDs
_real_platform = sys.platform
sys.platform = "linux"
try:
    _ip_spec.loader.exec_module(_ip)
except Exception as _e:
    sys.platform = _real_platform
    pytest.skip(f"Failed to load intel-pipeline.py: {_e}", allow_module_level=True)
finally:
    sys.platform = _real_platform

# Pull out functions to test
_slug = _ip._slug
_clean_cnpj = _ip._clean_cnpj
_fmt_duration = _ip._fmt_duration
_find_latest_json = _ip._find_latest_json
_load_json = _ip._load_json
_save_json = _ip._save_json
_strip_accents = _ip._strip_accents
gate1_cobertura = _ip.gate1_cobertura
gate2_cadastral = _ip.gate2_cadastral
gate3_ruido = _ip.gate3_ruido
gate4_conteudo = _ip.gate4_conteudo
gate5_recomendacao = _ip.gate5_recomendacao
print_gate_summary = _ip.print_gate_summary


# ============================================================
# HELPER FUNCTIONS
# ============================================================

class TestHelpers:
    """Test utility functions."""

    def test_slug_basic(self):
        result = _slug("LCM Construções LTDA")
        assert result == "lcm-construcoes-ltda"

    def test_slug_special_chars(self):
        result = _slug("Empresa & Cia. [2026]")
        assert "&" not in result
        assert "[" not in result

    def test_slug_truncation(self):
        long_name = "A" * 100
        result = _slug(long_name)
        assert len(result) <= 40

    def test_clean_cnpj(self):
        assert _clean_cnpj("01.721.078/0001-68") == "01721078000168"

    def test_clean_cnpj_already_clean(self):
        assert _clean_cnpj("01721078000168") == "01721078000168"

    def test_fmt_duration_seconds(self):
        assert _fmt_duration(45.3) == "45.3s"

    def test_fmt_duration_minutes(self):
        result = _fmt_duration(125)
        assert result == "2m05s"

    def test_strip_accents(self):
        assert _strip_accents("Construção") == "Construcao"
        assert _strip_accents("São Paulo") == "Sao Paulo"


class TestFindLatestJson:
    """Test _find_latest_json file discovery."""

    def test_no_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_ip, "INTEL_DIR", tmp_path / "empty_intel")
        result = _find_latest_json("01721078000168")
        assert result is None

    def test_finds_most_recent(self, tmp_path, monkeypatch):
        intel_dir = tmp_path / "intel"
        intel_dir.mkdir()
        monkeypatch.setattr(_ip, "INTEL_DIR", intel_dir)

        f1 = intel_dir / "intel-01721078000168-old.json"
        f2 = intel_dir / "intel-01721078000168-new.json"
        f1.write_text("{}", encoding="utf-8")
        import time
        time.sleep(0.05)
        f2.write_text("{}", encoding="utf-8")

        result = _find_latest_json("01721078000168")
        assert result is not None
        assert "new" in result.name

    def test_ignores_other_cnpj(self, tmp_path, monkeypatch):
        intel_dir = tmp_path / "intel"
        intel_dir.mkdir()
        monkeypatch.setattr(_ip, "INTEL_DIR", intel_dir)

        f1 = intel_dir / "intel-99999999000199-other.json"
        f1.write_text("{}", encoding="utf-8")

        result = _find_latest_json("01721078000168")
        assert result is None


class TestLoadSaveJson:
    """Test _load_json and _save_json."""

    def test_round_trip(self, tmp_path):
        data = {"key": "value", "nested": {"n": 42}}
        path = tmp_path / "test.json"
        _save_json(path, data)
        loaded = _load_json(path)
        assert loaded == data


# ============================================================
# GATE 1: COBERTURA
# ============================================================

class TestGate1Cobertura:
    """Test gate1_cobertura validation."""

    def test_passes_with_editais(self, sample_editais_intel):
        data = {
            "editais": sample_editais_intel,
            "empresa": {"_source": {"status": "API"}, "razao_social": "TEST"},
            "estatisticas": {},
        }
        passed, issues, fixed = gate1_cobertura(data, ["SC", "PR", "RS"])
        assert passed is True

    def test_fails_with_zero_editais(self):
        data = {
            "editais": [],
            "empresa": {"_source": {"status": "API"}, "razao_social": "TEST"},
            "estatisticas": {},
        }
        passed, issues, fixed = gate1_cobertura(data, ["SC"])
        assert passed is False
        assert any("Zero editais" in i for i in issues)

    def test_fails_with_api_failed_empresa(self):
        data = {
            "editais": [{"uf": "SC", "objeto": "test"}],
            "empresa": {"_source": {"status": "API_FAILED"}},
            "estatisticas": {},
        }
        passed, issues, fixed = gate1_cobertura(data, ["SC"])
        assert passed is False

    def test_warns_on_missing_ufs(self, sample_editais_intel):
        """Request for MG but no editais from MG -> warning but still passes."""
        data = {
            "editais": sample_editais_intel,  # Only SC, PR, RS
            "empresa": {"_source": {"status": "API"}, "razao_social": "TEST"},
            "estatisticas": {},
        }
        passed, issues, fixed = gate1_cobertura(data, ["SC", "PR", "RS", "MG"])
        assert passed is True
        assert any("MG" in i for i in issues)


# ============================================================
# GATE 2: CADASTRAL
# ============================================================

class TestGate2Cadastral:
    """Test gate2_cadastral validation."""

    def test_passes_no_sanctions(self, sample_editais_intel):
        for ed in sample_editais_intel:
            ed["cnae_compatible"] = True
        data = {
            "editais": sample_editais_intel,
            "empresa": {"sancionada": False, "sicaf": {"status": "OK"}},
        }
        passed, issues, fixed = gate2_cadastral(data, 20)
        assert passed is True

    def test_marks_all_nao_recomendado_when_sanctioned(self, sample_editais_intel):
        for ed in sample_editais_intel:
            ed["cnae_compatible"] = True
        data = {
            "editais": sample_editais_intel,
            "empresa": {"sancionada": True, "sicaf": {"status": "OK"}},
        }
        passed, issues, fixed = gate2_cadastral(data, 20)
        # Sanctions don't abort, but mark override
        assert any("SANCIONADA" in i for i in issues)
        for ed in sample_editais_intel:
            assert "recomendacao_override" in ed


# ============================================================
# GATE 3: RUIDO
# ============================================================

class TestGate3Ruido:
    """Test gate3_ruido validation."""

    def test_fails_with_zero_editais(self):
        data = {"editais": []}
        passed, issues, fixed = gate3_ruido(data)
        assert passed is False

    def test_passes_with_mixed_editais(self, sample_editais_intel):
        for ed in sample_editais_intel[:3]:
            ed["cnae_compatible"] = True
            ed["needs_llm_review"] = False
        for ed in sample_editais_intel[3:]:
            ed["cnae_compatible"] = False
            ed["needs_llm_review"] = False
        data = {"editais": sample_editais_intel}
        passed, issues, fixed = gate3_ruido(data)
        assert passed is True

    def test_fails_with_pending_llm_review(self, sample_editais_intel):
        for ed in sample_editais_intel:
            ed["cnae_compatible"] = True
            ed["needs_llm_review"] = True
        data = {"editais": sample_editais_intel}
        passed, issues, fixed = gate3_ruido(data)
        assert passed is False


# ============================================================
# GATE 4: CONTEUDO
# ============================================================

class TestGate4Conteudo:
    """Test gate4_conteudo validation."""

    def test_passes_with_docs(self, sample_editais_intel):
        for ed in sample_editais_intel[:3]:
            ed["cnae_compatible"] = True
            ed["texto_documentos"] = "Edital completo com requisitos tecnicos..."
        data = {"editais": sample_editais_intel}
        passed, issues, fixed = gate4_conteudo(data, 3)
        assert passed is True

    def test_fails_no_compatible(self):
        data = {"editais": [{"cnae_compatible": False}]}
        passed, issues, fixed = gate4_conteudo(data, 20)
        assert passed is False


# ============================================================
# GATE 5: RECOMENDACAO
# ============================================================

class TestGate5Recomendacao:
    """Test gate5_recomendacao validation."""

    def test_removes_nao_participar(self, make_edital, valid_analise):
        nao_analise = dict(valid_analise)
        nao_analise["recomendacao_acao"] = "NAO PARTICIPAR"

        editais = [
            make_edital(objeto="Obra boa", analise=dict(valid_analise)),
            make_edital(objeto="Obra ruim", analise=nao_analise),
        ]
        for ed in editais:
            ed["cnae_compatible"] = True

        data = {
            "editais": editais,
            "empresa": {"capital_social": "0"},
        }
        passed, issues, fixed = gate5_recomendacao(data, 5)
        assert passed is True

    def test_removes_over_capacity(self, make_edital, valid_analise):
        editais = [
            make_edital(
                objeto="Mega obra bilionaria",
                valor_estimado=50_000_000,
                analise=dict(valid_analise),
            ),
        ]
        for ed in editais:
            ed["cnae_compatible"] = True

        data = {
            "editais": editais,
            "empresa": {"capital_social": "100000,00"},  # 100k -> cap 1M
        }
        passed, issues, fixed = gate5_recomendacao(data, 5)
        # The over-capacity edital should be removed
        assert any("capacidade" in f.lower() or "Acima" in i for f in fixed for i in issues)


# ============================================================
# GATE SUMMARY PRINTER
# ============================================================

class TestPrintGateSummary:
    """Test print_gate_summary output."""

    def test_passed_no_issues(self, capsys):
        print_gate_summary("Gate 1", True, [], [])
        captured = capsys.readouterr()
        assert "PASSED" in captured.out

    def test_passed_with_warnings(self, capsys):
        print_gate_summary("Gate 1", True, ["warn1"], ["fix1"])
        captured = capsys.readouterr()
        assert "PASSED" in captured.out
        assert "1 avisos" in captured.out

    def test_failed(self, capsys):
        print_gate_summary("Gate 1", False, ["error1", "error2"], [])
        captured = capsys.readouterr()
        assert "FAILED" in captured.out


# ============================================================
# CLI ARGUMENT PARSING
# ============================================================

class TestCliParsing:
    """Test main() argument parsing."""

    def test_invalid_cnpj_returns_1(self, monkeypatch):
        monkeypatch.setattr("sys.argv", [
            "intel-pipeline.py", "--cnpj", "123", "--ufs", "SC",
        ])
        with patch("builtins.print"):
            result = _ip.main()
        assert result == 1

    def test_empty_ufs_returns_1(self, monkeypatch):
        monkeypatch.setattr("sys.argv", [
            "intel-pipeline.py", "--cnpj", "01721078000168", "--ufs", "",
        ])
        with patch("builtins.print"):
            result = _ip.main()
        assert result == 1

    def test_from_step_without_json_returns_1(self, monkeypatch, tmp_path):
        """--from-step 2 requires existing JSON."""
        monkeypatch.setattr(_ip, "INTEL_DIR", tmp_path / "empty")
        monkeypatch.setattr("sys.argv", [
            "intel-pipeline.py",
            "--cnpj", "01721078000168",
            "--ufs", "SC",
            "--from-step", "2",
        ])
        with patch("builtins.print"):
            result = _ip.main()
        assert result == 1


# ============================================================
# STEP TIMEOUTS
# ============================================================

class TestStepTimeouts:
    """Test timeout constants are reasonable."""

    def test_collect_timeout(self):
        assert _ip.TIMEOUT_COLLECT == 600

    def test_enrich_timeout(self):
        assert _ip.TIMEOUT_ENRICH == 300

    def test_llm_gate_timeout(self):
        assert _ip.TIMEOUT_LLM_GATE == 120

    def test_extract_docs_timeout(self):
        assert _ip.TIMEOUT_EXTRACT_DOCS == 600

    def test_excel_timeout(self):
        assert _ip.TIMEOUT_EXCEL == 60
