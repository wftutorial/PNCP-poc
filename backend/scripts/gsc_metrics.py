"""
S14: Google Search Console metrics extraction.

Usage:
    python -m scripts.gsc_metrics           # last 7 days
    python -m scripts.gsc_metrics --days 28 # last 28 days

Requires GOOGLE_SERVICE_ACCOUNT_KEY env var (JSON string or file path).
When credentials are not configured, logs a warning and exits gracefully.
"""

import os
import json
import logging
import asyncio
from datetime import date, timedelta

logger = logging.getLogger(__name__)

SITE_URL = "sc-domain:smartlic.tech"


def _get_gsc_service():
    """Build GSC API service from credentials. Returns None if unconfigured."""
    key_raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
    if not key_raw:
        logger.warning("GOOGLE_SERVICE_ACCOUNT_KEY not set — skipping GSC extraction")
        return None

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        # Handle both JSON string and file path
        if key_raw.strip().startswith("{"):
            info = json.loads(key_raw)
        else:
            with open(key_raw) as f:
                info = json.load(f)

        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        return build("searchconsole", "v1", credentials=credentials)
    except ImportError:
        logger.warning("google-api-python-client not installed — skipping GSC extraction")
        return None
    except Exception as exc:
        logger.error("Failed to initialize GSC service: %s", exc)
        return None


async def fetch_and_store(days: int = 7) -> dict:
    """Fetch GSC data for the last N days and upsert into seo_metrics."""
    service = _get_gsc_service()
    if not service:
        return {"status": "skipped", "reason": "no_credentials"}

    try:
        from supabase_client import get_supabase

        supabase = get_supabase()
        end_date = date.today() - timedelta(days=1)  # GSC data has 2-day lag
        start_date = end_date - timedelta(days=days)

        rows_upserted = 0

        for single_date in _date_range(start_date, end_date):
            date_str = single_date.isoformat()

            # Fetch sitewide totals
            totals = _query_gsc(service, date_str, date_str, dimensions=[])
            if not totals:
                continue

            # Fetch top queries
            top_queries = _query_gsc(service, date_str, date_str, dimensions=["query"], row_limit=20)

            # Fetch top pages
            top_pages = _query_gsc(service, date_str, date_str, dimensions=["page"], row_limit=20)

            row = {
                "date": date_str,
                "impressions": int(totals.get("impressions", 0)),
                "clicks": int(totals.get("clicks", 0)),
                "ctr": round(totals.get("ctr", 0), 4),
                "avg_position": round(totals.get("position", 0), 2),
                "pages_indexed": len(top_pages) if top_pages else 0,
                "top_queries": top_queries or [],
                "top_pages": top_pages or [],
                "source": "gsc",
            }

            supabase.table("seo_metrics").upsert(
                row, on_conflict="date,source"
            ).execute()
            rows_upserted += 1

        return {"status": "ok", "days_processed": rows_upserted}

    except Exception as exc:
        logger.error("GSC fetch_and_store failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def _query_gsc(service, start_date: str, end_date: str, dimensions: list, row_limit: int = 1):
    """Execute a GSC searchAnalytics query."""
    try:
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": row_limit,
        }
        response = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
        rows = response.get("rows", [])

        if not dimensions:
            # Sitewide totals
            if rows:
                return rows[0]
            return None

        # Dimension-based results
        return [
            {
                dimensions[0]: row["keys"][0],
                "clicks": int(row.get("clicks", 0)),
                "impressions": int(row.get("impressions", 0)),
                "position": round(row.get("position", 0), 1),
            }
            for row in rows
        ]
    except Exception as exc:
        logger.error("GSC query failed for %s: %s", start_date, exc)
        return None


def _date_range(start: date, end: date):
    """Yield dates from start to end inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch GSC metrics")
    parser.add_argument("--days", type=int, default=7, help="Number of days to fetch")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(fetch_and_store(args.days))
    print(json.dumps(result, indent=2))
