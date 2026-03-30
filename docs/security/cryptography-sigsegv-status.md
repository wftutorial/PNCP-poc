# Cryptography SIGSEGV Status Report
**Data:** 2026-03-30
**Versao atual:** 46.0.5 (installed), pin allows >=46.0.5,<47.0.0
**Pin:** `cryptography>=46.0.5,<47.0.0` in `backend/requirements.txt` (DEBT-018 SYS-028)

## Situacao Atual

The cryptography package is pinned to `>=46.0.5,<47.0.0` in `backend/requirements.txt`. The pin was originally `==46.0.5` (STORY-303 AC10) but was relaxed to a range pin by DEBT-018 SYS-028 to allow patch updates while blocking major version jumps.

**Known discrepancy:** The test file `backend/tests/test_story303_crash_recovery.py` (lines 79-110) still asserts `cryptography==46.0.5` exact pin and rejects any `>=` specifier. This means the current `requirements.txt` will **fail** the STORY-303 AC10 test. This test needs to be updated to match the DEBT-018 range pin, or the requirements.txt needs to revert to exact pin.

### Usage in Codebase

The cryptography package is used in exactly one production module:
- **`backend/oauth.py`** (line 27): `from cryptography.fernet import Fernet` -- used for Google OAuth state encryption

It is also used in test files for JWT/ES256 key generation:
- `backend/tests/test_auth_es256.py` -- EC key generation for JWT tests
- `backend/tests/test_debt102_jwt_pncp_compliance.py` -- EC key generation for JWT tests

PyJWT also depends on cryptography for ES256 algorithm support (used by Supabase Auth JWKS verification).

## Historico

### Timeline of SIGSEGV incidents

1. **CRIT-SIGSEGV (original):** Gunicorn forked workers with `--preload` caused SIGSEGV. OpenSSL C bindings initialized in the master process became invalid after `fork()` in child workers. The root cause is that OpenSSL maintains internal state (locks, random number generators, engine state) that is not fork-safe.

2. **CRIT-SIGSEGV-v2:** Discovered that `uvicorn[standard]` extras pulled in `uvloop`, which reintroduced fork-unsafe behavior via `chardet`/`hiredis`/`cryptography` C extension interactions.

3. **CRIT-041:** Aggressive removal of ALL fork-unsafe C extensions from the Docker image: `grpcio`, `grpcio-status`, `opentelemetry-exporter-otlp-proto-grpc`, `opentelemetry-exporter-otlp`, `httptools`, `uvloop` are all uninstalled post pip-install in `backend/Dockerfile`.

4. **STORY-303:** Comprehensive crash recovery implementation:
   - `--preload` disabled by default in `backend/start.sh` (GUNICORN_PRELOAD=false)
   - Cryptography pinned to exact version
   - SIGSEGV detection in `backend/gunicorn_conf.py` worker_exit hook (exit code -11)
   - Sentry alerting on SIGSEGV events
   - Railway healthcheckTimeout=300s to compensate for slower non-preload startup

5. **HARDEN-002:** jemalloc disabled in Dockerfile -- `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2` is commented out because jemalloc + OpenSSL malloc hooks caused segfaults on POST body parsing via Starlette BaseHTTPMiddleware threading.

6. **Railway production config (`railway.toml`):** The startCommand bypasses `start.sh` entirely and runs `uvicorn main:app` in standalone mode (no forking at all), eliminating the fork-safety risk completely for the production deployment.

### Current Mitigations (Defense in Depth)

| Layer | Mitigation | File |
|-------|-----------|------|
| 1 | `--preload` disabled by default | `backend/start.sh` (line 43) |
| 2 | uvloop/httptools/grpcio removed from Docker image | `backend/Dockerfile` (lines 41-50) |
| 3 | jemalloc disabled | `backend/Dockerfile` (line 25-28) |
| 4 | uvicorn standalone (no fork) in Railway production | `backend/railway.toml` (line 23) |
| 5 | faulthandler disabled in production workers | `backend/gunicorn_conf.py` (line 124) |
| 6 | SIGSEGV detection + Sentry alert in worker_exit | `backend/gunicorn_conf.py` (lines 180-200) |
| 7 | WEB_CONCURRENCY warning (do not set) | `backend/railway.toml` (lines 18-22) |
| 8 | cryptography version pin <47.0 | `backend/requirements.txt` (line 56) |

