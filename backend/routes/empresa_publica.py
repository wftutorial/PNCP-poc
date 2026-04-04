"""P3 SEO: Public CNPJ B2G profile endpoint for /cnpj/[cnpj].

Aggregates BrasilAPI (company data) + Portal da Transparência (contracts)
+ datalake (open bids in detected sector) into a single public profile.

Public (no auth). Cache: InMemory 24h TTL.
"""

import logging
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sectors import SECTORS
from utils.cnae_mapping import map_cnae_to_setor, get_setor_name

logger = logging.getLogger(__name__)
router = APIRouter(tags=["empresa-publica"])

_CACHE_TTL_SECONDS = 24 * 60 * 60  # 24h
_perfil_cache: dict[str, tuple[dict, float]] = {}

_CNPJ_RE = re.compile(r"^\d{14}$")
_BRASILAPI_TIMEOUT = 15
_PT_TIMEOUT = 20


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class ContratoPublico(BaseModel):
    orgao: str
    valor: Optional[float] = None
    data_inicio: Optional[str] = None
    descricao: str


class EmpresaInfo(BaseModel):
    razao_social: str
    cnpj: str
    cnae_principal: str
    porte: str
    uf: str
    situacao: str


class PerfilB2GResponse(BaseModel):
    empresa: EmpresaInfo
    contratos: list[ContratoPublico]
    score: str  # "ATIVO" | "INICIANTE" | "SEM_HISTORICO"
    setor_detectado: str
    setor_nome: str
    editais_abertos_setor: int
    total_contratos_24m: int
    valor_total_24m: float
    ufs_atuacao: list[str]
    aviso_legal: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/empresa/{cnpj}/perfil-b2g",
    response_model=PerfilB2GResponse,
    summary="Perfil B2G público de uma empresa por CNPJ",
)
async def perfil_b2g(cnpj: str):
    cnpj_clean = re.sub(r"\D", "", cnpj)

    if not _CNPJ_RE.match(cnpj_clean):
        raise HTTPException(status_code=400, detail="CNPJ inválido — informe 14 dígitos numéricos")

    cached = _get_cached(cnpj_clean)
    if cached:
        return PerfilB2GResponse(**cached)

    data = await _build_perfil(cnpj_clean)
    _set_cached(cnpj_clean, data)
    return PerfilB2GResponse(**data)


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def _get_cached(key: str) -> Optional[dict]:
    if key not in _perfil_cache:
        return None
    data, ts = _perfil_cache[key]
    if time.time() - ts >= _CACHE_TTL_SECONDS:
        del _perfil_cache[key]
        return None
    return data


def _set_cached(key: str, data: dict) -> None:
    _perfil_cache[key] = (data, time.time())


# ---------------------------------------------------------------------------
# BrasilAPI
# ---------------------------------------------------------------------------

async def _fetch_brasilapi(cnpj: str) -> dict:
    """Fetch company data from BrasilAPI (public, no auth)."""
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    async with httpx.AsyncClient(timeout=_BRASILAPI_TIMEOUT) as client:
        resp = await client.get(url)

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="CNPJ não encontrado na base de dados")
    if resp.status_code != 200:
        logger.warning("BrasilAPI error %d for %s", resp.status_code, cnpj)
        raise HTTPException(status_code=502, detail="Erro ao consultar dados da empresa")

    return resp.json()


# ---------------------------------------------------------------------------
# Portal da Transparência — contracts
# ---------------------------------------------------------------------------

async def _fetch_contratos_pt(cnpj: str) -> list[dict]:
    """Fetch government contracts from Portal da Transparência."""
    import os

    api_key = os.getenv("PORTAL_TRANSPARENCIA_API_KEY", "")
    if not api_key:
        logger.warning("PORTAL_TRANSPARENCIA_API_KEY not set — skipping contracts")
        return []

    url = "https://api.portaldatransparencia.gov.br/api-de-dados/contratos"
    params = {"cpfCnpj": cnpj, "pagina": 1, "quantidade": 20}
    headers = {"chave-api-dados": api_key}

    try:
        async with httpx.AsyncClient(timeout=_PT_TIMEOUT) as client:
            resp = await client.get(url, params=params, headers=headers)

        if resp.status_code == 429:
            logger.warning("Portal Transparência rate limited for %s", cnpj)
            return []
        if resp.status_code != 200:
            logger.warning("Portal Transparência %d for %s", resp.status_code, cnpj)
            return []

        return resp.json() if isinstance(resp.json(), list) else []
    except Exception as e:
        logger.warning("Portal Transparência error for %s: %s", cnpj, e)
        return []


