"""Tests for validate_feature_flags() — TD-BE-027 Feature Flag Startup Validation.

Validates that the startup function catches type errors, out-of-range values, and
viability weight sum errors before the app starts, raising ValueError with a clear
message instead of letting the app crash on first use.
"""

import os
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(env_overrides: dict[str, str]) -> None:
    """Run validate_feature_flags() with the given env overrides."""
    from config.features import validate_feature_flags
    with patch.dict(os.environ, env_overrides, clear=False):
        validate_feature_flags()


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.timeout(30)
def test_validate_feature_flags_defaults_pass() -> None:
    """All flags at their default values must pass validation."""
    # Remove any env vars that could have been set by other tests so we rely on
    # the hard-coded defaults inside validate_feature_flags.
    clean_env = {
        k: v for k, v in os.environ.items()
        if not any(k.startswith(prefix) for prefix in [
            "LLM_", "OPENAI_", "TERM_", "QA_", "FILTER_", "MAX_", "ZERO_",
            "PENDING_", "ITEM_", "TRIAL_", "USD_", "VIABILITY_", "USER_",
            "PROXIMITY_", "DEEP_", "LLM_",
        ])
    }
    from config.features import validate_feature_flags
    with patch.dict(os.environ, clean_env, clear=True):
        validate_feature_flags()  # Must not raise


@pytest.mark.timeout(30)
def test_validate_feature_flags_valid_overrides_pass() -> None:
    """Explicitly valid non-default values must pass."""
    _run({
        "LLM_ARBITER_TEMPERATURE": "0.7",
        "LLM_ARBITER_MAX_TOKENS": "100",
        "OPENAI_TIMEOUT_S": "10",
        "VIABILITY_WEIGHT_MODALITY": "0.40",
        "VIABILITY_WEIGHT_TIMELINE": "0.20",
        "VIABILITY_WEIGHT_VALUE_FIT": "0.20",
        "VIABILITY_WEIGHT_GEOGRAPHY": "0.20",
    })


# ---------------------------------------------------------------------------
# Type errors — non-numeric values
# ---------------------------------------------------------------------------


@pytest.mark.timeout(30)
def test_validate_rejects_temperature_non_numeric() -> None:
    """LLM_ARBITER_TEMPERATURE=abc must fail with ValueError."""
    with pytest.raises(ValueError, match="LLM_ARBITER_TEMPERATURE"):
        _run({"LLM_ARBITER_TEMPERATURE": "abc"})


@pytest.mark.timeout(30)
def test_validate_rejects_max_tokens_non_numeric() -> None:
    """LLM_ARBITER_MAX_TOKENS=xyz must fail."""
    with pytest.raises(ValueError, match="LLM_ARBITER_MAX_TOKENS"):
        _run({"LLM_ARBITER_MAX_TOKENS": "xyz"})


@pytest.mark.timeout(30)
def test_validate_rejects_timeout_non_numeric() -> None:
    """OPENAI_TIMEOUT_S=not-a-number must fail."""
    with pytest.raises(ValueError, match="OPENAI_TIMEOUT_S"):
        _run({"OPENAI_TIMEOUT_S": "not-a-number"})


@pytest.mark.timeout(30)
def test_validate_rejects_sample_rate_non_numeric() -> None:
    """QA_AUDIT_SAMPLE_RATE=ten-percent must fail."""
    with pytest.raises(ValueError, match="QA_AUDIT_SAMPLE_RATE"):
        _run({"QA_AUDIT_SAMPLE_RATE": "ten-percent"})


@pytest.mark.timeout(30)
def test_validate_rejects_trial_duration_non_numeric() -> None:
    """TRIAL_DURATION_DAYS=two-weeks must fail."""
    with pytest.raises(ValueError, match="TRIAL_DURATION_DAYS"):
        _run({"TRIAL_DURATION_DAYS": "two-weeks"})


# ---------------------------------------------------------------------------
# Range errors — values outside allowed bounds
# ---------------------------------------------------------------------------


@pytest.mark.timeout(30)
def test_validate_rejects_temperature_above_max() -> None:
    """LLM_ARBITER_TEMPERATURE=3.0 exceeds OpenAI maximum of 2.0."""
    with pytest.raises(ValueError, match="LLM_ARBITER_TEMPERATURE"):
        _run({"LLM_ARBITER_TEMPERATURE": "3.0"})


@pytest.mark.timeout(30)
def test_validate_rejects_temperature_below_min() -> None:
    """LLM_ARBITER_TEMPERATURE=-1 is below minimum 0.0."""
    with pytest.raises(ValueError, match="LLM_ARBITER_TEMPERATURE"):
        _run({"LLM_ARBITER_TEMPERATURE": "-1"})


@pytest.mark.timeout(30)
def test_validate_rejects_max_tokens_zero() -> None:
    """LLM_ARBITER_MAX_TOKENS=0 is below minimum 1."""
    with pytest.raises(ValueError, match="LLM_ARBITER_MAX_TOKENS"):
        _run({"LLM_ARBITER_MAX_TOKENS": "0"})


@pytest.mark.timeout(30)
def test_validate_rejects_sample_rate_above_one() -> None:
    """QA_AUDIT_SAMPLE_RATE=1.5 exceeds maximum of 1.0."""
    with pytest.raises(ValueError, match="QA_AUDIT_SAMPLE_RATE"):
        _run({"QA_AUDIT_SAMPLE_RATE": "1.5"})


