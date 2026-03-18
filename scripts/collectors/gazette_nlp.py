#!/usr/bin/env python3
"""
NLP analyzer for Brazilian Diario Oficial (gazette) content.

Extracts structured procurement events from gazette text returned
by the Querido Diario API. Detects:
  - Suspensions of active procurement processes
  - Results/awards of recent bidding processes
  - Price registration (atas de registro de preco)
  - Extensions/amendments to existing contracts
  - Cancellations and deserted/failed processes
  - Reopenings and reschedulings
  - Organ behavioral patterns (frequent cancellations, delays)

Uses rule-based NLP (regex + keyword patterns) -- no LLM required.
Designed for Portuguese legal/bureaucratic text.

Usage:
    from collectors.gazette_nlp import GazetteAnalyzer

    analyzer = GazetteAnalyzer()
    events = analyzer.extract_events(gazette_text, context={"orgao": "Prefeitura de X"})
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import io
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional

def _fix_win_encoding():
    """Fix Windows console encoding — only call from __main__."""
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Shared regex patterns
# ---------------------------------------------------------------------------

_PROCESSO_PATTERN = re.compile(
    r"(?:"
    r"(?:Preg[aã]o(?:\s+(?:Eletr[oô]nico|Presencial))?\s+n[.ºo°]*\s*)"
    r"|(?:PE\s+n[.ºo°]*\s*)"
    r"|(?:Concorr[eê]ncia\s+n[.ºo°]*\s*)"
    r"|(?:Tomada\s+de\s+Pre[cç]os?\s+n[.ºo°]*\s*)"
    r"|(?:Dispensa\s+(?:de\s+Licita[cç][aã]o\s+)?n[.ºo°]*\s*)"
    r"|(?:Inexigibilidade\s+n[.ºo°]*\s*)"
    r"|(?:Licita[cç][aã]o\s+n[.ºo°]*\s*)"
    r"|(?:Processo(?:\s+(?:Licitat[oó]rio|Administrativo))?\s+n[.ºo°]*\s*)"
    r"|(?:Chamada\s+P[uú]blica\s+n[.ºo°]*\s*)"
    r")"
    r"(\d{1,5}\s*/\s*\d{4})",
    re.IGNORECASE,
)

_VALOR_PATTERN = re.compile(
    r"R\$\s*"
    r"(\d{1,3}(?:\.\d{3})*,\d{2}"  # R$ 1.234.567,89
    r"|\d+(?:\.\d+)?(?:,\d{1,2})?)",  # R$ 1234567.89 or R$1234
    re.IGNORECASE,
)

_DATE_PATTERN = re.compile(
    r"(\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{4})"  # DD/MM/YYYY
    r"|(\d{1,2}\s+de\s+"
    r"(?:janeiro|fevereiro|mar[cç]o|abril|maio|junho"
    r"|julho|agosto|setembro|outubro|novembro|dezembro)"
    r"\s+de\s+\d{4})",
    re.IGNORECASE,
)

_CNPJ_PATTERN = re.compile(
    r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
)

# Month name to number mapping for date parsing
_MONTH_MAP = {
    "janeiro": "01", "fevereiro": "02", "marco": "03", "março": "03",
    "abril": "04", "maio": "05", "junho": "06",
    "julho": "07", "agosto": "08", "setembro": "09",
    "outubro": "10", "novembro": "11", "dezembro": "12",
}


# ---------------------------------------------------------------------------
# GazetteEvent dataclass
# ---------------------------------------------------------------------------

@dataclass
class GazetteEvent:
    """A structured event extracted from gazette text.

    Attributes:
        event_type: One of SUSPENSION, AWARD, PRICE_REGISTER, AMENDMENT,
                    CANCELLATION, EXTENSION, REOPENING.
        confidence: Score from 0.0 to 1.0 indicating extraction confidence.
        description: Human-readable summary of the event.
        orgao: Organ name if known (from context or text).
        processo: Process number if extracted (e.g. "123/2026").
        valor: Monetary value if mentioned.
        date_ref: Date reference if found (DD/MM/YYYY).
        raw_excerpt: The matched text excerpt.
    """

    event_type: str
    confidence: float
    description: str
    orgao: str | None = None
    processo: str | None = None
    valor: float | None = None
    date_ref: str | None = None
    raw_excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict, dropping None values."""
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None and v != ""}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _parse_brl_value(raw: str) -> float | None:
    """Parse a BRL value string to float.

    Handles:
        '1.234.567,89' -> 1234567.89
        '1234567.89'   -> 1234567.89
        '1234'         -> 1234.0
    """
    try:
        cleaned = raw.strip()
        if "," in cleaned:
            # Brazilian format: 1.234,56
            cleaned = cleaned.replace(".", "").replace(",", ".")
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def _extract_first_value(text: str) -> float | None:
    """Extract the first BRL monetary value from text."""
    m = _VALOR_PATTERN.search(text)
    if m:
        return _parse_brl_value(m.group(1))
    return None