# ---------------------------------------------------------------------------
# Datalake — open bids count
# ---------------------------------------------------------------------------

async def _count_editais_abertos(setor_id: str, uf: str) -> int:
    """Count open bids in detected sector/UF from datalake (last 30 days)."""
    try:
        from datalake_query import query_datalake

        sector = SECTORS.get(setor_id)
        if not sector:
            return 0

        now = datetime.now(timezone.utc)
        results = await query_datalake(
            ufs=[uf],
            data_inicial=(now - timedelta(days=30)).strftime("%Y-%m-%d"),
            data_final=now.strftime("%Y-%m-%d"),
            keywords=list(sector.keywords),
            limit=2000,
        )
        return len(results)
    except Exception as e:
        logger.warning("Datalake count failed for %s/%s: %s", setor_id, uf, e)
        return 0


# ---------------------------------------------------------------------------
# Build profile
# ---------------------------------------------------------------------------

async def _build_perfil(cnpj: str) -> dict:
    # 1. Company data
    bapi = await _fetch_brasilapi(cnpj)

    razao_social = bapi.get("razao_social") or bapi.get("nome_fantasia") or "Empresa"
    cnae_raw = bapi.get("cnae_fiscal") or bapi.get("cnae_fiscal_principal") or ""
    cnae_str = str(cnae_raw)
    porte_raw = bapi.get("porte") or bapi.get("descricao_porte") or ""
    uf = bapi.get("uf") or ""
    situacao = bapi.get("descricao_situacao_cadastral") or bapi.get("situacao_cadastral") or ""

    # 2. Detect sector from CNAE
    setor_id = map_cnae_to_setor(cnae_str)
    setor_nome = get_setor_name(setor_id)

    # 3. Contracts from Portal da Transparência
    contratos_raw = await _fetch_contratos_pt(cnpj)

    # Parse contracts — last 24 months
    cutoff = datetime.now(timezone.utc) - timedelta(days=730)
    contratos_parsed: list[dict] = []
    ufs_set: set[str] = set()
    valor_total = 0.0

    for c in contratos_raw:
        orgao_data = c.get("unidadeGestora", {})
        orgao_nome = orgao_data.get("nome") or orgao_data.get("nomeOrgao") or "Não informado"

        valor = None
        for vf in ("valorFinalCompra", "valorInicial", "valorInicialCompra"):
            if c.get(vf) and float(c[vf]) > 0:
                valor = float(c[vf])
                break

        data_inicio = c.get("dataInicioVigencia") or c.get("dataFimCompra") or ""
        if data_inicio and len(data_inicio) > 10:
            data_inicio = data_inicio[:10]

        descricao = c.get("objeto") or c.get("descricaoObjeto") or "Sem descrição"
        if len(descricao) > 200:
            descricao = descricao[:197] + "..."

        uf_contrato = orgao_data.get("uf") or ""
        if uf_contrato:
            ufs_set.add(uf_contrato)

        if valor:
            valor_total += valor

        contratos_parsed.append({
            "orgao": orgao_nome,
            "valor": valor,
            "data_inicio": data_inicio,
            "descricao": descricao,
        })

    # Limit to 10 most recent
    contratos_parsed = contratos_parsed[:10]
    total_24m = len(contratos_raw)

    # 4. Score
    if total_24m >= 5:
        score = "ATIVO"
    elif total_24m >= 1:
        score = "INICIANTE"
    else:
        score = "SEM_HISTORICO"

    # 5. Open bids in detected sector
    editais_count = await _count_editais_abertos(setor_id, uf) if uf else 0

    return {
        "empresa": {
            "razao_social": razao_social,
            "cnpj": cnpj,
            "cnae_principal": cnae_str,
            "porte": str(porte_raw),
            "uf": uf,
            "situacao": str(situacao),
        },
        "contratos": contratos_parsed,
        "score": score,
        "setor_detectado": setor_id,
        "setor_nome": setor_nome,
        "editais_abertos_setor": editais_count,
        "total_contratos_24m": total_24m,
        "valor_total_24m": round(valor_total, 2),
        "ufs_atuacao": sorted(ufs_set),
        "aviso_legal": "Dados de fontes públicas: CNPJ aberto (BrasilAPI) e Portal da Transparência do Governo Federal.",
    }
