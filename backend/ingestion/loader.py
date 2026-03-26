"""Load transformed PNCP records into Supabase via RPC.

Uses two Supabase stored procedures:
  - upsert_pncp_raw_bids(p_records jsonb)  — bulk upsert returning counts
  - purge_old_bids(p_retention_days int)   — delete rows older than N days
"""

import json
import logging
from typing import Any

from supabase_client import get_supabase
from ingestion.config import INGESTION_UPSERT_BATCH_SIZE

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

async def bulk_upsert(
    records: list[dict],
    *,
    batch_size: int = INGESTION_UPSERT_BATCH_SIZE,
) -> dict[str, int]:
    """Upsert records into pncp_raw_bids via Supabase RPC.

    The RPC function ``upsert_pncp_raw_bids`` must accept a single jsonb
    parameter ``p_records`` and return a row with columns:
        inserted int, updated int, unchanged int

    Args:
        records: List of row dicts produced by transformer.transform_batch().
        batch_size: Max rows per RPC call (default 500, tuned for 1 MB limit).

    Returns:
        Aggregated counts: {"inserted": N, "updated": N, "unchanged": N, "total": N, "batches": N}
    """
    if not records:
        logger.debug("bulk_upsert: no records to upsert")
        return {"inserted": 0, "updated": 0, "unchanged": 0, "total": 0, "batches": 0}

    totals: dict[str, int] = {"inserted": 0, "updated": 0, "unchanged": 0, "total": 0, "batches": 0}
    batches = _chunk(records, batch_size)
    supabase = get_supabase()

    for batch_idx, batch in enumerate(batches):
        batch_num = batch_idx + 1
        logger.info(
            "bulk_upsert: batch %d — upserting %d records",
            batch_num,
            len(batch),
        )

        try:
            payload = _serialize_batch(batch)

            result = (
                supabase
                .rpc("upsert_pncp_raw_bids", {"p_records": payload})
                .execute()
            )

            counts = _extract_counts(result, batch_num)
            totals["inserted"] += counts.get("inserted", 0)
            totals["updated"] += counts.get("updated", 0)
            totals["unchanged"] += counts.get("unchanged", 0)
            totals["total"] += len(batch)
            totals["batches"] += 1

            logger.info(
                "bulk_upsert: batch %d done — inserted=%d updated=%d unchanged=%d",
                batch_num,
                counts.get("inserted", 0),
                counts.get("updated", 0),
                counts.get("unchanged", 0),
            )

        except Exception as exc:
            logger.error(
                "bulk_upsert: batch %d failed — %s: %s — skipping and continuing",
                batch_num,
                type(exc).__name__,
                exc,
            )
            # Continue with remaining batches — partial success is better than abort
            continue

    logger.info(
        "bulk_upsert: complete — inserted=%d updated=%d unchanged=%d total=%d batches=%d",
        totals["inserted"],
        totals["updated"],
        totals["unchanged"],
        totals["total"],
        totals["batches"],
    )
    return totals


# ---------------------------------------------------------------------------
# Purge
# ---------------------------------------------------------------------------

async def purge_old_bids(retention_days: int = 12) -> int:
    """Delete rows from pncp_raw_bids older than retention_days.

    Calls the ``purge_old_bids`` Supabase RPC which returns the number
    of deleted rows.

    Args:
        retention_days: Rows with fetched_at older than this many days are deleted.

    Returns:
        Number of deleted rows (0 on error).
    """
    supabase = get_supabase()
    try:
        result = (
            supabase
            .rpc("purge_old_bids", {"p_retention_days": retention_days})
            .execute()
        )
        deleted = _extract_scalar(result, default=0)
        logger.info("purge_old_bids: deleted %d rows (retention=%d days)", deleted, retention_days)
        return deleted
    except Exception as exc:
        logger.error("purge_old_bids: failed — %s: %s", type(exc).__name__, exc)
        return 0


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _chunk(lst: list, size: int) -> list[list]:
    """Split a list into chunks of at most ``size`` items."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def _serialize_batch(batch: list[dict]) -> str:
    """Serialise batch to a JSON string.

    raw_payload inside each record is already a dict; json.dumps handles it.
    Any non-serialisable values are converted to strings as a safety net.
    """
    return json.dumps(batch, default=str, ensure_ascii=False)


def _extract_counts(result: Any, batch_num: int) -> dict[str, int]:
    """Extract inserted/updated/unchanged counts from the RPC result.

    The Supabase Python client returns results as a list of dicts.
    The RPC is expected to return a single-row result set.
    """
    try:
        data = result.data
        if isinstance(data, list) and data:
            row = data[0]
            return {
                "inserted": int(row.get("inserted", 0)),
                "updated": int(row.get("updated", 0)),
                "unchanged": int(row.get("unchanged", 0)),
            }
        # RPC returned nothing — treat as 0 counts (may happen on empty batches)
        logger.debug("bulk_upsert: batch %d RPC returned empty data", batch_num)
        return {"inserted": 0, "updated": 0, "unchanged": 0}
    except Exception as exc:
        logger.warning(
            "bulk_upsert: batch %d could not parse RPC counts — %s: %s",
            batch_num,
            type(exc).__name__,
            exc,
        )
        return {"inserted": 0, "updated": 0, "unchanged": 0}


def _extract_scalar(result: Any, default: int = 0) -> int:
    """Extract a scalar integer from an RPC result."""
    try:
        data = result.data
        if isinstance(data, (int, float)):
            return int(data)
        if isinstance(data, list) and data:
            row = data[0]
            if isinstance(row, (int, float)):
                return int(row)
            if isinstance(row, dict):
                # First value found in the dict
                val = next(iter(row.values()), default)
                return int(val)
        return default
    except Exception:
        return default
