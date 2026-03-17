"""
Tests for the PNCP contract CNPJ client-side filtering logic
and the validate-report-data.py CONTRACT_CNPJ_MISMATCH / IMPLAUSIBLE_CONTRACT_VOLUME checks.

These tests are self-contained and do NOT import collect-report-data.py (which has
heavy dependencies). Instead, the filtering logic is replicated inline to test the
exact same algorithm.
"""
from __future__ import annotations

import sys
import os
import pytest

# ---------------------------------------------------------------------------
# 1. Replicate the client-side CNPJ filter from collect-report-data.py
# ---------------------------------------------------------------------------

def filter_contracts_by_cnpj(items: list[dict], cnpj14: str) -> list[dict]:
    """Replicate the client-side CNPJ filter from collect_pncp_contratos_fornecedor.

    Mirrors lines 816-825 of collect-report-data.py: for each contract, strip
    punctuation from niFornecedor and compare to cnpj14.  Non-matching items
    are discarded.
    """
    matched = []
    for c in items:
        ni = (c.get("niFornecedor") or "").replace(".", "").replace("/", "").replace("-", "")
        if ni != cnpj14:
            continue
        matched.append(c)
    return matched


def should_early_terminate(total_records: int) -> bool:
    """Replicate the early-termination check from collect_pncp_contratos_fornecedor.

    Mirrors lines 856-859: if the API reports >10,000 total records, the endpoint
    is clearly not filtering by supplier and we should stop paginating.
    """
    return total_records > 10_000


# ---------------------------------------------------------------------------
# 2. Import the validate function from validate-report-data.py
# ---------------------------------------------------------------------------

# The module has side effects at import time (replaces sys.stdout on Windows
# with a TextIOWrapper, which closes pytest's capture file descriptors).
# We use importlib.util to load the module with the side-effect lines
# neutralised by temporarily making sys.platform report non-win32.
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import importlib.util
import types

_validate_path = os.path.join(SCRIPTS_DIR, "validate-report-data.py")
_spec = importlib.util.spec_from_file_location("validate_report_data", _validate_path)
_validate_mod = importlib.util.module_from_spec(_spec)

# Temporarily pretend we are not on Windows so the module-level
# sys.stdout/stderr wrapping is skipped during exec_module.
_real_platform = sys.platform
sys.platform = "linux"
try:
    _spec.loader.exec_module(_validate_mod)
finally:
    sys.platform = _real_platform

validate = _validate_mod.validate


# ===========================================================================
# Test Suite A: Client-side CNPJ Filter
# ===========================================================================

class TestCnpjFilter:
    """Tests for the client-side niFornecedor filter."""

    TARGET_CNPJ = "18742098000118"

    def test_matching_contracts_pass_through(self):
        """Contracts whose niFornecedor matches the target CNPJ are kept."""
        items = [
            {"niFornecedor": "18742098000118", "objetoContrato": "Serviço A"},
            {"niFornecedor": "18742098000118", "objetoContrato": "Serviço B"},
        ]
        result = filter_contracts_by_cnpj(items, self.TARGET_CNPJ)
        assert len(result) == 2

    def test_non_matching_contracts_are_discarded(self):
        """Contracts from other CNPJs are filtered out."""
        items = [
            {"niFornecedor": "99999999000199", "objetoContrato": "Other company"},
            {"niFornecedor": "11111111000111", "objetoContrato": "Another company"},
        ]
        result = filter_contracts_by_cnpj(items, self.TARGET_CNPJ)
        assert len(result) == 0

    def test_mixed_matching_and_non_matching(self):
        """Only matching contracts survive filtering."""
        items = [
            {"niFornecedor": "18742098000118", "objetoContrato": "Match 1"},
            {"niFornecedor": "99999999000199", "objetoContrato": "Foreign"},
            {"niFornecedor": "18742098000118", "objetoContrato": "Match 2"},
            {"niFornecedor": "00000000000000", "objetoContrato": "Foreign 2"},
        ]
        result = filter_contracts_by_cnpj(items, self.TARGET_CNPJ)
        assert len(result) == 2
        assert result[0]["objetoContrato"] == "Match 1"
        assert result[1]["objetoContrato"] == "Match 2"

    def test_formatted_cnpj_with_punctuation(self):
        """niFornecedor with dots/slashes/dashes is normalised before comparison."""
        items = [
            {"niFornecedor": "18.742.098/0001-18", "objetoContrato": "Formatted"},
        ]
        result = filter_contracts_by_cnpj(items, self.TARGET_CNPJ)
        assert len(result) == 1

    def test_empty_ni_fornecedor_is_discarded(self):
        """Contracts with empty or missing niFornecedor are filtered out."""
        items = [
            {"niFornecedor": "", "objetoContrato": "Empty NI"},
            {"objetoContrato": "Missing NI field"},
            {"niFornecedor": None, "objetoContrato": "None NI"},
        ]
        result = filter_contracts_by_cnpj(items, self.TARGET_CNPJ)
        assert len(result) == 0

    def test_empty_response(self):
        """Empty list in, empty list out."""
        result = filter_contracts_by_cnpj([], self.TARGET_CNPJ)
        assert result == []

    def test_all_contracts_match(self):
        """When every contract belongs to the target, all pass through."""
        items = [{"niFornecedor": self.TARGET_CNPJ} for _ in range(100)]
        result = filter_contracts_by_cnpj(items, self.TARGET_CNPJ)
        assert len(result) == 100

    def test_single_contract_match(self):
        """Single matching contract in a sea of foreign ones."""
        items = [{"niFornecedor": f"0000000000{i:04d}"} for i in range(50)]
        items[25] = {"niFornecedor": self.TARGET_CNPJ}
        result = filter_contracts_by_cnpj(items, self.TARGET_CNPJ)
        assert len(result) == 1


