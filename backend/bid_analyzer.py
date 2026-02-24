"""STORY-259: Per-Bid Intelligence — Batch + Deep Analysis.

Two levels of bid analysis:
- Level 1 (Batch): 1 LLM call for all approved bids → summary justification per bid
- Level 2 (Deep): 1 LLM call per bid on-demand → detailed analysis card

Uses GPT-4.1-nano via structured output (response_format).
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# =============================================================================
# Schemas
# =============================================================================

class BidAnalysis(BaseModel):
    """Level 1: Batch analysis result per bid (STORY-259 AC2)."""
    bid_id: str
    justificativas: list[str] = Field(default_factory=list)
    acao_recomendada: str = "AVALIAR COM CAUTELA"
    compatibilidade_pct: int = Field(default=50, ge=0, le=100)


class DeepBidAnalysis(BaseModel):
    """Level 2: Deep on-demand analysis (STORY-259 AC8)."""
    bid_id: str
    score: float = Field(default=5.0, ge=0.0, le=10.0)
    decisao_sugerida: str = "AVALIAR COM CAUTELA"
    compatibilidade_pct: int = Field(default=50, ge=0, le=100)
    analise_prazo: str = ""
    analise_requisitos: list[str] = Field(default_factory=list)
    analise_competitividade: str = ""
    riscos: list[str] = Field(default_factory=list)
    justificativas_favoraveis: list[str] = Field(default_factory=list)
    justificativas_contra: list[str] = Field(default_factory=list)
    recomendacao_final: str = ""


# =============================================================================
# Level 1: Batch Analysis
# =============================================================================

def _build_profile_section(user_profile: dict | None) -> str:
    """Build profile section for LLM prompt, omitting absent fields (AC5)."""
    if not user_profile:
        return ""

    lines = ["PERFIL DO LICITANTE:"]

    field_map = {
        "setor_id": "Setor",
        "porte_empresa": "Porte",
        "faixa_valor_min": None,
        "faixa_valor_max": None,
        "ufs_atuacao": "UFs de atuação",
        "atestados": "Atestados/Certificações",
        "experiencia_licitacoes": "Experiência",
        "capacidade_funcionarios": "Funcionários",
        "faturamento_anual": "Faturamento anual",
    }

    for key, label in field_map.items():
        val = user_profile.get(key)
        if val is None or val == "" or val == []:
            continue
        if key == "faixa_valor_min":
            val_min = user_profile.get("faixa_valor_min")
            val_max = user_profile.get("faixa_valor_max")
            if val_min is not None or val_max is not None:
                lines.append(f"- Faixa de valor: R$ {val_min or 0:,.0f} – R$ {val_max or 0:,.0f}")
            continue
        if key == "faixa_valor_max":
            continue
        if isinstance(val, list):
            val = ", ".join(str(v) for v in val)
        if label:
            lines.append(f"- {label}: {val}")

    return "\n".join(lines) if len(lines) > 1 else ""


def _condense_bid(bid: dict, idx: int) -> str:
    """Condense a bid into a single line for batch prompt."""
    bid_id = bid.get("id") or bid.get("numeroControlePNCP") or f"bid_{idx}"
    objeto = (bid.get("objetoCompra") or bid.get("objeto") or "")[:150]
    valor = bid.get("valorTotalEstimado") or bid.get("valor_estimado") or 0
    uf = bid.get("uf") or ""
    modalidade = bid.get("modalidade") or ""
    return f"[{bid_id}] {objeto} | R${valor:,.0f} | {uf} | {modalidade}"


def batch_analyze_bids(
    bids: list[dict],
    user_profile: dict | None = None,
    sector_name: str = "",
) -> list[BidAnalysis]:
    """AC1: Batch analysis via single LLM call.

    Args:
        bids: List of approved bids (max 50).
        user_profile: User profile data (optional).
        sector_name: Sector display name.

    Returns:
        List of BidAnalysis, one per bid.
    """
    if not bids:
        return []

    # Limit to 50 bids
    bids_to_analyze = bids[:50]

    # Build condensed bid list
    bid_lines = [_condense_bid(b, i) for i, b in enumerate(bids_to_analyze)]
    bids_text = "\n".join(bid_lines)

    profile_text = _build_profile_section(user_profile)

    system_prompt = (
        "Você é um analista especializado em licitações públicas brasileiras. "
        "Analise cada edital abaixo e retorne um JSON array com a análise de cada um."
    )

    user_prompt = f"""Analise os editais abaixo para o setor "{sector_name}".

{profile_text}

EDITAIS:
{bids_text}

Para CADA edital, retorne:
- bid_id: identificador do edital (texto entre colchetes)
- justificativas: lista de 2-4 justificativas curtas (ex: "Setor compatível", "Valor dentro da faixa")
- acao_recomendada: "PARTICIPAR" | "AVALIAR COM CAUTELA" | "NÃO PARTICIPAR"
- compatibilidade_pct: 0-100

