#!/usr/bin/env python3
"""
Gerador de planilha Excel para Intel-Busca.

Gera planilha profissional com TODAS as oportunidades encontradas,
classificadas por compatibilidade CNAE e capacidade financeira.

Usage:
    python scripts/intel-excel.py --input docs/intel/intel-12345678000190-2026-03-18.json
    python scripts/intel-excel.py --input data.json --output custom.xlsx
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Windows console encoding fix
if sys.platform == "win32":
    import io
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except (ValueError, AttributeError):
        pass

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side, numbers
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Design tokens (from report-b2g)
INK = "1B2A3D"
BG_SUBTLE = "F5F6F8"
WHITE = "FFFFFF"
GREEN_TEXT = "1B7A3D"
RED_TEXT = "B5342A"
AMBER_TEXT = "B8860B"
LINK_BLUE = "0563C1"

CURRENCY_FMT = '[$R$-416] #,##0.00'
DATE_FMT = "DD/MM/YYYY"
DATETIME_FMT = "DD/MM/YYYY HH:MM"
PCT_FMT = "0.0%"

# Regex to strip illegal XML 1.0 control characters that openpyxl rejects.
# Keeps tab (\x09), newline (\x0a), and carriage return (\x0d).
_ILLEGAL_XML_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")

# Column definitions: (header, width, align)
COLUMNS = [
    ("N\u00ba", 5, "center"),
    ("Objeto", 55, "left"),
    ("\u00d3rg\u00e3o", 35, "left"),
    ("UF", 5, "center"),
    ("Munic\u00edpio", 20, "left"),
    ("Valor Estimado", 18, "right"),
    ("Modalidade", 20, "left"),
    ("Publica\u00e7\u00e3o", 13, "center"),
    ("Abertura Propostas", 18, "center"),
    ("Encerramento", 18, "center"),
    ("Dist\u00e2ncia (km)", 12, "right"),
    ("Custo Proposta", 14, "right"),
    ("ROI", 10, "center"),
    ("Popula\u00e7\u00e3o", 12, "right"),
    ("Compat\u00edvel CNAE", 12, "center"),
    ("Dentro Capacidade", 14, "center"),
    ("Densidade KW", 10, "center"),
    ("Keywords", 25, "left"),
    ("Link PNCP", 12, "center"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sanitize(value) -> str:
    """Remove illegal XML control characters from a string."""
    if value is None:
        return ""
    s = str(value)
    return _ILLEGAL_XML_RE.sub("", s)


def _parse_dt(value) -> datetime | None:
    """Parse datetime flexibly (ISO, BR, with/without time). Returns naive."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    s = str(value).strip()
    # Try ISO with timezone
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.replace(tzinfo=None)
    except (ValueError, AttributeError):
        pass
    # Try ISO without tz
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _safe_float(value) -> float | None:
    """Convert value to float, returning None on failure."""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            # Handle BR format "1.234,56" -> "1234.56"
            value = value.replace(".", "").replace(",", ".")
        return float(value)
    except (ValueError, TypeError):
        return None


def _cnae_label(item: dict) -> str:
    """Build CNAE label from cnae_compatible field."""
    val = item.get("cnae_compatible")
    if val is True or str(val).upper() in ("TRUE", "SIM", "YES", "1"):
        return "SIM"
    if val is False or str(val).upper() in ("FALSE", "NAO", "NÃO", "NO", "0"):
        return "N\u00c3O"
    if val is None:
        return "AVALIAR"
    # String values like "AVALIAR", "PARCIAL", etc.
    s = str(val).upper().strip()
    if s in ("SIM", "YES", "TRUE"):
        return "SIM"
    if s in ("NAO", "NÃO", "NO", "FALSE"):
        return "N\u00c3O"
    return "AVALIAR"


def _capacity_label(valor: float | None, capacity_10x: float | None) -> str:
    """Determine if value is within financial capacity (10x capital)."""
    if valor is None or capacity_10x is None:
        return "N/D"
    return "SIM" if valor <= capacity_10x else "N\u00c3O"


def _format_cnpj(cnpj: str) -> str:
    """Format CNPJ: 12.345.678/0001-90."""
    d = re.sub(r"\D", "", str(cnpj))
    if len(d) == 14:
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
    return str(cnpj)


