#!/usr/bin/env python3
"""Prometheus label lint — static analysis for SmartLic backend.

Scans all Python files in backend/ for Prometheus metric usage and flags
calls to .inc(), .set(), or .observe() on labeled metrics that are
missing the required .labels() call before them.

The canonical bug pattern this catches (from commit 02325b8d):

    # WRONG — raises ValueError at runtime:
    BIDS_PROCESSED_TOTAL.inc(42)

    # CORRECT:
    BIDS_PROCESSED_TOTAL.labels(source="datalake").inc(42)

Returns exit code 0 if no violations found, 1 otherwise.

Usage:
    python scripts/lint_prometheus_labels.py
    python scripts/lint_prometheus_labels.py --backend-dir backend/
    python scripts/lint_prometheus_labels.py --verbose
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Metric call methods that operate on a metric value (not the metric object).
# These must be preceded by .labels(...) if the metric has declared labelnames.
_TERMINAL_METHODS = {"inc", "dec", "set", "observe"}

# Pattern used for the quick-scan pass to find files worth AST-parsing.
_QUICK_PATTERN = re.compile(r"\.(inc|dec|set|observe)\(")


class Violation(NamedTuple):
    file: str
    line: int
    col: int
    metric_name: str
    method: str
    snippet: str


# ---------------------------------------------------------------------------
# Step 1: Parse metrics.py to learn which metrics have labels
# ---------------------------------------------------------------------------

def _extract_labeled_metrics(metrics_file: Path) -> dict[str, list[str]]:
    """Return {metric_variable_name: [label1, label2, ...]} for all metrics
    that declare at least one label in metrics.py.

    We look for patterns like:
        MY_METRIC = _create_counter("...", "...", labelnames=["a", "b"])
        MY_METRIC = _create_counter("...", "...", ["a", "b"])
    """
    try:
        source = metrics_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(metrics_file))
    except (SyntaxError, OSError) as exc:
        print(f"WARNING: Could not parse {metrics_file}: {exc}", file=sys.stderr)
        return {}

    labeled: dict[str, list[str]] = {}

    for node in ast.walk(tree):
        # Look for top-level assignments: MY_METRIC = _create_*(...)
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue

        call = node.value
        if not isinstance(call, ast.Call):
            continue

        func = call.func
        func_name = ""
        if isinstance(func, ast.Name):
            func_name = func.id
        elif isinstance(func, ast.Attribute):
            func_name = func.attr

        if not func_name.startswith("_create_"):
            continue

        metric_var = target.id
        labels = _extract_labelnames_from_call(call)
        if labels:
            labeled[metric_var] = labels

    return labeled


def _extract_labelnames_from_call(call: ast.Call) -> list[str]:
    """Extract label list from a _create_*(..., labelnames=[...]) call.

    Accepts both keyword form (labelnames=[...]) and positional form
    (third positional arg is the label list, matching _create_counter signature).
    """
    # Keyword argument: labelnames=[...]
    for kw in call.keywords:
        if kw.arg == "labelnames":
            return _ast_list_to_strings(kw.value)

    # Positional: _create_counter(name, doc, labelnames_list, ...)
    # Signatures in metrics.py all have labelnames as 3rd positional arg (index 2).
    if len(call.args) >= 3:
        return _ast_list_to_strings(call.args[2])

    return []


def _ast_list_to_strings(node: ast.expr) -> list[str]:
    """Convert an AST List/Tuple of string constants to a Python list of str."""
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    result = []
    for elt in node.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            result.append(elt.value)
    return result


# ---------------------------------------------------------------------------
# Step 2: Scan source files for bare .inc() / .set() / .observe() calls
# ---------------------------------------------------------------------------

def _scan_file(
    path: Path,
    labeled_metrics: dict[str, list[str]],
    backend_root: Path,
) -> list[Violation]:
    """Return violations found in a single Python file."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: Could not read {path}: {exc}", file=sys.stderr)
        return []

    # Quick pre-filter: skip files with no terminal method calls.
    if not _QUICK_PATTERN.search(source):
        return []

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        print(f"WARNING: Syntax error in {path}: {exc}", file=sys.stderr)
        return []

    violations: list[Violation] = []
    lines = source.splitlines()
    rel_path = str(path.relative_to(backend_root.parent))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # We need a method call: something.method(...)
        if not isinstance(node.func, ast.Attribute):
            continue

        method_name = node.func.attr
        if method_name not in _TERMINAL_METHODS:
            continue

        receiver = node.func.value

        # Case A: METRIC_NAME.inc() — direct call on a Name
        if isinstance(receiver, ast.Name):
            metric_name = receiver.id
            if metric_name in labeled_metrics:
                snippet = _safe_line(lines, node.lineno)
                violations.append(Violation(
                    file=rel_path,
                    line=node.lineno,
                    col=node.col_offset,
                    metric_name=metric_name,
                    method=method_name,
                    snippet=snippet.strip(),
                ))

        # Case B: METRIC_NAME.something.inc() (chained but labels() is not in the chain)
        # We check: if the chain starts with a known labeled metric but has no
        # .labels() call anywhere in the chain before the terminal method.
        elif isinstance(receiver, ast.Call):
            root_name, has_labels = _inspect_call_chain(receiver)
            if root_name in labeled_metrics and not has_labels:
                snippet = _safe_line(lines, node.lineno)
                violations.append(Violation(
                    file=rel_path,
                    line=node.lineno,
                    col=node.col_offset,
                    metric_name=root_name,
                    method=method_name,
                    snippet=snippet.strip(),
                ))

    return violations


