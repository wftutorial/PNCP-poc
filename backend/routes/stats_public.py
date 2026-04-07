"""Public statistics endpoint for /estatisticas SEO page.

Returns ~15-20 aggregate stats from the PNCP datalake (last 30 days).
Public (no auth). Cache: InMemory 6h TTL.
"""

import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["stats_public"])

_CACHE_TTL_SECONDS = 6 * 60 * 60  # 6h
_stats_cache: dict[str, tuple[dict, float]] = {}

_MODALIDADE_NAMES: dict[int, str] = {
    4: "Concorrência",
    5: "Pregão Eletrônico",
    6: "Pregão Presencial",
    7: "Leilão",
    8: "Dispensa",
    12: "Credenciamento",
}


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class PublicStat(BaseModel):
    id: str
    label: str
    value: float
    formatted_value: str
    unit: str
    context: str
    source: str
    period: str
    sector: Optional[str] = None
    uf: Optional[str] = None


class PublicStatsResponse(BaseModel):
    updated_at: str
    total_stats: int
    stats: list[PublicStat]


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/stats/public",
    response_model=PublicStatsResponse,
    summary="Estatísticas públicas agregadas do PNCP (sem auth)",
)
async def stats_public():
    cached = _get_cached("global")
    if cached:
        return PublicStatsResponse(**cached)

    data = await _generate_stats()
    _set_cached("global", data)
    return PublicStatsResponse(**data)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def _get_cached(key: str) -> Optional[dict]:
    if key not in _stats_cache:
        return None
    data, ts = _stats_cache[key]
    if time.time() - ts >= _CACHE_TTL_SECONDS:
        del _stats_cache[key]
        return None
    return data


def _set_cached(key: str, data: dict) -> None:
    _stats_cache[key] = (data, time.time())


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _fmt_int(n: float) -> str:
    """Format integer with dot-separated thousands (Brazilian locale)."""
    return f"{int(n):,}".replace(",", ".")


def _fmt_brl(v: float) -> str:
    """Format BRL value abbreviating large numbers."""
    if v >= 1_000_000_000:
        return f"R$ {v / 1_000_000_000:.1f} bi".replace(".", ",")
    if v >= 1_000_000:
        return f"R$ {v / 1_000_000:.1f} mi".replace(".", ",")
    if v >= 1_000:
        return f"R$ {v / 1_000:.0f} mil"
    return f"R$ {v:.0f}"


def _fmt_pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")


# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------


