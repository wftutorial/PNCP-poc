#!/usr/bin/env python3
"""
OCDS (Open Contracting Data Standard) client for Brazilian procurement data.

Fetches structured procurement data from Compras.gov.br OCDS endpoints.
Supplements existing PNCP/PCP data with richer contract-level information:
  - Award details (winner, bid value, discount)
  - Bid statistics (number of bidders, bid range)
  - Contract amendments
  - Implementation milestones

OCDS Brazil endpoints:
  - https://compras.dados.gov.br/contratos/v1/contratos.json (legacy)
  - https://dadosabertos.compras.gov.br/modulo-contrato/... (v3)

References:
  - https://standard.open-contracting.org/latest/en/
  - https://www.gov.br/compras/pt-br/acesso-a-informacao/dados-abertos

Usage:
    from collectors.ocds_client import OCDSClient

    client = OCDSClient()
    releases = client.search_releases(buyer_id="...", since="2025-01-01")
    awards = client.get_awards_for_organ(cnpj_orgao="...", keyword="construcao")
"""
from __future__ import annotations

import argparse
import json
import io
import os
import re
import sys
import time
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

def _fix_win_encoding():
    """Fix Windows console encoding — only call from __main__."""
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import httpx
except ImportError:
    print("ERROR: httpx required. pip install httpx")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
OCDS_CACHE_FILE = str(_DATA_DIR / "ocds_cache.json")

CACHE_TTL_DAYS = 7

# Rate-limiting: max ~30 req/min => 2s between requests
_MIN_REQUEST_INTERVAL_S = 2.0

# OCDS v3 endpoints (Compras.gov.br dados abertos)
_BASE_V3 = "https://dadosabertos.compras.gov.br"
_URL_LICITACAO_V3 = f"{_BASE_V3}/modulo-licitacao/1_consultarLicitacao"
_URL_CONTRATO_V3 = f"{_BASE_V3}/modulo-contrato/1_consultarContrato"

# Legacy endpoints (fallback)
_BASE_LEGACY = "https://compras.dados.gov.br"
_URL_LICITACAO_LEGACY = f"{_BASE_LEGACY}/licitacoes/v1/licitacoes.json"
_URL_CONTRATO_LEGACY = f"{_BASE_LEGACY}/contratos/v1/contratos.json"

# Default user agent
_USER_AGENT = "SmartLic-OCDS/0.1 (+https://smartlic.tech)"


# ---------------------------------------------------------------------------
# Persistent cache helpers (same pattern as competitive_cache)
# ---------------------------------------------------------------------------

_cache: dict = {}
_cache_lock = threading.Lock()
_cache_loaded = False


def _load_json_cache(path: str) -> dict:
    """Load a JSON cache file. Returns empty dict if missing/corrupt."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _save_json_cache(path: str, data: dict) -> None:
    """Save data to a JSON cache file atomically."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


def _ensure_cache_loaded() -> None:
    """Lazy-load the OCDS cache from disk, discarding expired entries."""
    global _cache, _cache_loaded
    if _cache_loaded:
        return
    with _cache_lock:
        if _cache_loaded:
            return
        raw = _load_json_cache(OCDS_CACHE_FILE)
        now = datetime.now(timezone.utc)
        fresh: dict = {}
        for k, v in raw.items():
            cached_at = v.get("_cached_at", "2000-01-01")
            try:
                age = (now - datetime.fromisoformat(cached_at)).days
                if age <= CACHE_TTL_DAYS:
                    fresh[k] = v
            except (ValueError, TypeError):
                pass
        _cache = fresh
        _cache_loaded = True


def _cache_get(key: str) -> Any | None:
    """Get a value from cache (None if missing or expired)."""
    _ensure_cache_loaded()
    entry = _cache.get(key)
    if entry is None:
        return None
    cached_at = entry.get("_cached_at", "2000-01-01")
    try:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached_at)).days
        if age > CACHE_TTL_DAYS:
            return None
    except (ValueError, TypeError):
        return None
    return entry.get("data")


