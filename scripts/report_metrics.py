#!/usr/bin/env python3
"""
Metrics tracker for B2G Report pipeline.

Tracks quality metrics across report generations for trend analysis.
Writes to data/report_metrics.jsonl (append-only).

Usage:
    # Record metrics from a completed report
    python scripts/report_metrics.py record --json data.json

    # Show summary of recent reports
    python scripts/report_metrics.py summary

    # Show summary of last N reports
    python scripts/report_metrics.py summary --last 10
"""
from __future__ import annotations

import argparse
import json
import sys
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _fix_win_encoding():
    """Fix Windows console encoding — only call from __main__."""
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

METRICS_FILE = Path(__file__).resolve().parent.parent / "data" / "report_metrics.jsonl"


def _extract_numeric(
    value: Any,
    sub_keys: tuple[str, ...] = ("total", "probability", "value"),
) -> float | None:
    """Extract a numeric value from a raw field.

    If *value* is already a number, return it directly.
    If it is a dict, try each *sub_key* in order until a numeric is found.
    Otherwise return None.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for sk in sub_keys:
            v = value.get(sk)
            if isinstance(v, (int, float)):
                return float(v)
    return None


def record_metrics(data: dict) -> dict:
    """Extract metrics from a completed report JSON.

    Handles missing fields gracefully -- any field not present in *data*
    is omitted from the returned metric dict rather than raising.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---------- helpers ----------
    def _get(key: str, default: Any = None) -> Any:
        return data.get(key, default)

    def _deep_get(*keys: str, default: Any = None) -> Any:
        """Walk nested dicts: _deep_get('delivery_validation', 'gate_deterministic')."""
        obj: Any = data
        for k in keys:
            if not isinstance(obj, dict):
                return default
            obj = obj.get(k)
            if obj is None:
                return default
        return obj

    def _count_by_recomendacao(label: str) -> int | None:
        editais = _get("editais") or _get("oportunidades") or []
        if not editais:
            return None
        return sum(
            1
            for e in editais
            if (e.get("recomendacao") or "").upper() == label.upper()
        )

    def _avg_field(
        field: str,
        sub_keys: tuple[str, ...] = ("total", "probability", "value"),
    ) -> float | None:
        """Average a numeric field across editais.

        Handles both flat numeric values and dict-valued fields
        (e.g. risk_score.total, win_probability.probability).
        """
        editais = _get("editais") or _get("oportunidades") or []
        vals: list[float] = []
        for e in editais:
            raw = e.get(field)
            if raw is None:
                continue
            num = _extract_numeric(raw, sub_keys)
            if num is not None:
                vals.append(num)
        if not vals:
            return None
        return round(sum(vals) / len(vals), 2)

    # ---------- empresa info ----------
    empresa_raw = _get("empresa")
    if isinstance(empresa_raw, dict):
        cnpj = empresa_raw.get("cnpj") or _get("cnpj")
        razao = empresa_raw.get("razao_social") or empresa_raw.get("nome_fantasia")
    else:
        cnpj = _get("cnpj")
        razao = empresa_raw if isinstance(empresa_raw, str) else _get("razao_social")

    # ---------- source stats ----------
    fontes = _get("fontes") or _get("sources") or []
    sources_ok = sources_failed = sources_partial = 0
    for f in fontes:
        if not isinstance(f, dict):
            continue
        status = (f.get("status") or "").lower()
        if status in ("ok", "success", "api"):
            sources_ok += 1
        elif status in ("failed", "error"):
            sources_failed += 1
        elif status in ("partial",):
            sources_partial += 1

    # Also count _source fields scattered across top-level sections
    if not fontes:
        for section_key in ("empresa", "sicaf", "querido_diario", "portfolio",
                            "maturity_profile", "coverage_diagnostic"):
            section = _get(section_key)
            if isinstance(section, dict):
                src = section.get("_source")
                if isinstance(src, dict):
                    st = (src.get("status") or "").upper()
                    if st in ("API", "OK", "SUCCESS"):
                        sources_ok += 1
                    elif st in ("FAILED", "ERROR"):
                        sources_failed += 1
                    elif st in ("UNAVAILABLE", "PARTIAL"):
                        sources_partial += 1

    # ---------- auditor stats ----------
    auditor = _get("auditor") or _get("quality_audit") or {}
    checks = auditor.get("checks") or [] if isinstance(auditor, dict) else []
    auditor_total = len(checks) if checks else _get("auditor_checks_total")
    auditor_failed = (
        sum(1 for c in checks if not c.get("passed", True))
        if checks
        else _get("auditor_checks_failed")
    )
    auditor_rebaixamentos = (
        auditor.get("rebaixamentos") if isinstance(auditor, dict) else None
    ) or _get("auditor_rebaixamentos")

    # ---------- delivery_validation (gates) ----------
    dv = _get("delivery_validation") or {}

    det_gate = (
        _deep_get("delivery_validation", "gate_deterministic")
        or _get("gate_deterministic")
        or _get("deterministic_gate")
    )
    if isinstance(det_gate, dict):
        det_checks_failed = det_gate.get("checks_failed", 0)
        det_gate = det_gate.get("result")
    else:
        det_checks_failed = _get("deterministic_checks_failed")

    adv_gate = (
        _deep_get("delivery_validation", "gate_adversarial")
        or _get("gate_adversarial")
        or _get("adversarial_gate")
    )
    if isinstance(adv_gate, dict):
        adv_gate = adv_gate.get("result")

    # ---------- section presence ----------
    sections = _get("sections") or {}
    resumo = _get("resumo_executivo") or sections.get("resumo_executivo")
    intel = _get("inteligencia_mercado") or sections.get("inteligencia_mercado")
    passos = _get("proximos_passos") or sections.get("proximos_passos")

    # ---------- editais counts ----------
    editais_list = _get("editais") or _get("oportunidades") or []
    total_editais = len(editais_list) if editais_list else _get("total_editais")

    # ---------- keywords source ----------
    keywords_source = _get("_keywords_source") or _get("keywords_source")

    # ---------- build metric ----------
    metric: dict[str, Any] = {"timestamp": now}

    if cnpj is not None:
        metric["cnpj"] = cnpj
    if razao is not None:
        metric["empresa"] = razao
    if keywords_source is not None:
        metric["keywords_source"] = keywords_source

    if total_editais is not None:
        metric["total_editais"] = total_editais

    # Recommendation breakdown
    rec_map = {
        "dispensas": "DISPENSA",
        "participar": "PARTICIPAR",
        "avaliar": "AVALIAR",
        "nao_recomendado": "NAO RECOMENDADO",
        "vetados": "VETADO",
    }
    for mkey, label in rec_map.items():
        # Prefer explicit field in data, fall back to counting editais
        explicit = _get(mkey)
        if explicit is not None:
            metric[mkey] = explicit
        else:
            counted = _count_by_recomendacao(label)
            if counted is not None:
                metric[mkey] = counted

    # Gates
    if det_gate is not None:
        metric["gate_deterministic"] = det_gate
    if adv_gate is not None:
        metric["gate_adversarial"] = adv_gate

    # Auditor
    if auditor_total is not None:
        metric["auditor_checks_total"] = auditor_total
    if auditor_failed is not None:
        metric["auditor_checks_failed"] = auditor_failed
    if auditor_rebaixamentos is not None:
        metric["auditor_rebaixamentos"] = auditor_rebaixamentos
    if det_checks_failed is not None:
        metric["deterministic_checks_failed"] = det_checks_failed

    # Sources
    total_src = sources_ok + sources_failed + sources_partial
    if total_src > 0:
        metric["sources_ok"] = sources_ok
        metric["sources_failed"] = sources_failed
        metric["sources_partial"] = sources_partial

    # Averages from editais
    avg_risk = _avg_field("risk_score", ("total",))
    if avg_risk is not None:
        metric["avg_risk_score"] = avg_risk

    avg_win = _avg_field("win_probability", ("probability",))
    if avg_win is not None:
        metric["avg_win_probability"] = avg_win

    # Coverage percentages (may be top-level)
    for field in ("acervo_confirmado_pct", "price_benchmark_coverage_pct"):
        v = _get(field)
        if v is not None:
            metric[field] = v

    # Section presence
    metric["has_resumo_executivo"] = resumo is not None and bool(resumo)
    metric["has_inteligencia_mercado"] = intel is not None and bool(intel)
    metric["has_proximos_passos"] = passos is not None and bool(passos)

    return metric


