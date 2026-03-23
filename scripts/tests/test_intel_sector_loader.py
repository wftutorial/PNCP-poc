"""
Tests for scripts/intel_sector_loader.py — centralized intel sectors config loader.

Tests cover:
- Config loading and caching
- CNAE-to-sector mapping (build_cnae_to_sector_map)
- Sector hints (build_sector_hints_map)
- CNAE refinements (get_cnae_refinements, get_all_cnae_refinements)
- Incompatible objects (get_incompatible_objects, get_all_incompatible_objects)
- LLM fallback config (get_llm_fallback_config)
- Backward compatibility when config file missing
- Cache invalidation
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from intel_sector_loader import (
    load_intel_sectors_config,
    invalidate_cache,
    build_cnae_to_sector_map,
    build_sector_hints_map,
    get_cnae_refinements,
    get_incompatible_objects,
    get_all_cnae_refinements,
    get_all_incompatible_objects,
    get_llm_fallback_config,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear config cache before each test."""
    invalidate_cache()
    yield
    invalidate_cache()


class TestLoadConfig:
    def test_loads_config_successfully(self):
        config = load_intel_sectors_config()
        assert isinstance(config, dict)
        assert "sectors" in config
        assert len(config["sectors"]) >= 15

    def test_caching_returns_same_object(self):
        c1 = load_intel_sectors_config()
        c2 = load_intel_sectors_config()
        assert c1 is c2  # Same cached object

    def test_invalidate_cache(self):
        c1 = load_intel_sectors_config()
        invalidate_cache()
        c2 = load_intel_sectors_config()
        assert c1 is not c2  # Fresh load

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            load_intel_sectors_config("/nonexistent/path.yaml")


class TestBuildCnaeToSectorMap:
    def test_returns_dict(self):
        result = build_cnae_to_sector_map()
        assert isinstance(result, dict)

    def test_has_expected_mappings(self):
        result = build_cnae_to_sector_map()
        assert result["4120"] == "engenharia"
        assert result["4211"] == "engenharia_rodoviaria"
        assert result["6201"] == "software"
        assert result["8121"] == "facilities"
        assert result["4781"] == "vestuario"
        assert result["1011"] == "alimentos"

    def test_all_15_sectors_represented(self):
        result = build_cnae_to_sector_map()
        sectors = set(result.values())
        expected = {
            "engenharia", "engenharia_rodoviaria", "manutencao_predial",
            "vestuario", "alimentos", "informatica", "software",
            "facilities", "vigilancia", "saude", "transporte",
            "mobiliario", "papelaria", "materiais_eletricos", "materiais_hidraulicos",
        }
        assert sectors == expected

    def test_count_matches_original(self):
        result = build_cnae_to_sector_map()
        # Original hardcoded dict had 108 entries
        assert len(result) >= 100


class TestBuildSectorHintsMap:
    def test_returns_dict(self):
        result = build_sector_hints_map()
        assert isinstance(result, dict)

    def test_has_15_sectors(self):
        result = build_sector_hints_map()
        assert len(result) == 15

    def test_engenharia_hints(self):
        result = build_sector_hints_map()
        hints = result["engenharia"]
        assert "engenharia" in hints
        assert any("construç" in h or "construc" in h for h in hints)

    def test_software_hints(self):
        result = build_sector_hints_map()
        hints = result["software"]
        assert "software" in hints


class TestGetCnaeRefinements:
    def test_4120_has_refinements(self):
        result = get_cnae_refinements("4120")
        assert "exclude_patterns" in result
        assert "extra_include" in result
        assert "ponte" in result["exclude_patterns"]
        assert any("creche" in kw for kw in result["extra_include"])

    def test_4211_has_refinements(self):
        result = get_cnae_refinements("4211")
        assert "exclude_patterns" in result
        assert "extra_include" in result

    def test_unknown_cnae_returns_empty(self):
        result = get_cnae_refinements("9999")
        assert result == {}

    def test_all_refinements(self):
        result = get_all_cnae_refinements()
        assert "4120" in result
        assert "4211" in result
        assert "4322" in result
        assert "4330" in result
        assert "4399" in result
        assert len(result) == 5


