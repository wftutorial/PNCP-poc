#!/usr/bin/env python3
"""Tests for intel-llm-gate.py — keyword-based noise gate."""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "intel_llm_gate", SCRIPTS_DIR / "intel-llm-gate.py"
)
intel_llm_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intel_llm_gate)

# Aliases
NEG_KW_DEFAULT = intel_llm_gate.NEG_KW_DEFAULT
POS_KW_FALLBACK = intel_llm_gate.POS_KW_FALLBACK
_load_sectors_yaml = intel_llm_gate._load_sectors_yaml
_build_pos_kw_from_sectors = intel_llm_gate._build_pos_kw_from_sectors


# ============================================================
# KEYWORD LISTS
# ============================================================


class TestNegativeKeywords:
    def test_neg_kw_is_nonempty(self):
        assert len(NEG_KW_DEFAULT) > 30

    def test_neg_kw_all_lowercase(self):
        for kw in NEG_KW_DEFAULT:
            assert kw == kw.lower(), f"Neg keyword not lowercase: {kw}"

    def test_common_exclusions_present(self):
        all_kw = " ".join(NEG_KW_DEFAULT)
        assert "software" in all_kw
        assert "aliment" in all_kw
        assert "medicament" in all_kw
        assert "vigilancia" in all_kw
        assert "combustivel" in all_kw


class TestPositiveKeywordsFallback:
    def test_pos_kw_is_nonempty(self):
        assert len(POS_KW_FALLBACK) > 40

    def test_construction_terms_present(self):
        all_kw = " ".join(POS_KW_FALLBACK)
        assert "obra" in all_kw
        assert "paviment" in all_kw
        assert "saneamento" in all_kw
        assert "drenag" in all_kw


# ============================================================
# SECTOR KEYWORD LOADING
# ============================================================


class TestBuildPosKwFromSectors:
    def test_extracts_keywords(self):
        sectors_yaml = {
            "sectors": {
                "construcao": {
                    "keywords": ["obra", "construcao", "edificacao"],
                },
            }
        }
        kws, matched = _build_pos_kw_from_sectors(["construcao"], sectors_yaml)
        assert "obra" in kws
        assert "construcao" in kws
        assert matched == ["construcao"]

    def test_deduplicates(self):
        sectors_yaml = {
            "sectors": {
                "a": {"keywords": ["obra", "construcao"]},
                "b": {"keywords": ["obra", "drenagem"]},
            }
        }
        kws, matched = _build_pos_kw_from_sectors(["a", "b"], sectors_yaml)
        assert kws.count("obra") == 1

    def test_missing_sector_returns_empty(self):
        sectors_yaml = {"sectors": {}}
        kws, matched = _build_pos_kw_from_sectors(["nonexistent"], sectors_yaml)
        assert kws == []
        assert matched == []

    def test_empty_yaml(self):
        kws, matched = _build_pos_kw_from_sectors(["construcao"], {})
        assert kws == []

    def test_sector_without_keywords_key(self):
        sectors_yaml = {"sectors": {"construcao": {"name": "Construcao"}}}
        kws, matched = _build_pos_kw_from_sectors(["construcao"], sectors_yaml)
        assert kws == []

    def test_multiple_sectors(self):
        sectors_yaml = {
            "sectors": {
                "construcao": {"keywords": ["obra", "edificacao"]},
                "saneamento": {"keywords": ["esgoto", "drenagem"]},
            }
        }
        kws, matched = _build_pos_kw_from_sectors(
            ["construcao", "saneamento"], sectors_yaml
        )
        assert "obra" in kws
        assert "esgoto" in kws
        assert len(matched) == 2


# ============================================================
# GATE CLASSIFICATION LOGIC
# ============================================================