def append_metric(metric: dict) -> None:
    """Append a single metric dict as a JSON line to the JSONL file.

    Creates the file and parent directories if they do not exist.
    """
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(metric, ensure_ascii=False) + "\n")


def load_metrics(last_n: int = 0) -> list[dict]:
    """Load metrics from the JSONL file.

    Args:
        last_n: If > 0, return only the last *last_n* entries.
                If 0, return all entries.
    """
    if not METRICS_FILE.exists():
        return []

    metrics: list[dict] = []
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                metrics.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # skip corrupt lines

    if last_n > 0:
        metrics = metrics[-last_n:]

    return metrics


def print_summary(metrics: list[dict]) -> None:
    """Pretty-print an aggregated summary of the given metrics."""
    n = len(metrics)
    if n == 0:
        print("No metrics recorded yet.")
        return

    # ---------- helpers ----------
    def _avg(key: str) -> float | None:
        vals = [m[key] for m in metrics if key in m and m[key] is not None]
        return round(sum(vals) / len(vals), 1) if vals else None

    def _sum(key: str) -> int:
        return sum(m.get(key, 0) for m in metrics)

    def _count_gate(key: str, value: str) -> int:
        return sum(1 for m in metrics if (m.get(key) or "").upper() == value.upper())

    # ---------- gate adversarial breakdown ----------
    gate_passed = _count_gate("gate_adversarial", "PASSED")
    gate_revised = _count_gate("gate_adversarial", "REVISED")
    gate_blocked = _count_gate("gate_adversarial", "BLOCKED")
    gate_line = f"{gate_passed} PASSED, {gate_revised} REVISED, {gate_blocked} BLOCKED"

    # ---------- source failure rate ----------
    total_sources = _sum("sources_ok") + _sum("sources_failed") + _sum("sources_partial")
    source_fail_rate = (
        round(_sum("sources_failed") / total_sources * 100, 1) if total_sources > 0 else 0.0
    )

    # ---------- averages ----------
    avg_editais = _avg("total_editais")
    avg_auditor_fail = _avg("auditor_checks_failed")
    avg_risk = _avg("avg_risk_score")
    avg_win = _avg("avg_win_probability")
    avg_acervo = _avg("acervo_confirmado_pct")
    avg_price = _avg("price_benchmark_coverage_pct")

    # ---------- print ----------
    header = f"B2G Report Metrics -- Last {n} report{'s' if n != 1 else ''}"
    print(header)
    print("=" * len(header))
    print(f"  Reports generated:     {n}")
    if avg_editais is not None:
        print(f"  Avg editais/report:    {avg_editais}")
    print(f"  Gate adversarial:      {gate_line}")
    if avg_auditor_fail is not None:
        print(f"  Avg auditor failures:  {avg_auditor_fail}")
    if avg_risk is not None:
        print(f"  Avg risk score:        {avg_risk}")
    if avg_win is not None:
        print(f"  Avg win probability:   {round(avg_win * 100, 1) if avg_win < 1 else avg_win}%")
    print(f"  Source failure rate:    {source_fail_rate}%")
    if avg_acervo is not None:
        print(f"  Acervo confirmed:      {avg_acervo}%")
    if avg_price is not None:
        print(f"  Price benchmark:       {avg_price}%")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="B2G Report metrics tracker (append-only JSONL)."
    )
    sub = parser.add_subparsers(dest="command")

    # record
    rec = sub.add_parser("record", help="Record metrics from a completed report JSON")
    rec.add_argument("--json", required=True, dest="json_path", help="Path to report JSON file")

    # summary
    summ = sub.add_parser("summary", help="Show summary of recorded reports")
    summ.add_argument("--last", type=int, default=0, help="Show only last N reports")

    args = parser.parse_args()

    if args.command == "record":
        json_path = Path(args.json_path)
        if not json_path.exists():
            print(f"ERROR: File not found: {json_path}", file=sys.stderr)
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        metric = record_metrics(data)
        append_metric(metric)
        print(f"Recorded metric for {metric.get('empresa', metric.get('cnpj', 'unknown'))}")
        print(f"  -> {METRICS_FILE}")

    elif args.command == "summary":
        metrics = load_metrics(last_n=args.last)
        print_summary(metrics)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    _fix_win_encoding()
    main()
