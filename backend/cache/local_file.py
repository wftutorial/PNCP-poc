"""cache/local_file.py — Local file cache layer (L3, 24h TTL emergency fallback).

HARDEN-018: Enforces 200MB max size with oldest-first eviction.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from cache.enums import (
    LOCAL_CACHE_DIR, LOCAL_CACHE_TTL_HOURS,
    LOCAL_CACHE_MAX_SIZE_MB, LOCAL_CACHE_TARGET_SIZE_MB,
)

logger = logging.getLogger(__name__)


def _check_cache_dir_size() -> int:
    """HARDEN-018 AC1/AC2: Check local cache dir size, evict oldest files if > 200MB.

    Returns the number of files deleted.
    """
    if not LOCAL_CACHE_DIR.exists():
        return 0

    files = list(LOCAL_CACHE_DIR.glob("*.json"))
    if not files:
        return 0

    file_stats = []
    total_size = 0
    for f in files:
        try:
            st = f.stat()
            file_stats.append((f, st.st_mtime, st.st_size))
            total_size += st.st_size
        except OSError:
            continue

    max_bytes = LOCAL_CACHE_MAX_SIZE_MB * 1024 * 1024
    if total_size <= max_bytes:
        return 0

    target_bytes = LOCAL_CACHE_TARGET_SIZE_MB * 1024 * 1024
    file_stats.sort(key=lambda x: x[1])  # oldest first

    deleted = 0
    for file_path, _mtime, size in file_stats:
        if total_size <= target_bytes:
            break
        try:
            file_path.unlink()
            total_size -= size
            deleted += 1
        except OSError as e:
            logger.warning(f"HARDEN-018: Failed to evict cache file {file_path}: {e}")

    if deleted > 0:
        logger.info(
            f"HARDEN-018: Evicted {deleted} oldest cache files, "
            f"dir now ~{total_size / (1024 * 1024):.1f}MB"
        )

    return deleted


def _save_to_local(cache_key: str, results: list, sources: list) -> None:
    """Save to local JSON file (Level 3)."""
    LOCAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _check_cache_dir_size()

    cache_data = {
        "results": results,
        "sources_json": sources,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    cache_file = LOCAL_CACHE_DIR / f"{cache_key[:32]}.json"
    cache_file.write_text(json.dumps(cache_data), encoding="utf-8")


def _get_from_local(cache_key: str) -> Optional[dict]:
    """Read from local JSON file (Level 3).

    A-03 AC1: Validates TTL — returns None if fetched_at + 24h < now(UTC).
    A-03 AC2: Includes _cache_age_hours in returned dict when valid.
    """
    cache_file = LOCAL_CACHE_DIR / f"{cache_key[:32]}.json"
    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    fetched_at_str = data.get("fetched_at")
    if not fetched_at_str:
        return None

    try:
        fetched_at = datetime.fromisoformat(fetched_at_str.replace("Z", "+00:00"))
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600
    except (ValueError, TypeError):
        return None

    if age_hours > LOCAL_CACHE_TTL_HOURS:
        return None

    data["_cache_age_hours"] = round(age_hours, 1)
    return data


def cleanup_local_cache() -> int:
    """Delete local cache files older than LOCAL_CACHE_TTL_HOURS (AC8).

    Returns the number of files deleted.
    """
    if not LOCAL_CACHE_DIR.exists():
        return 0

    now = datetime.now(timezone.utc)
    deleted_count = 0

    for file_path in LOCAL_CACHE_DIR.glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
            age_hours = (now - mtime).total_seconds() / 3600

            if age_hours > LOCAL_CACHE_TTL_HOURS:
                file_path.unlink()
                deleted_count += 1
        except OSError as e:
            logger.warning(f"Failed to clean up cache file {file_path}: {e}")

    if deleted_count > 0:
        logger.info(f"Cache cleanup: deleted {deleted_count} expired local files")

    _check_cache_dir_size()

    return deleted_count


def get_local_cache_stats() -> dict:
    """Get statistics about local cache files for health check (AC7)."""
    if not LOCAL_CACHE_DIR.exists():
        return {"files_count": 0, "total_size_mb": 0.0}

    files = list(LOCAL_CACHE_DIR.glob("*.json"))
    total_size = sum(f.stat().st_size for f in files if f.exists())

    return {
        "files_count": len(files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
    }