def _extract_first_processo(text: str) -> str | None:
    """Extract the first process number from text."""
    m = _PROCESSO_PATTERN.search(text)
    if m:
        return m.group(1).replace(" ", "")
    return None


def _extract_first_date(text: str) -> str | None:
    """Extract the first date reference from text, normalized to DD/MM/YYYY."""
    m = _DATE_PATTERN.search(text)
    if not m:
        return None
    if m.group(1):
        # DD/MM/YYYY format — normalize spacing
        return m.group(1).replace(" ", "")
    if m.group(2):
        # "DD de MONTH de YYYY" format
        parts = m.group(2).lower().split()
        day = parts[0].zfill(2)
        month_name = parts[2]
        year = parts[4]
        month_num = _MONTH_MAP.get(month_name)
        if month_num:
            return f"{day}/{month_num}/{year}"
    return None


def _get_excerpt(text: str, match: re.Match, window: int = 200) -> str:
    """Return a text window around a regex match for context."""
    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    excerpt = text[start:end].strip()
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt + "..."
    return excerpt


# ---------------------------------------------------------------------------
# GazetteAnalyzer
# ---------------------------------------------------------------------------

class GazetteAnalyzer:
    """Rule-based NLP analyzer for gazette (Diario Oficial) text.

    Extracts structured procurement events using regex + keyword patterns.
    All patterns use ``re.IGNORECASE`` and handle accented/non-accented
    variants of Portuguese legal terms.
    """

    # --- Suspension patterns ---
    _SUSPENSION_PATTERNS = [
        (re.compile(r"SUSPENS[AÃ]O", re.IGNORECASE), 0.9),
        (re.compile(r"FICA\s+SUSPENS[OA]", re.IGNORECASE), 0.9),
        (re.compile(r"SUSPENDER\s+O\s+CERTAME", re.IGNORECASE), 0.9),
        (re.compile(r"SUSPENDER\s+A\s+LICITA[CÇ][AÃ]O", re.IGNORECASE), 0.9),
        (re.compile(r"SUSPENS[AÃ]O\s+TEMPOR[AÁ]RIA", re.IGNORECASE), 0.9),
        (re.compile(r"SUSPENS[OA]\s+(?:O|A)\s+(?:PREG[AÃ]O|PROCESSO)", re.IGNORECASE), 0.9),
        (re.compile(r"FICA\s+SUSPENSO\s+O\s+PRAZO", re.IGNORECASE), 0.6),
    ]

    # --- Award patterns ---
    _AWARD_PATTERNS = [
        (re.compile(r"ADJUDICA[CÇ][AÃ]O", re.IGNORECASE), 0.9),
        (re.compile(r"HOMOLOGA[CÇ][AÃ]O", re.IGNORECASE), 0.9),
        (re.compile(r"RESULTADO\s+(?:DE\s+)?(?:LICITA[CÇ][AÃ]O|PREG[AÃ]O|JULGAMENTO)", re.IGNORECASE), 0.9),
        (re.compile(r"VENCEDORA?\b", re.IGNORECASE), 0.6),
        (re.compile(r"EMPRESA\s+VENCEDORA", re.IGNORECASE), 0.9),
        (re.compile(r"ADJUDICAD[OA]\s+(?:AO?|PARA)", re.IGNORECASE), 0.9),
        (re.compile(r"HOMOLOG(?:O|OU|AR)\s+O\s+RESULTADO", re.IGNORECASE), 0.9),
    ]

    # --- Cancellation patterns ---
    _CANCELLATION_PATTERNS = [
        (re.compile(r"REVOGA[CÇ][AÃ]O", re.IGNORECASE), 0.9),
        (re.compile(r"ANULA[CÇ][AÃ]O", re.IGNORECASE), 0.9),
        (re.compile(r"CANCELAMENTO", re.IGNORECASE), 0.9),
        (re.compile(r"DECLARAD[OA]\s+DESERT[OA]", re.IGNORECASE), 0.9),
        (re.compile(r"DECLARAD[OA]\s+FRACASSAD[OA]", re.IGNORECASE), 0.9),
        (re.compile(r"REVOGAR\s+(?:A|O)\s+(?:LICITA[CÇ][AÃ]O|PREG[AÃ]O|PROCESSO)", re.IGNORECASE), 0.9),
        (re.compile(r"ANULAR\s+(?:A|O)\s+(?:LICITA[CÇ][AÃ]O|PREG[AÃ]O|PROCESSO)", re.IGNORECASE), 0.9),
        (re.compile(r"TORNA(?:R)?\s+SEM\s+EFEITO", re.IGNORECASE), 0.6),
    ]

    # --- Price register patterns ---
    _PRICE_REGISTER_PATTERNS = [
        (re.compile(r"ATA\s+DE\s+REGISTRO\s+DE\s+PRE[CÇ]O", re.IGNORECASE), 0.9),
        (re.compile(r"\bSRP\b", re.IGNORECASE), 0.6),
        (re.compile(r"SISTEMA\s+DE\s+REGISTRO\s+DE\s+PRE[CÇ]O", re.IGNORECASE), 0.9),
        (re.compile(r"REGISTRO\s+DE\s+PRE[CÇ]OS?\s+N[.ºo°]*", re.IGNORECASE), 0.9),
        (re.compile(r"EXTRATO\s+(?:DA\s+)?ATA\s+DE\s+REGISTRO", re.IGNORECASE), 0.9),
    ]

    # --- Amendment patterns ---
    _AMENDMENT_PATTERNS = [
        (re.compile(r"TERMO\s+ADITIVO", re.IGNORECASE), 0.9),
        (re.compile(r"\bADITIVO\b", re.IGNORECASE), 0.6),
        (re.compile(r"APOSTILAMENTO", re.IGNORECASE), 0.9),
        (re.compile(r"PRORROGA[CÇ][AÃ]O", re.IGNORECASE), 0.9),
        (re.compile(r"ADITAMENTO", re.IGNORECASE), 0.9),
        (re.compile(r"ACR[EÉ]SCIMO\s+DE\s+\d+", re.IGNORECASE), 0.9),
        (re.compile(r"SUPRESS[AÃ]O\s+DE\s+\d+", re.IGNORECASE), 0.9),
    ]

    # --- Reopening patterns ---
    _REOPENING_PATTERNS = [
        (re.compile(r"REABERTURA", re.IGNORECASE), 0.9),
        (re.compile(r"NOVA\s+DATA", re.IGNORECASE), 0.6),
        (re.compile(r"REAGENDAMENTO", re.IGNORECASE), 0.9),
        (re.compile(r"RETIFICA[CÇ][AÃ]O\s+(?:DE\s+)?(?:DATA|PRAZO|EDITAL)", re.IGNORECASE), 0.9),
        (re.compile(r"FICA\s+(?:ALTERADA?|PRORROGADA?)\s+A\s+DATA", re.IGNORECASE), 0.9),
        (re.compile(r"NOVA\s+SESS[AÃ]O", re.IGNORECASE), 0.6),
    ]

    def __init__(self) -> None:
        """Initialize the analyzer. No external dependencies needed."""
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_events(
        self,
        text: str,
        context: dict[str, Any] | None = None,
    ) -> list[GazetteEvent]:
        """Extract all structured events from gazette text.

        Args:
            text: Raw gazette text (Portuguese, possibly all-caps).
            context: Optional context dict. Recognized keys:
                - ``orgao``: Organ name to attach to events.
                - ``cnpj_orgao``: Organ CNPJ for filtering.

        Returns:
            List of ``GazetteEvent`` objects sorted by confidence descending.
        """
        if not text or not text.strip():
            return []

        orgao = (context or {}).get("orgao")

        all_events: list[GazetteEvent] = []
        all_events.extend(self._extract_suspensions(text))
        all_events.extend(self._extract_awards(text))
        all_events.extend(self._extract_cancellations(text))
        all_events.extend(self._extract_price_registers(text))
        all_events.extend(self._extract_amendments(text))
        all_events.extend(self._extract_reopenings(text))

        # Attach orgao from context if not already set
        if orgao:
            for ev in all_events:
                if not ev.orgao:
                    ev.orgao = orgao

        # Deduplicate: if same event_type + processo, keep highest confidence
        all_events = self._deduplicate(all_events)

        # Sort by confidence descending
        all_events.sort(key=lambda e: e.confidence, reverse=True)
        return all_events

    # ------------------------------------------------------------------
    # Private extractors
    # ------------------------------------------------------------------

    def _extract_suspensions(self, text: str) -> list[GazetteEvent]:
        """Extract suspension events from text."""
        return self._run_patterns(
            text,
            self._SUSPENSION_PATTERNS,
            event_type="SUSPENSION",
            description_tpl="Suspensao de processo licitatorio",
        )

    def _extract_awards(self, text: str) -> list[GazetteEvent]:
        """Extract award/result events from text."""
        return self._run_patterns(
            text,
            self._AWARD_PATTERNS,
            event_type="AWARD",
            description_tpl="Resultado/adjudicacao de licitacao",
        )

    def _extract_cancellations(self, text: str) -> list[GazetteEvent]:
        """Extract cancellation events from text."""
        events = self._run_patterns(
            text,
            self._CANCELLATION_PATTERNS,
            event_type="CANCELLATION",
            description_tpl="Cancelamento/revogacao/anulacao de licitacao",
        )
        # Refine description for deserted/failed
        for ev in events:
            excerpt_upper = ev.raw_excerpt.upper()
            if "DESERT" in excerpt_upper:
                ev.description = "Licitacao declarada deserta"
            elif "FRACASSAD" in excerpt_upper:
                ev.description = "Licitacao declarada fracassada"
        return events

    def _extract_price_registers(self, text: str) -> list[GazetteEvent]:
        """Extract price registration events from text."""
        return self._run_patterns(
            text,
            self._PRICE_REGISTER_PATTERNS,
            event_type="PRICE_REGISTER",
            description_tpl="Ata de registro de preco",
        )

    def _extract_amendments(self, text: str) -> list[GazetteEvent]:
        """Extract amendment/addendum events from text."""
        events = self._run_patterns(
            text,
            self._AMENDMENT_PATTERNS,
            event_type="AMENDMENT",
            description_tpl="Termo aditivo/apostilamento de contrato",
        )
        # Try to extract percentage from amendment context
        pct_pattern = re.compile(
            r"(?:acr[eé]scimo|supress[aã]o|reajuste)\s+de\s+(\d+(?:[.,]\d+)?)\s*%",
            re.IGNORECASE,
        )
        for ev in events:
            m = pct_pattern.search(ev.raw_excerpt)
            if m:
                pct = m.group(1).replace(",", ".")
                ev.description += f" ({pct}%)"

        # Detect extension subtype (PRORROGACAO -> EXTENSION)
        extension_pattern = re.compile(r"PRORROGA[CÇ][AÃ]O", re.IGNORECASE)
        for ev in events:
            if extension_pattern.search(ev.raw_excerpt):
                ev.event_type = "EXTENSION"
                ev.description = "Prorrogacao de contrato"
        return events

    def _extract_reopenings(self, text: str) -> list[GazetteEvent]:
        """Extract reopening/rescheduling events from text."""
        return self._run_patterns(
            text,
            self._REOPENING_PATTERNS,
            event_type="REOPENING",
            description_tpl="Reabertura/reagendamento de licitacao",
        )

    # ------------------------------------------------------------------
    # Shared extraction engine
    # ------------------------------------------------------------------

    def _run_patterns(
        self,
        text: str,
        patterns: list[tuple[re.Pattern, float]],
        event_type: str,
        description_tpl: str,
    ) -> list[GazetteEvent]:
        """Run a list of (pattern, confidence) pairs and build events."""
        events: list[GazetteEvent] = []
        seen_positions: set[int] = set()  # avoid duplicate matches in overlapping windows

        for pattern, confidence in patterns:
            for match in pattern.finditer(text):
                # Skip if we already captured an event near this position
                pos_bucket = match.start() // 100
                if pos_bucket in seen_positions:
                    continue
                seen_positions.add(pos_bucket)

                excerpt = _get_excerpt(text, match, window=250)
                processo = _extract_first_processo(excerpt)
                valor = _extract_first_value(excerpt)
                date_ref = _extract_first_date(excerpt)

                events.append(
                    GazetteEvent(
                        event_type=event_type,
                        confidence=confidence,
                        description=description_tpl,
                        processo=processo,
                        valor=valor,
                        date_ref=date_ref,
                        raw_excerpt=excerpt,
                    )
                )
        return events

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate(events: list[GazetteEvent]) -> list[GazetteEvent]:
        """Deduplicate events: same event_type + processo keeps highest confidence."""
        best: dict[tuple[str, str | None], GazetteEvent] = {}
        no_processo: list[GazetteEvent] = []

        for ev in events:
            if ev.processo:
                key = (ev.event_type, ev.processo)
                existing = best.get(key)
                if not existing or ev.confidence > existing.confidence:
                    best[key] = ev
            else:
                no_processo.append(ev)

        # For events without processo, deduplicate by event_type + position bucket
        seen_types: dict[str, list[GazetteEvent]] = {}
        for ev in no_processo:
            if ev.event_type not in seen_types:
                seen_types[ev.event_type] = []
            # Check overlap with existing excerpts of same type
            is_dup = False
            for existing in seen_types[ev.event_type]:
                # If excerpts share significant overlap, consider duplicate
                overlap = len(set(ev.raw_excerpt[:80]) & set(existing.raw_excerpt[:80]))
                if overlap > 40:
                    if ev.confidence > existing.confidence:
                        seen_types[ev.event_type].remove(existing)
                        seen_types[ev.event_type].append(ev)
                    is_dup = True
                    break
            if not is_dup:
                seen_types[ev.event_type].append(ev)

        result = list(best.values())
        for evs in seen_types.values():
            result.extend(evs)
        return result