Retorne APENAS um JSON array. Sem explicações extras."""

    try:
        from llm_arbiter import _get_client

        client = _get_client()
        if client is None:
            logger.warning("LLM client unavailable — using fallback batch analysis")
            return _batch_fallback(bids_to_analyze, user_profile, sector_name)

        from config import LLM_ARBITER_MODEL
        response = client.chat.completions.create(
            model=LLM_ARBITER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "[]"
        parsed = json.loads(content)

        # Handle both {"analyses": [...]} and [...] formats
        if isinstance(parsed, dict):
            items = parsed.get("analyses") or parsed.get("analises") or parsed.get("items") or []
        elif isinstance(parsed, list):
            items = parsed
        else:
            items = []

        results = []
        for item in items:
            try:
                results.append(BidAnalysis(
                    bid_id=str(item.get("bid_id", "")),
                    justificativas=item.get("justificativas", []),
                    acao_recomendada=item.get("acao_recomendada", "AVALIAR COM CAUTELA"),
                    compatibilidade_pct=max(0, min(100, int(item.get("compatibilidade_pct", 50)))),
                ))
            except Exception:
                continue

        # Fill in any missing bids with fallback
        result_ids = {r.bid_id for r in results}
        for i, bid in enumerate(bids_to_analyze):
            bid_id = str(bid.get("id") or bid.get("numeroControlePNCP") or f"bid_{i}")
            if bid_id not in result_ids:
                fb = _single_bid_fallback(bid, user_profile, sector_name)
                fb.bid_id = bid_id
                results.append(fb)

        return results

    except Exception as e:
        logger.warning(f"Batch LLM analysis failed ({type(e).__name__}): {e}")
        return _batch_fallback(bids_to_analyze, user_profile, sector_name)


# =============================================================================
# Level 2: Deep Analysis (On-Demand)
# =============================================================================

def deep_analyze_bid(
    bid: dict,
    user_profile: dict | None = None,
    sector_name: str = "",
) -> DeepBidAnalysis:
    """AC7-AC9: Deep analysis via dedicated LLM call.

    Args:
        bid: Full bid data dict.
        user_profile: Complete user profile.
        sector_name: Sector display name.

    Returns:
        DeepBidAnalysis with detailed breakdown.
    """
    bid_id = str(bid.get("id") or bid.get("numeroControlePNCP") or "unknown")
    objeto = bid.get("objetoCompra") or bid.get("objeto") or ""
    valor = bid.get("valorTotalEstimado") or bid.get("valor_estimado") or 0
    modalidade = bid.get("modalidade") or ""
    uf = bid.get("uf") or ""
    orgao = bid.get("orgaoEntidade", {}).get("razaoSocial", "") if isinstance(bid.get("orgaoEntidade"), dict) else str(bid.get("orgaoEntidade", ""))
    data_abertura = bid.get("dataEncerramentoProposta") or bid.get("dataAberturaPropostas") or ""

    profile_text = _build_profile_section(user_profile)

    system_prompt = (
        "Você é um consultor sênior de licitações públicas brasileiras. "
        "Forneça uma análise aprofundada e personalizada da licitação abaixo."
    )

    user_prompt = f"""Analise esta licitação para o perfil do licitante abaixo.

LICITAÇÃO:
- Objeto: {objeto[:2000]}
- Valor estimado: R$ {valor:,.2f}
- Modalidade: {modalidade}
- UF: {uf}
- Órgão: {orgao}
- Data abertura/encerramento: {data_abertura}

{profile_text}