def _format_brl(value) -> str:
    """Format value as R$ string."""
    v = _safe_float(value)
    if v is None:
        return "N/D"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# Styles factory
# ---------------------------------------------------------------------------


def _make_styles():
    """Create all reusable styles."""
    header_font = Font(bold=True, color=WHITE, size=11)
    header_fill = PatternFill(start_color=INK, end_color=INK, fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    alt_fill = PatternFill(start_color=BG_SUBTLE, end_color=BG_SUBTLE, fill_type="solid")
    no_fill = PatternFill(fill_type=None)

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    green_font = Font(color=GREEN_TEXT, bold=True)
    red_font = Font(color=RED_TEXT, bold=True)
    amber_font = Font(color=AMBER_TEXT, bold=True)
    link_font = Font(color=LINK_BLUE, underline="single")
    bold_font = Font(bold=True)

    return {
        "header_font": header_font,
        "header_fill": header_fill,
        "header_align": header_align,
        "alt_fill": alt_fill,
        "no_fill": no_fill,
        "thin_border": thin_border,
        "green_font": green_font,
        "red_font": red_font,
        "amber_font": amber_font,
        "link_font": link_font,
        "bold_font": bold_font,
    }


# ---------------------------------------------------------------------------
# Sheet builders
# ---------------------------------------------------------------------------


def _build_oportunidades(wb: Workbook, items: list[dict], capacity_10x: float | None):
    """Build Sheet 1: Oportunidades."""
    ws = wb.active
    ws.title = "Oportunidades"
    st = _make_styles()

    # --- Headers ---
    for col_idx, (header, width, _) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = st["header_font"]
        cell.fill = st["header_fill"]
        cell.alignment = st["header_align"]
        cell.border = st["thin_border"]
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.freeze_panes = "A2"

    # --- Sort by valor desc (None values last) ---
    def sort_key(it):
        v = _safe_float(it.get("valor_estimado"))
        return v if v is not None else -1

    sorted_items = sorted(items, key=sort_key, reverse=True)

    # --- Data rows ---
    for row_num, item in enumerate(sorted_items, start=2):
        data_idx = row_num - 1  # 1-based row number
        is_alt = (row_num % 2) == 0
        row_fill = st["alt_fill"] if is_alt else st["no_fill"]

        valor = _safe_float(item.get("valor_estimado"))
        cnae_label = _cnae_label(item)
        cap_label = _capacity_label(valor, capacity_10x)
        kw_density = _safe_float(item.get("keyword_density"))

        # Match keywords — can be list or comma-separated string
        match_kw = item.get("match_keywords", item.get("keywords_matched", ""))
        if isinstance(match_kw, list):
            match_kw = ", ".join(str(k) for k in match_kw)

        # Link
        link_pncp = item.get("link_pncp", item.get("link", ""))

        # A: Row number
        ws.cell(row=row_num, column=1, value=data_idx)

        # B: Objeto
        ws.cell(row=row_num, column=2, value=_sanitize(item.get("objeto", item.get("objetoCompra", ""))))

        # C: Orgao
        ws.cell(row=row_num, column=3, value=_sanitize(item.get("orgao", item.get("nomeOrgao", ""))))

        # D: UF
        ws.cell(row=row_num, column=4, value=item.get("uf", ""))

        # E: Municipio
        ws.cell(row=row_num, column=5, value=_sanitize(item.get("municipio", "")))

        # F: Valor Estimado
        val_cell = ws.cell(row=row_num, column=6)
        if valor is not None:
            val_cell.value = valor
            val_cell.number_format = CURRENCY_FMT
        else:
            val_cell.value = "Sigiloso"

        # G: Modalidade
        ws.cell(row=row_num, column=7, value=_sanitize(
            item.get("modalidade_nome", item.get("modalidadeNome", ""))
        ))

        # H: Data Publicacao
        dt_pub = _parse_dt(item.get("data_publicacao", item.get("dataPublicacaoPncp")))
        pub_cell = ws.cell(row=row_num, column=8, value=dt_pub)
        if dt_pub:
            pub_cell.number_format = DATE_FMT

        # I: Abertura Propostas
        dt_ab = _parse_dt(item.get("data_abertura_proposta", item.get("dataAberturaProposta")))
        ab_cell = ws.cell(row=row_num, column=9, value=dt_ab)
        if dt_ab:
            ab_cell.number_format = DATETIME_FMT

        # J: Encerramento
        dt_enc = _parse_dt(item.get("data_encerramento_proposta", item.get("dataEncerramentoProposta")))
        enc_cell = ws.cell(row=row_num, column=10, value=dt_enc)
        if dt_enc:
            enc_cell.number_format = DATETIME_FMT

        # K: Distância (km)
        dist_data = item.get("distancia", {})
        dist_km = _safe_float(dist_data.get("km")) if isinstance(dist_data, dict) else None
        dist_cell = ws.cell(row=row_num, column=11)
        if dist_km is not None:
            dist_cell.value = dist_km
            dist_cell.number_format = '#,##0'
        else:
            dist_cell.value = ""

        # L: Custo Proposta
        custo_data = item.get("custo_proposta", {})
        custo_total = _safe_float(custo_data.get("total")) if isinstance(custo_data, dict) else None
        custo_cell = ws.cell(row=row_num, column=12)
        if custo_total is not None:
            custo_cell.value = custo_total
            custo_cell.number_format = CURRENCY_FMT
        else:
            custo_cell.value = ""

        # M: ROI
        roi_data = item.get("roi_proposta", {})
        roi_class = roi_data.get("classificacao", "") if isinstance(roi_data, dict) else ""
        roi_cell = ws.cell(row=row_num, column=13, value=roi_class)
        if roi_class in ("EXCELENTE", "BOM"):
            roi_cell.font = st["green_font"]
        elif roi_class in ("MARGINAL", "DESFAVORAVEL"):
            roi_cell.font = st["red_font"]
        elif roi_class == "MODERADO":
            roi_cell.font = st["amber_font"]

        # N: População
        ibge_data = item.get("ibge", {})
        pop = ibge_data.get("populacao") if isinstance(ibge_data, dict) else None
        pop_cell = ws.cell(row=row_num, column=14)
        if pop is not None:
            pop_cell.value = pop
            pop_cell.number_format = '#,##0'
        else:
            pop_cell.value = ""

        # O: Compativel CNAE
        cnae_cell = ws.cell(row=row_num, column=15, value=cnae_label)
        if cnae_label == "SIM":
            cnae_cell.font = st["green_font"]
        elif cnae_label == "N\u00c3O":
            cnae_cell.font = st["red_font"]
        else:
            cnae_cell.font = st["amber_font"]

        # P: Dentro Capacidade
        cap_cell = ws.cell(row=row_num, column=16, value=cap_label)
        if cap_label == "SIM":
            cap_cell.font = st["green_font"]
        elif cap_label == "N\u00c3O":
            cap_cell.font = st["red_font"]
        else:
            cap_cell.font = Font(color="808080")

        # Q: Densidade KW
        kw_cell = ws.cell(row=row_num, column=17)
        if kw_density is not None:
            kw_cell.value = kw_density / 100.0 if kw_density > 1 else kw_density
            kw_cell.number_format = PCT_FMT
        else:
            kw_cell.value = ""

        # R: Keywords
        ws.cell(row=row_num, column=18, value=_sanitize(match_kw))

        # S: Link PNCP
        if link_pncp:
            link_cell = ws.cell(row=row_num, column=19, value="Abrir")
            link_cell.hyperlink = str(link_pncp)
            link_cell.font = st["link_font"]
        else:
            ws.cell(row=row_num, column=19, value="")

        # Apply row-level styling
        for col in range(1, len(COLUMNS) + 1):
            cell = ws.cell(row=row_num, column=col)
            cell.border = st["thin_border"]
            # Only set fill if not already a styled cell (links, cnae, capacity, roi keep font)
            if col not in (13, 15, 16, 19):
                if is_alt and cell.fill == PatternFill(fill_type=None):
                    cell.fill = row_fill
            elif is_alt:
                cell.fill = row_fill
            # Alignment per column
            _, _, h_align = COLUMNS[col - 1]
            cell.alignment = Alignment(horizontal=h_align, vertical="top", wrap_text=True)

    # --- Total row ---
    if sorted_items:
        total_row = len(sorted_items) + 2
        count_cell = ws.cell(row=total_row, column=1, value=len(sorted_items))
        count_cell.font = st["bold_font"]

        label_cell = ws.cell(row=total_row, column=5, value="TOTAL:")
        label_cell.font = st["bold_font"]

        sum_cell = ws.cell(
            row=total_row,
            column=6,
            value=f"=SUM(F2:F{total_row - 1})",
        )
        sum_cell.number_format = CURRENCY_FMT
        sum_cell.font = st["bold_font"]

        for col in range(1, len(COLUMNS) + 1):
            ws.cell(row=total_row, column=col).border = st["thin_border"]


def _build_resumo_uf(wb: Workbook, items: list[dict]):
    """Build Sheet 2: Resumo por UF."""
    ws = wb.create_sheet("Resumo por UF")
    st = _make_styles()

    # Aggregate
    uf_data: dict[str, dict] = defaultdict(lambda: {
        "qtd_total": 0, "qtd_compat": 0, "valor_total": 0.0, "valor_compat": 0.0,
    })
    for item in items:
        uf = item.get("uf", "N/D") or "N/D"
        d = uf_data[uf]
        d["qtd_total"] += 1
        valor = _safe_float(item.get("valor_estimado")) or 0.0
        d["valor_total"] += valor
        if _cnae_label(item) == "SIM":
            d["qtd_compat"] += 1
            d["valor_compat"] += valor

    headers = ["UF", "Qtd Total", "Qtd Compat\u00edvel", "Valor Total", "Valor Compat\u00edvel"]
    widths = [8, 12, 16, 20, 20]

    for col, (h, w) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = st["header_font"]
        cell.fill = st["header_fill"]
        cell.alignment = st["header_align"]
        cell.border = st["thin_border"]
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.freeze_panes = "A2"

    for row, (uf, d) in enumerate(sorted(uf_data.items()), start=2):
        ws.cell(row=row, column=1, value=uf).border = st["thin_border"]
        ws.cell(row=row, column=2, value=d["qtd_total"]).border = st["thin_border"]
        ws.cell(row=row, column=3, value=d["qtd_compat"]).border = st["thin_border"]
        vc = ws.cell(row=row, column=4, value=d["valor_total"])
        vc.number_format = CURRENCY_FMT
        vc.border = st["thin_border"]
        vcc = ws.cell(row=row, column=5, value=d["valor_compat"])
        vcc.number_format = CURRENCY_FMT
        vcc.border = st["thin_border"]

    # Totals
    if uf_data:
        tr = len(uf_data) + 2
        ws.cell(row=tr, column=1, value="TOTAL").font = st["bold_font"]
        ws.cell(row=tr, column=2, value=f"=SUM(B2:B{tr-1})").font = st["bold_font"]
        ws.cell(row=tr, column=3, value=f"=SUM(C2:C{tr-1})").font = st["bold_font"]
        tc4 = ws.cell(row=tr, column=4, value=f"=SUM(D2:D{tr-1})")
        tc4.number_format = CURRENCY_FMT
        tc4.font = st["bold_font"]
        tc5 = ws.cell(row=tr, column=5, value=f"=SUM(E2:E{tr-1})")
        tc5.number_format = CURRENCY_FMT
        tc5.font = st["bold_font"]
        for col in range(1, 6):
            ws.cell(row=tr, column=col).border = st["thin_border"]


def _build_resumo_modalidade(wb: Workbook, items: list[dict]):
    """Build Sheet 3: Resumo por Modalidade."""
    ws = wb.create_sheet("Resumo por Modalidade")
    st = _make_styles()

    mod_data: dict[str, dict] = defaultdict(lambda: {"qtd": 0, "valor_total": 0.0})
    for item in items:
        mod = _sanitize(
            item.get("modalidade_nome", item.get("modalidadeNome", ""))
        ) or "N/D"
        d = mod_data[mod]
        d["qtd"] += 1
        d["valor_total"] += _safe_float(item.get("valor_estimado")) or 0.0

    headers = ["Modalidade", "Qtd", "Valor Total"]
    widths = [35, 10, 22]

    for col, (h, w) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = st["header_font"]
        cell.fill = st["header_fill"]
        cell.alignment = st["header_align"]
        cell.border = st["thin_border"]
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.freeze_panes = "A2"

    for row, (mod, d) in enumerate(sorted(mod_data.items()), start=2):
        ws.cell(row=row, column=1, value=mod).border = st["thin_border"]
        ws.cell(row=row, column=2, value=d["qtd"]).border = st["thin_border"]
        vc = ws.cell(row=row, column=3, value=d["valor_total"])
        vc.number_format = CURRENCY_FMT
        vc.border = st["thin_border"]

    if mod_data:
        tr = len(mod_data) + 2
        ws.cell(row=tr, column=1, value="TOTAL").font = st["bold_font"]
        ws.cell(row=tr, column=2, value=f"=SUM(B2:B{tr-1})").font = st["bold_font"]
        tc3 = ws.cell(row=tr, column=3, value=f"=SUM(C2:C{tr-1})")
        tc3.number_format = CURRENCY_FMT
        tc3.font = st["bold_font"]
        for col in range(1, 4):
            ws.cell(row=tr, column=col).border = st["thin_border"]


def _build_metadata(wb: Workbook, data: dict, items: list[dict]):
    """Build Sheet 4: Metadata."""
    ws = wb.create_sheet("Metadata")
    st = _make_styles()

    # Header styling for column A
    header_fill = PatternFill(start_color=INK, end_color=INK, fill_type="solid")
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 50

    empresa = data.get("empresa", {})
    busca = data.get("busca", {})
    stats = data.get("stats", data.get("estatisticas", {}))

    # Parse capital social
    capital_raw = empresa.get("capital_social")
    capital = _safe_float(capital_raw)
    capacity_10x = capital * 10 if capital else None

    # Count compatible
    total = len(items)
    compat_count = sum(1 for i in items if _cnae_label(i) == "SIM")
    incompat_count = total - compat_count
    valor_compat = sum(
        _safe_float(i.get("valor_estimado")) or 0
        for i in items
        if _cnae_label(i) == "SIM"
    )

    # CNAE info
    cnae_principal = empresa.get("cnae_principal", {})
    if isinstance(cnae_principal, dict):
        cnae_str = f"{cnae_principal.get('codigo', '')} - {cnae_principal.get('descricao', '')}"
    else:
        cnae_str = str(cnae_principal) if cnae_principal else "N/D"

    # UFs
    ufs = busca.get("ufs", [])
    if isinstance(ufs, list):
        ufs_str = ", ".join(str(u) for u in ufs)
    else:
        ufs_str = str(ufs) if ufs else "N/D"

    # Period
    data_ini = busca.get("data_inicio", busca.get("dataInicial", ""))
    data_fim = busca.get("data_fim", busca.get("dataFinal", ""))
    dt_ini = _parse_dt(data_ini)
    dt_fim = _parse_dt(data_fim)
    if dt_ini and dt_fim:
        periodo_str = f"{dt_ini.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}"
        dias = (dt_fim - dt_ini).days
    else:
        periodo_str = f"{data_ini} a {data_fim}" if data_ini else "N/D"
        dias = busca.get("dias", "N/D")

    setor = busca.get("setor", busca.get("setor_mapeado", "N/D"))
    total_bruto = stats.get("total_bruto", stats.get("total_pncp", total))

    # SICAF / Sanctions enrichment data
    sicaf = empresa.get("sicaf", {})
    sicaf_status = sicaf.get("status", "N/D") if isinstance(sicaf, dict) else "N/D"
    sancoes = empresa.get("sancoes", {})
    sancionada = empresa.get("sancionada", False)
    restricao_sicaf = empresa.get("restricao_sicaf")

    sancoes_str = "Nenhuma"
    if isinstance(sancoes, dict) and sancionada:
        ativas = [k.upper() for k, v in sancoes.items() if v and k not in ("sancionada", "inconclusive")]
        sancoes_str = ", ".join(ativas) if ativas else "SIM (detalhes indispon\u00edveis)"

    restricao_str = "SIM" if restricao_sicaf else ("N\u00c3O" if restricao_sicaf is not None else "N/D")

    rows = [
        ("CNPJ", _format_cnpj(empresa.get("cnpj", "N/D"))),
        ("Raz\u00e3o Social", empresa.get("razao_social", "N/D")),
        ("CNAE Principal", cnae_str),
        ("Capital Social", _format_brl(capital) if capital else "N/D"),
        ("Capacidade (10\u00d7)", _format_brl(capacity_10x) if capacity_10x else "N/D"),
        ("", ""),  # separator
        ("SICAF Status", sicaf_status),
        ("Restri\u00e7\u00e3o SICAF", restricao_str),
        ("San\u00e7\u00f5es Ativas", sancoes_str),
        ("Empresa Sancionada", "SIM \u26d4" if sancionada else "N\u00c3O \u2705"),
        ("", ""),  # separator
        ("UFs Buscadas", ufs_str),
        ("Per\u00edodo", periodo_str),
        ("Dias", dias),
        ("Setor Mapeado", setor),
        ("Total Bruto (PNCP)", total_bruto),
        ("Total Compat\u00edvel CNAE", compat_count),
        ("Total Incompat\u00edvel", incompat_count),
        ("Valor Total Compat\u00edvel", _format_brl(valor_compat)),
        ("Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        ("Script", "intel-collect.py + intel-enrich.py + intel-excel.py"),
    ]

    for row_idx, (label, value) in enumerate(rows, start=1):
        label_cell = ws.cell(row=row_idx, column=1, value=label)
        label_cell.font = Font(bold=True)
        label_cell.fill = PatternFill(start_color="E8EBF0", end_color="E8EBF0", fill_type="solid")
        label_cell.border = st["thin_border"]

        val_cell = ws.cell(row=row_idx, column=2, value=value)
        val_cell.border = st["thin_border"]
        val_cell.alignment = Alignment(wrap_text=True)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------


def generate_excel(data: dict, output_path: str) -> str:
    """
    Generate Excel workbook from intel-collect JSON data.

    Args:
        data: Parsed JSON dict with keys: empresa, busca, oportunidades/items, stats.
        output_path: Output .xlsx file path.

    Returns:
        Absolute path to generated file.
    """
    # Extract items — support multiple key names
    items = (
        data.get("oportunidades")
        or data.get("items")
        or data.get("editais")
        or data.get("resultados")
        or []
    )

    if not isinstance(items, list):
        print(f"WARN: campo de oportunidades nao e lista, tipo={type(items).__name__}")
        items = []

    # Compute capacity
    empresa = data.get("empresa", {})
    capital = _safe_float(empresa.get("capital_social"))
    capacity_10x = capital * 10 if capital else None

    wb = Workbook()

    # Sheet 1: Oportunidades
    _build_oportunidades(wb, items, capacity_10x)

    # Sheet 2: Resumo por UF
    _build_resumo_uf(wb, items)

    # Sheet 3: Resumo por Modalidade
    _build_resumo_modalidade(wb, items)

    # Sheet 4: Metadata
    _build_metadata(wb, data, items)

    # Save
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb.save(output_path)

    return os.path.abspath(output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Gera planilha Excel a partir do JSON do intel-collect.py"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Caminho do JSON de entrada (output do intel-collect.py)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Caminho do .xlsx de saida (default: mesmo basename com .xlsx)",
    )
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"ERRO: Arquivo nao encontrado: {input_path}")
        sys.exit(1)

    # Default output: same name with .xlsx
    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}.xlsx"

    # Load JSON
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Generate
    abs_path = generate_excel(data, output_path)

    # Summary
    items = (
        data.get("oportunidades")
        or data.get("items")
        or data.get("editais")
        or data.get("resultados")
        or []
    )
    size_kb = os.path.getsize(abs_path) / 1024
    n = len(items) if isinstance(items, list) else 0

    compat = sum(1 for i in items if _cnae_label(i) == "SIM") if isinstance(items, list) else 0

    print(f"Excel gerado: {abs_path} ({n} editais, {size_kb:.0f}KB)")
    print(f"  Compativeis CNAE: {compat} | Incompativeis: {n - compat}")
    print(f"  Abas: Oportunidades, Resumo por UF, Resumo por Modalidade, Metadata")


if __name__ == "__main__":
    main()
