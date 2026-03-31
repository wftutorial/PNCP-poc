#!/usr/bin/env python3
"""
Load test for cryptography package stability (DEBT-206 / CRIT-SIGSEGV).

Tests that the installed cryptography version handles repeated crypto operations
without SIGSEGV or crashes. Designed to be run before upgrading to a new
major version of cryptography.

Usage:
    python scripts/security/test_cryptography_load.py
    python scripts/security/test_cryptography_load.py --requests 100
    python scripts/security/test_cryptography_load.py --requests 200 --workers 4

Exit codes:
    0 = All requests completed without crashes
    1 = Crashes detected or test failed
    2 = Setup error
"""
import argparse
import concurrent.futures
import os
import sys
import time
from pathlib import Path


def _single_crypto_operation(request_id: int) -> dict:
    """Simulate a single crypto operation as the backend would perform."""
    try:
        import cryptography
        from cryptography.hazmat.primitives import hashes, hmac, serialization
        from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        results = []

        # 1. AES-GCM encryption (used for session tokens)
        key = os.urandom(32)
        iv = os.urandom(12)
        data = b"smartlic-test-payload-" + str(request_id).encode()
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag
        # Decrypt to verify
        decryptor = Cipher(
            algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
        ).decryptor()
        pt = decryptor.update(ct) + decryptor.finalize()
        assert pt == data, f"AES-GCM round-trip failed for request {request_id}"
        results.append("aes_gcm")

        # 2. HMAC-SHA256 (used in webhook signature verification)
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        sig = h.finalize()
        assert len(sig) == 32
        results.append("hmac_sha256")

        # 3. EC key generation (used in JWT ES256 flows)
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()
        # Sign and verify
        from cryptography.hazmat.primitives.asymmetric.utils import (
            decode_dss_signature, encode_dss_signature
        )
        signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
        public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        results.append("ec_sign_verify")

        # 4. Hash (used throughout for content hashing)
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        h = digest.finalize()
        assert len(h) == 32
        results.append("sha256_hash")

        return {
            "request_id": request_id,
            "status": "ok",
            "crypto_version": cryptography.__version__,
            "operations": results,
        }
    except Exception as e:
        return {
            "request_id": request_id,
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
        }


def run_load_test(num_requests: int, num_workers: int) -> dict:
    """Run the load test with the specified parameters."""
    print(f"[*] cryptography load test: {num_requests} requests, {num_workers} workers")

    import cryptography
    print(f"[*] cryptography version: {cryptography.__version__}")

    start = time.time()
    successes = 0
    errors = 0
    error_details = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(_single_crypto_operation, i): i
            for i in range(num_requests)
        }
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            if result["status"] == "ok":
                successes += 1
            else:
                errors += 1
                error_details.append(result)
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{num_requests} ({successes} ok, {errors} errors)")

    elapsed = time.time() - start
    return {
        "cryptography_version": cryptography.__version__,
        "num_requests": num_requests,
        "num_workers": num_workers,
        "successes": successes,
        "errors": errors,
        "elapsed_seconds": round(elapsed, 2),
        "requests_per_second": round(num_requests / elapsed, 1),
        "error_details": error_details,
        "result": "PASS" if errors == 0 else "FAIL",
    }


def main():
    parser = argparse.ArgumentParser(description="Cryptography load test for DEBT-206")
    parser.add_argument("--requests", type=int, default=100,
                        help="Number of requests to simulate (default: 100)")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of parallel workers (default: 4)")
    args = parser.parse_args()

    try:
        import cryptography
    except ImportError:
        print("[!] cryptography package not installed", file=sys.stderr)
        sys.exit(2)

    result = run_load_test(args.requests, args.workers)

    print(f"\n=== Cryptography Load Test Results ===")
    print(f"Version:       {result['cryptography_version']}")
    print(f"Requests:      {result['successes']}/{result['num_requests']} OK")
    print(f"Errors:        {result['errors']}")
    print(f"Elapsed:       {result['elapsed_seconds']}s")
    print(f"Throughput:    {result['requests_per_second']} req/s")
    print(f"Result:        {result['result']}")

    if result["errors"] > 0:
        print("\nErrors:")
        for err in result["error_details"]:
            print(f"  [{err['request_id']}] {err['error_type']}: {err['error']}")

    if result["result"] == "PASS":
        print(f"\nPASS: {args.requests} requests completed without crashes")
        sys.exit(0)
    else:
        print(f"\nFAIL: {result['errors']} errors detected")
        sys.exit(1)


if __name__ == "__main__":
    main()