@pytest.mark.timeout(30)
def test_validate_rejects_sample_rate_negative() -> None:
    """QA_AUDIT_SAMPLE_RATE=-0.1 is below minimum 0.0."""
    with pytest.raises(ValueError, match="QA_AUDIT_SAMPLE_RATE"):
        _run({"QA_AUDIT_SAMPLE_RATE": "-0.1"})


@pytest.mark.timeout(30)
def test_validate_rejects_trial_duration_zero() -> None:
    """TRIAL_DURATION_DAYS=0 is below minimum 1."""
    with pytest.raises(ValueError, match="TRIAL_DURATION_DAYS"):
        _run({"TRIAL_DURATION_DAYS": "0"})


@pytest.mark.timeout(30)
def test_validate_rejects_usd_rate_zero() -> None:
    """USD_TO_BRL_RATE=0 is below minimum 0.01."""
    with pytest.raises(ValueError, match="USD_TO_BRL_RATE"):
        _run({"USD_TO_BRL_RATE": "0"})


@pytest.mark.timeout(30)
def test_validate_rejects_batch_size_zero() -> None:
    """LLM_ZERO_MATCH_BATCH_SIZE=0 is below minimum 1."""
    with pytest.raises(ValueError, match="LLM_ZERO_MATCH_BATCH_SIZE"):
        _run({"LLM_ZERO_MATCH_BATCH_SIZE": "0"})


@pytest.mark.timeout(30)
def test_validate_rejects_density_threshold_above_one() -> None:
    """TERM_DENSITY_HIGH_THRESHOLD=2.0 exceeds maximum of 1.0."""
    with pytest.raises(ValueError, match="TERM_DENSITY_HIGH_THRESHOLD"):
        _run({"TERM_DENSITY_HIGH_THRESHOLD": "2.0"})


# ---------------------------------------------------------------------------
# Viability weight sum
# ---------------------------------------------------------------------------


@pytest.mark.timeout(30)
def test_validate_rejects_viability_weights_not_summing_to_one() -> None:
    """Viability weights that don't sum to 1.0 (±0.01) must fail."""
    with pytest.raises(ValueError, match="[Vv]iability weight"):
        _run({
            "VIABILITY_WEIGHT_MODALITY": "0.50",
            "VIABILITY_WEIGHT_TIMELINE": "0.25",
            "VIABILITY_WEIGHT_VALUE_FIT": "0.25",
            "VIABILITY_WEIGHT_GEOGRAPHY": "0.25",  # sum = 1.25
        })


@pytest.mark.timeout(30)
def test_validate_accepts_viability_weights_summing_to_one() -> None:
    """Viability weights that sum to exactly 1.0 must pass."""
    _run({
        "VIABILITY_WEIGHT_MODALITY": "0.40",
        "VIABILITY_WEIGHT_TIMELINE": "0.30",
        "VIABILITY_WEIGHT_VALUE_FIT": "0.20",
        "VIABILITY_WEIGHT_GEOGRAPHY": "0.10",
    })


@pytest.mark.timeout(30)
def test_validate_accepts_viability_weights_within_tolerance() -> None:
    """Viability weights summing to 0.995 (within ±0.01 tolerance) must pass."""
    _run({
        "VIABILITY_WEIGHT_MODALITY": "0.299",
        "VIABILITY_WEIGHT_TIMELINE": "0.250",
        "VIABILITY_WEIGHT_VALUE_FIT": "0.250",
        "VIABILITY_WEIGHT_GEOGRAPHY": "0.200",  # sum = 0.999
    })


# ---------------------------------------------------------------------------
# Multiple errors reported together
# ---------------------------------------------------------------------------


@pytest.mark.timeout(30)
def test_validate_accumulates_multiple_errors() -> None:
    """All invalid flags are reported at once, not just the first one."""
    with pytest.raises(ValueError) as exc_info:
        _run({
            "LLM_ARBITER_TEMPERATURE": "abc",
            "LLM_ARBITER_MAX_TOKENS": "xyz",
            "QA_AUDIT_SAMPLE_RATE": "99",
        })
    message = str(exc_info.value)
    assert "LLM_ARBITER_TEMPERATURE" in message
    assert "LLM_ARBITER_MAX_TOKENS" in message
    assert "QA_AUDIT_SAMPLE_RATE" in message
    # Error count in message
    assert "3 error" in message


# ---------------------------------------------------------------------------
# CRITICAL log on failure
# ---------------------------------------------------------------------------


@pytest.mark.timeout(30)
def test_validate_logs_critical_on_failure(caplog: pytest.LogCaptureFixture) -> None:
    """Each invalid flag triggers a CRITICAL log entry before raising."""
    import logging
    with caplog.at_level(logging.CRITICAL, logger="config"):
        with pytest.raises(ValueError):
            _run({"LLM_ARBITER_TEMPERATURE": "abc"})

    critical_records = [r for r in caplog.records if r.levelno == logging.CRITICAL]
    assert len(critical_records) >= 1
    assert any("LLM_ARBITER_TEMPERATURE" in r.message for r in critical_records)


# ---------------------------------------------------------------------------
# Startup integration: create_app() raises on bad config
# ---------------------------------------------------------------------------


@pytest.mark.timeout(30)
def test_create_app_raises_on_invalid_feature_flag() -> None:
    """create_app() must propagate ValueError from validate_feature_flags()."""
    with patch.dict(os.environ, {"LLM_ARBITER_TEMPERATURE": "abc"}):
        with pytest.raises(ValueError, match="LLM_ARBITER_TEMPERATURE"):
            # Import here to avoid side effects at module level
            from startup.app_factory import create_app
            create_app()
