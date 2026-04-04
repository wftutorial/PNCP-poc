"""SEO-PLAYBOOK P6: Shareable viability analysis routes.

POST /share/analise — create shareable link (auth required)
GET  /share/analise/{hash} — public view (no auth)
"""

import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException

from auth import require_auth
from schemas.share import ShareAnaliseRequest, ShareAnaliseResponse, SharedAnalisePublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/share", tags=["share"])

SHARE_BASE_URL = "https://smartlic.tech/analise"


@router.post("/analise", response_model=ShareAnaliseResponse)
async def create_shared_analysis(
    body: ShareAnaliseRequest,
    user: dict = Depends(require_auth),
):
    """Create a shareable analysis link for a bid's viability assessment."""
    from supabase_client import get_supabase, sb_execute

    user_id = user["id"]
    share_hash = secrets.token_urlsafe(9)  # 12 chars

    sb = get_supabase()
    row = {
        "hash": share_hash,
        "user_id": user_id,
        "bid_id": body.bid_id,
        "bid_title": body.bid_title,
        "bid_orgao": body.bid_orgao,
        "bid_uf": body.bid_uf,
        "bid_valor": float(body.bid_valor) if body.bid_valor is not None else None,
        "bid_modalidade": body.bid_modalidade,
        "viability_score": body.viability_score,
        "viability_level": body.viability_level,
        "viability_factors": body.viability_factors,
    }

    try:
        await sb_execute(sb.table("shared_analyses").insert(row))
    except Exception:
        logger.exception("Failed to create shared analysis")
        raise HTTPException(status_code=500, detail="Erro ao criar link de compartilhamento.")

    url = f"{SHARE_BASE_URL}/{share_hash}"
    logger.info("Shared analysis created: hash=%s user=%s bid=%s", share_hash, user_id, body.bid_id)
    return ShareAnaliseResponse(url=url, hash=share_hash)


@router.get("/analise/{hash}", response_model=SharedAnalisePublic)
async def get_shared_analysis(hash: str):
    """Public endpoint: retrieve a shared viability analysis by hash."""
    from supabase_client import get_supabase, sb_execute

    sb = get_supabase()

    try:
        result = await sb_execute(
            sb.table("shared_analyses")
            .select("hash,bid_id,bid_title,bid_orgao,bid_uf,bid_valor,bid_modalidade,viability_score,viability_level,viability_factors,view_count,created_at")
            .eq("hash", hash)
            .gt("expires_at", "now()")
            .limit(1)
        )
    except Exception:
        logger.exception("Failed to fetch shared analysis hash=%s", hash)
        raise HTTPException(status_code=500, detail="Erro ao buscar análise.")

    if not result.data:
        raise HTTPException(status_code=404, detail="Análise não encontrada ou expirada.")

    # Increment view count asynchronously (best-effort)
    try:
        await sb_execute(sb.rpc("increment_share_view", {"share_hash": hash}))
    except Exception:
        logger.warning("Failed to increment view count for hash=%s", hash)

    row = result.data[0]
    return SharedAnalisePublic(
        hash=row["hash"],
        bid_id=row["bid_id"],
        bid_title=row["bid_title"],
        bid_orgao=row.get("bid_orgao"),
        bid_uf=row.get("bid_uf"),
        bid_valor=float(row["bid_valor"]) if row.get("bid_valor") is not None else None,
        bid_modalidade=row.get("bid_modalidade"),
        viability_score=row["viability_score"],
        viability_level=row["viability_level"],
        viability_factors=row.get("viability_factors", {}),
        view_count=row.get("view_count", 0),
        created_at=str(row["created_at"]),
    )