## Analise de CVEs

### CVE-2026-26007 (Fixed in 46.0.5)

- **Severity:** Moderate
- **Description:** Prior to 46.0.5, functions `public_key_from_numbers`, `EllipticCurvePublicNumbers.public_key()`, `load_der_public_key()` and `load_pem_public_key()` did not verify that the point belongs to the expected prime-order subgroup of the curve. Missing validation allows an attacker to provide a public key point from a small-order subgroup, affecting ECDSA signature verification and ECDH shared key negotiation. Only SECT curves are impacted.
- **Status:** Fixed in our pinned minimum (46.0.5)
- **Source:** https://www.openwall.com/lists/oss-security/2026/02/10/4

### 46.0.6 Security Fix (Name Constraints)

- **Severity:** Low
- **Description:** Name constraints were not applied to peer names during verification when the leaf certificate contains a wildcard DNS SAN. Ordinary X.509 topologies (including Web PKI) are not affected.
- **Status:** Fixed in 46.0.6. Our pin `>=46.0.5,<47.0.0` allows this update. Recommend updating to 46.0.6.

### No Known CVEs in 46.0.5-46.0.6 Range Affecting Fork-Safety

The CVEs in this range are related to cryptographic validation logic, not to the OpenSSL C bindings fork-safety issue. The fork-safety problem is an inherent architectural limitation of OpenSSL when used across `fork()` boundaries, not a CVE.

## Teste de Compatibilidade (47.0)

### Current Status of 47.0

As of 2026-03-30, cryptography 47.0.0 has **not been released**. The documentation at cryptography.io shows `47.0.0.dev1` (development version). The latest stable release is **46.0.6**.

### What 47.0.0.dev1 Includes (from changelog)

- Updated wheels compiled with OpenSSL 3.5.3 (Windows, macOS, Linux)
- New ppc64le and win_arm64 wheels for PyPI
- Support for free-threaded Python 3.14

### Fork-Safety Assessment for 47.x

**Unknown.** The pyca/cryptography project has not announced any fork-safety improvements in the 47.x changelog. The underlying issue is architectural:

1. OpenSSL maintains global state (RAND, engine, error queues) per-process
2. `fork()` copies this state but does not re-initialize it
3. Child processes that use the stale OpenSSL state may crash

This is an **OpenSSL limitation**, not a cryptography package bug. The cryptography package is a binding layer. Unless OpenSSL itself adds fork-safety (via `OPENSSL_fork_prepare`/`OPENSSL_fork_parent`/`OPENSSL_fork_child` hooks), or the cryptography package adds explicit `os.register_at_fork()` handlers, the issue will persist.

**Note:** OpenSSL 3.x has some fork-safety improvements (`RAND_keep_random_devices_open`), but these are not comprehensive enough to guarantee safety in all use cases (particularly with engines and custom providers).

### Testing Required Before 47.x Upgrade

1. Build Docker image with `cryptography>=47.0.0,<48.0.0`
2. Run: `gunicorn main:app -k uvicorn.workers.UvicornWorker -w 2 --preload --timeout 30`
3. Send 100+ concurrent HTTPS requests (triggers OpenSSL in workers)
4. Monitor for SIGSEGV (exit code -11) in worker processes
5. If no crashes after 1000 requests with `--preload`, fork-safety is likely acceptable
6. Also test with jemalloc re-enabled (`LD_PRELOAD=libjemalloc.so.2`)

## Configuracao Gunicorn

### Current Production Config