def _cache_set(key: str, data: Any) -> None:
    """Set a value in cache and persist to disk."""
    _ensure_cache_loaded()
    with _cache_lock:
        _cache[key] = {
            "data": data,
            "_cached_at": datetime.now(timezone.utc).isoformat(),
        }
        _save_json_cache(OCDS_CACHE_FILE, _cache)


# ---------------------------------------------------------------------------
# Text similarity helper
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    """Lowercase tokenize, stripping punctuation."""
    return set(re.findall(r"[a-zA-Z\u00c0-\u024f]{3,}", text.lower()))


def _jaccard(a: str, b: str) -> float:
    """Jaccard similarity between two strings (token-level)."""
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _normalize_cnpj(cnpj: str) -> str:
    """Strip formatting from CNPJ, return digits only."""
    return re.sub(r"\D", "", cnpj or "")


def _parse_date(s: str | None) -> datetime | None:
    """Best-effort ISO date parse."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        pass
    # Try date-only
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError, IndexError):
        return None


# ---------------------------------------------------------------------------
# OCDSClient
# ---------------------------------------------------------------------------

class OCDSClient:
    """Client for OCDS data from Brazilian procurement portals."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 2,
        verbose: bool = True,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.verbose = verbose
        self._last_request_ts: float = 0.0
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": _USER_AGENT, "Accept": "application/json"},
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OCDSClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- internal helpers ---------------------------------------------------

    def _log(self, msg: str) -> None:
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[OCDS {ts}] {msg}")

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        elapsed = time.monotonic() - self._last_request_ts
        if elapsed < _MIN_REQUEST_INTERVAL_S:
            time.sleep(_MIN_REQUEST_INTERVAL_S - elapsed)

    def _get(self, url: str, params: dict | None = None) -> dict | None:
        """HTTP GET with retry + error handling.

        Returns parsed JSON dict on success, None on failure.
        """
        for attempt in range(1, self.max_retries + 2):  # +1 for initial attempt
            self._rate_limit()
            try:
                self._last_request_ts = time.monotonic()
                resp = self._client.get(url, params=params)
                if resp.status_code == 404:
                    self._log(f"  404 Not Found: {url}")
                    return None
                if resp.status_code >= 500:
                    self._log(
                        f"  Server error {resp.status_code} on attempt {attempt}/{self.max_retries + 1}: {url}"
                    )
                    if attempt <= self.max_retries:
                        time.sleep(2 * attempt)  # exponential backoff
                        continue
                    return None
                if resp.status_code >= 400:
                    self._log(f"  HTTP {resp.status_code}: {url}")
                    return None
                data = resp.json()
                return data
            except httpx.TimeoutException:
                self._log(f"  Timeout on attempt {attempt}/{self.max_retries + 1}: {url}")
                if attempt <= self.max_retries:
                    time.sleep(2 * attempt)
                    continue
                return None
            except (httpx.HTTPError, json.JSONDecodeError) as e:
                self._log(f"  Error on attempt {attempt}/{self.max_retries + 1}: {e}")
                if attempt <= self.max_retries:
                    time.sleep(2 * attempt)
                    continue
                return None
        return None

    # -- V3 endpoints -------------------------------------------------------

    def _search_licitacao_v3(
        self,
        cnpj_orgao: str | None = None,
        keyword: str | None = None,
        since: str | None = None,
        until: str | None = None,
        pagina: int = 1,
        tam_pagina: int = 50,
    ) -> list[dict]:
        """Query Compras.gov.br v3 licitacao endpoint."""
        params: dict[str, Any] = {
            "pagina": pagina,
            "tamanhoPagina": tam_pagina,
        }
        if cnpj_orgao:
            params["cnpjOrgao"] = _normalize_cnpj(cnpj_orgao)
        if since:
            params["dataInicial"] = since[:10]
        if until:
            params["dataFinal"] = until[:10]
        if keyword:
            params["objetoCompra"] = keyword

        data = self._get(_URL_LICITACAO_V3, params=params)
        if not data:
            return []

        # v3 returns {"data": [...]} or a list directly
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("data", data.get("resultado", []))
        return []

    def _search_contrato_v3(
        self,
        cnpj_orgao: str | None = None,
        since: str | None = None,
        until: str | None = None,
        pagina: int = 1,
        tam_pagina: int = 50,
    ) -> list[dict]:
        """Query Compras.gov.br v3 contrato endpoint."""
        params: dict[str, Any] = {
            "pagina": pagina,
            "tamanhoPagina": tam_pagina,
        }
        if cnpj_orgao:
            params["cnpjOrgao"] = _normalize_cnpj(cnpj_orgao)
        if since:
            params["dataInicial"] = since[:10]
        if until:
            params["dataFinal"] = until[:10]

        data = self._get(_URL_CONTRATO_V3, params=params)
        if not data:
            return []

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("data", data.get("resultado", []))
        return []

    def _search_licitacao_legacy(
        self,
        cnpj_orgao: str | None = None,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """Fallback: legacy Compras.dados.gov.br licitacoes endpoint."""
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if cnpj_orgao:
            params["uasg"] = _normalize_cnpj(cnpj_orgao)
        if keyword:
            params["objeto"] = keyword

        data = self._get(_URL_LICITACAO_LEGACY, params=params)
        if not data:
            return []
        if isinstance(data, dict):
            return data.get("_embedded", {}).get("licitacoes", data.get("data", []))
        if isinstance(data, list):
            return data
        return []

    # -- Public API ---------------------------------------------------------

    def search_releases(
        self,
        buyer_id: str | None = None,
        keyword: str | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search OCDS releases (procurement processes).

        Tries v3 endpoint first, falls back to legacy.

        Args:
            buyer_id: CNPJ of the buying organ (digits only or formatted).
            keyword: Search term for object description.
            since: Start date ISO (YYYY-MM-DD).
            until: End date ISO (YYYY-MM-DD).
            limit: Max results to return.

        Returns:
            List of OCDS-like release dicts. Each has at minimum:
            ``ocid``, ``date``, ``buyer``, ``title``, ``tag``, ``value``.
        """
        cache_key = f"releases:{_normalize_cnpj(buyer_id or '')}:{keyword or ''}:{since or ''}:{until or ''}"
        cached = _cache_get(cache_key)
        if cached is not None:
            self._log(f"Cache hit for releases ({len(cached)} items)")
            return cached[:limit]

        self._log(f"Searching releases buyer={buyer_id} kw={keyword} since={since}")

        # Try v3 first
        results = self._search_licitacao_v3(
            cnpj_orgao=buyer_id, keyword=keyword, since=since, until=until, tam_pagina=min(limit, 50)
        )

        # Fallback to legacy if v3 returned nothing
        if not results:
            self._log("  v3 returned 0 results, trying legacy endpoint...")
            results = self._search_licitacao_legacy(
                cnpj_orgao=buyer_id, keyword=keyword, limit=min(limit, 50)
            )

        # Normalize to OCDS-like structure
        normalized = []
        for item in results[:limit]:
            release = self._normalize_release(item)
            if release:
                normalized.append(release)

        self._log(f"  Found {len(normalized)} releases")
        if normalized:
            _cache_set(cache_key, normalized)

        return normalized

    def get_awards_for_organ(
        self,
        cnpj_orgao: str,
        keyword: str = "",
        months: int = 24,
    ) -> list[dict]:
        """Get award data for a specific organ.

        Searches contracts and licitacoes for the given organ CNPJ,
        optionally filtered by keyword in the object description.

        Args:
            cnpj_orgao: CNPJ of the buying organ.
            keyword: Optional keyword filter on object description.
            months: How many months back to search (default 24).

        Returns:
            List of simplified award dicts with keys:
            ``ocid``, ``date``, ``buyer``, ``title``, ``value``,
            ``currency``, ``suppliers``, ``n_tenderers``, ``status``.
        """
        cnpj_clean = _normalize_cnpj(cnpj_orgao)
        cache_key = f"awards:{cnpj_clean}:{keyword}:{months}"
        cached = _cache_get(cache_key)
        if cached is not None:
            self._log(f"Cache hit for awards ({len(cached)} items)")
            return cached

        self._log(f"Fetching awards for organ={cnpj_clean} kw={keyword} months={months}")

        since = (datetime.now(timezone.utc) - timedelta(days=months * 30)).strftime("%Y-%m-%d")
        until = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Fetch contratos
        contratos = self._search_contrato_v3(cnpj_orgao=cnpj_clean, since=since, until=until)
        self._log(f"  Got {len(contratos)} contratos from v3")

        # Also fetch licitacoes for richer data
        licitacoes = self._search_licitacao_v3(
            cnpj_orgao=cnpj_clean, keyword=keyword or None, since=since, until=until
        )
        self._log(f"  Got {len(licitacoes)} licitacoes from v3")

        awards: list[dict] = []

        # Process contratos into award format
        for c in contratos:
            award = self._contrato_to_award(c)
            if award is None:
                continue
            # Apply keyword filter client-side
            if keyword and keyword.lower() not in (award.get("title") or "").lower():
                continue
            awards.append(award)

        # Process licitacoes (may have award info embedded)
        for lic in licitacoes:
            award = self._licitacao_to_award(lic)
            if award is None:
                continue
            # Avoid duplicates by ocid
            existing_ocids = {a["ocid"] for a in awards}
            if award["ocid"] in existing_ocids:
                continue
            if keyword and keyword.lower() not in (award.get("title") or "").lower():
                continue
            awards.append(award)

        # Sort by date descending
        awards.sort(key=lambda a: a.get("date", ""), reverse=True)

        self._log(f"  Total awards after filtering: {len(awards)}")
        if awards:
            _cache_set(cache_key, awards)

        return awards

    def get_bid_statistics(self, ocid: str) -> dict | None:
        """Get bid-level statistics for a specific process.

        Attempts to retrieve detailed bid data from the OCDS release.

        Args:
            ocid: The OCDS process identifier (or internal ID).

        Returns:
            Dict with keys: ``n_bids``, ``min_bid``, ``max_bid``,
            ``avg_bid``, ``winner_bid``, ``discount_pct``.
            None if data unavailable.
        """
        cache_key = f"bids:{ocid}"
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached

        self._log(f"Fetching bid statistics for ocid={ocid}")

        # Try to get detailed licitacao data by searching with the ocid
        # The v3 API may support lookup by numero
        data = self._get(_URL_LICITACAO_V3, params={"numero": ocid, "tamanhoPagina": 1})
        if not data:
            # Try legacy
            data = self._get(_URL_LICITACAO_LEGACY, params={"licitacao": ocid, "limit": 1})

        if not data:
            self._log(f"  No bid data found for {ocid}")
            return None

        # Extract bid items from response
        items = []
        if isinstance(data, dict):
            items = data.get("data", data.get("resultado", []))
            if not items and "propostas" in data:
                items = [data]
        elif isinstance(data, list):
            items = data

        if not items:
            return None

        item = items[0] if items else {}

        # Extract proposal/bid values
        propostas = item.get("propostas", item.get("itensResultado", []))
        bid_values = []
        winner_value: float | None = None
        estimated_value: float | None = None

        for p in propostas:
            val = _safe_float(p.get("valorProposta", p.get("valor", p.get("vlrOferta"))))
            if val and val > 0:
                bid_values.append(val)
                if p.get("vencedor") or p.get("situacao", "").lower() in ("vencedor", "adjudicado"):
                    winner_value = val

        # Try to get estimated value
        estimated_value = _safe_float(
            item.get("valorEstimado", item.get("vlrEstimado", item.get("valor_estimado")))
        )

        if not bid_values:
            self._log(f"  No bid values found for {ocid}")
            return None

        if winner_value is None:
            winner_value = min(bid_values)  # assume lowest bid wins

        discount_pct = 0.0
        if estimated_value and estimated_value > 0 and winner_value:
            discount_pct = round((estimated_value - winner_value) / estimated_value * 100, 2)

        stats = {
            "n_bids": len(bid_values),
            "min_bid": round(min(bid_values), 2),
            "max_bid": round(max(bid_values), 2),
            "avg_bid": round(sum(bid_values) / len(bid_values), 2),
            "winner_bid": round(winner_value, 2),
            "discount_pct": discount_pct,
        }

        _cache_set(cache_key, stats)
        return stats

    def enrich_editais_with_ocds(self, editais: list[dict]) -> dict:
        """Enrich editais with OCDS award/bid data.

        For each edital, attempts to find a matching OCDS release and
        attaches ``_ocds_data`` field with award and bid statistics.

        Matching strategy (in priority order):
        1. ``numero_controle_pncp`` -> OCDS ``ocid``
        2. Fuzzy match on ``cnpj_orgao`` + ``objeto`` similarity (Jaccard >= 0.5)
        3. Date proximity (+-30 days of ``data_abertura``)

        Args:
            editais: List of edital dicts (from SmartLic search pipeline).

        Returns:
            Summary dict: ``{"enriched": int, "not_found": int, "errors": int}``
        """
        summary = {"enriched": 0, "not_found": 0, "errors": 0}

        if not editais:
            return summary

        self._log(f"Enriching {len(editais)} editais with OCDS data...")

        # Group editais by organ CNPJ for batch lookup
        by_organ: dict[str, list[dict]] = {}
        for ed in editais:
            cnpj = _normalize_cnpj(ed.get("cnpj_orgao", ed.get("cnpjOrgao", "")))
            if cnpj:
                by_organ.setdefault(cnpj, []).append(ed)
            else:
                ed["_ocds_data"] = None
                summary["not_found"] += 1

        # For each organ, fetch releases and try to match
        for cnpj, organ_editais in by_organ.items():
            try:
                # Determine date range from editais
                dates = []
                for ed in organ_editais:
                    d = _parse_date(
                        ed.get("data_abertura", ed.get("dataAbertura", ed.get("data_publicacao")))
                    )
                    if d:
                        dates.append(d)

                since = None
                until = None
                if dates:
                    min_date = min(dates) - timedelta(days=30)
                    max_date = max(dates) + timedelta(days=30)
                    since = min_date.strftime("%Y-%m-%d")
                    until = max_date.strftime("%Y-%m-%d")

                releases = self.search_releases(buyer_id=cnpj, since=since, until=until, limit=100)

                for ed in organ_editais:
                    match = self._find_best_match(ed, releases)
                    if match:
                        ed["_ocds_data"] = match
                        summary["enriched"] += 1
                    else:
                        ed["_ocds_data"] = None
                        summary["not_found"] += 1

            except Exception as e:
                self._log(f"  Error enriching organ {cnpj}: {e}")
                for ed in organ_editais:
                    ed["_ocds_data"] = None
                    summary["errors"] += 1

        self._log(
            f"Enrichment complete: {summary['enriched']} enriched, "
            f"{summary['not_found']} not found, {summary['errors']} errors"
        )
        return summary

    # -- Normalization helpers -----------------------------------------------

    def _normalize_release(self, item: dict) -> dict | None:
        """Normalize a raw API response item into an OCDS-like release dict."""
        if not item or not isinstance(item, dict):
            return None

        ocid = (
            item.get("ocid")
            or item.get("numero")
            or item.get("numeroLicitacao")
            or item.get("licitacao")
            or item.get("id", "")
        )
        if not ocid:
            return None

        title = (
            item.get("objeto")
            or item.get("objetoCompra")
            or item.get("description")
            or item.get("descricao")
            or ""
        )

        buyer = (
            item.get("nomeOrgao")
            or item.get("orgao", {}).get("nome", "")
            if isinstance(item.get("orgao"), dict)
            else item.get("orgao", "")
        )

        date_str = (
            item.get("dataAbertura")
            or item.get("data_abertura")
            or item.get("dataPublicacao")
            or item.get("date")
            or ""
        )

        value = _safe_float(
            item.get("valorEstimado")
            or item.get("vlrEstimado")
            or item.get("valor_estimado")
            or item.get("value", {}).get("amount")
            if isinstance(item.get("value"), dict)
            else item.get("value", 0)
        )

        status = (
            item.get("situacao")
            or item.get("status")
            or item.get("tag", "")
        )

        return {
            "ocid": str(ocid),
            "date": str(date_str)[:10] if date_str else "",
            "buyer": str(buyer),
            "title": str(title)[:500],
            "tag": str(status),
            "value": value or 0.0,
            "currency": "BRL",
            "_raw_keys": list(item.keys())[:10],  # debug: first 10 keys
        }

    def _contrato_to_award(self, contrato: dict) -> dict | None:
        """Convert a v3 contrato response to a simplified award dict."""
        if not contrato or not isinstance(contrato, dict):
            return None

        ocid = (
            contrato.get("numero")
            or contrato.get("numeroContrato")
            or contrato.get("id", "")
        )
        if not ocid:
            return None

        title = (
            contrato.get("objeto")
            or contrato.get("objetoContrato")
            or contrato.get("descricao")
            or ""
        )

        buyer = (
            contrato.get("nomeOrgao")
            or contrato.get("orgao", "")
        )

        date_str = (
            contrato.get("dataAssinatura")
            or contrato.get("dataInicio")
            or contrato.get("dataPublicacao")
            or ""
        )

        value = _safe_float(
            contrato.get("valorInicial")
            or contrato.get("valorContrato")
            or contrato.get("valor")
        )

        # Supplier info
        supplier_name = contrato.get("nomeContratado") or contrato.get("fornecedor", "")
        supplier_id = _normalize_cnpj(contrato.get("cnpjContratado") or contrato.get("cpfCnpjContratado", ""))
        suppliers = []
        if supplier_name or supplier_id:
            suppliers.append({"name": str(supplier_name), "id": supplier_id})

        status_raw = contrato.get("situacao", contrato.get("status", "")).lower()
        status = "active"
        if "encerrad" in status_raw or "conclu" in status_raw or "finaliz" in status_raw:
            status = "closed"
        elif "cancel" in status_raw or "rescind" in status_raw:
            status = "cancelled"

        return {
            "ocid": str(ocid),
            "date": str(date_str)[:10] if date_str else "",
            "buyer": str(buyer),
            "title": str(title)[:500],
            "value": value or 0.0,
            "currency": "BRL",
            "suppliers": suppliers,
            "n_tenderers": int(contrato.get("qtdLicitantes", contrato.get("quantidadeLicitantes", 0))),
            "status": status,
        }

    def _licitacao_to_award(self, lic: dict) -> dict | None:
        """Convert a v3 licitacao response to a simplified award dict."""
        if not lic or not isinstance(lic, dict):
            return None

        ocid = (
            lic.get("ocid")
            or lic.get("numero")
            or lic.get("numeroLicitacao")
            or lic.get("id", "")
        )
        if not ocid:
            return None

        title = (
            lic.get("objeto")
            or lic.get("objetoCompra")
            or lic.get("descricao")
            or ""
        )

        buyer = lic.get("nomeOrgao") or lic.get("orgao", "")

        date_str = (
            lic.get("dataAbertura")
            or lic.get("dataPublicacao")
            or ""
        )

        value = _safe_float(
            lic.get("valorEstimado")
            or lic.get("vlrEstimado")
            or lic.get("valor")
        )

        status_raw = (lic.get("situacao") or lic.get("status") or "").lower()
        status = "active"
        if any(t in status_raw for t in ("homologad", "adjudicad", "encerrad", "conclu")):
            status = "closed"
        elif "cancel" in status_raw or "revogad" in status_raw:
            status = "cancelled"

        return {
            "ocid": str(ocid),
            "date": str(date_str)[:10] if date_str else "",
            "buyer": str(buyer),
            "title": str(title)[:500],
            "value": value or 0.0,
            "currency": "BRL",
            "suppliers": [],  # licitacao may not have winner yet
            "n_tenderers": int(lic.get("qtdLicitantes", lic.get("quantidadeLicitantes", 0))),
            "status": status,
        }

    # -- Matching logic ------------------------------------------------------

    def _find_best_match(self, edital: dict, releases: list[dict]) -> dict | None:
        """Find the best OCDS release matching an edital.

        Priority:
        1. Exact match on numero_controle_pncp -> ocid
        2. Fuzzy match on object text + date proximity + same organ
        """
        if not releases:
            return None

        # Strategy 1: exact ocid match
        pncp_id = edital.get("numero_controle_pncp", edital.get("numeroControlePncp", ""))
        if pncp_id:
            for r in releases:
                if r.get("ocid") == pncp_id or pncp_id in str(r.get("ocid", "")):
                    return r

        # Strategy 2: fuzzy match on objeto + date proximity
        edital_obj = edital.get("objeto", edital.get("title", ""))
        edital_date = _parse_date(
            edital.get("data_abertura", edital.get("dataAbertura", edital.get("data_publicacao")))
        )

        best_score = 0.0
        best_match: dict | None = None

        for r in releases:
            score = 0.0

            # Text similarity (max 0.6 weight)
            release_title = r.get("title", "")
            text_sim = _jaccard(edital_obj, release_title)
            score += text_sim * 0.6

            # Date proximity (max 0.4 weight)
            release_date = _parse_date(r.get("date"))
            if edital_date and release_date:
                day_diff = abs((edital_date - release_date).days)
                if day_diff <= 30:
                    date_score = 1.0 - (day_diff / 30.0)
                    score += date_score * 0.4

            if score > best_score:
                best_score = score
                best_match = r

        # Require minimum combined score (Jaccard >= 0.5 equivalent)
        if best_score >= 0.5:
            return best_match

        return None


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _safe_float(v: Any) -> float:
    """Convert to float safely, return 0.0 on failure."""
    if v is None:
        return 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="OCDS client for Brazilian procurement data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/collectors/ocds_client.py --cnpj-orgao 12345678000190 --keyword "construcao"
  python scripts/collectors/ocds_client.py --cnpj-orgao 12345678000190 --months 12
  python scripts/collectors/ocds_client.py --search --keyword "pavimentacao" --since 2025-06-01
        """,
    )
    parser.add_argument("--cnpj-orgao", help="CNPJ of the buying organ (digits or formatted)")
    parser.add_argument("--keyword", default="", help="Keyword filter on object description")
    parser.add_argument("--months", type=int, default=24, help="Months back to search (default: 24)")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD) for release search")
    parser.add_argument("--until", help="End date (YYYY-MM-DD) for release search")
    parser.add_argument("--search", action="store_true", help="Search releases (instead of awards)")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--output", help="Write JSON output to file (default: stdout)")

    args = parser.parse_args()

    if not args.cnpj_orgao and not args.search:
        parser.error("Either --cnpj-orgao or --search is required")

    with OCDSClient(verbose=not args.quiet) as client:
        if args.search:
            results = client.search_releases(
                buyer_id=args.cnpj_orgao,
                keyword=args.keyword or None,
                since=args.since,
                until=args.until,
                limit=args.limit,
            )
            label = "releases"
        else:
            results = client.get_awards_for_organ(
                cnpj_orgao=args.cnpj_orgao,
                keyword=args.keyword,
                months=args.months,
            )
            results = results[: args.limit]
            label = "awards"

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {len(results)} {label} to {args.output}")
    else:
        print(f"\n{'='*60}")
        print(f"  {len(results)} {label} found")
        print(f"{'='*60}\n")
        print(output)

    # Print summary stats
    if results and not args.search:
        total_value = sum(r.get("value", 0) for r in results)
        with_suppliers = sum(1 for r in results if r.get("suppliers"))
        statuses = {}
        for r in results:
            s = r.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1

        print(f"\n--- Summary ---")
        print(f"  Total value:    R$ {total_value:,.2f}")
        print(f"  With suppliers: {with_suppliers}/{len(results)}")
        print(f"  By status:      {statuses}")


if __name__ == "__main__":
    _fix_win_encoding()
    main()
