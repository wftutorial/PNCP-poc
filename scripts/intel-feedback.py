#!/usr/bin/env python3
"""
CLI para registrar resultados de licitações (win/loss) para calibração.

Usage:
    python scripts/intel-feedback.py --cnpj 12345678000190 --edital PNCP-123 --outcome win
    python scripts/intel-feedback.py --cnpj 12345678000190 --edital PNCP-123 --outcome loss --valor-vencedor 500000
    python scripts/intel-feedback.py --report --cnpj 12345678000190
    python scripts/intel-feedback.py --list
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

# Windows console encoding fix
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "buffer") and not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer") and not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except (ValueError, AttributeError):
        pass

# Ensure scripts/ is on sys.path for lib imports
_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from lib.win_loss_tracker import calibration_report, list_outcomes, record_outcome


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Registrar resultados de licitacoes para calibracao do intel-busca.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--cnpj", help="CNPJ da empresa (14 digitos)")
    parser.add_argument("--edital", help="Identificador do edital (ex: PNCP-123)")
    parser.add_argument(
        "--outcome",
        choices=["win", "loss", "no_bid", "deserted", "cancelled"],
        help="Resultado da licitacao",
    )
    parser.add_argument("--valor-proposta", type=float, default=0, help="Valor da proposta (R$)")
    parser.add_argument("--valor-vencedor", type=float, default=0, help="Valor do lance vencedor (R$)")
    parser.add_argument("--bid-score", type=float, default=0, help="Bid score no momento da analise (0-1)")
    parser.add_argument("--victory-fit", type=float, default=0, help="Victory fit no momento da analise (0-1)")
    parser.add_argument("--notes", default="", help="Notas opcionais")
    parser.add_argument("--report", action="store_true", help="Gerar relatorio de calibracao")
    parser.add_argument("--list", action="store_true", dest="list_outcomes", help="Listar outcomes recentes")
    parser.add_argument("--limit", type=int, default=20, help="Limite de outcomes a listar (default: 20)")

    args = parser.parse_args()

    if args.report:
        report = calibration_report(args.cnpj)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if args.list_outcomes:
        outcomes = list_outcomes(args.cnpj, args.limit)
        if not outcomes:
            print("Nenhum outcome registrado.")
            return
        for o in outcomes:
            ts = o.get("timestamp", "?")[:10]
            print(
                f"  [{ts}] {o['outcome'].upper():>10} | "
                f"CNPJ={o['cnpj']} | edital={o['edital_id']} | "
                f"bid_score={o.get('bid_score_at_time', 0):.2f}"
            )
        return

    # Record mode — requires cnpj, edital, outcome
    if not args.cnpj or not args.edital or not args.outcome:
        parser.error("--cnpj, --edital, e --outcome sao obrigatorios para registrar um outcome")

    cnpj = args.cnpj.replace(".", "").replace("/", "").replace("-", "")
    entry = record_outcome(
        cnpj=cnpj,
        edital_id=args.edital,
        outcome=args.outcome,
        valor_proposta=args.valor_proposta,
        valor_vencedor=args.valor_vencedor,
        bid_score=args.bid_score,
        victory_fit=args.victory_fit,
        notes=args.notes,
    )
    print(f"Outcome registrado: {entry['outcome'].upper()} para edital {entry['edital_id']}")
    print(f"  Arquivo: {Path('data/win_loss_tracker.json').resolve()}")

    # Show calibration hint
    report = calibration_report(cnpj)
    if report.get("total", 0) >= 5:
        print(f"\n  Calibracao ({report['total']} outcomes): "
              f"win_rate={report['win_rate']:.0%}, "
              f"threshold sugerido={report['suggested_threshold']:.3f}")


if __name__ == "__main__":
    main()