class TestGetIncompatibleObjects:
    def test_4120_has_patterns(self):
        result = get_incompatible_objects("4120")
        assert isinstance(result, list)
        assert len(result) > 0
        # Should contain bridge, medication, etc.
        assert any("ponte" in p for p in result)
        assert any("medicamento" in p for p in result)

    def test_4211_has_patterns(self):
        result = get_incompatible_objects("4211")
        assert len(result) > 0

    def test_unknown_cnae_returns_empty(self):
        result = get_incompatible_objects("9999")
        assert result == []

    def test_all_incompatible(self):
        result = get_all_incompatible_objects()
        assert "4120" in result
        assert "4211" in result
        assert len(result) == 2


class TestGetLlmFallbackConfig:
    def test_returns_config(self):
        result = get_llm_fallback_config()
        assert isinstance(result, dict)
        assert result["enabled"] is True
        assert result["model"] == "gpt-4.1-nano"
        assert result["on_failure"] == "reject"

    def test_has_prompt_template(self):
        result = get_llm_fallback_config()
        assert "prompt_template" in result
        assert "SIM" in result["prompt_template"]
        assert "NAO" in result["prompt_template"]


class TestLlmFallbackGate:
    """Test the LLM fallback gate function in intel-collect.py."""

    @pytest.fixture
    def _load_intel_collect(self):
        """Import intel-collect.py functions."""
        import importlib.util
        ic_path = str(SCRIPTS_DIR / "intel-collect.py")
        spec = importlib.util.spec_from_file_location("intel_collect", ic_path)
        if spec is None or spec.loader is None:
            pytest.skip(f"Cannot load {ic_path}")
        mod = importlib.util.module_from_spec(spec)
        real_platform = sys.platform
        sys.platform = "linux"
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.platform = real_platform
        return mod

    def test_skips_when_not_geral(self, _load_intel_collect):
        ic = _load_intel_collect
        editais = [{"objeto": "test", "needs_llm_review": True}]
        stats = ic.apply_llm_fallback_gate(editais, "4120 - Construção", "engenharia")
        assert stats["llm_reviewed"] == 0

    def test_processes_geral_sector(self, _load_intel_collect):
        ic = _load_intel_collect
        editais = [
            {"objeto": "Construção de escola", "needs_llm_review": True, "cnae_compatible": False},
            {"objeto": "Compra de medicamentos", "needs_llm_review": True, "cnae_compatible": False},
            {"objeto": "Already classified", "needs_llm_review": False, "cnae_compatible": True},
        ]
        # Mock OpenAI to avoid real API calls
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            stats = ic.apply_llm_fallback_gate(editais, "9999 - Desconhecido", "geral")
        # Without API key, all LLM calls fail -> reject (zero noise)
        assert stats["llm_reviewed"] == 2
        assert stats["llm_failed"] == 2

    def test_llm_accept_marks_compatible(self, _load_intel_collect):
        ic = _load_intel_collect
        ed = {"objeto": "Limpeza predial", "needs_llm_review": True, "cnae_compatible": False}

        with patch.object(ic, "_llm_classify_edital_relevance", return_value=True):
            stats = ic.apply_llm_fallback_gate([ed], "8121 - Limpeza", "geral")

        assert stats["llm_accepted"] == 1
        assert ed["cnae_compatible"] is True
        assert ed["needs_llm_review"] is False
        assert ed["gate2_decision"]["reason"] == "LLM_FALLBACK_ACCEPT"

    def test_llm_reject_marks_incompatible(self, _load_intel_collect):
        ic = _load_intel_collect
        ed = {"objeto": "Medicamentos", "needs_llm_review": True, "cnae_compatible": False}

        with patch.object(ic, "_llm_classify_edital_relevance", return_value=False):
            stats = ic.apply_llm_fallback_gate([ed], "8121 - Limpeza", "geral")

        assert stats["llm_rejected"] == 1
        assert ed["cnae_compatible"] is False
        assert ed["exclusion_reason"] == "llm_fallback_reject"