# ---------------------------------------------------------------------------
# Organ behavior analysis
# ---------------------------------------------------------------------------

def analyze_organ_behavior(events: list[GazetteEvent]) -> dict[str, Any]:
    """Aggregate gazette events to detect organ behavioral patterns.

    Args:
        events: List of ``GazetteEvent`` extracted from gazette text.

    Returns:
        Dict with event counts, rates, and risk signals.
    """
    counts: dict[str, int] = {
        "suspensions": 0,
        "cancellations": 0,
        "awards": 0,
        "amendments": 0,
        "extensions": 0,
        "price_registers": 0,
        "reopenings": 0,
    }
    type_to_key = {
        "SUSPENSION": "suspensions",
        "CANCELLATION": "cancellations",
        "AWARD": "awards",
        "AMENDMENT": "amendments",
        "EXTENSION": "extensions",
        "PRICE_REGISTER": "price_registers",
        "REOPENING": "reopenings",
    }

    for ev in events:
        key = type_to_key.get(ev.event_type)
        if key:
            counts[key] += 1

    total = len(events)
    awards = counts["awards"]
    cancellations = counts["cancellations"]
    amendments = counts["amendments"] + counts["extensions"]
    suspensions = counts["suspensions"]

    # Cancellation rate
    denominator = awards + cancellations
    cancellation_rate = cancellations / denominator if denominator > 0 else 0.0

    # Amendment frequency relative to awards
    amendment_rate = amendments / awards if awards > 0 else 0.0
    amendment_frequency = "ALTA" if amendment_rate > 0.30 else "NORMAL"

    # Risk signals
    risk_signals: list[str] = []
    if cancellation_rate > 0.30:
        risk_signals.append("ALTO_CANCELAMENTO")
    if amendment_rate > 0.30:
        risk_signals.append("MUITOS_ADITIVOS")
    if suspensions >= 3 or (total > 0 and suspensions / total > 0.25):
        risk_signals.append("FREQUENTES_SUSPENSOES")

    return {
        "total_events": total,
        "suspensions": counts["suspensions"],
        "cancellations": counts["cancellations"],
        "awards": counts["awards"],
        "amendments": counts["amendments"],
        "extensions": counts["extensions"],
        "price_registers": counts["price_registers"],
        "reopenings": counts["reopenings"],
        "cancellation_rate": round(cancellation_rate, 3),
        "amendment_frequency": amendment_frequency,
        "risk_signals": risk_signals,
    }


