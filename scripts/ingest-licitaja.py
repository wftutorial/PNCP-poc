#!/usr/bin/env python3
"""
Ingest LicitaJá data into Supabase datalake (pncp_raw_bids).

Designed to run from GitHub Actions (no IP whitelist issues)
or locally. Fetches recent procurement data from LicitaJá API
and upserts into the same datalake table used by PNCP.

Usage:
    python scripts/ingest-licitaja.py
    python scripts/ingest-licitaja.py --dias 7 --ufs SC,PR,RS
    python scripts/ingest-licitaja.py --dry-run

Requires:
    pip install httpx supabase
    env: LICITAJA_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Load .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).resolve().parent.parent / ".env"))
except ImportError:
    pass

import httpx

# ============================================================
# CONFIG
# ============================================================

LICITAJA_BASE_URL = os.environ.get("LICITAJA_BASE_URL", "https://www.licitaja.com.br/api/v1")
LICITAJA_API_KEY = os.environ.get("LICITAJA_API_KEY", "")
LICITAJA_TIMEOUT = int(os.environ.get("LICITAJA_TIMEOUT", "30"))
LICITAJA_MAX_ITEMS_PER_PAGE = 25
LICITAJA_MAX_PAGES = 20  # 20 pages × 25 = 500 per keyword group

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# Rate limiting: 10 req/min -> 6s between requests
RATE_LIMIT_INTERVAL = 6.5  # seconds between API calls (conservative)

# All 27 UFs
ALL_UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
    "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
    "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]

# Modalidade name -> ID mapping (best-effort for LicitaJá)
MODALIDADE_MAP = {
    "pregão eletrônico": 6,
    "pregao eletronico": 6,
    "pregão presencial": 6,
    "concorrência": 4,
    "concorrencia": 4,
    "concorrência eletrônica": 4,
    "dispensa": 8,
    "dispensa eletrônica": 8,
    "dispensa de licitação": 8,
    "inexigibilidade": 9,
    "tomada de preços": 5,
    "tomada de precos": 5,
    "convite": 3,
    "leilão": 10,
    "credenciamento": 12,
}


# ============================================================
# HELPERS
# ============================================================

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _date_compact(dt: datetime) -> str:
    """YYYYMMDD format for LicitaJá API."""
    return dt.strftime("%Y%m%d")


def _parse_date(val: str | None) -> str | None:
    """Parse LicitaJá date formats to ISO 8601."""
    if not val:
        return None
    val = val.strip()
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            dt = datetime.strptime(val.rstrip("Z"), fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    # Try unix timestamp
    try:
        ts = float(val)
        if ts > 1e12:
            ts /= 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except (ValueError, OSError):
        pass
    return None


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        f = float(val)
        return f if f > 0 else None
    except (ValueError, TypeError):
        return None


def _modalidade_id(type_str: str | None) -> int | None:
    if not type_str:
        return None
    return MODALIDADE_MAP.get(type_str.lower().strip())


def _compute_content_hash(objeto: str, valor: Any, situacao: str) -> str:
    canonical = f"{(objeto or '').lower().strip()}|{valor or ''}|{(situacao or '').lower().strip()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _strip_city_suffix(city: str | None) -> str | None:
    """Remove state suffix from city name (e.g., 'São Paulo-SP' -> 'São Paulo')."""
    if not city:
        return None
    parts = city.rsplit("-", 1)
    if len(parts) == 2 and len(parts[1].strip()) == 2:
        return parts[0].strip()
    return city.strip()


# ============================================================
# LICITAJA API CLIENT (minimal, sync)
# ============================================================

class LicitaJaIngester:
    def __init__(self, api_key: str, verbose: bool = True):
        self.api_key = api_key
        self.verbose = verbose
        self.client = httpx.Client(
            timeout=LICITAJA_TIMEOUT,
            headers={
                "X-API-KEY": api_key,
                "Accept": "application/json",
                "User-Agent": "SmartLic-Ingester/1.0",
            },
        )
        self.stats = {"pages": 0, "items": 0, "errors": 0}
        self._last_request = 0.0

    def _rate_wait(self):
        elapsed = time.monotonic() - self._last_request
        if elapsed < RATE_LIMIT_INTERVAL:
            time.sleep(RATE_LIMIT_INTERVAL - elapsed)
        self._last_request = time.monotonic()

    def search(
        self,
        states: list[str],
        date_from: str,
        date_to: str,
        keyword: str = "",
        page: int = 1,
    ) -> tuple[list[dict], int]:
        """Single page search. Returns (results, total)."""
        self._rate_wait()

        params: dict[str, Any] = {
            "smartsearch": 0,
            "order": 0,
            "page": page,
            "items": LICITAJA_MAX_ITEMS_PER_PAGE,
            "state": ",".join(states),
            "opening_date_from": date_from.replace("-", ""),
            "opening_date_to": date_to.replace("-", ""),
        }
        if keyword:
            params["keyword"] = keyword

        try:
            resp = self.client.get(f"{LICITAJA_BASE_URL}/tender/search", params=params)

            if resp.status_code == 401:
                print("ERROR: LicitaJá API key inválida (401 Unauthorized)")
                return [], 0
            if resp.status_code == 429:
                print("  WARN: Rate limited (429), aguardando 30s...")
                time.sleep(30)
                return [], 0
            if resp.status_code >= 500:
                self.stats["errors"] += 1
                return [], 0

            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            total = data.get("total_results", 0)
            self.stats["pages"] += 1
            self.stats["items"] += len(results)
            return results, total

        except Exception as exc:
            self.stats["errors"] += 1
            if self.verbose:
                print(f"  WARN: LicitaJá request failed: {exc}")
            return [], 0

    def search_all(
        self,
        states: list[str],
        date_from: str,
        date_to: str,
        keyword: str = "",
        max_pages: int = LICITAJA_MAX_PAGES,
    ) -> list[dict]:
        """Paginate through all results."""
        all_results: list[dict] = []
        seen_ids: set[str] = set()

        for page in range(1, max_pages + 1):
            results, total = self.search(states, date_from, date_to, keyword, page)

            if not results:
                break

            for item in results:
                tid = item.get("tenderId", "")
                if tid and tid not in seen_ids:
                    seen_ids.add(tid)
                    all_results.append(item)

            if self.verbose and page == 1:
                print(f"    Total: {total} resultados (keyword='{keyword[:30]}')")

            if len(results) < LICITAJA_MAX_ITEMS_PER_PAGE:
                break  # last page

        return all_results

    def close(self):
        self.client.close()


# ============================================================
# TRANSFORMER: LicitaJá -> pncp_raw_bids row
# ============================================================

def transform_licitaja_item(item: dict, crawl_batch_id: str) -> dict | None:
    """Convert a LicitaJá API item to a pncp_raw_bids row dict."""
    tender_id = item.get("tenderId", "").strip()
    if not tender_id:
        return None

    objeto = item.get("tender_object") or ""
    valor = _safe_float(item.get("value"))
    situacao = item.get("status") or ""
    uf = (item.get("state") or "").upper().strip()

    if not objeto or not uf:
        return None

    pncp_id = f"LICITAJA-{tender_id}"

    return {
        "pncp_id": pncp_id,
        "objeto_compra": objeto[:2000],  # truncate to avoid oversized rows
        "valor_total_estimado": valor,
        "modalidade_id": _modalidade_id(item.get("type")),
        "modalidade_nome": item.get("type") or "",
        "situacao_compra": situacao,
        "esfera_id": None,
        "uf": uf[:2],
        "municipio": _strip_city_suffix(item.get("city")),
        "codigo_municipio_ibge": None,
        "orgao_razao_social": item.get("agency") or "",
        "orgao_cnpj": item.get("cnpj") or "",
        "unidade_nome": None,
        "data_publicacao": _parse_date(item.get("catalog_date")),
        "data_abertura": _parse_date(item.get("opening_date")),
        "data_encerramento": _parse_date(item.get("close_date")),
        "link_sistema_origem": item.get("url") or f"https://www.licitaja.com.br/licitacao/{tender_id}",
        "link_pncp": None,
        "content_hash": _compute_content_hash(objeto, valor, situacao),
        "source": "licitaja",
        "crawl_batch_id": crawl_batch_id,
        "is_active": True,
    }


# ============================================================
# SUPABASE LOADER
# ============================================================

def upsert_to_supabase(records: list[dict], dry_run: bool = False) -> dict:
    """Upsert records into pncp_raw_bids via Supabase RPC."""
    if not records:
        return {"inserted": 0, "updated": 0, "unchanged": 0}

    if dry_run:
        print(f"  [DRY RUN] Would upsert {len(records)} records")
        return {"inserted": len(records), "updated": 0, "unchanged": 0}

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        sys.exit(1)

    totals = {"inserted": 0, "updated": 0, "unchanged": 0}
    batch_size = 500

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = i // batch_size + 1

        try:
            resp = httpx.post(
                f"{SUPABASE_URL}/rest/v1/rpc/upsert_pncp_raw_bids",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json={"p_records": json.dumps(batch, default=str)},
                timeout=60,
            )

            if resp.status_code >= 400:
                print(f"  ERROR: Supabase RPC batch {batch_num} failed: {resp.status_code} {resp.text[:200]}")
                continue

            data = resp.json()
            if isinstance(data, list) and data:
                row = data[0]
            elif isinstance(data, dict):
                row = data
            else:
                row = {}

            totals["inserted"] += row.get("inserted", 0)
            totals["updated"] += row.get("updated", 0)
            totals["unchanged"] += row.get("unchanged", 0)

            print(f"  Batch {batch_num}: +{row.get('inserted', 0)} ins, "
                  f"{row.get('updated', 0)} upd, {row.get('unchanged', 0)} unch")

        except Exception as exc:
            print(f"  ERROR: Supabase RPC batch {batch_num} exception: {exc}")

    return totals


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Ingest LicitaJá -> Supabase datalake")
    parser.add_argument("--dias", type=int, default=10, help="Lookback days (default: 10)")
    parser.add_argument("--ufs", type=str, default=None, help="UFs (comma-separated, default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to Supabase")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    args = parser.parse_args()

    if not LICITAJA_API_KEY:
        print("ERROR: LICITAJA_API_KEY not set")
        sys.exit(1)

    ufs = args.ufs.upper().split(",") if args.ufs else ALL_UFS
    dias = args.dias
    now = _now_utc()
    date_from = (now - timedelta(days=dias)).strftime("%Y-%m-%d")
    date_to = now.strftime("%Y-%m-%d")
    crawl_batch_id = f"licitaja_{now.strftime('%Y%m%d_%H%M%S')}"

    print(f"{'='*60}")
    print(f"  LICITAJA DATALAKE INGESTION")
    print(f"  UFs:        {len(ufs)} ({', '.join(ufs[:5])}{'...' if len(ufs) > 5 else ''})")
    print(f"  Período:    {date_from} -> {date_to} ({dias} dias)")
    print(f"  Batch:      {crawl_batch_id}")
    print(f"  Dry run:    {args.dry_run}")
    print(f"{'='*60}")

    t0 = time.time()
    ingester = LicitaJaIngester(LICITAJA_API_KEY, verbose=not args.quiet)

    # Fetch all UFs in one search (LicitaJá supports comma-separated states)
    # Split into batches of 5 UFs to avoid oversized queries
    all_items: list[dict] = []
    seen_ids: set[str] = set()
    uf_batch_size = 5

    for i in range(0, len(ufs), uf_batch_size):
        uf_batch = ufs[i:i + uf_batch_size]
        print(f"\n[{i // uf_batch_size + 1}] Buscando UFs: {', '.join(uf_batch)}...")

        # Search without keyword first (broad catch)
        results = ingester.search_all(uf_batch, date_from, date_to)
        for item in results:
            tid = item.get("tenderId", "")
            if tid not in seen_ids:
                seen_ids.add(tid)
                all_items.append(item)

        print(f"    -> {len(results)} resultados, {len(all_items)} total acumulado")

    print(f"\nTotal bruto: {len(all_items)} editais de {ingester.stats['pages']} páginas")

    # Transform
    print("\nTransformando para schema datalake...")
    rows: list[dict] = []
    skipped = 0
    for item in all_items:
        row = transform_licitaja_item(item, crawl_batch_id)
        if row:
            rows.append(row)
        else:
            skipped += 1

    print(f"  Transformados: {len(rows)} | Descartados: {skipped}")

    if not rows:
        print("\nNenhum registro para inserir. Encerrando.")
        ingester.close()
        return

    # Upsert
    print(f"\nUpserting {len(rows)} registros no Supabase...")
    totals = upsert_to_supabase(rows, dry_run=args.dry_run)

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  RESULTADO")
    print(f"  Inseridos:    {totals['inserted']}")
    print(f"  Atualizados:  {totals['updated']}")
    print(f"  Inalterados:  {totals['unchanged']}")
    print(f"  Erros API:    {ingester.stats['errors']}")
    print(f"  Tempo total:  {elapsed:.1f}s")
    print(f"{'='*60}")

    ingester.close()

    # Exit with error if no records were inserted/updated (potential auth issue)
    if totals["inserted"] == 0 and totals["updated"] == 0 and not args.dry_run:
        if ingester.stats["errors"] > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
