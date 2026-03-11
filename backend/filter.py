"""Keyword matching engine for uniform/apparel procurement filtering.

DEBT-110 AC4 + DEBT-118 AC10-AC13: This file is a FACADE that re-exports
all filter functions from decomposed sub-modules:
  - filter_keywords.py  — keyword constants, matching, normalization, red flags
  - filter_density.py   — sector context, proximity, co-occurrence
  - filter_status.py    — status, modalidade, esfera, prazo filtering
  - filter_value.py     — value range, pagination
  - filter_uf.py        — single-bid filter, batch, orgao, municipio
  - filter_basic.py     — basic filters, keyword matching, density, deadline (DEBT-118)
  - filter_llm.py       — LLM zero-match + arbiter classification (DEBT-118)
  - filter_recovery.py  — synonym recovery pipeline / FLUXO 2 (DEBT-118)
  - filter_utils.py     — shared value parsing helpers (DEBT-118)

The orchestrator function aplicar_todos_filtros() remains in this file
as pure orchestration, delegating all logic to sub-modules.
All existing imports from 'filter' continue to work unchanged.
"""

import logging
from typing import Callable, Set, Tuple, List, Dict, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# DEBT-110 AC4: Re-exports from decomposed sub-modules
# ============================================================================

from filter_keywords import (  # noqa: F401 — re-export
    STOPWORDS_PT,
    validate_terms,
    remove_stopwords,
    KEYWORDS_UNIFORMES,
    KEYWORDS_EXCLUSAO,
    normalize_text,
    _strip_org_context,
    _strip_org_context_with_detail,
    GLOBAL_EXCLUSIONS,
    GLOBAL_EXCLUSIONS_NORMALIZED,
    GLOBAL_EXCLUSION_OVERRIDES,
    RED_FLAGS_MEDICAL,
    RED_FLAGS_ADMINISTRATIVE,
    RED_FLAGS_INFRASTRUCTURE,
    RED_FLAGS_PER_SECTOR,
    has_sector_red_flags,
    has_red_flags,
    match_keywords,
    _get_tracker,
    _INFRA_EXEMPT_SECTORS,
    _MEDICAL_EXEMPT_SECTORS,
    _ADMIN_EXEMPT_SECTORS,
)

from filter_density import (  # noqa: F401
    SETOR_VOCABULARIOS,
    analisar_contexto_setor,
    obter_setor_dominante,
    check_proximity_context,
    check_co_occurrence,
)

from filter_status import (  # noqa: F401
    filtrar_por_status,
    filtrar_por_modalidade,
    filtrar_por_esfera,
    filtrar_por_prazo_aberto,
)

from filter_value import (  # noqa: F401
    filtrar_por_valor,
    paginar_resultados,
)

from filter_uf import (  # noqa: F401
    filter_licitacao,
    filter_batch,
    filtrar_por_orgao,
    filtrar_por_municipio,
)

# STORY-248 AC9: Lazy import to avoid circular dependency at module load time.
_filter_stats_tracker = None


