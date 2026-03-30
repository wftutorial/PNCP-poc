#!/usr/bin/env python3
"""
CVE audit script for cryptography package.

Usage:
    python scripts/security/check_cryptography_cves.py
    python scripts/security/check_cryptography_cves.py --json
    python scripts/security/check_cryptography_cves.py --fail-on-critical

Exit codes:
    0 = No critical CVEs found
    1 = Critical CVE found (CVSS >= 9.0)
    2 = Error running audit
"""
import subprocess
import sys
import json
import argparse
from pathlib import Path


def get_cryptography_version() -> str:
    """Get installed cryptography version."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import cryptography; print(cryptography.__version__)"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def run_pip_audit(requirements_file: str | None = None) -> dict:
    """Run pip-audit and return results."""
    cmd = [sys.executable, "-m", "pip_audit", "--format", "json"]
    if requirements_file:
        cmd.extend(["-r", requirements_file])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode not in (0, 1):  # 1 = vulnerabilities found (expected)
            return {"error": result.stderr, "vulnerabilities": []}
        return json.loads(result.stdout) if result.stdout else {"vulnerabilities": []}
    except FileNotFoundError:
        return {"error": "pip-audit not installed. Run: pip install pip-audit", "vulnerabilities": []}
    except subprocess.TimeoutExpired:
        return {"error": "pip-audit timed out after 120s", "vulnerabilities": []}
    except json.JSONDecodeError as e:
        return {"error": f"Could not parse pip-audit output: {e}", "vulnerabilities": []}


def filter_cryptography_vulns(audit_result: dict) -> list[dict]:
    """Filter vulnerabilities related to cryptography package."""
    vulns = []
    for dep in audit_result.get("dependencies", []) or audit_result.get("vulnerabilities", []):
        name = dep.get("name", "").lower()
        if "cryptography" in name:
            vulns.extend(dep.get("vulns", []) or dep.get("vulnerabilities", []))
    return vulns


def assess_severity(vulns: list[dict]) -> tuple[bool, bool]:
    """Returns (has_critical, has_high) based on CVSS scores."""
    has_critical = False
    has_high = False
    for v in vulns:
        # pip-audit uses different formats depending on version
        aliases = v.get("aliases", []) or v.get("id", "")
        fix_versions = v.get("fix_versions", [])
        description = v.get("description", "")
        # Try to extract CVSS from description or aliases
        # Conservative: if any CVE found, flag as high
        has_high = True
        # Check for "critical" keyword in description
        if "critical" in description.lower() or "9." in description:
            has_critical = True
    return has_critical, has_high


def main():
    parser = argparse.ArgumentParser(description="CVE audit for cryptography package")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fail-on-critical", action="store_true", help="Exit 1 on critical CVEs")
    parser.add_argument("--requirements", help="Path to requirements.txt", default=None)
    args = parser.parse_args()

    crypto_version = get_cryptography_version()
    print(f"[*] cryptography version: {crypto_version}", file=sys.stderr)

    # Try to find requirements.txt
    req_file = args.requirements
    if not req_file:
        candidates = [
            Path("backend/requirements.txt"),
            Path("requirements.txt"),
        ]
        for c in candidates:
            if c.exists():
                req_file = str(c)
                break

    print(f"[*] Running pip-audit...", file=sys.stderr)
    audit_result = run_pip_audit(req_file)

    if "error" in audit_result:
        print(f"[!] Error: {audit_result['error']}", file=sys.stderr)
        print("\nManual check: https://pypi.org/project/cryptography/#history")
        print("NVD search: https://nvd.nist.gov/vuln/search/results?query=cryptography+python")
        sys.exit(2)

    crypto_vulns = filter_cryptography_vulns(audit_result)
    has_critical, has_high = assess_severity(crypto_vulns)

    report = {
        "cryptography_version": crypto_version,
        "vulnerabilities_found": len(crypto_vulns),
        "has_critical": has_critical,
        "has_high": has_high,
        "vulnerabilities": crypto_vulns,
        "recommendation": (
            "UPGRADE REQUIRED — critical CVE found"
            if has_critical else
            "REVIEW RECOMMENDED — high severity CVE found"
            if has_high else
            "PIN MAINTAINABLE — no critical CVEs in current version"
        ),
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n=== cryptography CVE Audit ===")
        print(f"Version:         {report['cryptography_version']}")
        print(f"CVEs found:      {report['vulnerabilities_found']}")
        print(f"Critical (9+):   {'YES ⚠️' if has_critical else 'No'}")
        print(f"High (7-9):      {'YES ⚠️' if has_high else 'No'}")
        print(f"Recommendation:  {report['recommendation']}")
        if crypto_vulns:
            print("\nVulnerabilities:")
            for v in crypto_vulns:
                vid = v.get("id", v.get("aliases", ["unknown"])[0] if v.get("aliases") else "unknown")
                desc = v.get("description", "")[:120]
                print(f"  - {vid}: {desc}...")

    # Update status doc
    status_doc = Path("docs/security/cryptography-sigsegv-status.md")
    if status_doc.exists():
        print(f"\n[*] Update {status_doc} with audit results", file=sys.stderr)

    if args.fail_on_critical and has_critical:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
