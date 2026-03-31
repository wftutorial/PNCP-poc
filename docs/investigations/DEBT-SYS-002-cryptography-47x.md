# DEBT-SYS-002: Cryptography 47.x Upgrade Investigation

**Date:** 2026-03-31
**Author:** Claude (automated research)
**Status:** KEEP PIN — do not upgrade yet
**Current pin:** `cryptography>=46.0.5,<47.0.0`
**Latest stable:** 46.0.6 (released 2026-03-25)
**47.0.0 status:** Unreleased (dev1 on main branch as of 2026-03-27)

---

## Executive Summary

**Recommendation: KEEP the current `<47.0.0` pin.** Version 47.0.0 has not been released yet (still in development). The current pin `>=46.0.5,<47.0.0` already covers both CVEs disclosed in the 46.x range. The fork-safety concern with Gunicorn `--preload` is an inherent OpenSSL/C-extension issue that 47.x does NOT address — the changelog contains zero mentions of fork safety improvements.

---

## 1. Latest Stable Versions

| Version | Release Date | Notes |
|---------|-------------|-------|
| **46.0.6** | 2026-03-25 | Fix for CVE-2026-34073 (DNS name constraint bypass) |
| 46.0.5 | 2026-02-10 | Fix for CVE-2026-26007 (SECT curve subgroup attack, CVSS 8.2) |
| 46.0.4 | 2026-01-28 | Dropped win_arm64 wheels; OpenSSL 3.5.5 |
| 46.0.3 | 2025-10-15 | LibreSSL 4.2.0 compilation fix |
| 46.0.2 | 2025-10-01 | OpenSSL 3.5.4 wheels |
| 46.0.1 | 2025-09-17 | Python 3.14 install fix |
| 46.0.0 | 2025-09-16 | Major: dropped Python 3.7, OpenSSL 3.5.3, ppc64le wheels |
| **47.0.0** | **UNRELEASED** | dev1 tag on main as of 2026-03-27 |

---

## 2. CVEs in the 46.x Range

### CVE-2026-26007 — Subgroup Attack on SECT Curves (CVSS 8.2)

- **Fixed in:** 46.0.5 (2026-02-10)
- **Impact:** `public_key_from_numbers()`, `EllipticCurvePublicNumbers.public_key()`, `load_der_public_key()`, `load_pem_public_key()` did not verify that EC public key points belong to the expected prime-order subgroup. An attacker could craft a malicious public key on binary (SECT*) curves to leak private key bits via ECDH or forge ECDSA signatures.
- **Relevance to SmartLic:** LOW. SmartLic does not use SECT binary curves directly. The fix is defensive and already covered by our `>=46.0.5` floor.
- **Action:** Already mitigated by current pin.

### CVE-2026-34073 — DNS Name Constraint Bypass (Medium-Low)

- **Fixed in:** 46.0.6 (2026-03-25)
- **Impact:** Name constraints were not applied to peer names during X.509 verification when the leaf certificate contained a wildcard DNS SAN. Exploitation requires uncommon X.509 topologies that the Web PKI avoids.
- **Relevance to SmartLic:** LOW. SmartLic uses Supabase-managed TLS and does not perform custom X.509 certificate chain validation.
- **Action:** Update pin floor to `>=46.0.6` for defense-in-depth (patch-level change, no risk).

---

## 3. Fork Safety / SIGSEGV Analysis

### The Core Issue

The SIGSEGV concern with Gunicorn `--preload` is NOT a cryptography library bug. It is an inherent characteristic of how OpenSSL's C bindings interact with `fork()`:

1. **Gunicorn `--preload`** loads the application in the master process, then `fork()`s workers.
2. **OpenSSL internal state** (connection contexts, RNG state, file descriptors) is duplicated but not re-initialized in child processes.
3. When a child worker touches the inherited OpenSSL state, it can trigger a **SIGSEGV** because the C-level pointers reference parent-process memory that is no longer valid after copy-on-write.

### What OpenSSL 3.5.x Provides

- OpenSSL 3.5 (shipped in cryptography 46.0.x wheels) has fork-safe CSPRNG (since OpenSSL 1.1.1d).
- However, the RNG is only one component. SSL contexts, connection objects, and engine state are still NOT fork-safe.
- There is no `os.register_at_fork()` integration in the cryptography library to re-initialize OpenSSL state post-fork.

### What 47.0.0 (dev) Changes

Reviewing the full changelog for 47.0.0.dev1:

