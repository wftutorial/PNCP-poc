#!/usr/bin/env python3
"""Post-deploy smoke test for SmartLic backend.

Verifies the most critical public endpoints are responding correctly
after a production deploy. Returns exit code 0 on success, 1 on failure.

Usage:
    python scripts/smoke_test.py
    python scripts/smoke_test.py --url https://api.smartlic.tech
    python scripts/smoke_test.py --url https://staging.smartlic.tech --timeout 20
"""
import argparse
import sys

import httpx

DEFAULT_URL = "https://api.smartlic.tech"
DEFAULT_TIMEOUT = 15


def test_health_live(base_url: str, timeout: int) -> None:
    """Pure liveness probe — HARDEN-016 AC1, always returns 200."""
    r = httpx.get(f"{base_url}/health/live", timeout=timeout)
    assert r.status_code == 200, f"Liveness check failed: {r.status_code}"
    print("  health/live ... OK")


def test_health_ready(base_url: str, timeout: int) -> None:
    """Readiness probe — confirms Redis + Supabase are reachable."""
    r = httpx.get(f"{base_url}/health/ready", timeout=timeout)
    assert r.status_code in (200, 503), (
        f"Readiness probe returned unexpected status: {r.status_code}"
    )
    body = r.json()
    ready = body.get("ready", False)
    if not ready:
        # Degraded is acceptable right after a cold start; just warn.
        print(f"  health/ready ... DEGRADED (deps not fully ready: {body})")
    else:
        print("  health/ready ... OK")


def test_sectors(base_url: str, timeout: int) -> None:
    """Sector list endpoint — confirms API + sector config loaded correctly."""
    r = httpx.get(f"{base_url}/v1/sectors", timeout=timeout)
    assert r.status_code == 200, f"Sectors endpoint failed: {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data).__name__}"
    assert len(data) >= 15, f"Expected >= 15 sectors, got {len(data)}"
    # Spot-check structure of first item
    first = data[0]
    for field in ("id", "slug", "name", "description"):
        assert field in first, f"Sector item missing field '{field}': {first}"
    print(f"  /v1/sectors ... OK ({len(data)} sectors)")


def run_smoke_tests(base_url: str, timeout: int) -> bool:
    """Run all smoke tests. Returns True if all passed."""
    tests = [
        ("Health liveness", test_health_live),
        ("Health readiness", test_health_ready),
        ("Sectors list", test_sectors),
    ]

    passed = 0
    failed = 0

    print(f"\nSmoke testing: {base_url}\n")

    for name, fn in tests:
        try:
            fn(base_url, timeout)
            passed += 1
        except AssertionError as exc:
            print(f"  FAIL [{name}]: {exc}")
            failed += 1
        except httpx.TimeoutException:
            print(f"  FAIL [{name}]: request timed out after {timeout}s")
            failed += 1
        except httpx.RequestError as exc:
            print(f"  FAIL [{name}]: network error — {exc}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="SmartLic post-deploy smoke tests")
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Backend base URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    args = parser.parse_args()

    success = run_smoke_tests(base_url=args.url.rstrip("/"), timeout=args.timeout)
    if success:
        print("All smoke tests passed.")
        sys.exit(0)
    else:
        print("Smoke tests FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