def _inspect_call_chain(node: ast.expr) -> tuple[str, bool]:
    """Walk a call chain and return (root_name, has_labels_call).

    Given: METRIC.labels(x=1).inc()
    The receiver of .inc() is: METRIC.labels(x=1) — an ast.Call
    We recurse to find the root Name and whether .labels() appears.
    """
    has_labels = False
    current = node

    while True:
        if isinstance(current, ast.Call):
            if isinstance(current.func, ast.Attribute):
                if current.func.attr == "labels":
                    has_labels = True
                current = current.func.value
            else:
                # Unexpected call shape — bail out
                return ("", has_labels)
        elif isinstance(current, ast.Name):
            return (current.id, has_labels)
        elif isinstance(current, ast.Attribute):
            # e.g. metrics.METRIC_NAME (attribute access on module)
            current = current.value
        else:
            return ("", has_labels)


def _safe_line(lines: list[str], lineno: int) -> str:
    """Return the source line at lineno (1-indexed), or empty string."""
    idx = lineno - 1
    if 0 <= idx < len(lines):
        return lines[idx]
    return ""


# ---------------------------------------------------------------------------
# Step 3: Collect Python files from backend/
# ---------------------------------------------------------------------------

_SKIP_DIRS = {"__pycache__", ".venv", "venv", "migrations", "tests", "snapshots"}


def _collect_python_files(backend_dir: Path) -> list[Path]:
    """Yield all .py files under backend_dir, skipping noise directories."""
    found = []
    for root, dirs, files in os.walk(backend_dir):
        # Prune directories in-place so os.walk skips them.
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for fname in files:
            if fname.endswith(".py"):
                found.append(Path(root) / fname)
    return sorted(found)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lint Prometheus label usage in SmartLic backend Python code"
    )
    parser.add_argument(
        "--backend-dir",
        default="backend",
        help="Path to the backend directory (default: backend/)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each file being scanned",
    )
    args = parser.parse_args()

    backend_dir = Path(args.backend_dir).resolve()
    metrics_file = backend_dir / "metrics.py"

    if not backend_dir.is_dir():
        print(f"ERROR: backend directory not found: {backend_dir}", file=sys.stderr)
        sys.exit(1)

    if not metrics_file.exists():
        print(f"ERROR: metrics.py not found at: {metrics_file}", file=sys.stderr)
        sys.exit(1)

    # Step 1: learn which metrics have labels
    labeled_metrics = _extract_labeled_metrics(metrics_file)
    print(f"Found {len(labeled_metrics)} metrics with declared labels in metrics.py")
    if args.verbose:
        for name, labels in sorted(labeled_metrics.items()):
            print(f"  {name}: [{', '.join(labels)}]")

    # Step 2: scan backend files
    py_files = _collect_python_files(backend_dir)
    print(f"Scanning {len(py_files)} Python files in {backend_dir.name}/\n")

    all_violations: list[Violation] = []
    for path in py_files:
        if args.verbose:
            print(f"  Checking {path.name}...")
        violations = _scan_file(path, labeled_metrics, backend_dir)
        all_violations.extend(violations)

    # Step 3: report
    if not all_violations:
        print("No Prometheus label violations found.")
        sys.exit(0)

    print(f"Found {len(all_violations)} Prometheus label violation(s):\n")
    for v in all_violations:
        labels = labeled_metrics.get(v.metric_name, [])
        print(
            f"  {v.file}:{v.line}:{v.col} — {v.metric_name}.{v.method}() "
            f"called without .labels() (required: [{', '.join(labels)}])"
        )
        print(f"    {v.snippet}")
        print()

    print(
        "Fix: call .labels(<required_labels>).{method}() instead of .{method}() directly."
        .format(method="inc/set/observe")
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