- **Zero mentions** of fork safety, SIGSEGV, multiprocessing, prefork, or Gunicorn.
- Major changes are API-level: dropped Python 3.8, removed SECT curves, requires OpenSSL 3.0+, added HPKE, Argon2d/2i.
- No `register_at_fork()` hooks or post-fork re-initialization added.

### Conclusion on Fork Safety

**47.x does NOT fix the fork-safety issue.** The problem is architectural (OpenSSL C state + Unix `fork()`) and would require either:
- The cryptography library to add `os.register_at_fork()` hooks (no plans visible), or
- Gunicorn to use `spawn` instead of `fork` (not supported for Uvicorn workers), or
- Application-level mitigation: avoid `--preload` (which SmartLic already does in `start.sh`).

---

## 4. Breaking Changes in 47.0.0 (Preview)

If/when 47.0.0 releases, these breaking changes will need evaluation:

| Change | Impact on SmartLic | Risk |
|--------|-------------------|------|
| Dropped Python 3.8 support | None (we use 3.12) | NONE |
| Requires OpenSSL >= 3.0.0 | Railway Docker uses 3.5.x | NONE |
| Removed SECT* binary curves | Not used | NONE |
| Dropped LibreSSL < 4.1 | Not used | NONE |
| `TypeError` instead of `ValueError` for invalid key encoding | Review any `except ValueError` around key ops | LOW |
| CFB/OFB/CFB8 moved to decrepit module | Not used directly | NONE |
| Camellia moved to decrepit module | Not used | NONE |
| MSRV Rust 1.83.0 | Only affects building from source | NONE |
| Deprecated 32-bit Windows wheels | Dev machines are 64-bit | NONE |

**Estimated migration effort:** Low (1-2 hours) once released, assuming fork-safety is handled by our existing `--preload` avoidance.

---

## 5. Recommendation

### Immediate Action (this sprint)

Update the pin floor from `>=46.0.5` to `>=46.0.6` to pick up CVE-2026-34073 fix:

```
cryptography>=46.0.6,<47.0.0       # CVE-2026-34073 fix + fork-safety pin
```

### Short-term (when 47.0.0 releases)

1. Wait 2-4 weeks after 47.0.0 GA for community feedback on regressions.
2. Test in a branch with the Gunicorn smoke test documented in requirements.txt:
   ```bash
   gunicorn main:app -k uvicorn.workers.UvicornWorker -w 2 --preload --timeout 30
   ```
3. If workers do NOT SIGSEGV, widen the pin to `<48.0.0`.
4. If workers SIGSEGV, keep `<47.0.0` and re-evaluate at 47.1.0.

### Long-term

- The fork-safety issue is mitigated by NOT using `--preload` (current `start.sh` behavior).
- Monitor pyca/cryptography for `register_at_fork()` support (no plans as of 2026-03-31).
- Re-evaluate quarterly per the existing DEBT-018 SYS-028 cadence.

---

## 6. Sources

- [PyPI cryptography](https://pypi.org/project/cryptography/) — version history
- [Cryptography Changelog](https://cryptography.io/en/latest/changelog/) — official changelog
- [GitHub CHANGELOG.rst](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst) — source changelog
- [CVE-2026-26007 Advisory](https://advisories.gitlab.com/pkg/pypi/cryptography/CVE-2026-26007/) — SECT curve subgroup attack
- [CVE-2026-26007 Analysis (SecurityOnline)](https://securityonline.info/cve-2026-26007-python-cryptography-flaw-cvss-8-2-leaks-private-keys/) — CVSS 8.2 detail
- [CVE-2026-34073 Advisory](https://advisories.gitlab.com/pkg/pypi/cryptography/CVE-2026-34073/) — DNS name constraint bypass
- [oss-security: 46.0.5 release](https://www.openwall.com/lists/oss-security/2026/02/10/4) — CVE-2026-26007 disclosure
- [OpenSSL Random fork-safety](https://wiki.openssl.org/index.php/Random_fork-safety) — OpenSSL fork-safety docs
- [Gunicorn fork SIGSEGV issue #2761](https://github.com/benoitc/gunicorn/issues/2761) — macOS fork crashes
- [pyca/cryptography SIGSEGV issue #3815](https://github.com/pyca/cryptography/issues/3815) — segfault reports
- [Snyk cryptography vulnerabilities](https://security.snyk.io/package/pip/cryptography) — vulnerability tracker
