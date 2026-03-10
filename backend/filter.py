"""Keyword matching engine for uniform/apparel procurement filtering.

DEBT-110 AC4: This file is now a FACADE that re-exports all filter functions
from decomposed sub-modules:
  - filter_keywords.py — keyword constants, matching, normalization, red flags
  - filter_density.py  — sector context, proximity, co-occurrence
  - filter_status.py   — status, modalidade, esfera, prazo filtering
  - filter_value.py    — value range, pagination
  - filter_uf.py       — single-bid filter, batch, orgao, municipio

The orchestrator function aplicar_todos_filtros() remains in this file.
All existing imports from 'filter' continue to work unchanged.
"""

import logging
import random
import re
import time
import threading
import unicodedata
import uuid
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from typing import Callable, Set, Tuple, List, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# DEBT-110 AC4: Re-exports from decomposed sub-modules
# ============================================================================

# filter_keywords.py — keyword matching, normalization, red flags
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

# filter_density.py — sector context, proximity, co-occurrence
from filter_density import (  # noqa: F401
    SETOR_VOCABULARIOS,
    analisar_contexto_setor,
    obter_setor_dominante,
    check_proximity_context,
    check_co_occurrence,
)

# filter_status.py — status, modalidade, esfera, prazo
from filter_status import (  # noqa: F401
    filtrar_por_status,
    filtrar_por_modalidade,
    filtrar_por_esfera,
    filtrar_por_prazo_aberto,
)

# filter_value.py — value range, pagination
from filter_value import (  # noqa: F401
    filtrar_por_valor,
    paginar_resultados,
)

# filter_uf.py — single-bid filter, batch, orgao, municipio
from filter_uf import (  # noqa: F401
    filter_licitacao,
    filter_batch,
    filtrar_por_orgao,
    filtrar_por_municipio,
)