# ---------------------------------------------------------------------------
# Querido Diario enrichment
# ---------------------------------------------------------------------------

def enrich_querido_diario(qd_data: list[dict]) -> list[dict]:
    """Enrich Querido Diario data with extracted events.

    Takes the ``querido_diario`` list from the report JSON. For each entry
    that contains an ``excerpts`` field, runs the analyzer on each excerpt
    and adds an ``events`` field.

    Args:
        qd_data: List of QD entry dicts, each with optional ``excerpts`` key.

    Returns:
        The same list with ``events`` and ``behavior`` fields added.
    """
    analyzer = GazetteAnalyzer()
    all_events: list[GazetteEvent] = []

    for entry in qd_data:
        excerpts = entry.get("excerpts") or entry.get("excertos") or []
        if isinstance(excerpts, str):
            excerpts = [excerpts]

        context = {}
        if entry.get("orgao"):
            context["orgao"] = entry["orgao"]

        entry_events: list[GazetteEvent] = []
        for excerpt_text in excerpts:
            if not isinstance(excerpt_text, str):
                continue
            events = analyzer.extract_events(excerpt_text, context=context)
            entry_events.extend(events)

        # Deduplicate across excerpts within same entry
        entry_events = analyzer._deduplicate(entry_events)
        entry_events.sort(key=lambda e: e.confidence, reverse=True)

        entry["events"] = [ev.to_dict() for ev in entry_events]
        all_events.extend(entry_events)

    # Add overall behavior analysis across all entries
    if qd_data:
        behavior = analyze_organ_behavior(all_events)
        # Attach behavior to the first entry as a summary (or could be separate)
        qd_data.append({"_behavior_summary": behavior})

    return qd_data


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Command-line interface for gazette NLP analysis."""
    parser = argparse.ArgumentParser(
        description="NLP analyzer for Brazilian gazette (Diario Oficial) content.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--json",
        metavar="FILE",
        help="Path to report JSON file. Enriches querido_diario entries.",
    )
    group.add_argument(
        "--text",
        metavar="TEXT",
        help="Analyze a single text string directly.",
    )
    parser.add_argument(
        "--orgao",
        help="Organ name to attach to extracted events (used with --text).",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file path (default: stdout for --text, overwrite for --json).",
    )

    args = parser.parse_args()
    analyzer = GazetteAnalyzer()

    if args.text:
        # Analyze single text
        context = {"orgao": args.orgao} if args.orgao else None
        events = analyzer.extract_events(args.text, context=context)
        behavior = analyze_organ_behavior(events)

        result = {
            "events": [ev.to_dict() for ev in events],
            "behavior": behavior,
        }
        output_str = json.dumps(result, ensure_ascii=False, indent=2)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"[gazette_nlp] Output written to {args.output}")
        else:
            print(output_str)

    elif args.json:
        # Enrich report JSON
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Find querido_diario key in report data
        qd_data = None
        if isinstance(data, dict):
            qd_data = data.get("querido_diario") or data.get("querido_diario_data")
        elif isinstance(data, list):
            qd_data = data

        if qd_data is None or not isinstance(qd_data, list):
            print("[gazette_nlp] ERROR: No querido_diario data found in JSON.", file=sys.stderr)
            sys.exit(1)

        enriched = enrich_querido_diario(qd_data)

        # Write back
        if isinstance(data, dict):
            key = "querido_diario" if "querido_diario" in data else "querido_diario_data"
            data[key] = enriched

        output_path = args.output or args.json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[gazette_nlp] Enriched {len(enriched)} entries -> {output_path}")


if __name__ == "__main__":
    _fix_win_encoding()
    main()