async def _generate_stats() -> dict:
    from datalake_query import query_datalake
    from sectors import SECTORS

    now = datetime.now(timezone.utc)
    updated_at = now.isoformat()
    data_final = now.strftime("%Y-%m-%d")
    data_inicial = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    all_results: list[dict] = []
    try:
        from unified_schemas.unified import VALID_UFS
        all_results = await query_datalake(
            ufs=list(VALID_UFS),
            data_inicial=data_inicial,
            data_final=data_final,
            limit=5000,
        )
    except Exception as exc:
        logger.warning("stats_public: datalake query failed: %s", exc)

    source_label = "PNCP — Portal Nacional de Contratações Públicas"
    period_label = "Últimos 30 dias"
    context_base = "Dados do PNCP processados pelo SmartLic"

    stats: list[dict] = []
    total = len(all_results)

    # ------------------------------------------------------------------
    # 1. Total bids this month
    # ------------------------------------------------------------------
    stats.append({
        "id": "total_bids_month",
        "label": "Editais publicados no último mês",
        "value": float(total),
        "formatted_value": _fmt_int(total),
        "unit": "editais",
        "context": f"Total de contratações publicadas no PNCP nos últimos 30 dias",
        "source": source_label,
        "period": period_label,
    })

    # ------------------------------------------------------------------
    # Value extraction
    # ------------------------------------------------------------------
    values: list[float] = []
    for r in all_results:
        v = r.get("valorTotalEstimado") or r.get("valorEstimado") or r.get("valor_estimado")
        if v and isinstance(v, (int, float)) and float(v) > 0:
            values.append(float(v))

    values.sort()

    # 2. Total estimated value
    total_value = sum(values)
    stats.append({
        "id": "total_value_month",
        "label": "Valor total estimado no último mês",
        "value": round(total_value, 2),
        "formatted_value": _fmt_brl(total_value),
        "unit": "R$",
        "context": "Soma dos valores estimados de todas as contratações publicadas",
        "source": source_label,
        "period": period_label,
    })

    # 3. Average value per bid
    avg_value = total_value / len(values) if values else 0.0
    stats.append({
        "id": "avg_value_month",
        "label": "Valor médio por edital",
        "value": round(avg_value, 2),
        "formatted_value": _fmt_brl(avg_value),
        "unit": "R$",
        "context": "Média dos valores estimados dos editais com valor informado",
        "source": source_label,
        "period": period_label,
    })

    # 4. Median value
    if values:
        mid = len(values) // 2
        median_value = (
            (values[mid - 1] + values[mid]) / 2
            if len(values) % 2 == 0
            else values[mid]
        )
    else:
        median_value = 0.0
    stats.append({
        "id": "median_value_month",
        "label": "Valor mediano por edital",
        "value": round(median_value, 2),
        "formatted_value": _fmt_brl(median_value),
        "unit": "R$",
        "context": "Valor mediano — metade dos editais está abaixo deste valor",
        "source": source_label,
        "period": period_label,
    })

    # 5. % bids with value > R$1M
    count_1m = sum(1 for v in values if v >= 1_000_000)
    pct_1m = (count_1m / total * 100) if total > 0 else 0.0
    stats.append({
        "id": "pct_bids_over_1m",
        "label": "Editais com valor acima de R$ 1 milhão",
        "value": round(pct_1m, 1),
        "formatted_value": _fmt_pct(pct_1m),
        "unit": "%",
        "context": f"{_fmt_int(count_1m)} de {_fmt_int(total)} editais superam R$ 1 milhão",
        "source": source_label,
        "period": period_label,
    })

    # ------------------------------------------------------------------
    # 6. Top UFs by count
    # ------------------------------------------------------------------
    uf_counts: dict[str, int] = {}
    for r in all_results:
        uf = r.get("uf") or r.get("siglaUf") or r.get("ufSigla") or ""
        if isinstance(uf, str) and len(uf) == 2:
            uf_counts[uf.upper()] = uf_counts.get(uf.upper(), 0) + 1

    if uf_counts:
        top_uf, top_uf_count = max(uf_counts.items(), key=lambda x: x[1])
        stats.append({
            "id": "top_uf_count",
            "label": f"UF com mais editais publicados",
            "value": float(top_uf_count),
            "formatted_value": f"{top_uf} — {_fmt_int(top_uf_count)}",
            "unit": "editais",
            "context": f"{top_uf} lidera o ranking de publicações no período",
            "source": source_label,
            "period": period_label,
            "uf": top_uf,
        })

    # 7-11. Top 5 UFs
    top5_ufs = sorted(uf_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for rank, (uf, cnt) in enumerate(top5_ufs, 1):
        pct_uf = (cnt / total * 100) if total > 0 else 0.0
        stats.append({
            "id": f"uf_rank_{rank}_{uf.lower()}",
            "label": f"Editais publicados — {uf}",
            "value": float(cnt),
            "formatted_value": _fmt_int(cnt),
            "unit": "editais",
            "context": f"{_fmt_pct(pct_uf)} do total nacional no período",
            "source": source_label,
            "period": period_label,
            "uf": uf,
        })

    # ------------------------------------------------------------------
    # 12. Top sectors (keyword match against SECTORS)
    # ------------------------------------------------------------------
    sector_counts: dict[str, int] = {}
    for r in all_results:
        objeto = (r.get("objeto") or r.get("descricaoObjeto") or "").lower()
        if not objeto:
            continue
        for sector_id, sector in SECTORS.items():
            for kw in list(sector.keywords)[:30]:  # limit per-bid check
                if kw.lower() in objeto:
                    sector_counts[sector_id] = sector_counts.get(sector_id, 0) + 1
                    break  # count each bid once per sector

    top5_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for rank, (sector_id, cnt) in enumerate(top5_sectors, 1):
        sector_name = SECTORS[sector_id].name if sector_id in SECTORS else sector_id
        pct_s = (cnt / total * 100) if total > 0 else 0.0
        stats.append({
            "id": f"sector_rank_{rank}_{sector_id}",
            "label": f"Editais do setor — {sector_name}",
            "value": float(cnt),
            "formatted_value": _fmt_int(cnt),
            "unit": "editais",
            "context": f"{_fmt_pct(pct_s)} dos editais com keywords deste setor",
            "source": source_label,
            "period": period_label,
            "sector": sector_name,
        })

    # ------------------------------------------------------------------
    # 13. Modalidade distribution
    # ------------------------------------------------------------------
    modal_counts: dict[int, int] = {}
    for r in all_results:
        code = r.get("codigoModalidadeContratacao")
        if isinstance(code, int) and code in _MODALIDADE_NAMES:
            modal_counts[code] = modal_counts.get(code, 0) + 1

    if modal_counts:
        top_modal_code, top_modal_count = max(modal_counts.items(), key=lambda x: x[1])
        top_modal_name = _MODALIDADE_NAMES.get(top_modal_code, f"Código {top_modal_code}")
        pct_modal = (top_modal_count / total * 100) if total > 0 else 0.0
        stats.append({
            "id": "top_modalidade",
            "label": f"Modalidade mais utilizada — {top_modal_name}",
            "value": float(top_modal_count),
            "formatted_value": _fmt_int(top_modal_count),
            "unit": "editais",
            "context": f"{_fmt_pct(pct_modal)} dos editais são via {top_modal_name}",
            "source": source_label,
            "period": period_label,
        })

    return {
        "updated_at": updated_at,
        "total_stats": len(stats),
        "stats": stats,
    }