# ===========================================================================
# Test Suite B: Early Termination
# ===========================================================================

class TestEarlyTermination:
    """Tests for the >10,000 total records early-termination logic."""

    def test_normal_count_does_not_terminate(self):
        """Counts within normal range do not trigger termination."""
        assert should_early_terminate(0) is False
        assert should_early_terminate(50) is False
        assert should_early_terminate(500) is False
        assert should_early_terminate(9999) is False
        assert should_early_terminate(10_000) is False

    def test_excessive_count_triggers_termination(self):
        """Counts above 10,000 trigger early termination."""
        assert should_early_terminate(10_001) is True
        assert should_early_terminate(100_000) is True
        assert should_early_terminate(2_100_000) is True

    def test_boundary_value(self):
        """Exactly 10,000 does not terminate; 10,001 does."""
        assert should_early_terminate(10_000) is False
        assert should_early_terminate(10_001) is True


# ===========================================================================
# Test Suite C: CONTRACT_CNPJ_MISMATCH Block (validate-report-data.py)
# ===========================================================================

class TestContractCnpjMismatchBlock:
    """Tests for the CONTRACT_CNPJ_MISMATCH block in validate()."""

    CNPJ = "18742098000118"

    def _make_data(self, contracts: list[dict], cnpj: str = CNPJ) -> dict:
        return {
            "empresa": {
                "cnpj": cnpj,
                "historico_contratos": contracts,
            },
            "editais": [],
            "_metadata": {"sources": {"opencnpj": {"status": "API"}, "pncp": {"status": "API"}}},
            "_keywords_source": "clustering",
        }

    def test_all_contracts_match_no_block(self):
        """No block when all contracts belong to the same CNPJ."""
        contracts = [{"cnpj_fornecedor": self.CNPJ} for _ in range(30)]
        result = validate(self._make_data(contracts))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 0

    def test_high_mismatch_triggers_block(self):
        """Block when >20% of contracts have a foreign CNPJ."""
        # 8 foreign + 2 matching = 80% mismatch (well above 20% threshold)
        contracts = (
            [{"cnpj_fornecedor": "99999999000199"} for _ in range(8)]
            + [{"cnpj_fornecedor": self.CNPJ} for _ in range(2)]
        )
        result = validate(self._make_data(contracts))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 1
        assert result["verdict"] == "BLOCKED"

    def test_low_mismatch_triggers_warning_not_block(self):
        """Warning (not block) when <=20% of contracts have a foreign CNPJ."""
        # 1 foreign + 9 matching = 10% mismatch (<=20%)
        contracts = (
            [{"cnpj_fornecedor": "99999999000199"}]
            + [{"cnpj_fornecedor": self.CNPJ} for _ in range(9)]
        )
        result = validate(self._make_data(contracts))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 0
        minor_warnings = [w for w in result["warnings"] if "CONTRACT_CNPJ_MINOR" in w]
        assert len(minor_warnings) == 1

    def test_exactly_20_pct_mismatch_is_not_blocked(self):
        """Boundary: exactly 20% foreign is NOT blocked (threshold is >20%)."""
        # 2 foreign + 8 matching out of 10 checked = 20% exactly
        contracts = (
            [{"cnpj_fornecedor": "99999999000199"} for _ in range(2)]
            + [{"cnpj_fornecedor": self.CNPJ} for _ in range(8)]
        )
        result = validate(self._make_data(contracts))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 0

    def test_21_pct_mismatch_is_blocked(self):
        """Just above 20% foreign triggers the block."""
        # Need foreign/checked > 0.2.  With checked=50 (max sample), need >10 foreign.
        # 11 foreign + 39 matching = 22% > 20%
        contracts = (
            [{"cnpj_fornecedor": "99999999000199"} for _ in range(11)]
            + [{"cnpj_fornecedor": self.CNPJ} for _ in range(39)]
        )
        result = validate(self._make_data(contracts))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 1

    def test_empty_cnpj_fornecedor_not_counted(self):
        """Contracts with empty cnpj_fornecedor are not counted in the check."""
        contracts = (
            [{"cnpj_fornecedor": ""} for _ in range(20)]
            + [{"cnpj_fornecedor": self.CNPJ} for _ in range(5)]
        )
        result = validate(self._make_data(contracts))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 0

    def test_no_contracts_no_check(self):
        """No contracts means no CNPJ mismatch check."""
        result = validate(self._make_data([]))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 0

    def test_no_empresa_cnpj_no_check(self):
        """Missing empresa CNPJ skips the check."""
        data = self._make_data([{"cnpj_fornecedor": "99999999000199"}], cnpj="")
        result = validate(data)
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 0

    def test_sample_capped_at_50(self):
        """Validator only samples the first 50 contracts."""
        # 60 contracts: first 50 all match, last 10 don't.
        # Since validator checks [:50], it should not see any foreign.
        contracts = (
            [{"cnpj_fornecedor": self.CNPJ} for _ in range(50)]
            + [{"cnpj_fornecedor": "99999999000199"} for _ in range(10)]
        )
        result = validate(self._make_data(contracts))
        mismatch_blocks = [b for b in result["blocks"] if "CONTRACT_CNPJ_MISMATCH" in b]
        assert len(mismatch_blocks) == 0