| Setting | Value | Source |
|---------|-------|--------|
| **Runner** | `uvicorn standalone` (no fork) | `backend/railway.toml` line 23 |
| **--preload** | DISABLED (default false) | `backend/start.sh` line 43 |
| **Workers** | N/A (single process in production) | `backend/railway.toml` |
| **WEB_CONCURRENCY** | NOT SET (dangerous) | `backend/railway.toml` warning |
| **Timeout** | 120s (Railway) / 180s (Gunicorn fallback) | `backend/start.sh` line 63 |
| **Keep-alive** | 75s (> Railway proxy 60s) | `backend/start.sh` line 65 |
| **Max-requests** | 1000 + jitter 50 | `backend/start.sh` lines 67-68 |
| **Graceful timeout** | 30s | `backend/start.sh` line 55 |
| **faulthandler** | Disabled in production | `backend/gunicorn_conf.py` line 127 |

### uvloop Status

uvloop is **explicitly removed** from the Docker image in `backend/Dockerfile` (line 47). The `uvicorn` package is installed **without** `[standard]` extras to prevent uvloop from being pulled in as a transitive dependency.

### Risk Assessment

**Current production risk: MINIMAL.** Railway runs `uvicorn main:app` in standalone mode (single process, no forking). The fork-safety issue only manifests when:
1. Gunicorn prefork model is used (`-w N` with N > 0), AND
2. `--preload` is enabled, AND
3. Worker processes use cryptography/OpenSSL after fork

Since production uses none of these conditions, the SIGSEGV risk is effectively eliminated. The pin exists as a defense-in-depth measure for environments that might use Gunicorn (local development, staging, or future multi-worker configs).

## Recomendacao

**WAIT -- Do not upgrade to 47.x yet.**

### Justification

1. **47.0.0 is not released yet** (still in dev). No stable version to evaluate.
2. **Production risk is minimal** -- Railway runs uvicorn standalone (no fork), making fork-safety moot.
3. **46.0.6 is available** within current pin range and includes security fixes. Recommend updating to 46.0.6.
4. **No fork-safety improvements announced** in 47.x changelog. The OpenSSL limitation is architectural.

### Immediate Actions

1. **Update to 46.0.6** -- Within current pin range, includes name constraints security fix
2. **Fix test discrepancy** -- Update `test_story303_crash_recovery.py` AC10 test to accept range pin `>=46.0.5,<47.0.0` instead of exact `==46.0.5`, OR revert requirements.txt to exact pin `==46.0.6`
3. **No code changes needed** -- Current mitigations are comprehensive

## Plano de Upgrade (quando seguro)

### Pre-conditions

- [ ] cryptography 47.0.0 is released as stable on PyPI
- [ ] 47.0.x changelog reviewed for breaking changes
- [ ] No new CVEs reported in 47.0.0 within 30 days of release

### Steps

1. **Create feature branch:** `fix/cryptography-47-upgrade`
2. **Update pin:** `cryptography>=47.0.0,<48.0.0` in `backend/requirements.txt`
3. **Build Docker image locally:**
   ```bash
   cd backend && docker build -t smartlic-crypto-test .
   ```
4. **Fork-safety smoke test (critical):**
   ```bash
   docker run -it smartlic-crypto-test \
     gunicorn main:app -k uvicorn.workers.UvicornWorker -w 2 --preload --timeout 30
   # Send 1000+ requests with concurrent HTTPS calls
   # Monitor for exit code -11 (SIGSEGV)
   ```
5. **jemalloc compatibility test:**
   ```bash
   docker run -e LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 \
     smartlic-crypto-test gunicorn main:app -k uvicorn.workers.UvicornWorker -w 2 --timeout 30
   ```
6. **Run full test suite:** `pytest --timeout=30 -q`
7. **Update test assertions** in `test_story303_crash_recovery.py` for new version pin
8. **Deploy to staging** -- monitor for 48 hours for SIGSEGV in Sentry
9. **Deploy to production** -- monitor Railway logs for worker crashes
10. **Update this document** with test results

### Rollback Plan

1. Revert `requirements.txt` to previous pin
2. Push to main (triggers auto-deploy)
3. Railway will rebuild Docker image with old version
4. No data migration needed (cryptography is a runtime dependency only)

## Proxima Revisao

**2026-06-30** (Q3 2026) -- or sooner if:
- cryptography 47.0.0 is released
- New CVEs are reported in 46.x
- Production SIGSEGV incidents are detected via Sentry
