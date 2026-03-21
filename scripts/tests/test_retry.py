"""
Tests for scripts/lib/retry.py — retry decorator with exponential backoff.
"""
from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from lib.retry import retry_on_failure


# ============================================================
# BASIC FUNCTIONALITY
# ============================================================

class TestRetryBasic:
    """Test basic retry decorator functionality."""

    def test_no_retry_on_success(self):
        """Function succeeds first try -- no retries."""
        call_count = 0

        @retry_on_failure(max_retries=3, base_delay=0.01)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count == 1

    def test_retry_on_exception_then_succeed(self):
        """Fail twice then succeed."""
        call_count = 0

        @retry_on_failure(max_retries=3, base_delay=0.01)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection refused")
            return "recovered"

        result = flaky()
        assert result == "recovered"
        assert call_count == 3

    def test_exhausted_retries_raises(self):
        """All retries exhausted -- original exception propagates."""
        @retry_on_failure(max_retries=2, base_delay=0.01)
        def always_fail():
            raise TimeoutError("timed out")

        with pytest.raises(TimeoutError, match="timed out"):
            always_fail()

    def test_non_retryable_exception_propagates_immediately(self):
        """Exceptions not in retryable_exceptions are NOT retried."""
        call_count = 0

        @retry_on_failure(
            max_retries=3,
            base_delay=0.01,
            retryable_exceptions=(ConnectionError,),
        )
        def type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("bad type")

        with pytest.raises(TypeError):
            type_error()
        assert call_count == 1  # No retry


# ============================================================
# HTTP STATUS CODE RETRIES
# ============================================================

class TestRetryStatusCodes:
    """Test retry based on HTTP status codes."""

    def test_retry_on_500(self):
        """HTTP 500 triggers retry."""
        call_count = 0

        class FakeResponse:
            def __init__(self, code):
                self.status_code = code

        @retry_on_failure(max_retries=2, base_delay=0.01)
        def server_error():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return FakeResponse(500)
            return FakeResponse(200)

        result = server_error()
        assert result.status_code == 200
        assert call_count == 3

    def test_retry_on_429_rate_limit(self):
        """HTTP 429 triggers retry."""
        call_count = 0

        class FakeResponse:
            def __init__(self, code):
                self.status_code = code

        @retry_on_failure(max_retries=1, base_delay=0.01)
        def rate_limited():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return FakeResponse(429)
            return FakeResponse(200)

        result = rate_limited()
        assert result.status_code == 200
        assert call_count == 2

    def test_no_retry_on_400(self):
        """HTTP 400 is NOT in retryable_status_codes -- no retry."""
        call_count = 0

        class FakeResponse:
            def __init__(self, code):
                self.status_code = code

        @retry_on_failure(max_retries=3, base_delay=0.01)
        def bad_request():
            nonlocal call_count
            call_count += 1
            return FakeResponse(400)

        result = bad_request()
        assert result.status_code == 400
        assert call_count == 1  # No retry

    def test_retryable_status_exhausted_returns_last_response(self):
        """When retries are exhausted with a retryable status code, returns last response."""
        class FakeResponse:
            def __init__(self, code):
                self.status_code = code

        @retry_on_failure(max_retries=1, base_delay=0.01)
        def always_503():
            return FakeResponse(503)

        result = always_503()
        assert result.status_code == 503


# ============================================================
# DELAY BEHAVIOR
# ============================================================

class TestRetryDelay:
    """Test exponential backoff and delay caps."""

    def test_exponential_backoff_timing(self):
        """Verify delays grow exponentially."""
        delays = []

        original_sleep = time.sleep

        def mock_sleep(secs):
            delays.append(secs)
            # Don't actually sleep in tests

        call_count = 0

        @retry_on_failure(max_retries=3, base_delay=1.0, max_delay=30.0)
        def fail_thrice():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise ConnectionError("fail")
            return "ok"

        with patch("lib.retry.time.sleep", side_effect=mock_sleep):
            result = fail_thrice()

        assert result == "ok"
        assert len(delays) == 3
        assert delays[0] == 1.0    # 1.0 * 2^0
        assert delays[1] == 2.0    # 1.0 * 2^1
        assert delays[2] == 4.0    # 1.0 * 2^2

    def test_max_delay_cap(self):
        """Delay never exceeds max_delay."""
        delays = []

        @retry_on_failure(max_retries=5, base_delay=10.0, max_delay=15.0)
        def always_fail():
            raise ConnectionError("fail")

        with patch("lib.retry.time.sleep", side_effect=lambda s: delays.append(s)):
            with pytest.raises(ConnectionError):
                always_fail()

        # All delays should be capped at 15.0
        for d in delays:
            assert d <= 15.0


# ============================================================
# EDGE CASES
# ============================================================

class TestRetryEdgeCases:
    """Test edge cases of the retry decorator."""

    def test_zero_retries(self):
        """max_retries=0 means no retries -- single attempt."""
        call_count = 0

        @retry_on_failure(max_retries=0, base_delay=0.01)
        def fail_once():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            fail_once()
        assert call_count == 1

    def test_preserves_function_name(self):
        """Decorated function retains original __name__."""
        @retry_on_failure()
        def my_function():
            pass

        assert my_function.__name__ == "my_function"

    def test_passes_args_and_kwargs(self):
        """Arguments are forwarded correctly on each attempt."""
        call_count = 0

        @retry_on_failure(max_retries=1, base_delay=0.01)
        def add(a, b, extra=0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("fail")
            return a + b + extra

        result = add(1, 2, extra=10)
        assert result == 13
        assert call_count == 2

    def test_result_without_status_code_returned_directly(self):
        """Non-HTTP results (no status_code attr) are returned as-is."""
        @retry_on_failure(max_retries=3, base_delay=0.01)
        def returns_dict():
            return {"data": [1, 2, 3]}

        result = returns_dict()
        assert result == {"data": [1, 2, 3]}