# ===========================================================================
# Test Suite D: IMPLAUSIBLE_CONTRACT_VOLUME Warning (validate-report-data.py)
# ===========================================================================

class TestImplausibleContractVolume:
    """Tests for the IMPLAUSIBLE_CONTRACT_VOLUME warning in validate()."""

    CNPJ = "18742098000118"

    def _make_data(self, n_contracts: int, capital: float) -> dict:
        contracts = [{"cnpj_fornecedor": self.CNPJ} for _ in range(n_contracts)]
        return {
            "empresa": {
                "cnpj": self.CNPJ,
                "capital_social": capital,
                "historico_contratos": contracts,
            },
            "editais": [],
            "_metadata": {"sources": {"opencnpj": {"status": "API"}, "pncp": {"status": "API"}}},
            "_keywords_source": "clustering",
        }

    def test_high_volume_low_capital_triggers_warning(self):
        """501 contracts with capital <=R$100k triggers the warning."""
        result = validate(self._make_data(501, 50_000))
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 1

    def test_high_volume_high_capital_no_warning(self):
        """501 contracts with capital >R$100k does NOT trigger the warning."""
        result = validate(self._make_data(501, 200_000))
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 0

    def test_low_volume_low_capital_no_warning(self):
        """500 contracts (boundary) with low capital does NOT trigger the warning."""
        result = validate(self._make_data(500, 50_000))
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 0

    def test_exactly_500_no_warning(self):
        """Boundary: exactly 500 contracts does not trigger (threshold is >500)."""
        result = validate(self._make_data(500, 10_000))
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 0

    def test_exactly_100k_capital_triggers_warning(self):
        """Capital of exactly R$100,000 triggers (threshold is <=100,000)."""
        result = validate(self._make_data(501, 100_000))
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 1

    def test_zero_capital_triggers_warning(self):
        """Zero capital with high volume triggers the warning."""
        result = validate(self._make_data(600, 0))
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 1

    def test_none_capital_triggers_warning(self):
        """None capital (treated as 0) with high volume triggers the warning."""
        data = self._make_data(600, 0)
        data["empresa"]["capital_social"] = None
        result = validate(data)
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 1

    def test_no_contracts_no_warning(self):
        """Zero contracts never triggers the warning."""
        result = validate(self._make_data(0, 1_000))
        impl_warnings = [w for w in result["warnings"] if "IMPLAUSIBLE_CONTRACT_VOLUME" in w]
        assert len(impl_warnings) == 0
