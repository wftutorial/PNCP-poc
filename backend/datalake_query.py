"""Query the PNCP data lake (pncp_raw_bids) instead of hitting the live API.

When DATALAKE_QUERY_ENABLED=true, the search pipeline calls query_datalake()
instead of PNCPClient. The returned records are in the SAME flat dict format
produced by PNCPClient._normalize_item(), so filter.py / llm.py / excel.py
work without any changes.

Full-text search uses PostgreSQL tsquery via the search_datalake RPC function.
Falls back to an empty list (fail-open) if Supabase is unreachable.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def query_datalake(
    *,
    ufs: list[str],
    data_inicial: str,
    data_final: str,
    modalidades: list[int] | None = None,
    keywords: list[str] | None = None,
    custom_terms: list[str] | None = None,
    valor_min: float | None = None,
    valor_max: float | None = None,
    esferas: list[str] | None = None,
    modo_busca: str = "publicacao",
    limit: int = 2000,
) -> list[dict]:
    """Query pncp_raw_bids via the search_datalake Supabase RPC.

    Returns records in the SAME flat dict format as PNCPClient._normalize_item()
    so downstream filter.py / llm.py / excel.py work unchanged.

    Args:
        ufs: List of UF codes, e.g. ["SC", "PR"]. Required.
        data_inicial: Start date, "YYYY-MM-DD".
        data_final: End date, "YYYY-MM-DD".
        modalidades: Modality codes to include (None = all).
        keywords: Sector keywords (OR-joined in tsquery).
        custom_terms: User-supplied terms (AND-joined on top of keywords).
        valor_min: Minimum estimated value (None = no lower bound).
        valor_max: Maximum estimated value (None = no upper bound).
        esferas: Esfera codes to include (None = all).
        modo_busca: "publicacao" or "abertura".
        limit: Max rows returned by the RPC.

    Returns:
        List of flat bid dicts compatible with _normalize_item() output.
        Returns [] on any error (fail-open).
    """
    try:
        from supabase_client import get_supabase
        sb = get_supabase()
    except Exception as e:
        logger.warning(f"[DatalakeQuery] Supabase unavailable: {e}")
        return []

    tsquery = _build_tsquery(keywords, custom_terms)

    rpc_params: dict[str, Any] = {
        "p_ufs": ufs,
        "p_date_start": data_inicial,
        "p_date_end": data_final,
        "p_tsquery": tsquery,
        "p_modalidades": modalidades,
        "p_valor_min": valor_min,
        "p_valor_max": valor_max,
        "p_esferas": esferas,
        "p_modo": modo_busca,
        "p_limit": limit,
    }

    logger.info(
        f"[DatalakeQuery] ufs={ufs}, dates={data_inicial}/{data_final}, "
        f"tsquery={tsquery!r}, limit={limit}"
    )

    try:
        result = sb.rpc("search_datalake", rpc_params).execute()
    except Exception as e:
        logger.error(f"[DatalakeQuery] RPC failed: {type(e).__name__}: {e}")
        return []

    rows = result.data or []
    normalized = [_row_to_normalized(row) for row in rows]

    logger.info(f"[DatalakeQuery] Returned {len(normalized)} records from local DB")
    return normalized


# ---------------------------------------------------------------------------
# tsquery construction
# ---------------------------------------------------------------------------


def _build_tsquery(
    keywords: list[str] | None,
    custom_terms: list[str] | None,
) -> str | None:
    """Build a PostgreSQL tsquery string from sector keywords and custom terms.

    Strategy:
    - Keywords are OR-joined (any keyword can match).
    - Custom terms are AND-joined on top of the keyword block.
    - Multi-word keywords are wrapped in a phrase query (<->).
    - Returns None when both inputs are empty/None (search_datalake RPC
      should treat None as "no full-text filter — return all rows").

    Examples:
        keywords=["construção", "obras"], custom_terms=None
          -> "construção | obras"

        keywords=["pavimentação"], custom_terms=["asfalto"]
          -> "(pavimentação) & asfalto"

        keywords=None, custom_terms=["creche", "escola"]
          -> "creche & escola"
    """
    parts: list[str] = []

    if keywords:
        cleaned = [_clean_token(k) for k in keywords if k and k.strip()]
        if cleaned:
            keyword_tokens = [_keyword_to_tstoken(k) for k in cleaned]
            parts.append(" | ".join(keyword_tokens))

    if custom_terms:
        cleaned = [_clean_token(t) for t in custom_terms if t and t.strip()]
        if cleaned:
            custom_tokens = [_keyword_to_tstoken(t) for t in cleaned]
            parts.extend(custom_tokens)

    if not parts:
        return None

    if len(parts) == 1:
        return parts[0]

    # keyword block AND each custom term
    keyword_block = parts[0]
    extra_terms = parts[1:]
    combined = f"({keyword_block})" + "".join(f" & {t}" for t in extra_terms)
    return combined


def _clean_token(token: str) -> str:
    """Strip whitespace and remove characters that break tsquery syntax."""
    token = token.strip()
    # Remove characters not valid in tsquery lexemes (keep letters, digits, hyphens)
    token = re.sub(r"[^\w\s\-]", "", token, flags=re.UNICODE)
    return token.strip()


def _keyword_to_tstoken(keyword: str) -> str:
    """Convert a keyword to a tsquery token.

    Single word -> plain lexeme.
    Multi-word  -> phrase query using <-> operator (e.g. "pré moldado" -> "pré<->moldado").
    """
    words = keyword.split()
    if len(words) == 1:
        return words[0]
    return "<->".join(words)


# ---------------------------------------------------------------------------
# Row → normalized dict
# ---------------------------------------------------------------------------


def _row_to_normalized(row: dict) -> dict:
    """Map a pncp_raw_bids DB row back to the flat dict produced by _normalize_item().

    The pncp_raw_bids table stores the original PNCP API payload in a `raw_data`
    JSONB column, plus extracted columns for fast querying.  We prefer the
    extracted columns (authoritative, indexed) and fall back to raw_data for
    fields that are not extracted.

    Column → flat key mapping (mirrors _normalize_item() output):

    DB column               | Flat key
    ----------------------- | ---------------------------
    numero_controle_pncp    | numeroControlePNCP + codigoCompra
    uf                      | uf
    municipio_nome          | municipio
    nome_orgao              | nomeOrgao
    objeto_compra           | objetoCompra
    valor_total_estimado    | valorTotalEstimado
    modalidade_id           | codigoModalidadeContratacao
    modalidade_nome         | modalidadeNome
    situacao_id             | situacaoCompraId
    data_publicacao         | dataPublicacaoFormatted (used by filter_status)
    data_abertura           | dataAberturaProposta
    link_sistema_origem     | linkSistemaOrigem
    esfera_id               | esferaId
    raw_data                | merged last (provides any remaining fields)
    """
    # Start with raw_data as base (provides all original PNCP fields)
    raw: dict = {}
    raw_data = row.get("raw_data")
    if isinstance(raw_data, dict):
        raw = dict(raw_data)

    # Override/set extracted columns (these are authoritative)
    numero_controle = row.get("numero_controle_pncp") or raw.get("numeroControlePNCP", "")
    if numero_controle:
        raw["numeroControlePNCP"] = numero_controle
        # _normalize_item() sets codigoCompra = numeroControlePNCP
        raw["codigoCompra"] = numero_controle

    uf = row.get("uf") or raw.get("uf", "")
    if uf:
        raw["uf"] = uf

    municipio = row.get("municipio_nome") or raw.get("municipio", "")
    if municipio:
        raw["municipio"] = municipio

    nome_orgao = row.get("nome_orgao") or raw.get("nomeOrgao", "")
    if nome_orgao:
        raw["nomeOrgao"] = nome_orgao

    objeto_compra = row.get("objeto_compra") or raw.get("objetoCompra", "")
    if objeto_compra:
        raw["objetoCompra"] = objeto_compra

    valor = row.get("valor_total_estimado")
    if valor is not None:
        try:
            raw["valorTotalEstimado"] = float(valor)
        except (TypeError, ValueError):
            pass

    modalidade_id = row.get("modalidade_id")
    if modalidade_id is not None:
        raw["codigoModalidadeContratacao"] = int(modalidade_id)

    modalidade_nome = row.get("modalidade_nome") or raw.get("modalidadeNome", "")
    if modalidade_nome:
        raw["modalidadeNome"] = modalidade_nome

    situacao_id = row.get("situacao_id")
    if situacao_id is not None:
        raw["situacaoCompraId"] = situacao_id

    data_publicacao = row.get("data_publicacao") or raw.get("dataPublicacaoFormatted")
    if data_publicacao:
        raw["dataPublicacaoFormatted"] = str(data_publicacao)

    data_abertura = row.get("data_abertura") or raw.get("dataAberturaProposta")
    if data_abertura:
        raw["dataAberturaProposta"] = str(data_abertura)

    link = row.get("link_sistema_origem") or raw.get("linkSistemaOrigem", "")
    if link:
        raw["linkSistemaOrigem"] = link

    esfera_id = row.get("esfera_id") or raw.get("esferaId")
    if esfera_id is not None:
        raw["esferaId"] = esfera_id

    # Tag as datalake source for observability (does not affect downstream logic)
    raw["_source"] = "datalake"

    return raw