# STORY-248 AC9: Lazy import to avoid circular dependency at module load time.
# Kept for backward compat — _get_tracker is re-exported from filter_keywords.
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
    setor: Optional[str] = None,  # STORY-179 AC1: sector ID for max_contract_value check
    modo_busca: str = "publicacao",  # STORY-240 AC4: "publicacao" or "abertas"
    custom_terms: Optional[List[str]] = None,  # STORY-267: user's free search terms
    on_progress: Optional[Callable[[int, int, str], None]] = None,  # STORY-329 AC1: (processed, total, phase)
    pncp_degraded: bool = False,  # CRIT-054 AC4: relax status filter for PCP v2 when PNCP is down
) -> Tuple[List[dict], Dict[str, int]]:
    """
    Aplica todos os filtros em sequência otimizada (fail-fast).

    A ordem dos filtros é otimizada para descartar licitações o mais cedo
    possível, priorizando filtros rápidos (O(1)) antes dos lentos (regex):

    1. UF (O(1) - set lookup) - mais rápido
    2. Status (O(1) - string comparison)
    3. Esfera (O(1) - string comparison)
    4. Modalidade (O(1) - int comparison)
    5. Município (O(1) - string comparison)
    6. Órgão (O(n) - string contains) - P2 filter
    7. Valor (O(1) - numeric comparison)
    8. Keywords (O(n) - regex matching) - mais lento

    Args:
        licitacoes: Lista de licitações da API PNCP
        ufs_selecionadas: Set de UFs selecionadas (ex: {"SP", "RJ"})
        status: Status desejado ("recebendo_proposta", "em_julgamento", "encerrada", "todos")
        modalidades: Lista de códigos de modalidade (None = todas)
        valor_min: Valor mínimo (None = sem limite)
        valor_max: Valor máximo (None = sem limite)
        esferas: Lista de esferas ("F", "E", "M") (None = todas)
        municipios: Lista de códigos IBGE (None = todos)
        orgaos: Lista de nomes de órgãos para filtrar (None = todos)
        keywords: Set de keywords para matching (None = usa KEYWORDS_UNIFORMES)
        exclusions: Set de exclusões (None = usa KEYWORDS_EXCLUSAO)

    Returns:
        Tuple contendo:
        - List[dict]: Licitações aprovadas em todos os filtros
        - Dict[str, int]: Estatísticas detalhadas de rejeição

    Examples:
        >>> bids = [
        ...     {"uf": "SP", "valorTotalEstimado": 100000, "objetoCompra": "Uniformes"},
        ...     {"uf": "RJ", "valorTotalEstimado": 500000, "objetoCompra": "Outros"},
        ... ]
        >>> aprovadas, stats = aplicar_todos_filtros(
        ...     bids,
        ...     ufs_selecionadas={"SP"},
        ...     valor_min=50000,
        ...     valor_max=200000
        ... )
        >>> stats["total"]
        2
        >>> stats["aprovadas"]
        1
    """
    stats: Dict[str, int] = {
        "total": len(licitacoes),
        "aprovadas": 0,
        "rejeitadas_uf": 0,
        "rejeitadas_status": 0,
        "rejeitadas_esfera": 0,
        "esfera_indeterminada": 0,  # UX-403 AC6: bids with unknown sphere (fail-open)
        "rejeitadas_modalidade": 0,
        "rejeitadas_municipio": 0,
        "rejeitadas_orgao": 0,
        "rejeitadas_valor": 0,
        "rejeitadas_valor_alto": 0,  # STORY-179 AC1: Camada 1A (value threshold)
        "rejeitadas_keyword": 0,
        "rejeitadas_min_match": 0,
        "rejeitadas_prazo": 0,
        "rejeitadas_prazo_aberto": 0,  # STORY-240 AC4: bids with passed deadline
        "rejeitadas_outros": 0,
        # STORY-179 AC2: Camada 2A (term density ratio)
        "aprovadas_alta_densidade": 0,  # density > 5% (high confidence, no LLM)
        "rejeitadas_baixa_densidade": 0,  # density < 1% (low confidence, reject)
        "duvidosas_llm_arbiter": 0,  # 1% ≤ density ≤ 5% (send to LLM)
    }

    logger.debug(
        f"aplicar_todos_filtros: iniciando com {len(licitacoes)} licitações"
    )

    # Etapa 1: Filtro de UF (mais rápido - O(1))
    resultado_uf: List[dict] = []
    for lic in licitacoes:
        uf = lic.get("uf", "")
        if uf in ufs_selecionadas:
            resultado_uf.append(lic)
        else:
            stats["rejeitadas_uf"] += 1
            # STORY-248 AC9: Record UF mismatch
            try:
                _get_tracker().record_rejection(
                    "uf_mismatch",
                    sector=setor,
                    description_preview=lic.get("objetoCompra", "")[:100],
                )
            except Exception:
                pass

    logger.debug(
        f"  Após filtro UF: {len(resultado_uf)} "
        f"(rejeitadas: {stats['rejeitadas_uf']})"
    )

    # Etapa 2: Filtro de Status
    # CRITICAL FIX (2026-02-06): Use inferred status (_status_inferido) instead of
    # raw API fields (situacaoCompra, etc.) because PNCP returns values like
    # "Divulgada no PNCP" which don't match simple string patterns.
    # The status_inference.py module correctly infers status from dates and values.
    if status and status != "todos":
        resultado_status: List[dict] = []
        status_lower = status.lower()
        # GTM-FIX-030 AC13: Diagnostic counters for status_mismatch analysis
        _status_distribution: Dict[str, int] = {}

        for lic in resultado_uf:
            # Use inferred status if available (set by enriquecer_com_status_inferido)
            status_inferido = lic.get("_status_inferido", "")

            if status_inferido:
                _status_distribution[status_inferido] = _status_distribution.get(status_inferido, 0) + 1
                # Direct comparison with inferred status
                if status_inferido == status_lower:
                    resultado_status.append(lic)
                # CRIT-054 AC2/AC4: Pass through PCP v2 records with unknown status
                # When status is "desconhecido" (PCP v2 unmapped), don't reject —
                # these are likely valid records whose status PCP reports differently.
                # Also pass through "todos" from PCP v2 (fallback inference).
                elif status_inferido in ("desconhecido", "todos") and lic.get("_source") == "PORTAL_COMPRAS":
                    lic["_status_unconfirmed"] = True
                    resultado_status.append(lic)
                    try:
                        from metrics import FILTER_PASSTHROUGH_TOTAL
                        FILTER_PASSTHROUGH_TOTAL.labels(reason="unknown_status").inc()
                    except Exception:
                        pass
                else:
                    stats["rejeitadas_status"] += 1
                    # STORY-248 AC9: Record status mismatch
                    try:
                        _get_tracker().record_rejection(
                            "status_mismatch",
                            sector=setor,
                            description_preview=lic.get("objetoCompra", "")[:100],
                        )
                    except Exception:
                        pass
            else:
                # Fallback: try raw API fields (legacy behavior)
                situacao = (
                    lic.get("situacaoCompraNome", "")
                    or lic.get("situacaoCompra", "")
                    or lic.get("situacao", "")
                    or lic.get("statusCompra", "")
                    or ""
                ).lower()

                status_map = {
                    "recebendo_proposta": [
                        "recebendo propostas", "aberta", "publicada",
                        "divulgada", "vigente", "ativa", "em andamento"
                    ],
                    "em_julgamento": [
                        "propostas encerradas", "em julgamento", "julgamento",
                        "análise", "analise", "classificação", "classificacao"
                    ],
                    "encerrada": [
                        "encerrada", "finalizada", "homologada", "adjudicada",
                        "anulada", "revogada", "cancelada", "fracassada",
                        "deserta", "suspensa", "concluída", "concluida"
                    ],
                }
                termos = status_map.get(status_lower, [])

                if any(t in situacao for t in termos):
                    resultado_status.append(lic)
                else:
                    stats["rejeitadas_status"] += 1
                    # STORY-248 AC9: Record status mismatch (fallback path)
                    try:
                        _get_tracker().record_rejection(
                            "status_mismatch",
                            sector=setor,
                            description_preview=lic.get("objetoCompra", "")[:100],
                        )
                    except Exception:
                        pass

        # GTM-FIX-030 AC13: Log status distribution for diagnostics
        logger.debug(
            f"  Status filter: wanted='{status_lower}', "
            f"distribution={_status_distribution}, "
            f"passed={len(resultado_status)}, rejected={stats['rejeitadas_status']}"
        )
        logger.debug(
            f"  Após filtro Status: {len(resultado_status)} "
            f"(rejeitadas: {stats['rejeitadas_status']})"
        )
    else:
        resultado_status = resultado_uf

    # Etapa 3: Filtro de Esfera
    # UX-403 AC1: When all 3 spheres selected, treat as None (skip filter)
    esferas_efetivas = esferas
    if esferas and set(e.upper() for e in esferas) == {"F", "E", "M"}:
        esferas_efetivas = None

    if esferas_efetivas:
        resultado_esfera: List[dict] = []
        esferas_upper = [e.upper() for e in esferas_efetivas]

        for lic in resultado_status:
            esfera_id = (
                lic.get("esferaId", "")
                or lic.get("esfera", "")
                or ""
            ).upper()

            if esfera_id in esferas_upper:
                resultado_esfera.append(lic)
            elif esfera_id:
                # Known sphere but doesn't match filter — reject
                stats["rejeitadas_esfera"] += 1
            else:
                # Fallback por tipo de órgão
                tipo_orgao = (lic.get("tipoOrgao", "") or lic.get("nomeOrgao", "")).lower()
                matched = False
                for esf in esferas_upper:
                    if esf == "F" and any(k in tipo_orgao for k in ["federal", "ministério", "ministerio"]):
                        matched = True
                    elif esf == "E" and any(k in tipo_orgao for k in ["estadual", "estado"]):
                        matched = True
                    elif esf == "M" and any(k in tipo_orgao for k in ["municipal", "prefeitura"]):
                        matched = True
                if matched:
                    resultado_esfera.append(lic)
                else:
                    # UX-403 AC2: fail-open — include bid with unknown sphere
                    lic["_esfera_inferred"] = False
                    resultado_esfera.append(lic)
                    stats["esfera_indeterminada"] += 1  # UX-403 AC6

        logger.debug(
            f"  Após filtro Esfera: {len(resultado_esfera)} "
            f"(rejeitadas: {stats['rejeitadas_esfera']}, "
            f"indeterminadas: {stats['esfera_indeterminada']})"
        )
    else:
        resultado_esfera = resultado_status

    # Etapa 4: Filtro de Modalidade
    if modalidades:
        resultado_modalidade: List[dict] = []
        for lic in resultado_esfera:
            mod_id = lic.get("modalidadeId") or lic.get("codigoModalidadeContratacao")
            try:
                mod_id = int(mod_id) if mod_id is not None else None
            except (ValueError, TypeError):
                mod_id = None

            if mod_id in modalidades:
                resultado_modalidade.append(lic)
            else:
                stats["rejeitadas_modalidade"] += 1

        logger.debug(
            f"  Após filtro Modalidade: {len(resultado_modalidade)} "
            f"(rejeitadas: {stats['rejeitadas_modalidade']})"
        )
    else:
        resultado_modalidade = resultado_esfera

    # Etapa 5: Filtro de Município
    if municipios:
        resultado_municipio: List[dict] = []
        municipios_str = [str(m).strip() for m in municipios]

        for lic in resultado_modalidade:
            codigo = str(
                lic.get("codigoMunicipioIbge")
                or lic.get("municipioId")
                or ""
            ).strip()

            if codigo in municipios_str:
                resultado_municipio.append(lic)
            else:
                stats["rejeitadas_municipio"] += 1

        logger.debug(
            f"  Após filtro Município: {len(resultado_municipio)} "
            f"(rejeitadas: {stats['rejeitadas_municipio']})"
        )
    else:
        resultado_municipio = resultado_modalidade

    # Etapa 6: Filtro de Órgão (P2)
    if orgaos:
        resultado_orgao: List[dict] = []
        orgaos_norm = [normalize_text(o) for o in orgaos if o]

        for lic in resultado_municipio:
            nome_orgao = (
                lic.get("nomeOrgao", "")
                or lic.get("orgao", "")
                or lic.get("nomeUnidade", "")
                or ""
            )
            nome_orgao_norm = normalize_text(nome_orgao)

            matched = False
            for termo in orgaos_norm:
                if termo in nome_orgao_norm:
                    matched = True
                    break

            if matched:
                resultado_orgao.append(lic)
            else:
                stats["rejeitadas_orgao"] += 1

        logger.debug(
            f"  Após filtro Órgão: {len(resultado_orgao)} "
            f"(rejeitadas: {stats['rejeitadas_orgao']})"
        )
    else:
        resultado_orgao = resultado_municipio

    # Etapa 7: Filtro de Valor
    if valor_min is not None or valor_max is not None:
        resultado_valor: List[dict] = []
        for lic in resultado_orgao:
            valor = lic.get("valorTotalEstimado") or lic.get("valorEstimado") or 0

            if isinstance(valor, str):
                try:
                    valor = float(valor.replace(".", "").replace(",", "."))
                except ValueError:
                    valor = 0.0
            else:
                valor = float(valor) if valor else 0.0

            if valor_min is not None and valor < valor_min:
                stats["rejeitadas_valor"] += 1
                continue
            if valor_max is not None and valor > valor_max:
                stats["rejeitadas_valor"] += 1
                continue

            resultado_valor.append(lic)

        logger.debug(
            f"  Após filtro Valor: {len(resultado_valor)} "
            f"(rejeitadas: {stats['rejeitadas_valor']})"
        )
    else:
        resultado_valor = resultado_orgao

    # Etapa 7.5: Filtro de Prazo Aberto (STORY-240 AC4)
    # When modo_busca="abertas", reject bids whose proposal deadline has passed.
    # Applied BEFORE keywords filter (fail-fast: eliminates closed bids before heavy regex).
    if modo_busca == "abertas":
        resultado_valor, rejeitadas_prazo = filtrar_por_prazo_aberto(resultado_valor)
        stats["rejeitadas_prazo_aberto"] = rejeitadas_prazo
        logger.debug(
            f"  Após filtro Prazo Aberto: {len(resultado_valor)} "
            f"(rejeitadas: {rejeitadas_prazo})"
        )

    # STORY-179 AC1.3: Camada 1A - Value Threshold (Anti-False Positive)
    # Apply sector-specific max_contract_value check BEFORE keyword matching
    # to reject obvious false positives (e.g., R$ 47.6M "melhorias urbanas" + uniformes)
    # STORY-267 AC12: Disable sector ceiling for custom_terms searches
    _skip_sector_ceiling = False
    if custom_terms:
        from config import get_feature_flag as _gff_ac12
        if _gff_ac12("TERM_SEARCH_FILTER_CONTEXT"):
            _skip_sector_ceiling = True

    if setor and not _skip_sector_ceiling:
        from sectors import get_sector

        try:
            setor_config = get_sector(setor)
            max_value = setor_config.max_contract_value

            if max_value is not None:
                resultado_valor_teto: List[dict] = []
                for lic in resultado_valor:
                    valor = lic.get("valorTotalEstimado") or lic.get("valorEstimado") or 0

                    if isinstance(valor, str):
                        try:
                            valor = float(valor.replace(".", "").replace(",", "."))
                        except ValueError:
                            valor = 0.0
                    else:
                        valor = float(valor) if valor else 0.0

                    if valor > max_value:
                        stats["rejeitadas_valor_alto"] += 1
                        logger.debug(
                            f"  Rejeitada por Camada 1A (valor > R$ {max_value:,.2f}): "
                            f"valor=R$ {valor:,.2f} setor={setor} "
                            f"objeto={lic.get('objetoCompra', '')[:80]}"
                        )
                        # STORY-248 AC9: Record value exceed
                        try:
                            _get_tracker().record_rejection(
                                "value_exceed",
                                sector=setor,
                                description_preview=lic.get("objetoCompra", "")[:100],
                            )
                        except Exception:
                            pass
                        continue

                    resultado_valor_teto.append(lic)

                logger.debug(
                    f"  Após Camada 1A (Value Threshold): {len(resultado_valor_teto)} "
                    f"(rejeitadas_valor_alto: {stats['rejeitadas_valor_alto']})"
                )
                resultado_valor = resultado_valor_teto
        except KeyError:
            logger.warning(f"Setor '{setor}' não encontrado - pulando Camada 1A")

    # Etapa 8: Filtro de Keywords (mais lento - regex)
    # AC9.1: Pre-compile regex patterns once for the batch
    kw = keywords if keywords is not None else KEYWORDS_UNIFORMES
    exc = exclusions if exclusions is not None else KEYWORDS_EXCLUSAO

    compiled_patterns: Dict[str, re.Pattern] = {}
    for keyword in kw:
        try:
            escaped = re.escape(keyword)
            compiled_patterns[keyword] = re.compile(
                rf'\b{escaped}\b', re.IGNORECASE | re.UNICODE
            )
        except re.error:
            logger.warning(f"Failed to compile regex for keyword: {keyword}")

    # STORY-328 AC7-AC8: Compute effective global exclusions for this sector
    _effective_global_exc: Set[str] = set()
    if setor:
        _sector_overrides = GLOBAL_EXCLUSION_OVERRIDES.get(setor, set())
        _effective_global_exc = GLOBAL_EXCLUSIONS_NORMALIZED - _sector_overrides

    # STORY-329 AC1: Progress tracking for keyword matching loop
    _kw_total = len(resultado_valor)
    _kw_progress_step = min(50, max(1, int(_kw_total * 0.05))) if on_progress and _kw_total > 0 else 0

    resultado_keyword: List[dict] = []
    for _kw_idx, lic in enumerate(resultado_valor):
        # STORY-329 AC1: Emit progress every N items
        if _kw_progress_step > 0 and (_kw_idx + 1) % _kw_progress_step == 0:
            on_progress(_kw_idx + 1, _kw_total, "filter")

        objeto = lic.get("objetoCompra", "")

        # STORY-328 AC1/AC5: Strip org context BEFORE keyword matching
        objeto_for_matching = _strip_org_context(objeto)

        # STORY-328 AC23-AC24: Track stripping for metrics/logging
        if objeto_for_matching != objeto.strip():
            lic["_org_context_stripped"] = True
            removed_clause = objeto[len(objeto_for_matching):].strip() if len(objeto_for_matching) < len(objeto) else ""
            logger.debug(
                f"STORY-328: Stripped org context from bid "
                f"{lic.get('pncpId', lic.get('id', '?'))}: "
                f"'{removed_clause[:120]}'"
            )
            try:
                from metrics import ORG_CONTEXT_STRIPPED
                ORG_CONTEXT_STRIPPED.labels(sector=setor or "unknown").inc()
            except Exception:
                pass
        else:
            lic["_org_context_stripped"] = False

        # STORY-328 AC7-AC8: Check global exclusions before keyword matching
        if _effective_global_exc:
            objeto_norm_ge = normalize_text(objeto_for_matching)
            _hit_global_exc = False
            for ge in _effective_global_exc:
                if ge in objeto_norm_ge:
                    _hit_global_exc = True
                    logger.debug(
                        f"STORY-328: Global exclusion hit '{ge}' in "
                        f"objeto={objeto[:80]}"
                    )
                    break
            if _hit_global_exc:
                stats["rejeitadas_keyword"] = stats.get("rejeitadas_keyword", 0) + 1
                try:
                    _get_tracker().record_rejection(
                        "global_exclusion",
                        sector=setor,
                        description_preview=objeto[:100],
                    )
                except Exception:
                    pass
                continue

        # STORY-328 AC6: Cross-validate with nomeOrgao
        nome_orgao = lic.get("nomeOrgao", "") or lic.get("orgaoEntidade", {}).get("razaoSocial", "") or ""
        nome_orgao_norm = normalize_text(nome_orgao) if nome_orgao else ""

        match, matched_terms = match_keywords(
            objeto_for_matching, kw, exc, context_required,
            compiled_patterns=compiled_patterns,
        )

        # AC6: Discount keywords that appear ONLY in the org name (not in stripped object)
        if match and nome_orgao_norm and matched_terms:
            objeto_stripped_norm = normalize_text(objeto_for_matching)
            real_terms = []
            for term in matched_terms:
                term_norm = normalize_text(term)
                if term_norm in objeto_stripped_norm:
                    real_terms.append(term)
                elif term_norm in nome_orgao_norm:
                    logger.debug(
                        f"STORY-328 AC6: Discounting keyword '{term}' — "
                        f"found in orgName but not in stripped objeto"
                    )
            if real_terms:
                matched_terms = real_terms
            else:
                match = False

        if match:
            # Store matched terms on the bid for later scoring
            lic["_matched_terms"] = matched_terms

            # STORY-179 AC2.1: Calculate term density ratio
            # Count how many times matched terms appear in the text
            # STORY-328: Use stripped text for density calculation
            objeto_norm = normalize_text(objeto_for_matching)
            total_words = len(objeto_norm.split())
            term_count = 0
            for term in matched_terms:
                term_norm = normalize_text(term)
                # Count exact occurrences of this term in the text
                term_count += objeto_norm.count(term_norm)

            term_density = term_count / total_words if total_words > 0 else 0
            lic["_term_density"] = term_density

            resultado_keyword.append(lic)
        else:
            stats["rejeitadas_keyword"] += 1
            # STORY-248 AC9: Record keyword miss
            try:
                _get_tracker().record_rejection(
                    "keyword_miss",
                    sector=setor,
                    description_preview=objeto[:100],
                )
            except Exception:
                pass

    # ========================================================================
    # SECTOR-PROX: Camada 1B.3 — Proximity Context Filter
    # ========================================================================
    # After keyword match, before co-occurrence. Rejects bids where a matched
    # keyword appears near signature terms of ANOTHER sector (cross-sector FP).
    # 100% deterministic, zero LLM cost.
    from config import get_feature_flag, PROXIMITY_WINDOW_SIZE

    stats["proximity_rejections"] = 0

    # STORY-267 AC13: Disable proximity filter for custom_terms searches
    _skip_proximity = bool(custom_terms) and get_feature_flag("TERM_SEARCH_FILTER_CONTEXT")
    if get_feature_flag("PROXIMITY_CONTEXT_ENABLED") and setor and not _skip_proximity:
        from sectors import SECTORS as _SECTORS_PROX

        # Build other_sectors_signatures: all sectors except current
        other_sigs: Dict[str, set] = {}
        for sid, scfg in _SECTORS_PROX.items():
            if sid != setor and scfg.signature_terms:
                other_sigs[sid] = scfg.signature_terms

        if other_sigs:
            resultado_after_prox: List[dict] = []
            for lic in resultado_keyword:
                matched = lic.get("_matched_terms", [])
                if not matched:
                    resultado_after_prox.append(lic)
                    continue

                objeto = lic.get("objetoCompra", "")
                should_reject, rejection_detail = check_proximity_context(
                    objeto, matched, setor, other_sigs, PROXIMITY_WINDOW_SIZE
                )

                if should_reject:
                    stats["proximity_rejections"] += 1
                    lic["_rejection_reason"] = "proximity_context"
                    lic["_rejection_detail"] = rejection_detail
                    logger.debug(
                        f"Camada 1B.3: REJECT (proximity) "
                        f"detail={rejection_detail} "
                        f"objeto={objeto[:80]}"
                    )
                    try:
                        _get_tracker().record_rejection(
                            "proximity_context",
                            sector=setor,
                            description_preview=objeto[:100],
                        )
                    except Exception:
                        pass
                else:
                    resultado_after_prox.append(lic)

            if stats["proximity_rejections"] > 0:
                logger.info(
                    f"Camada 1B.3 (Proximity): rejected "
                    f"{stats['proximity_rejections']} bids in sector '{setor}'"
                )
            resultado_keyword = resultado_after_prox

    # ========================================================================
    # GTM-RESILIENCE-D03: Camada 1B.5 — Co-occurrence Negative Patterns
    # ========================================================================
    # After keyword match, before density zone. Rejects bids where a trigger
    # keyword co-occurs with a negative context and no positive signal.
    # Overrides auto-accept: even density >5% bids are rejected.
    # 100% deterministic, zero LLM cost.

    stats["co_occurrence_rejections"] = 0
    stats["co_occurrence_rejections_by_sector"] = {}

    # STORY-267 AC13: Disable co-occurrence rules for custom_terms searches
    _skip_co_occurrence = bool(custom_terms) and get_feature_flag("TERM_SEARCH_FILTER_CONTEXT")
    if get_feature_flag("CO_OCCURRENCE_RULES_ENABLED") and setor and not _skip_co_occurrence:
        from sectors import get_sector as _get_sector_co

        try:
            setor_config_co = _get_sector_co(setor)
            co_rules = setor_config_co.co_occurrence_rules

            if co_rules:
                resultado_after_co: List[dict] = []
                for lic in resultado_keyword:
                    objeto = lic.get("objetoCompra", "")
                    should_reject, rejection_detail = check_co_occurrence(
                        objeto, co_rules, setor
                    )

                    if should_reject:
                        stats["co_occurrence_rejections"] += 1
                        stats["co_occurrence_rejections_by_sector"][setor] = (
                            stats["co_occurrence_rejections_by_sector"].get(setor, 0) + 1
                        )
                        lic["_rejection_reason"] = "co_occurrence"
                        lic["_rejection_detail"] = rejection_detail
                        logger.debug(
                            f"Camada 1B.5: REJECT (co-occurrence) "
                            f"detail={rejection_detail} "
                            f"objeto={objeto[:80]}"
                        )
                        # AC4: Record in filter stats tracker
                        try:
                            _get_tracker().record_rejection(
                                "co_occurrence",
                                sector=setor,
                                description_preview=objeto[:100],
                            )
                        except Exception:
                            pass
                    else:
                        resultado_after_co.append(lic)

                if stats["co_occurrence_rejections"] > 0:
                    logger.info(
                        f"Camada 1B.5 (Co-occurrence): rejected "
                        f"{stats['co_occurrence_rejections']} bids in sector '{setor}'"
                    )
                resultado_keyword = resultado_after_co
        except KeyError:
            pass  # Sector not found — skip co-occurrence

    # ========================================================================
    # GTM-FIX-028: LLM Zero Match Classification
    # ========================================================================
    # Instead of auto-rejecting bids with 0 keyword matches, collect them
    # and send to LLM for sector-aware classification.
    from config import LLM_ZERO_MATCH_ENABLED

    resultado_llm_zero: List[dict] = []
    resultado_pending_review: List[dict] = []  # STORY-354 AC1: bids awaiting reclassification
    stats["llm_zero_match_calls"] = 0
    stats["llm_zero_match_aprovadas"] = 0
    stats["llm_zero_match_rejeitadas"] = 0
    stats["llm_zero_match_skipped_short"] = 0
    stats["pending_review_count"] = 0  # STORY-354 AC2

    # STORY-267 AC2: When custom_terms present + TERM_SEARCH_LLM_AWARE, use term-aware prompt
    _use_term_prompt_zm = False
    if custom_terms:
        from config import get_feature_flag as _gff_ac2
        _use_term_prompt_zm = _gff_ac2("TERM_SEARCH_LLM_AWARE")

    if LLM_ZERO_MATCH_ENABLED and setor:
        # Collect bids that were rejected by keyword gate (in resultado_valor but not in resultado_keyword)
        keyword_approved_ids = {id(lic) for lic in resultado_keyword}
        zero_match_pool: List[dict] = []
        for lic in resultado_valor:
            if id(lic) not in keyword_approved_ids:
                objeto = lic.get("objetoCompra", "")
                # AC3: Skip bids with objeto < 20 chars (PCP short resumo, insufficient signal)
                if len(objeto) < 20:
                    stats["llm_zero_match_skipped_short"] += 1
                    logger.debug(
                        f"LLM zero_match: SKIP (objeto < 20 chars) objeto={objeto!r}"
                    )
                    continue
                zero_match_pool.append(lic)

        # ====================================================================
        # CRIT-058: Cap + prioritize zero-match pool (sampling inteligente)
        # ====================================================================
        # Applies BEFORE the LLM loop (CRIT-057 budget guard applies DURING).
        from config import MAX_ZERO_MATCH_ITEMS, ZERO_MATCH_VALUE_RATIO
        from metrics import ZERO_MATCH_CAP_APPLIED_TOTAL, ZERO_MATCH_POOL_SIZE

        stats["zero_match_capped"] = False
        stats["zero_match_cap_value"] = MAX_ZERO_MATCH_ITEMS

        if zero_match_pool:
            ZERO_MATCH_POOL_SIZE.observe(len(zero_match_pool))

        if len(zero_match_pool) > MAX_ZERO_MATCH_ITEMS:
            import random as _random_058
            from middleware import search_id_var as _sid_var_058
            _sid_058 = _sid_var_058.get(None)
            _rng = _random_058.Random(hash(_sid_058) if _sid_058 else 42)

            # AC2: Sort by value descending (None/0/"" go to end)
            def _get_valor_for_sort(lic_item: dict) -> float:
                val = lic_item.get("valorTotalEstimado") or lic_item.get("valorEstimado") or 0
                if isinstance(val, str):
                    try:
                        return float(val.replace(".", "").replace(",", "."))
                    except ValueError:
                        return 0.0
                return float(val) if val else 0.0

            zero_match_pool.sort(key=_get_valor_for_sort, reverse=True)

            # AC3: Split — top by value + random sample from remainder
            n_value = int(MAX_ZERO_MATCH_ITEMS * ZERO_MATCH_VALUE_RATIO)
            n_random = MAX_ZERO_MATCH_ITEMS - n_value

            top_value = zero_match_pool[:n_value]
            remainder = zero_match_pool[n_value:]
            random_sample = _rng.sample(remainder, min(n_random, len(remainder)))

            to_classify = top_value + random_sample
            to_classify_ids = {id(x) for x in to_classify}

            # AC5: Mark deferred items as pending_review
            to_defer = [x for x in zero_match_pool if id(x) not in to_classify_ids]
            for lic_item in to_defer:
                lic_item["_relevance_source"] = "pending_review"
                lic_item["_pending_review"] = True
                lic_item["_pending_review_reason"] = "zero_match_cap_exceeded"
                lic_item["_term_density"] = 0.0
                lic_item["_matched_terms"] = []
                lic_item["_confidence_score"] = 0
                lic_item["_llm_evidence"] = []
                resultado_pending_review.append(lic_item)
                stats["pending_review_count"] += 1

            # AC4: Metrics
            stats["zero_match_capped"] = True
            ZERO_MATCH_CAP_APPLIED_TOTAL.inc()

            # AC6: Impact log with value bands
            classified_vals = [_get_valor_for_sort(x) for x in to_classify]
            deferred_vals = [_get_valor_for_sort(x) for x in to_defer]

            def _count_bands(vals: list) -> dict:
                bands = {">1M": 0, "100K-1M": 0, "10K-100K": 0, "<10K": 0}
                for v in vals:
                    if v > 1_000_000:
                        bands[">1M"] += 1
                    elif v > 100_000:
                        bands["100K-1M"] += 1
                    elif v > 10_000:
                        bands["10K-100K"] += 1
                    else:
                        bands["<10K"] += 1
                return bands

            logger.info(
                f"[CRIT-058] Zero-match pool capped: {len(to_classify)}/{len(zero_match_pool)} items "
                f"(cap={MAX_ZERO_MATCH_ITEMS}). "
                f"Value split: {n_value} by value + {len(random_sample)} random. "
                f"Classified bands={_count_bands(classified_vals)}, "
                f"Deferred bands={_count_bands(deferred_vals)}, "
                f"Classified total value={sum(classified_vals):,.0f}, "
                f"Deferred total value={sum(deferred_vals):,.0f}"
            )

            zero_match_pool = to_classify

        if zero_match_pool:
            # CRIT-059 AC1/AC11: When async zero-match is enabled, collect candidates
            # and return them in stats instead of calling LLM inline.
            from config import ASYNC_ZERO_MATCH_ENABLED
            if ASYNC_ZERO_MATCH_ENABLED:
                stats["zero_match_candidates"] = zero_match_pool
                stats["zero_match_candidates_count"] = len(zero_match_pool)
                logger.info(
                    f"[CRIT-059] Async zero-match: collected {len(zero_match_pool)} candidates "
                    f"for background job (inline LLM skipped)"
                )
                # Skip all inline LLM — candidates will be classified by ARQ job
                zero_match_pool = []

        if zero_match_pool:
            from llm_arbiter import classify_contract_primary_match as _classify_zm
            from llm_arbiter import _classify_zero_match_batch as _classify_batch
            from sectors import get_sector as _get_sector_zm
            from config import LLM_ZERO_MATCH_BATCH_ENABLED, LLM_ZERO_MATCH_BATCH_SIZE
            import time as _time_zm

            try:
                setor_config_zm = _get_sector_zm(setor)
                setor_name_zm = setor_config_zm.name
            except (KeyError, Exception):
                setor_name_zm = setor

            # UX-402: Helper to extract objeto/valor from a lic dict
            def _extract_item(lic_item: dict) -> dict:
                obj = lic_item.get("objetoCompra", "")
                obj = _strip_org_context(obj)
                val = lic_item.get("valorTotalEstimado") or lic_item.get("valorEstimado") or 0
                if isinstance(val, str):
                    try:
                        val = float(val.replace(".", "").replace(",", "."))
                    except ValueError:
                        val = 0.0
                else:
                    val = float(val) if val else 0.0
                return {"objeto": obj, "valor": val}

            # UX-402: Process a single LLM result and apply to lic_item
            def _apply_result(lic_item: dict, llm_result: dict) -> None:
                is_relevant = llm_result.get("is_primary", False) if isinstance(llm_result, dict) else llm_result
                if is_relevant:
                    stats["llm_zero_match_aprovadas"] += 1
                    if custom_terms:
                        from metrics import TERM_SEARCH_LLM_ACCEPTS
                        TERM_SEARCH_LLM_ACCEPTS.labels(zone="zero_match").inc()
                    lic_item["_relevance_source"] = "llm_zero_match"
                    lic_item["_term_density"] = 0.0
                    lic_item["_matched_terms"] = []
                    # D-02 AC4: Confidence capped at 70 for zero-match
                    if isinstance(llm_result, dict):
                        raw_conf = llm_result.get("confidence", 60)
                        lic_item["_confidence_score"] = min(raw_conf, 70)
                        lic_item["_llm_evidence"] = llm_result.get("evidence", [])
                    else:
                        lic_item["_confidence_score"] = 60
                        lic_item["_llm_evidence"] = []
                    resultado_llm_zero.append(lic_item)
                    logger.debug(
                        f"LLM zero_match: ACCEPT conf={lic_item.get('_confidence_score')} "
                        f"objeto={lic_item.get('objetoCompra', '')[:80]}"
                    )
                else:
                    _is_pending = isinstance(llm_result, dict) and llm_result.get("pending_review", False)
                    if _is_pending:
                        stats["pending_review_count"] += 1
                        lic_item["_relevance_source"] = "pending_review"
                        lic_item["_term_density"] = 0.0
                        lic_item["_matched_terms"] = []
                        lic_item["_confidence_score"] = 0
                        lic_item["_llm_evidence"] = []
                        lic_item["_pending_review"] = True
                        resultado_pending_review.append(lic_item)
                        logger.info(
                            f"LLM zero_match: PENDING_REVIEW (LLM unavailable) "
                            f"objeto={lic_item.get('objetoCompra', '')[:80]}"
                        )
                    else:
                        stats["llm_zero_match_rejeitadas"] += 1
                        if custom_terms:
                            from metrics import TERM_SEARCH_LLM_REJECTS
                            TERM_SEARCH_LLM_REJECTS.labels(zone="zero_match").inc()
                        if isinstance(llm_result, dict):
                            lic_item["_llm_rejection_reason"] = llm_result.get("rejection_reason", "")
                        logger.debug(
                            f"LLM zero_match: REJECT objeto={lic_item.get('objetoCompra', '')[:80]}"
                        )

            _llm_total = len(zero_match_pool)
            _batch_used = False
            # CRIT-057 AC1: Time budget for zero-match classification
            from config import FILTER_ZERO_MATCH_BUDGET_S
            stats["zero_match_budget_exceeded"] = 0
            _zm_budget_hit = False

            # UX-402 AC2/AC6: Try batch mode first, fallback to individual on failure
            if LLM_ZERO_MATCH_BATCH_ENABLED:
                try:
                    from metrics import LLM_ZERO_MATCH_BATCH_DURATION, LLM_ZERO_MATCH_BATCH_SIZE as _BATCH_SIZE_METRIC
                    _batch_start = _time_zm.time()

                    # Split into batches of LLM_ZERO_MATCH_BATCH_SIZE
                    batch_items = [_extract_item(lic) for lic in zero_match_pool]
                    batches = [
                        batch_items[i:i + LLM_ZERO_MATCH_BATCH_SIZE]
                        for i in range(0, len(batch_items), LLM_ZERO_MATCH_BATCH_SIZE)
                    ]
                    batch_lic_groups = [
                        zero_match_pool[i:i + LLM_ZERO_MATCH_BATCH_SIZE]
                        for i in range(0, len(zero_match_pool), LLM_ZERO_MATCH_BATCH_SIZE)
                    ]

                    # AC8: Observe batch sizes
                    for batch in batches:
                        _BATCH_SIZE_METRIC.observe(len(batch))

                    # Run batches in parallel via ThreadPoolExecutor
                    all_results: list[tuple[int, list[dict]]] = []
                    _completed_batch_indices: set = set()
                    with ThreadPoolExecutor(max_workers=3) as executor:
                        future_to_idx = {}
                        for idx, batch in enumerate(batches):
                            if _use_term_prompt_zm and custom_terms:
                                fut = executor.submit(
                                    _classify_batch,
                                    items=batch,
                                    setor_name=None,
                                    setor_id=None,
                                    termos_busca=custom_terms,
                                )
                            else:
                                fut = executor.submit(
                                    _classify_batch,
                                    items=batch,
                                    setor_name=setor_name_zm,
                                    setor_id=setor,
                                    termos_busca=None,
                                )
                            future_to_idx[fut] = idx

                        pending = set(future_to_idx.keys())
                        while pending:
                            # CRIT-057 AC1: Check time budget
                            _zm_elapsed = _time_zm.time() - _batch_start
                            if _zm_elapsed > FILTER_ZERO_MATCH_BUDGET_S:
                                _zm_budget_hit = True
                                for f in pending:
                                    f.cancel()
                                # Mark unclassified items as pending_review
                                for b_idx, b_group in enumerate(batch_lic_groups):
                                    if b_idx not in _completed_batch_indices:
                                        for lic_item in b_group:
                                            lic_item["_relevance_source"] = "pending_review"
                                            lic_item["_pending_review"] = True
                                            lic_item["_pending_review_reason"] = "zero_match_budget_exceeded"
                                            lic_item["_term_density"] = 0.0
                                            lic_item["_matched_terms"] = []
                                            lic_item["_confidence_score"] = 0
                                            lic_item["_llm_evidence"] = []
                                            resultado_pending_review.append(lic_item)
                                            stats["zero_match_budget_exceeded"] += 1
                                            stats["pending_review_count"] += 1
                                logger.warning(
                                    f"[CRIT-057] Zero-match budget exceeded after "
                                    f"{len(_completed_batch_indices)}/{len(batches)} batches "
                                    f"in {_zm_elapsed:.1f}s (budget={FILTER_ZERO_MATCH_BUDGET_S}s)"
                                )
                                break

                            # HARDEN-014 AC1: wait with per-future timeout
                            done, pending = wait(pending, timeout=20, return_when=FIRST_COMPLETED)

                            if not done:
                                # HARDEN-014 AC2: All pending futures exceeded timeout
                                from metrics import LLM_BATCH_TIMEOUT
                                for f in pending:
                                    f.cancel()
                                    LLM_BATCH_TIMEOUT.labels(phase="zero_match_batch").inc()
                                # HARDEN-014 AC3: Mark timed-out items as pending_review
                                for b_idx, b_group in enumerate(batch_lic_groups):
                                    if b_idx not in _completed_batch_indices:
                                        for lic_item in b_group:
                                            lic_item["_relevance_source"] = "pending_review"
                                            lic_item["_pending_review"] = True
                                            lic_item["_pending_review_reason"] = "llm_future_timeout"
                                            lic_item["_term_density"] = 0.0
                                            lic_item["_matched_terms"] = []
                                            lic_item["_confidence_score"] = 0
                                            lic_item["_llm_evidence"] = []
                                            resultado_pending_review.append(lic_item)
                                            stats["pending_review_count"] += 1
                                logger.warning(
                                    f"[HARDEN-014] Per-future timeout (20s) hit for "
                                    f"{len(pending)} batch futures, "
                                    f"{len(_completed_batch_indices)}/{len(batches)} completed"
                                )
                                break

                            for future in done:
                                idx = future_to_idx[future]
                                _completed_batch_indices.add(idx)
                                batch_results = future.result()
                                all_results.append((idx, batch_results))

                    # Sort by original batch index and apply results
                    all_results.sort(key=lambda x: x[0])
                    _llm_completed = 0
                    for idx, batch_results in all_results:
                        lic_group = batch_lic_groups[idx]
                        for lic_item, llm_result in zip(lic_group, batch_results):
                            _llm_completed += 1
                            stats["llm_zero_match_calls"] += 1
                            if on_progress:
                                on_progress(_llm_completed, _llm_total, "llm_classify")
                            _apply_result(lic_item, llm_result)

                    _batch_elapsed = _time_zm.time() - _batch_start
                    LLM_ZERO_MATCH_BATCH_DURATION.observe(_batch_elapsed)
                    # CRIT-057 AC3: Observe zero-match duration with budget label
                    try:
                        from metrics import FILTER_ZERO_MATCH_DURATION
                        FILTER_ZERO_MATCH_DURATION.labels(
                            mode="batch",
                            budget_exceeded=str(_zm_budget_hit).lower(),
                        ).observe(_batch_elapsed)
                    except Exception:
                        pass
                    _batch_used = True
                    logger.info(
                        f"UX-402: Batch mode completed {_llm_completed}/{_llm_total} items "
                        f"in {_batch_elapsed:.2f}s ({len(batches)} batches)"
                        + (f" [CRIT-057: budget hit, {stats['zero_match_budget_exceeded']} deferred]"
                           if _zm_budget_hit else "")
                    )

                except Exception as e:
                    logger.warning(
                        f"UX-402 AC2: Batch classification failed, falling back to individual: {e}"
                    )
                    # Reset counters for fallback path (batch partial results discarded)
                    stats["llm_zero_match_calls"] = 0
                    stats["llm_zero_match_aprovadas"] = 0
                    stats["llm_zero_match_rejeitadas"] = 0
                    stats["pending_review_count"] = 0
                    resultado_llm_zero.clear()
                    resultado_pending_review.clear()

            # AC2/AC6: Fallback to individual calls (or when batch disabled)
            if not _batch_used:
                def _classify_one(lic_item: dict) -> tuple[dict, dict]:
                    item = _extract_item(lic_item)
                    if _use_term_prompt_zm and custom_terms:
                        result = _classify_zm(
                            objeto=item["objeto"],
                            valor=item["valor"],
                            setor_name=None,
                            termos_busca=custom_terms,
                            prompt_level="zero_match",
                            setor_id=None,
                        )
                    else:
                        result = _classify_zm(
                            objeto=item["objeto"],
                            valor=item["valor"],
                            setor_name=setor_name_zm,
                            prompt_level="zero_match",
                            setor_id=setor,
                        )
                    return lic_item, result

                _llm_completed = 0
                _indiv_start = _time_zm.time()
                _indiv_classified_ids: set = set()
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {
                        executor.submit(_classify_one, lic): lic
                        for lic in zero_match_pool
                    }
                    pending = set(futures.keys())
                    while pending:
                        # CRIT-057 AC1: Check time budget
                        _zm_elapsed = _time_zm.time() - _indiv_start
                        if _zm_elapsed > FILTER_ZERO_MATCH_BUDGET_S:
                            _zm_budget_hit = True
                            for f in pending:
                                f.cancel()
                            for lic in zero_match_pool:
                                if id(lic) not in _indiv_classified_ids:
                                    lic["_relevance_source"] = "pending_review"
                                    lic["_pending_review"] = True
                                    lic["_pending_review_reason"] = "zero_match_budget_exceeded"
                                    lic["_term_density"] = 0.0
                                    lic["_matched_terms"] = []
                                    lic["_confidence_score"] = 0
                                    lic["_llm_evidence"] = []
                                    resultado_pending_review.append(lic)
                                    stats["zero_match_budget_exceeded"] += 1
                                    stats["pending_review_count"] += 1
                            logger.warning(
                                f"[CRIT-057] Zero-match budget exceeded after "
                                f"{_llm_completed}/{_llm_total} items "
                                f"in {_zm_elapsed:.1f}s (budget={FILTER_ZERO_MATCH_BUDGET_S}s)"
                            )
                            break

                        # HARDEN-014 AC1: wait with per-future timeout
                        done, pending = wait(pending, timeout=20, return_when=FIRST_COMPLETED)

                        if not done:
                            # HARDEN-014 AC2: All pending futures exceeded timeout
                            from metrics import LLM_BATCH_TIMEOUT
                            for f in pending:
                                f.cancel()
                                LLM_BATCH_TIMEOUT.labels(phase="zero_match_individual").inc()
                            # HARDEN-014 AC3: Mark timed-out items as pending_review
                            for lic in zero_match_pool:
                                if id(lic) not in _indiv_classified_ids:
                                    lic["_relevance_source"] = "pending_review"
                                    lic["_pending_review"] = True
                                    lic["_pending_review_reason"] = "llm_future_timeout"
                                    lic["_term_density"] = 0.0
                                    lic["_matched_terms"] = []
                                    lic["_confidence_score"] = 0
                                    lic["_llm_evidence"] = []
                                    resultado_pending_review.append(lic)
                                    stats["pending_review_count"] += 1
                            logger.warning(
                                f"[HARDEN-014] Per-future timeout (20s) hit for "
                                f"{len(pending)} individual futures, "
                                f"{_llm_completed}/{_llm_total} completed"
                            )
                            break

                        for future in done:
                            _llm_completed += 1
                            stats["llm_zero_match_calls"] += 1
                            _indiv_classified_ids.add(id(futures[future]))
                            if on_progress:
                                on_progress(_llm_completed, _llm_total, "llm_classify")
                            try:
                                lic_item, llm_result = future.result()
                                _apply_result(lic_item, llm_result)
                            except Exception as e:
                                from config import LLM_FALLBACK_PENDING_ENABLED
                                if LLM_FALLBACK_PENDING_ENABLED:
                                    stats["pending_review_count"] += 1
                                    lic_ref = futures[future]
                                    lic_ref["_relevance_source"] = "pending_review"
                                    lic_ref["_term_density"] = 0.0
                                    lic_ref["_matched_terms"] = []
                                    lic_ref["_confidence_score"] = 0
                                    lic_ref["_pending_review"] = True
                                    resultado_pending_review.append(lic_ref)
                                    logger.warning(f"LLM zero_match: FAILED → PENDING_REVIEW: {e}")
                                else:
                                    stats["llm_zero_match_rejeitadas"] += 1
                                    logger.error(f"LLM zero_match: FAILED (REJECT fallback): {e}")

                # CRIT-057 AC3: Observe zero-match duration (individual mode)
                _indiv_elapsed = _time_zm.time() - _indiv_start
                try:
                    from metrics import FILTER_ZERO_MATCH_DURATION
                    FILTER_ZERO_MATCH_DURATION.labels(
                        mode="individual",
                        budget_exceeded=str(_zm_budget_hit).lower(),
                    ).observe(_indiv_elapsed)
                except Exception:
                    pass

            logger.info(
                f"GTM-FIX-028 LLM Zero Match: "
                f"{stats['llm_zero_match_calls']} calls, "
                f"{stats['llm_zero_match_aprovadas']} approved, "
                f"{stats['llm_zero_match_rejeitadas']} rejected, "
                f"{stats['llm_zero_match_skipped_short']} skipped (short), "
                f"{stats['pending_review_count']} pending_review"
            )

    # ========================================================================
    # GTM-RESILIENCE-D01: Camada 1C — Item Inspection for Gray Zone (0-5%)
    # ========================================================================
    # Before sending gray-zone bids to LLM, attempt item-level inspection
    # from PNCP API. Majority rule on items can accept bids directly,
    # saving LLM calls and improving precision.
    from config import (
        TERM_DENSITY_HIGH_THRESHOLD,
        TERM_DENSITY_MEDIUM_THRESHOLD,
        TERM_DENSITY_LOW_THRESHOLD,
        QA_AUDIT_SAMPLE_RATE,
        get_feature_flag,
    )

    stats["item_inspections_performed"] = 0
    stats["item_inspections_accepted"] = 0

    resultado_item_accepted: List[dict] = []

    if setor and get_feature_flag("ITEM_INSPECTION_ENABLED"):
        # Collect gray zone bids: 0% < density <= 5% (have matched keywords but low density)
        gray_zone = [
            lic for lic in resultado_keyword
            if 0 < lic.get("_term_density", 0) <= TERM_DENSITY_HIGH_THRESHOLD
        ]

        if gray_zone:
            try:
                from item_inspector import inspect_bids_in_filter
                from sectors import get_sector as _get_sector_insp

                setor_config_insp = _get_sector_insp(setor)
                ds = setor_config_insp.domain_signals

                item_accepted, item_remaining, item_metrics = inspect_bids_in_filter(
                    gray_zone_bids=gray_zone,
                    sector_keywords={kw.lower() for kw in setor_config_insp.keywords},
                    ncm_prefixes=ds.ncm_prefixes,
                    unit_patterns=ds.unit_patterns,
                    size_patterns=ds.size_patterns,
                )

                stats["item_inspections_performed"] = item_metrics.get(
                    "item_inspections_performed", 0
                )
                stats["item_inspections_accepted"] = item_metrics.get(
                    "item_inspections_accepted", 0
                )

                # Accepted bids skip Camada 2A entirely (AC5: weight 3 > keyword weight 2)
                resultado_item_accepted = item_accepted

                # Replace gray zone in resultado_keyword with remaining (non-accepted)
                gray_zone_ids = {id(lic) for lic in gray_zone}
                remaining_ids = {id(lic) for lic in item_remaining}
                resultado_keyword = [
                    lic for lic in resultado_keyword
                    if id(lic) not in gray_zone_ids or id(lic) in remaining_ids
                ]

            except Exception as e:
                logger.warning(f"D-01 item inspection failed, continuing with LLM: {e}")

    # STORY-181 AC2: Camada 2A - Calibrated Term Density Decision Thresholds
    # Using configurable thresholds from config.py (env-var adjustable)

    resultado_densidade: List[dict] = []
    resultado_llm_standard: List[dict] = []  # density 2-5%: LLM standard prompt
    resultado_llm_conservative: List[dict] = []  # density 1-2%: LLM conservative prompt
    stats["rejeitadas_red_flags"] = 0
    stats["rejeitadas_red_flags_setorial"] = 0

    # CRIT-FLT-010: Check feature flag once per batch
    from config import get_feature_flag
    _sector_red_flags_enabled = get_feature_flag("SECTOR_RED_FLAGS_ENABLED")

    for lic in resultado_keyword:
        density = lic.get("_term_density", 0)
        # CRIT-004 AC11: Use search_id from ContextVar instead of independent trace_id
        from middleware import search_id_var
        _search_id = search_id_var.get("-")
        trace_id = _search_id[:8] if _search_id != "-" else str(uuid.uuid4())[:8]
        lic["_trace_id"] = trace_id
        objeto_preview = lic.get("objetoCompra", "")[:100]

        if density > TERM_DENSITY_HIGH_THRESHOLD:
            # High confidence (>5%) - dominant term, accept without LLM
            stats["aprovadas_alta_densidade"] += 1
            # GTM-FIX-028 AC8: Tag relevance source
            lic["_relevance_source"] = "keyword"
            # D-02 AC4: Keyword-accepted bids get confidence_score=95
            lic["_confidence_score"] = 95
            lic["_llm_evidence"] = []
            logger.debug(
                f"[{trace_id}] Camada 2A: ACCEPT (alta densidade) "
                f"density={density:.1%} objeto={objeto_preview}"
            )
            resultado_densidade.append(lic)
        elif density < TERM_DENSITY_LOW_THRESHOLD:
            # Low confidence (<1%) - peripheral term, reject
            stats["rejeitadas_baixa_densidade"] += 1
            logger.debug(
                f"[{trace_id}] Camada 2A: REJECT (baixa densidade) "
                f"density={density:.1%} objeto={objeto_preview}"
            )
            # STORY-248 AC9: Record density low rejection
            try:
                _get_tracker().record_rejection(
                    "density_low",
                    sector=setor,
                    description_preview=objeto_preview,
                )
            except Exception:
                pass
        elif density >= TERM_DENSITY_MEDIUM_THRESHOLD:
            # Medium-high zone (2-5%) - LLM with standard prompt
            objeto_norm = normalize_text(lic.get("objetoCompra", ""))

            # CRIT-FLT-010: Sector-specific red flags (threshold=1, before generic)
            if _sector_red_flags_enabled and setor:
                s_flagged, s_flags = has_sector_red_flags(objeto_norm, setor)
                if s_flagged:
                    stats["rejeitadas_red_flags_setorial"] += 1
                    logger.debug(
                        f"[{trace_id}] Camada 2A: REJECT (sector red flags: {s_flags}) "
                        f"density={density:.1%} objeto={objeto_preview}"
                    )
                    try:
                        _get_tracker().record_rejection(
                            "red_flags_sector",
                            sector=setor,
                            description_preview=objeto_preview,
                        )
                    except Exception:
                        pass
                    continue

            # STORY-181 AC6: Generic red flags (threshold=2)
            # CRIT-020: Pass setor to exempt infrastructure/medical sectors
            flagged, flag_terms = has_red_flags(
                objeto_norm,
                [RED_FLAGS_MEDICAL, RED_FLAGS_ADMINISTRATIVE, RED_FLAGS_INFRASTRUCTURE],
                setor=setor,
            )
            if flagged:
                stats["rejeitadas_red_flags"] += 1
                logger.debug(
                    f"[{trace_id}] Camada 2A: REJECT (red flags: {flag_terms}) "
                    f"density={density:.1%} objeto={objeto_preview}"
                )
                continue

            stats["duvidosas_llm_arbiter"] += 1
            lic["_llm_prompt_level"] = "standard"
            resultado_llm_standard.append(lic)
        else:
            # Low-medium zone (1-2%) - LLM with conservative prompt
            objeto_norm = normalize_text(lic.get("objetoCompra", ""))

            # CRIT-FLT-010: Sector-specific red flags (threshold=1, before generic)
            if _sector_red_flags_enabled and setor:
                s_flagged, s_flags = has_sector_red_flags(objeto_norm, setor)
                if s_flagged:
                    stats["rejeitadas_red_flags_setorial"] += 1
                    logger.debug(
                        f"[{trace_id}] Camada 2A: REJECT (sector red flags: {s_flags}) "
                        f"density={density:.1%} objeto={objeto_preview}"
                    )
                    try:
                        _get_tracker().record_rejection(
                            "red_flags_sector",
                            sector=setor,
                            description_preview=objeto_preview,
                        )
                    except Exception:
                        pass
                    continue

            # STORY-181 AC6: Generic red flags (threshold=2)
            # CRIT-020: Pass setor to exempt infrastructure/medical sectors
            flagged, flag_terms = has_red_flags(
                objeto_norm,
                [RED_FLAGS_MEDICAL, RED_FLAGS_ADMINISTRATIVE, RED_FLAGS_INFRASTRUCTURE],
                setor=setor,
            )
            if flagged:
                stats["rejeitadas_red_flags"] += 1
                logger.debug(
                    f"[{trace_id}] Camada 2A: REJECT (red flags: {flag_terms}) "
                    f"density={density:.1%} objeto={objeto_preview}"
                )
                continue

            stats["duvidosas_llm_arbiter"] += 1
            lic["_llm_prompt_level"] = "conservative"
            resultado_llm_conservative.append(lic)

    resultado_llm_candidates = resultado_llm_standard + resultado_llm_conservative

    logger.debug(
        f"  Após Camada 2A (Term Density): "
        f"{len(resultado_densidade)} aprovadas (alta densidade), "
        f"{len(resultado_llm_standard)} duvidosas (LLM standard), "
        f"{len(resultado_llm_conservative)} duvidosas (LLM conservative), "
        f"{stats.get('rejeitadas_red_flags', 0)} rejeitadas (red flags), "
        f"{stats.get('rejeitadas_red_flags_setorial', 0)} rejeitadas (sector red flags), "
        f"{stats['rejeitadas_baixa_densidade']} rejeitadas (baixa densidade)"
    )

    # STORY-179 AC3: Camada 3A - LLM Arbiter (GPT-4o-mini)
    # For contracts in the uncertain zone (1-5% density), use LLM to determine
    # if the contract is PRIMARILY about the sector/terms or just a tangential mention
    stats["aprovadas_llm_arbiter"] = 0
    stats["rejeitadas_llm_arbiter"] = 0
    stats["llm_arbiter_calls"] = 0

    # STORY-267 AC3: When custom_terms present + TERM_SEARCH_LLM_AWARE, use term-aware prompt
    _use_term_prompt_arbiter = False
    if custom_terms:
        from config import get_feature_flag as _gff_ac3
        _use_term_prompt_arbiter = _gff_ac3("TERM_SEARCH_LLM_AWARE")

    if resultado_llm_candidates:
        from llm_arbiter import classify_contract_primary_match

        # CRIT-FLT-002: Resolve sector name ONCE before dispatching threads
        _arbiter_setor_name = None
        if setor and not _use_term_prompt_arbiter:
            from sectors import get_sector
            try:
                _arbiter_setor_config = get_sector(setor)
                _arbiter_setor_name = _arbiter_setor_config.name
            except KeyError:
                logger.warning(f"Setor '{setor}' não encontrado para LLM arbiter")

        # CRIT-FLT-002 AC3: Thread-safe stats lock
        _arbiter_stats_lock = threading.Lock()

        def _classify_one_arbiter(lic_item):
            """Classify a single gray-zone bid via LLM arbiter (thread-safe)."""
            objeto = lic_item.get("objetoCompra", "")
            # STORY-328 AC14: Use stripped text for LLM classification
            objeto = _strip_org_context(objeto)
            valor = lic_item.get("valorTotalEstimado") or lic_item.get("valorEstimado") or 0
            prompt_level = lic_item.get("_llm_prompt_level", "standard")

            # Convert valor to float if needed
            if isinstance(valor, str):
                try:
                    valor = float(valor.replace(".", "").replace(",", "."))
                except ValueError:
                    valor = 0.0
            else:
                valor = float(valor) if valor else 0.0

            # STORY-267 AC3: Use term-aware prompt when custom_terms present
            if _use_term_prompt_arbiter and custom_terms:
                llm_result = classify_contract_primary_match(
                    objeto=objeto,
                    valor=valor,
                    setor_name=None,
                    termos_busca=custom_terms,
                    prompt_level=prompt_level,
                    setor_id=None,
                )
            else:
                termos = None
                if not _arbiter_setor_name:
                    termos = lic_item.get("_matched_terms", [])

                llm_result = classify_contract_primary_match(
                    objeto=objeto,
                    valor=valor,
                    setor_name=_arbiter_setor_name,
                    termos_busca=termos,
                    prompt_level=prompt_level,
                    setor_id=setor if _arbiter_setor_name else None,
                )
            return lic_item, llm_result, valor

        # CRIT-FLT-002 AC1+AC5: Parallel execution with timing
        t0_arbiter = time.monotonic()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(_classify_one_arbiter, lic): lic
                for lic in resultado_llm_candidates
            }
            pending = set(futures.keys())
            while pending:
                # HARDEN-014 AC1: wait with per-future timeout
                done, pending = wait(pending, timeout=20, return_when=FIRST_COMPLETED)

                if not done:
                    # HARDEN-014 AC2: All pending futures exceeded timeout — cancel and reject
                    from metrics import LLM_BATCH_TIMEOUT
                    for f in pending:
                        f.cancel()
                        LLM_BATCH_TIMEOUT.labels(phase="arbiter").inc()
                    with _arbiter_stats_lock:
                        stats["rejeitadas_llm_arbiter"] += len(pending)
                    logger.warning(
                        f"[HARDEN-014] Per-future timeout (20s) hit for "
                        f"{len(pending)} arbiter futures"
                    )
                    break

                for future in done:
                    with _arbiter_stats_lock:
                        stats["llm_arbiter_calls"] += 1
                    try:
                        lic, llm_result, valor = future.result()
                        trace_id = lic.get("_trace_id", "unknown")
                        prompt_level = lic.get("_llm_prompt_level", "standard")
                        objeto = lic.get("objetoCompra", "")
                        is_primary = llm_result.get("is_primary", False) if isinstance(llm_result, dict) else llm_result

                        if is_primary:
                            with _arbiter_stats_lock:
                                stats["aprovadas_llm_arbiter"] += 1
                            # GTM-FIX-028 AC8: Tag relevance source based on prompt level
                            lic["_relevance_source"] = f"llm_{prompt_level}"
                            # D-02 AC4: Confidence from LLM structured output
                            if isinstance(llm_result, dict):
                                lic["_confidence_score"] = llm_result.get("confidence", 70)
                                lic["_llm_evidence"] = llm_result.get("evidence", [])
                            else:
                                lic["_confidence_score"] = 70
                                lic["_llm_evidence"] = []
                            resultado_densidade.append(lic)
                            logger.debug(
                                f"[{trace_id}] Camada 3A: ACCEPT (LLM={prompt_level}) "
                                f"conf={lic.get('_confidence_score')} "
                                f"density={lic.get('_term_density', 0):.1%} "
                                f"objeto={objeto[:80]}"
                            )
                        else:
                            with _arbiter_stats_lock:
                                stats["rejeitadas_llm_arbiter"] += 1
                            # D-02 AC6: Store rejection reason for audit
                            if isinstance(llm_result, dict):
                                lic["_llm_rejection_reason"] = llm_result.get("rejection_reason", "")
                            logger.debug(
                                f"[{trace_id}] Camada 3A: REJECT (LLM={prompt_level}) "
                                f"density={lic.get('_term_density', 0):.1%} "
                                f"valor=R$ {valor:,.2f} objeto={objeto[:80]}"
                            )
                            # STORY-248 AC9: Record LLM rejection
                            try:
                                _get_tracker().record_rejection(
                                    "llm_reject",
                                    sector=setor,
                                    description_preview=objeto[:100],
                                )
                            except Exception:
                                pass

                        # STORY-181 AC7: QA Audit sampling (AC2: preserved in parallel)
                        # D-02 AC6: Now includes evidence and confidence in audit log
                        if random.random() < QA_AUDIT_SAMPLE_RATE:
                            lic["_qa_audit"] = True
                            lic["_qa_audit_decision"] = {
                                "trace_id": trace_id,
                                "llm_response": "SIM" if is_primary else "NAO",
                                "prompt_level": prompt_level,
                                "density": lic.get("_term_density", 0),
                                "matched_terms": lic.get("_matched_terms", []),
                                "valor": valor,
                                "confidence": llm_result.get("confidence") if isinstance(llm_result, dict) else None,
                                "evidence": llm_result.get("evidence") if isinstance(llm_result, dict) else None,
                                "rejection_reason": llm_result.get("rejection_reason") if isinstance(llm_result, dict) else None,
                            }

                    except Exception as e:
                        # AC4: Fallback on LLM failure = REJECT (zero-noise philosophy)
                        with _arbiter_stats_lock:
                            stats["rejeitadas_llm_arbiter"] += 1
                        logger.error(f"Camada 3A: LLM FAILED (REJECT fallback): {e}")

        elapsed_arbiter = time.monotonic() - t0_arbiter
        logger.info(
            f"Camada 3A resultado: "
            f"{stats['aprovadas_llm_arbiter']} aprovadas, "
            f"{stats['rejeitadas_llm_arbiter']} rejeitadas, "
            f"{stats['llm_arbiter_calls']} chamadas LLM, "
            f"elapsed={elapsed_arbiter:.2f}s (parallel, {len(resultado_llm_candidates)} bids)"
        )

    resultado_keyword = resultado_densidade

    # GTM-FIX-028: Merge LLM zero-match approved bids into the keyword results
    if resultado_llm_zero:
        resultado_keyword.extend(resultado_llm_zero)
        logger.info(
            f"GTM-FIX-028: Merged {len(resultado_llm_zero)} LLM zero-match bids "
            f"into resultado_keyword (total now: {len(resultado_keyword)})"
        )

    # STORY-354 AC1: Merge PENDING_REVIEW bids into results (not hidden from user)
    if resultado_pending_review:
        resultado_keyword.extend(resultado_pending_review)
        logger.info(
            f"STORY-354: Merged {len(resultado_pending_review)} PENDING_REVIEW bids "
            f"into resultado_keyword (total now: {len(resultado_keyword)})"
        )

    # GTM-RESILIENCE-D01: Merge item-inspection accepted bids (AC5: highest weight)
    if resultado_item_accepted:
        resultado_keyword.extend(resultado_item_accepted)
        logger.info(
            f"D-01: Merged {len(resultado_item_accepted)} item-inspection bids "
            f"into resultado_keyword (total now: {len(resultado_keyword)})"
        )

    # Etapa 8b: Minimum Match Floor (STORY-178 AC2.2)
    # When min_match_floor is provided, apply additional filtering
    if min_match_floor is not None and min_match_floor > 1:
        from relevance import should_include, count_phrase_matches

        resultado_min_match: List[dict] = []
        for lic in resultado_keyword:
            matched_terms = lic.get("_matched_terms", [])
            matched_count = len(matched_terms)
            has_phrase = count_phrase_matches(matched_terms) > 0

            if should_include(matched_count, len(kw), has_phrase):
                resultado_min_match.append(lic)
            else:
                stats["rejeitadas_min_match"] += 1

        resultado_keyword = resultado_min_match

    logger.debug(
        f"  Após filtro Keywords: {len(resultado_keyword)} "
        f"(rejeitadas_keyword: {stats['rejeitadas_keyword']}, "
        f"rejeitadas_min_match: {stats['rejeitadas_min_match']})"
    )

    # Etapa 9: Filtro de Prazo (safety net for "recebendo_proposta")
    # When the user explicitly filters by status="recebendo_proposta", apply a
    # HARD deadline check using dataEncerramentoProposta. If the encerramento
    # date is in the past, the bid is NOT open regardless of what _status_inferido
    # says. This catches edge cases where status inference is wrong.
    #
    # CREDIBILITY FIX (2026-02-09): Tightened all heuristics significantly.
    # Showing closed bids as "open" destroys user trust. It's better to miss
    # a few legitimate open bids than to show clearly closed ones.
    #
    # Policy: If we can't PROVE a bid is open, don't show it as open.
    # - Has future dataEncerramentoProposta → KEEP (proven open)
    # - Has past dataEncerramentoProposta → REJECT (proven closed)
    # - No deadline, abertura <= 15 days → KEEP (very likely still open)
    # - No deadline, abertura 16-30 days → KEEP only if situação says "recebendo"
    # - No deadline, abertura > 30 days → REJECT (probably closed)
    # - No deadline, no abertura, publication <= 15 days → KEEP (very recent)
    # - No deadline, no abertura, publication > 15 days → REJECT
    # - No dates at all → REJECT (cannot prove it's open)
    if status and status.lower() == "recebendo_proposta":
        aprovadas: List[dict] = []
        agora = datetime.now(timezone.utc)

        for lic in resultado_keyword:
            data_enc_str = lic.get("dataEncerramentoProposta")

            # Case 1: dataEncerramentoProposta exists — HARD deadline check
            if data_enc_str:
                try:
                    data_enc = datetime.fromisoformat(
                        data_enc_str.replace("Z", "+00:00")
                    )
                    # GTM-FIX-031: Ensure both datetimes are tz-aware
                    if data_enc.tzinfo is None:
                        data_enc = data_enc.replace(tzinfo=timezone.utc)
                    if data_enc < agora:
                        stats["rejeitadas_prazo"] += 1
                        logger.debug(
                            f"  Rejeitada por prazo: encerramento={data_enc.date()} "
                            f"objeto={lic.get('objetoCompra', '')[:80]}"
                        )
                        continue
                except (ValueError, AttributeError):
                    logger.warning(
                        f"Data de encerramento invalida no safety net: '{data_enc_str}'"
                    )
                aprovadas.append(lic)
                continue

            # Case 2: No dataEncerramentoProposta — strict heuristics
            # Without a deadline, we cannot be CERTAIN the bid is open.
            data_ab_str = lic.get("dataAberturaProposta")
            if data_ab_str:
                try:
                    data_ab = datetime.fromisoformat(
                        data_ab_str.replace("Z", "+00:00")
                    )
                    # GTM-FIX-031: Ensure tz-aware for safe comparison
                    if data_ab.tzinfo is None:
                        data_ab = data_ab.replace(tzinfo=timezone.utc)
                    dias_desde_abertura = (agora - data_ab).days

                    if dias_desde_abertura <= 15:
                        # Very recent opening — likely still open
                        aprovadas.append(lic)
                        continue
                    elif dias_desde_abertura <= 30:
                        # Recent but not brand new — only keep if situação
                        # explicitly says "recebendo" (actively receiving)
                        situacao = (
                            lic.get("situacaoCompraNome", "")
                            or lic.get("situacao", "")
                            or ""
                        ).lower()
                        if "recebendo" in situacao:
                            aprovadas.append(lic)
                            continue
                        else:
                            stats["rejeitadas_prazo"] += 1
                            logger.debug(
                                f"  Rejeitada por heurística (abertura 16-30d sem 'recebendo'): "
                                f"abertura={data_ab.date()} ({dias_desde_abertura}d) "
                                f"situação='{situacao}' "
                                f"objeto={lic.get('objetoCompra', '')[:80]}"
                            )
                            continue
                    else:
                        # > 30 days old without deadline — almost certainly closed
                        stats["rejeitadas_prazo"] += 1
                        logger.debug(
                            f"  Rejeitada por heurística (abertura antiga): "
                            f"abertura={data_ab.date()} ({dias_desde_abertura}d atrás) "
                            f"objeto={lic.get('objetoCompra', '')[:80]}"
                        )
                        continue
                except (ValueError, AttributeError):
                    pass

            # Case 3: No deadline, no opening date — check publication
            data_pub_str = lic.get("dataPublicacaoPncp") or lic.get("dataPublicacao")
            if data_pub_str:
                try:
                    data_pub = datetime.fromisoformat(
                        data_pub_str.replace("Z", "+00:00")
                    )
                    # GTM-FIX-031: Ensure tz-aware for safe comparison
                    if data_pub.tzinfo is None:
                        data_pub = data_pub.replace(tzinfo=timezone.utc)
                    dias_desde_pub = (agora - data_pub).days
                    if dias_desde_pub <= 15:
                        # Very recently published, no other dates — give benefit of doubt
                        aprovadas.append(lic)
                        continue
                    else:
                        stats["rejeitadas_prazo"] += 1
                        logger.debug(
                            f"  Rejeitada por heurística (publicação sem datas): "
                            f"publicação={data_pub.date()} ({dias_desde_pub}d atrás) "
                            f"objeto={lic.get('objetoCompra', '')[:80]}"
                        )
                        continue
                except (ValueError, AttributeError):
                    pass

            # Case 4: No dates at all — REJECT
            # Cannot prove this bid is open without any date information
            stats["rejeitadas_prazo"] += 1
            logger.debug(
                f"  Rejeitada por falta de datas: "
                f"objeto={lic.get('objetoCompra', '')[:80]}"
            )

        logger.debug(
            f"  Após filtro Prazo (safety net + heurísticas): {len(aprovadas)} "
            f"(rejeitadas: {stats['rejeitadas_prazo']})"
        )
    else:
        aprovadas = resultado_keyword

    # ========================================================================
    # STORY-179 FLUXO 2: Anti-False Negative Recovery Pipeline
    # ========================================================================
    # Recover contracts that were incorrectly rejected by keyword filters.
    # This happens when:
    # 1. Exclusion keywords reject legitimate contracts (Camada 1B)
    # 2. Synonym near-misses not covered by keyword set (Camada 2B)
    # 3. LLM recovery for ambiguous rejections (Camada 3B)
    # 4. Zero results relaxation (Camada 4)

    # Initialize FLUXO 2 stats
    stats["recuperadas_exclusion_recovery"] = 0
    stats["aprovadas_synonym_match"] = 0
    stats["synonyms_auto_approved"] = 0  # CRIT-FLT-006 AC3
    stats["recuperadas_llm_fn"] = 0
    stats["recuperadas_zero_results"] = 0
    stats["llm_arbiter_calls_fn_flow"] = 0
    stats["zero_results_relaxation_triggered"] = False

    # GTM-FIX-028 AC10: When LLM zero-match is enabled, skip FLUXO 2 to avoid
    # double-classification (zero-match bids already went through LLM)
    _skip_fluxo_2 = LLM_ZERO_MATCH_ENABLED and stats.get("llm_zero_match_calls", 0) > 0
    if _skip_fluxo_2:
        logger.info(
            "GTM-FIX-028 AC10: FLUXO 2 DISABLED — LLM zero-match already classified "
            f"{stats['llm_zero_match_calls']} bids"
        )

    # STORY-267 AC4+AC7: Term-aware recovery for custom_terms searches
    _use_term_prompt_recovery = False
    _use_term_synonyms = False
    if custom_terms:
        from config import get_feature_flag as _gff_ac4
        _use_term_prompt_recovery = _gff_ac4("TERM_SEARCH_LLM_AWARE")
        _use_term_synonyms = _gff_ac4("TERM_SEARCH_SYNONYMS")

    # Run recovery when we have a sector OR when we have custom_terms with term synonyms enabled
    _run_fluxo_2 = (setor or (_use_term_synonyms and custom_terms)) and not _skip_fluxo_2
    if _run_fluxo_2:
        from synonyms import find_synonym_matches, should_auto_approve_by_synonyms
        if _use_term_synonyms and custom_terms:
            from synonyms import find_term_synonym_matches
        from sectors import get_sector as _get_sector

        try:
            setor_config = _get_sector(setor) if setor else None
            setor_keywords = setor_config.keywords if setor_config else set()
            setor_name = setor_config.name if setor_config else None

            # Collect IDs of already-approved contracts to avoid duplicates
            aprovadas_ids = {id(lic) for lic in aprovadas}

            # ------------------------------------------------------------------
            # Camada 1B + 2B: Re-scan contracts rejected at keyword stage
            # ------------------------------------------------------------------
            # We look at contracts that passed UF/status/value filters but were
            # rejected by keyword matching (they exist in resultado_valor but
            # not in resultado_keyword).
            rejeitadas_keyword_pool: List[dict] = []
            for lic in resultado_valor:
                if id(lic) not in aprovadas_ids:
                    rejeitadas_keyword_pool.append(lic)

            logger.debug(
                f"FLUXO 2 iniciando: {len(rejeitadas_keyword_pool)} contratos no pool de "
                f"recuperação (rejeitados após filtros rápidos)"
            )

            recuperadas: List[dict] = []
            llm_candidates_fn: List[dict] = []

            for lic in rejeitadas_keyword_pool:
                objeto = lic.get("objetoCompra", "")
                if not objeto:
                    continue

                # STORY-267 AC7: Use term synonym matching when custom_terms present
                if _use_term_synonyms and custom_terms:
                    synonym_matches = find_term_synonym_matches(
                        custom_terms=custom_terms,
                        objeto=objeto,
                    )
                elif setor:
                    # Camada 2B: Check synonym matches (original sector-based)
                    synonym_matches = find_synonym_matches(
                        objeto=objeto,
                        setor_keywords=setor_keywords,
                        setor_id=setor,
                    )
                else:
                    synonym_matches = []

                if not synonym_matches:
                    continue  # No synonyms found, skip

                # Check if auto-approve threshold is met (2+ synonyms)
                if _use_term_synonyms and custom_terms:
                    # For term searches, auto-approve with 2+ matches directly
                    should_approve_flag = len(synonym_matches) >= 2
                    matches = synonym_matches
                else:
                    should_approve_flag, matches = should_auto_approve_by_synonyms(
                        objeto=objeto,
                        setor_keywords=setor_keywords,
                        setor_id=setor,
                        min_synonyms=2,
                    )

                if should_approve_flag:
                    # High confidence: 2+ distinct synonym matches → auto-approve
                    stats["aprovadas_synonym_match"] += 1
                    stats["synonyms_auto_approved"] += 1  # CRIT-FLT-006 AC3
                    lic["_recovered_by"] = "synonym_auto_approve"
                    lic["_synonym_matches"] = [
                        f"{canon}≈{syn}" for canon, syn in matches
                    ]
                    recuperadas.append(lic)
                    # STORY-267 AC16: Track term search synonym recoveries
                    if custom_terms:
                        from metrics import TERM_SEARCH_SYNONYM_RECOVERIES
                        TERM_SEARCH_SYNONYM_RECOVERIES.inc()
                    logger.debug(
                        f"  Recuperada por sinônimos (auto): {matches} "
                        f"objeto={objeto[:80]}"
                    )
                else:
                    # 1 synonym match → ambiguous, send to LLM (Camada 3B)
                    lic["_near_miss_synonyms"] = synonym_matches
                    llm_candidates_fn.append(lic)

            # ------------------------------------------------------------------
            # Camada 3B: LLM Recovery for ambiguous synonym matches
            # ------------------------------------------------------------------
            if llm_candidates_fn:
                from llm_arbiter import classify_contract_recovery

                for lic in llm_candidates_fn:
                    objeto = lic.get("objetoCompra", "")
                    # STORY-328 AC14: Use stripped text for LLM classification
                    objeto = _strip_org_context(objeto)
                    valor = lic.get("valorTotalEstimado") or lic.get("valorEstimado") or 0
                    if isinstance(valor, str):
                        try:
                            valor = float(valor.replace(".", "").replace(",", "."))
                        except ValueError:
                            valor = 0.0
                    else:
                        valor = float(valor) if valor else 0.0

                    near_miss = lic.get("_near_miss_synonyms", [])
                    near_miss_info = ", ".join(
                        f"{canon}≈{syn}" for canon, syn in near_miss
                    )

                    stats["llm_arbiter_calls_fn_flow"] += 1
                    # STORY-267 AC4: Use term-aware recovery when custom_terms present
                    if _use_term_prompt_recovery and custom_terms:
                        should_recover = classify_contract_recovery(
                            objeto=objeto,
                            valor=valor,
                            rejection_reason="keyword_no_match + synonym_near_miss",
                            termos_busca=custom_terms,
                            near_miss_info=near_miss_info,
                        )
                    else:
                        should_recover = classify_contract_recovery(
                            objeto=objeto,
                            valor=valor,
                            rejection_reason="keyword_no_match + synonym_near_miss",
                            setor_name=setor_name,
                            near_miss_info=near_miss_info,
                        )

                    if should_recover:
                        stats["recuperadas_llm_fn"] += 1
                        lic["_recovered_by"] = "llm_recovery"
                        lic["_synonym_matches"] = [
                            f"{canon}≈{syn}" for canon, syn in near_miss
                        ]
                        recuperadas.append(lic)
                        logger.debug(
                            f"  Recuperada por LLM (FN flow): near_miss={near_miss_info} "
                            f"objeto={objeto[:80]}"
                        )

            # Add recovered contracts to approved list
            if recuperadas:
                aprovadas.extend(recuperadas)
                logger.info(
                    f"FLUXO 2: {len(recuperadas)} contratos recuperados "
                    f"(synonym_auto: {stats['aprovadas_synonym_match']}, "
                    f"llm_recovery: {stats['recuperadas_llm_fn']})"
                )

            # ------------------------------------------------------------------
            # Camada 4: Zero Results Relaxation
            # ------------------------------------------------------------------
            if len(aprovadas) == 0 and len(rejeitadas_keyword_pool) > 0:
                stats["zero_results_relaxation_triggered"] = True
                logger.info(
                    "FLUXO 2 Camada 4: Zero results detected, attempting relaxation"
                )

                # Relaxation: accept any contract with at least 1 synonym match
                for lic in rejeitadas_keyword_pool:
                    if id(lic) in {id(r) for r in recuperadas}:
                        continue  # Already recovered

                    objeto = lic.get("objetoCompra", "")
                    if not objeto:
                        continue

                    # STORY-267: Use term synonyms in relaxation when custom_terms present
                    if _use_term_synonyms and custom_terms:
                        synonym_matches = find_term_synonym_matches(
                            custom_terms=custom_terms,
                            objeto=objeto,
                        )
                    elif setor:
                        synonym_matches = find_synonym_matches(
                            objeto=objeto,
                            setor_keywords=setor_keywords,
                            setor_id=setor,
                        )
                    else:
                        synonym_matches = []

                    if synonym_matches:
                        stats["recuperadas_zero_results"] += 1
                        lic["_recovered_by"] = "zero_results_relaxation"
                        lic["_synonym_matches"] = [
                            f"{canon}≈{syn}" for canon, syn in synonym_matches
                        ]
                        aprovadas.append(lic)

                if stats["recuperadas_zero_results"] > 0:
                    logger.info(
                        f"Camada 4 relaxation: recovered {stats['recuperadas_zero_results']} "
                        f"contracts via single-synonym matching"
                    )

        except KeyError:
            logger.warning(f"Setor '{setor}' não encontrado - pulando FLUXO 2")
        except Exception as e:
            logger.error(f"FLUXO 2 recovery failed: {e}", exc_info=True)

    logger.debug(
        f"FLUXO 2 resultado: "
        f"synonym_auto={stats['aprovadas_synonym_match']}, "
        f"llm_recovery={stats['recuperadas_llm_fn']}, "
        f"zero_results={stats['recuperadas_zero_results']}, "
        f"llm_calls_fn={stats['llm_arbiter_calls_fn_flow']}"
    )
    # ========================================================================

    stats["aprovadas"] = len(aprovadas)

    logger.info(
        f"aplicar_todos_filtros: concluído - {stats['aprovadas']}/{stats['total']} aprovadas "
        f"(FLUXO 1: {stats.get('aprovadas_llm_arbiter', 0)} via LLM arbiter, "
        f"FLUXO 2: {stats.get('recuperadas_llm_fn', 0)} recuperadas)"
    )
    logger.debug(f"  Estatísticas completas: {stats}")

    return aprovadas, stats
