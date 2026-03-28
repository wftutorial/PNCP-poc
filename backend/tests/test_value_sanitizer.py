"""Tests for ISSUE-022 value sanitization."""
import pytest
from utils.value_sanitizer import sanitize_valor, compute_robust_total, VALUE_HARD_CAP


class TestSanitizeValor:
    def test_none_returns_zero(self):
        assert sanitize_valor(None) == 0.0

    def test_negative_returns_zero(self):
        assert sanitize_valor(-100) == 0.0

    def test_zero_returns_zero(self):
        assert sanitize_valor(0) == 0.0

    def test_normal_value(self):
        assert sanitize_valor(1_000_000) == 1_000_000.0

    def test_string_value(self):
        assert sanitize_valor("500000") == 500_000.0

    def test_exceeds_hard_cap(self):
        assert sanitize_valor(10_000_000_001) == 0.0

    def test_at_hard_cap(self):
        assert sanitize_valor(10_000_000_000) == 10_000_000_000.0

    def test_invalid_string(self):
        assert sanitize_valor("abc") == 0.0


class TestComputeRobustTotal:
    def test_empty_list(self):
        total, median, outliers, sanitized = compute_robust_total([])
        assert total == 0.0
        assert outliers == 0

    def test_normal_values(self):
        total, median, outliers, sanitized = compute_robust_total(
            [100_000, 200_000, 300_000]
        )
        assert total == 600_000
        assert outliers == 0
        assert sanitized is False

    def test_with_outlier(self):
        # 3 normal values + 1 extreme outlier
        values = [100_000, 200_000, 150_000, 180_000, 5_000_000_000]
        total, median, outliers, sanitized = compute_robust_total(values)
        assert outliers >= 1
        assert total < 5_000_000_000  # Outlier should be excluded
        assert sanitized is True

    def test_all_zeros_excluded(self):
        total, median, outliers, sanitized = compute_robust_total([0, 0, 0])
        assert total == 0.0

    def test_single_value(self):
        total, median, outliers, sanitized = compute_robust_total([500_000])
        assert total == 500_000
        assert outliers == 0

    def test_two_values(self):
        total, median, outliers, sanitized = compute_robust_total(
            [100_000, 200_000]
        )
        assert total == 300_000

    def test_metro_sp_scenario(self):
        """Real scenario: 8 normal bids + 2 Metro SP R$10B each."""
        values = [
            557_763_820,  # Franca
            40_000_000,   # Araraquara
            33_500_000,   # São Vicente
            996_595_200,  # São José do Rio Pardo
            32_000_000,   # São José do Rio Preto
            0,            # Metro (capped to 0 by sanitize_valor)
            0,            # Metro (capped to 0 by sanitize_valor)
            37_000_000,   # Santo André
            137_500_000,  # Mogi
            245_300_000,  # Mairinque
        ]
        total, median, outliers, sanitized = compute_robust_total(values)
        assert total < 10_000_000_000  # Must NOT be trillions
        assert total > 1_000_000_000   # Should be ~2B range