Responda em JSON com os campos:
- score: float 0.0-10.0
- decisao_sugerida: "PARTICIPAR" | "AVALIAR COM CAUTELA" | "NÃO PARTICIPAR"
- compatibilidade_pct: int 0-100
- analise_prazo: string (avaliação do prazo)
- analise_requisitos: list[string] (requisitos detectados)
- analise_competitividade: string (estimativa de concorrência)
- riscos: list[string] (riscos identificados)
- justificativas_favoraveis: list[string] (pontos positivos)
- justificativas_contra: list[string] (pontos negativos)
- recomendacao_final: string (1-2 frases com recomendação)"""

    try:
        from llm_arbiter import _get_client

        client = _get_client()
        if client is None:
            return _deep_fallback(bid, user_profile, sector_name)

        from config import LLM_ARBITER_MODEL
        response = client.chat.completions.create(
            model=LLM_ARBITER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)

        return DeepBidAnalysis(
            bid_id=bid_id,
            score=max(0.0, min(10.0, float(parsed.get("score", 5.0)))),
            decisao_sugerida=parsed.get("decisao_sugerida", "AVALIAR COM CAUTELA"),
            compatibilidade_pct=max(0, min(100, int(parsed.get("compatibilidade_pct", 50)))),
            analise_prazo=parsed.get("analise_prazo", ""),
            analise_requisitos=parsed.get("analise_requisitos", []),
            analise_competitividade=parsed.get("analise_competitividade", ""),
            riscos=parsed.get("riscos", []),
            justificativas_favoraveis=parsed.get("justificativas_favoraveis", []),
            justificativas_contra=parsed.get("justificativas_contra", []),
            recomendacao_final=parsed.get("recomendacao_final", ""),
        )

    except Exception as e:
        logger.warning(f"Deep analysis LLM failed ({type(e).__name__}): {e}")
        return _deep_fallback(bid, user_profile, sector_name)


# =============================================================================
# Fallback Analysis (Pure Python — AC6)
# =============================================================================

def _action_from_score(score: int) -> str:
    """Map viability/combined score to recommended action."""
    if score >= 70:
        return "PARTICIPAR"
    elif score >= 40:
        return "AVALIAR COM CAUTELA"
    return "NÃO PARTICIPAR"


def _single_bid_fallback(
    bid: dict,
    user_profile: dict | None,
    sector_name: str,
) -> BidAnalysis:
    """Generate fallback analysis for a single bid based on available data."""
    bid_id = str(bid.get("id") or bid.get("numeroControlePNCP") or "unknown")

    justificativas = []
    score_sum = 0
    score_count = 0

    # Sector compatibility
    if sector_name:
        justificativas.append(f"Setor: {sector_name}")

    # Value analysis
    valor = bid.get("valorTotalEstimado") or bid.get("valor_estimado") or 0
    if valor > 0:
        if user_profile:
            val_min = user_profile.get("faixa_valor_min", 0) or 0
            val_max = user_profile.get("faixa_valor_max", 0) or 0
            if val_min and val_max and val_min <= valor <= val_max:
                justificativas.append(f"R$ {valor:,.0f} — dentro da sua faixa")
                score_sum += 80
            elif val_min and valor < val_min:
                justificativas.append(f"R$ {valor:,.0f} — abaixo da sua faixa")
                score_sum += 40
            elif val_max and valor > val_max:
                justificativas.append(f"R$ {valor:,.0f} — acima da sua faixa")
                score_sum += 40
            else:
                justificativas.append(f"R$ {valor:,.0f}")
                score_sum += 60
        else:
            justificativas.append(f"R$ {valor:,.0f}")
            score_sum += 60
        score_count += 1

    # Timeline
    from datetime import date
    data_enc = bid.get("dataEncerramentoProposta") or bid.get("dataAberturaPropostas")
    if data_enc:
        try:
            enc_date = date.fromisoformat(data_enc[:10])
            dias = (enc_date - date.today()).days
            if dias > 14:
                justificativas.append(f"{dias} dias restantes — prazo adequado")
                score_sum += 90
            elif dias >= 7:
                justificativas.append(f"{dias} dias restantes — prazo viável")
                score_sum += 70
            elif dias >= 1:
                justificativas.append(f"{dias} dias restantes — prazo apertado")
                score_sum += 40
            else:
                justificativas.append("Prazo encerrado ou insuficiente")
                score_sum += 10
            score_count += 1
        except (ValueError, TypeError):
            pass

    # Geography
    uf = bid.get("uf", "")
    if uf and user_profile:
        ufs_user = user_profile.get("ufs_atuacao", [])
        if uf in ufs_user:
            justificativas.append(f"{uf} — sua região de atuação")
            score_sum += 100
        else:
            justificativas.append(f"{uf} — fora da região principal")
            score_sum += 40
        score_count += 1

    # Combined score
    combined = score_sum // score_count if score_count > 0 else 50

    # Use viability data if available
    viability = bid.get("viability")
    if viability and isinstance(viability, dict):
        combined = viability.get("viability_score", combined)

    return BidAnalysis(
        bid_id=bid_id,
        justificativas=justificativas or [f"Oportunidade de {sector_name}"],
        acao_recomendada=_action_from_score(combined),
        compatibilidade_pct=max(0, min(100, combined)),
    )


def _batch_fallback(
    bids: list[dict],
    user_profile: dict | None,
    sector_name: str,
) -> list[BidAnalysis]:
    """AC6: Pure Python fallback for batch analysis."""
    return [_single_bid_fallback(bid, user_profile, sector_name) for bid in bids]


def _deep_fallback(
    bid: dict,
    user_profile: dict | None,
    sector_name: str,
) -> DeepBidAnalysis:
    """Pure Python fallback for deep analysis."""
    batch_result = _single_bid_fallback(bid, user_profile, sector_name)

    return DeepBidAnalysis(
        bid_id=batch_result.bid_id,
        score=round(batch_result.compatibilidade_pct / 10, 1),
        decisao_sugerida=batch_result.acao_recomendada,
        compatibilidade_pct=batch_result.compatibilidade_pct,
        analise_prazo="Avaliação automática baseada nos dados disponíveis.",
        analise_requisitos=["Verificar requisitos no edital completo"],
        analise_competitividade="Estimativa indisponível — análise detalhada requer LLM.",
        riscos=["Análise de riscos requer avaliação detalhada do edital"],
        justificativas_favoraveis=batch_result.justificativas,
        justificativas_contra=[],
        recomendacao_final=f"Ação: {batch_result.acao_recomendada}. Compatibilidade estimada: {batch_result.compatibilidade_pct}%.",
    )