class TestGateLogic:
    """Test the core classification: pos+no_neg=compatible, otherwise=incompatible."""

    def _run_gate(self, editais, pos_kw=None, neg_kw=None):
        """Simulate the gate logic from main() without file I/O."""
        if pos_kw is None:
            pos_kw = POS_KW_FALLBACK
        if neg_kw is None:
            neg_kw = NEG_KW_DEFAULT

        llm_review = [e for e in editais if e.get("needs_llm_review")]
        for e in llm_review:
            obj = (e.get("objeto", "") or "").lower()
            is_neg = any(kw in obj for kw in neg_kw)
            is_pos = any(kw in obj for kw in pos_kw)
            if is_pos and not is_neg:
                e["cnae_compatible"] = True
                e["needs_llm_review"] = False
                e["llm_review_result"] = "compatible_keyword_v2"
            else:
                e["cnae_compatible"] = False
                e["needs_llm_review"] = False
                e["llm_review_result"] = "incompatible_conservative"

    def test_construction_accepted(self):
        editais = [{"objeto": "Construcao de escola municipal", "needs_llm_review": True}]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is True

    def test_software_rejected(self):
        editais = [{"objeto": "Aquisicao de software de gestao", "needs_llm_review": True}]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is False

    def test_mixed_pos_and_neg_rejected(self):
        """If object has BOTH positive and negative keywords, conservative = reject."""
        editais = [
            {"objeto": "Construcao de software hospitalar", "needs_llm_review": True}
        ]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is False

    def test_no_keywords_rejected(self):
        """Object with neither positive nor negative keywords is rejected (conservative)."""
        editais = [{"objeto": "Servicos diversos gerais", "needs_llm_review": True}]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is False

    def test_empty_objeto_rejected(self):
        editais = [{"objeto": "", "needs_llm_review": True}]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is False

    def test_none_objeto_rejected(self):
        editais = [{"objeto": None, "needs_llm_review": True}]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is False

    def test_only_non_review_editais_skipped(self):
        editais = [
            {"objeto": "Obra de pavimentacao", "needs_llm_review": False, "cnae_compatible": True},
            {"objeto": "Obra de drenagem", "needs_llm_review": True},
        ]
        self._run_gate(editais)
        # First should be untouched
        assert editais[0]["cnae_compatible"] is True
        assert editais[0]["needs_llm_review"] is False
        # Second should be classified
        assert editais[1]["cnae_compatible"] is True
        assert editais[1]["needs_llm_review"] is False

    def test_unicode_objeto(self):
        """Unicode accents: 'construção' contains 'construc' prefix? No -- 'ç' != 'c'.
        The gate operates on raw .lower() without accent stripping, so accented
        chars may not match. This is expected conservative behavior."""
        editais = [
            {"objeto": "Construção de edificação pública", "needs_llm_review": True}
        ]
        self._run_gate(editais)
        # "construção".lower() = "construção", "construc" is NOT in "construção" (ç vs c)
        # But "edificac" IS a prefix match for "edificação"
        # Actually "edificac" is in POS_KW_FALLBACK as "edificac"
        # "edificação".lower() = "edificação", and "edificac" IS in "edificação"? No -- 'ç' != 'c'
        # So this will be rejected (conservative). Test conservative behavior.
        assert editais[0]["cnae_compatible"] is False

    def test_very_short_objeto(self):
        editais = [{"objeto": "RH", "needs_llm_review": True}]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is False

    def test_pavimentacao_accepted(self):
        editais = [
            {"objeto": "Servicos de pavimentacao asfaltica no municipio", "needs_llm_review": True}
        ]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is True

    def test_alimentacao_rejected(self):
        editais = [
            {"objeto": "Fornecimento de alimentacao escolar", "needs_llm_review": True}
        ]
        self._run_gate(editais)
        assert editais[0]["cnae_compatible"] is False


# ============================================================
# CLI INTEGRATION
# ============================================================


class TestLlmGateCLI:
    def test_missing_input_exits(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "intel-llm-gate.py")],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0

    def test_nonexistent_file_exits(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-llm-gate.py"),
                "--input", str(tmp_path / "nope.json"),
            ],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0

    def test_valid_input_runs(self, write_json):
        data = {
            "busca": {"sector_keys": []},
            "editais": [
                {"objeto": "Obra de pavimentacao", "needs_llm_review": True, "uf": "SC", "valor_estimado": 100000},
                {"objeto": "Software de gestao", "needs_llm_review": True, "uf": "PR", "valor_estimado": 50000},
            ],
        }
        path = write_json(data)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "intel-llm-gate.py"),
                "--input", str(path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0
        # Verify the file was updated
        updated = json.loads(path.read_text(encoding="utf-8"))
        for e in updated["editais"]:
            assert e["needs_llm_review"] is False
