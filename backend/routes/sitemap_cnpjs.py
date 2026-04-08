"""SEO Onda 1: Public endpoint for sitemap CNPJ expansion.

Returns top CNPJs (orgao_cnpj) from pncp_raw_bids with ≥1 bid,
enabling the frontend sitemap to generate /cnpj/{cnpj} URLs for
Google discovery. Public (no auth). Cache: InMemory 24h TTL.

Implementation layers:
1. get_sitemap_cnpjs_json RPC (RETURNS json scalar — bypasses PostgREST max-rows=1000)
2. Fallback: paginated table query (loop 1k/page until exhausted)
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sitemap"])

_CACHE_TTL_SECONDS = 24 * 60 * 60  # 24h
_sitemap_cache: dict[str, tuple[dict, float]] = {}

_MAX_CNPJS = 5000

# Seed list: CNPJs de empresas fornecedoras (B2G suppliers) com relatórios intel gerados.
# Estes aparecem PRIMEIRO no sitemap (prioridade sobre compradores/órgãos)
# para garantir indexação de fornecedores com conteúdo rico de contratos.
_SEED_SUPPLIER_CNPJS: list[str] = [
    "01721078000168",  # LCM Construções
    "07186297000170",  # CRV Construtora Rezende & Alvarenga
    "09225035000101",  # GJS Construções
    "18742098000118",  # Trena Terraplenagem
    "24515063000149",  # Extra Empreiteira
    "26420889000150",  # Gamarra Construtora
    "27735305000106",  # Infrainga Engenharia
    "33256335000124",  # Distriminas
    "39336452000184",  # Construsol Sobralense
    "42192677000119",  # LCA Infraestrutura
    "47673948000171",  # Borges Gomes
]


class SitemapCnpjsResponse(BaseModel):
    cnpjs: list[str]
    total: int
    updated_at: str


def _get_cached(key: str) -> Optional[dict]:
    if key not in _sitemap_cache:
        return None
    data, ts = _sitemap_cache[key]
    if time.time() - ts >= _CACHE_TTL_SECONDS:
        del _sitemap_cache[key]
        return None
    return data


def _set_cached(key: str, data: dict) -> None:
    _sitemap_cache[key] = (data, time.time())


@router.get(
    "/sitemap/cnpjs",
    response_model=SitemapCnpjsResponse,
    summary="CNPJs com ≥1 licitação no datalake (para sitemap)",
)
async def sitemap_cnpjs():
    cached = _get_cached("cnpjs")
    if cached:
        return SitemapCnpjsResponse(**cached)

    data = await _fetch_top_cnpjs()
    _set_cached("cnpjs", data)
    return SitemapCnpjsResponse(**data)


def _merge_with_seed(buyer_cnpjs: list[str]) -> list[str]:
    """Merge seed supplier CNPJs (priority) with buyer CNPJs, dedup, cap at _MAX_CNPJS."""
    seen: set[str] = set()
    result: list[str] = []
    # Seed suppliers first — they have richer contract content
    for cnpj in _SEED_SUPPLIER_CNPJS:
        if cnpj not in seen:
            seen.add(cnpj)
            result.append(cnpj)
    # Then buyer CNPJs (orgaos)
    for cnpj in buyer_cnpjs:
        if cnpj not in seen:
            seen.add(cnpj)
            result.append(cnpj)
    return result[:_MAX_CNPJS]


async def _fetch_top_cnpjs() -> dict:
    """Query pncp_raw_bids for distinct orgao_cnpj with ≥1 active bid.

    Uses get_sitemap_cnpjs_json RPC (RETURNS json scalar) which bypasses
    PostgREST max-rows=1000. Falls back to paginated table query if RPC
    doesn't exist yet (e.g., migration not yet applied).
    """
    try:
        from supabase_client import get_supabase

        sb = get_supabase()

        # Primary: JSON scalar RPC — not subject to max-rows limit
        try:
            resp = sb.rpc("get_sitemap_cnpjs_json", {"max_results": _MAX_CNPJS}).execute()
            if resp.data is not None:
                # resp.data is a JSON array of CNPJ strings
                raw = resp.data if isinstance(resp.data, list) else []
                buyer_list = [
                    c for c in raw
                    if c and isinstance(c, str) and len(c) >= 11
                ]
                cnpj_list = _merge_with_seed(buyer_list)
                logger.info(
                    "sitemap_cnpjs (JSON RPC): %d buyers + %d seed suppliers = %d total",
                    len(buyer_list),
                    len(_SEED_SUPPLIER_CNPJS),
                    len(cnpj_list),
                )
                return {
                    "cnpjs": cnpj_list,
                    "total": len(cnpj_list),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as rpc_err:
            logger.warning(
                "sitemap_cnpjs JSON RPC failed (%s), falling back to paginated query",
                rpc_err,
            )

        # Fallback: paginated table query (1k rows/page, full scan)
        counts: dict[str, int] = {}
        page_size = 1000
        offset = 0
        while True:
            resp = (
                sb.table("pncp_raw_bids")
                .select("orgao_cnpj")
                .eq("is_active", True)
                .not_.is_("orgao_cnpj", "null")
                .neq("orgao_cnpj", "")
                .range(offset, offset + page_size - 1)
                .execute()
            )
            if not resp.data:
                break
            for row in resp.data:
                cnpj = (row.get("orgao_cnpj") or "").strip()
                if cnpj and len(cnpj) >= 11:
                    counts[cnpj] = counts.get(cnpj, 0) + 1
            if len(resp.data) < page_size:
                break
            offset += page_size

        buyer_list = [
            cnpj
            for cnpj, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]
        cnpj_list = _merge_with_seed(buyer_list)

        logger.info(
            "sitemap_cnpjs (paginated): %d CNPJs from %d distinct, %d pages",
            len(cnpj_list),
            len(counts),
            (offset // page_size) + 1,
        )

        return {
            "cnpjs": cnpj_list,
            "total": len(cnpj_list),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error("sitemap_cnpjs failed: %s", e)
        return {
            "cnpjs": [],
            "total": 0,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