def aplicar_todos_filtros(
    licitacoes: List[dict],
    ufs_selecionadas: Set[str],
    status: str = "todos",
    modalidades: List[int] | None = None,
    valor_min: float | None = None,
    valor_max: float | None = None,
    esferas: List[str] | None = None,
    municipios: List[str] | None = None,
    orgaos: List[str] | None = None,
    keywords: Set[str] | None = None,
    exclusions: Set[str] | None = None,
    context_required: Dict[str, Set[str]] | None = None,
    min_match_floor: Optional[int] = None,
    setor: Optional[str] = None,
    modo_busca: str = "publicacao",
    custom_terms: Optional[List[str]] = None,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    pncp_degraded: bool = False,
) -> Tuple[List[dict], Dict[str, int]]:
    """Aplica todos os filtros em sequência otimizada (fail-fast).

    Returns:
        Tuple of (approved_bids, stats_dict).
    """
    from filter_basic import (
        apply_basic_filters,
        apply_keyword_filters,
        apply_item_inspection,
        apply_density_decision,
        apply_deadline_safety_net,
    )
    from filter_llm import classify_zero_match_pool, run_arbiter
    from filter_recovery import run_synonym_recovery

    stats: Dict[str, int] = {
        "total": len(licitacoes), "aprovadas": 0,
        "rejeitadas_uf": 0, "rejeitadas_status": 0, "rejeitadas_esfera": 0,
        "esfera_indeterminada": 0, "rejeitadas_modalidade": 0,
        "rejeitadas_municipio": 0, "rejeitadas_orgao": 0,
        "rejeitadas_valor": 0, "rejeitadas_valor_alto": 0,
        "rejeitadas_keyword": 0, "rejeitadas_min_match": 0,
        "rejeitadas_prazo": 0, "rejeitadas_prazo_aberto": 0,
        "rejeitadas_outros": 0, "aprovadas_alta_densidade": 0,
        "rejeitadas_baixa_densidade": 0, "duvidosas_llm_arbiter": 0,
    }

    logger.debug(f"aplicar_todos_filtros: iniciando com {len(licitacoes)} licitações")

    # Phase 1: Basic filters
    resultado_valor = apply_basic_filters(
        licitacoes, ufs_selecionadas, status, modalidades, valor_min,
        valor_max, esferas, municipios, orgaos, setor, modo_busca,
        custom_terms, stats,
    )

    # Phase 2: Keyword matching + proximity + co-occurrence
    resultado_keyword = apply_keyword_filters(
        resultado_valor, keywords, exclusions, context_required, setor,
        custom_terms, on_progress, stats,
    )

    # Phase 2B: LLM Zero-Match Classification
    resultado_llm_zero, resultado_pending_review = classify_zero_match_pool(
        zero_match_pool=[],
        resultado_valor=resultado_valor,
        resultado_keyword=resultado_keyword,
        setor=setor,
        custom_terms=custom_terms,
        on_progress=on_progress,
        stats=stats,
    )

    # Phase 2C: Item Inspection (Camada 1C)
    resultado_item_accepted = apply_item_inspection(
        resultado_keyword, setor, keywords, stats,
    )

    # Phase 2A: Density Decision + Red Flags
    kw = keywords if keywords is not None else KEYWORDS_UNIFORMES
    resultado_densidade, resultado_llm_candidates = apply_density_decision(
        resultado_keyword, setor, stats,
    )

    # Phase 3A: LLM Arbiter
    run_arbiter(
        resultado_llm_candidates=resultado_llm_candidates,
        setor=setor,
        custom_terms=custom_terms,
        resultado_densidade=resultado_densidade,
        stats=stats,
    )

    # Merge results
    resultado_keyword = resultado_densidade

    if resultado_llm_zero:
        resultado_keyword.extend(resultado_llm_zero)
        logger.info(
            f"GTM-FIX-028: Merged {len(resultado_llm_zero)} LLM zero-match bids "
            f"into resultado_keyword (total now: {len(resultado_keyword)})"
        )

    if resultado_pending_review:
        resultado_keyword.extend(resultado_pending_review)
        logger.info(
            f"STORY-354: Merged {len(resultado_pending_review)} PENDING_REVIEW bids "
            f"into resultado_keyword (total now: {len(resultado_keyword)})"
        )

    if resultado_item_accepted:
        resultado_keyword.extend(resultado_item_accepted)
        logger.info(
            f"D-01: Merged {len(resultado_item_accepted)} item-inspection bids "
            f"into resultado_keyword (total now: {len(resultado_keyword)})"
        )

    # Min match floor (STORY-178 AC2.2)
    if min_match_floor is not None and min_match_floor > 1:
        from relevance import should_include, count_phrase_matches
        resultado_min_match: List[dict] = []
        for lic in resultado_keyword:
            matched_terms = lic.get("_matched_terms", [])
            if should_include(len(matched_terms), len(kw), count_phrase_matches(matched_terms) > 0):
                resultado_min_match.append(lic)
            else:
                stats["rejeitadas_min_match"] += 1
        resultado_keyword = resultado_min_match

    logger.debug(
        f"  Após filtro Keywords: {len(resultado_keyword)} "
        f"(rejeitadas_keyword: {stats['rejeitadas_keyword']}, "
        f"rejeitadas_min_match: {stats['rejeitadas_min_match']})"
    )

    # Deadline safety net (Etapa 9)
    aprovadas = apply_deadline_safety_net(resultado_keyword, status, stats)

    # FLUXO 2: Synonym Recovery
    aprovadas = run_synonym_recovery(
        aprovadas=aprovadas,
        resultado_valor=resultado_valor,
        setor=setor,
        custom_terms=custom_terms,
        stats=stats,
        llm_zero_match_active=stats.get("llm_zero_match_calls", 0) > 0,
    )

    # Final stats
    stats["aprovadas"] = len(aprovadas)
    logger.info(
        f"aplicar_todos_filtros: concluído - {stats['aprovadas']}/{stats['total']} aprovadas "
        f"(FLUXO 1: {stats.get('aprovadas_llm_arbiter', 0)} via LLM arbiter, "
        f"FLUXO 2: {stats.get('recuperadas_llm_fn', 0)} recuperadas)"
    )
    logger.debug(f"  Estatísticas completas: {stats}")

    return aprovadas, stats
