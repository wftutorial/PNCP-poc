"""Cache cron jobs: cleanup, refresh, warmup, and coverage check."""

import asyncio
import logging
import os
from datetime import date, datetime, timedelta, timezone

from cron._loop import cron_loop, is_cb_or_connection_error
from cron.pncp_status import get_pncp_cron_status

logger = logging.getLogger(__name__)

# Intervals
CLEANUP_INTERVAL_SECONDS = 6 * 60 * 60
CACHE_REFRESH_INTERVAL_SECONDS = 4 * 60 * 60
COVERAGE_CHECK_INTERVAL = int(os.environ.get("ENSURE_COVERAGE_INTERVAL_HOURS", "1")) * 3600

# ISSUE-015: Critical sector+UF combos always warmed regardless of popularity.
MANDATORY_WARMUP_COMBOS = [
    {"setor_id": "engenharia", "ufs": ["SP"]},
    {"setor_id": "engenharia", "ufs": ["SC", "PR", "RS"]},
    {"setor_id": "engenharia", "ufs": ["MG", "RJ", "ES"]},
    {"setor_id": "vestuario", "ufs": ["SP"]},
    {"setor_id": "medicamentos", "ufs": ["SP"]},
    {"setor_id": "informatica", "ufs": ["SP"]},
    {"setor_id": "servicos_prediais", "ufs": ["SP"]},
    {"setor_id": "software_desenvolvimento", "ufs": ["SP"]},
    {"setor_id": "software_licencas", "ufs": ["SP"]},
]


# ---------------------------------------------------------------------------
# Cache cleanup
# ---------------------------------------------------------------------------

async def _do_cache_cleanup() -> dict:
    """Run local cache + filter stats cleanup."""
    from cache.local_file import cleanup_local_cache
    deleted = cleanup_local_cache()
    try:
        from filter.stats import filter_stats_tracker, discard_rate_tracker
        fs = filter_stats_tracker.cleanup_old()
        dr = discard_rate_tracker.cleanup_old()
        if fs or dr:
            logger.info("Filter stats cleanup: %d filter, %d discard entries removed", fs, dr)
    except Exception as e:
        logger.warning("Filter stats cleanup failed: %s", e)
    return {"deleted": deleted}


async def start_cache_cleanup_task() -> asyncio.Task:
    task = asyncio.create_task(
        cron_loop("Cache cleanup", _do_cache_cleanup, CLEANUP_INTERVAL_SECONDS,
                  initial_delay=CLEANUP_INTERVAL_SECONDS),
        name="cache_cleanup",
    )
    logger.info("Cache cleanup background task started (interval: 6h)")
    return task


# ---------------------------------------------------------------------------
# Cache refresh (SWR stale entries)
# ---------------------------------------------------------------------------

async def refresh_stale_cache_entries() -> dict:
    """GTM-ARCH-002 AC5: Refresh stale HOT/WARM cache entries."""
    from cache.admin import get_stale_entries_for_refresh
    from cache.swr import trigger_background_revalidation

    try:
        entries = await get_stale_entries_for_refresh(batch_size=25)
        if not entries:
            return {"status": "no_stale_entries", "refreshed": 0}

        refreshed = failed = 0
        for entry in entries:
            try:
                sp = entry.get("search_params", {})
                dispatched = await trigger_background_revalidation(
                    user_id=entry["user_id"],
                    params=sp,
                    request_data={
                        "ufs": sp.get("ufs", []),
                        "data_inicial": (date.today() - timedelta(days=10)).isoformat(),
                        "data_final": date.today().isoformat(),
                        "modalidades": sp.get("modalidades"),
                    },
                )
                if dispatched:
                    refreshed += 1
                await asyncio.sleep(2)
            except Exception as e:
                failed += 1
                logger.debug("Cache refresh dispatch failed for %s: %s", entry.get("params_hash", "?")[:12], e)

        logger.info("Cache refresh cycle: %d dispatched, %d failed out of %d stale entries", refreshed, failed, len(entries))
        return {"status": "completed", "refreshed": refreshed, "failed": failed, "total": len(entries)}
    except Exception as e:
        logger.error("Cache refresh error: %s", e, exc_info=True)
        return {"status": "error", "error": str(e), "refreshed": 0}


async def start_cache_refresh_task() -> asyncio.Task:
    async def _loop():
        await asyncio.sleep(60)
        while True:
            try:
                from config import CACHE_REFRESH_ENABLED
                if not CACHE_REFRESH_ENABLED:
                    await asyncio.sleep(CACHE_REFRESH_INTERVAL_SECONDS)
                    continue
                result = await refresh_stale_cache_entries()
                logger.info("Cache refresh cycle: %s at %s", result, datetime.now(timezone.utc).isoformat())
                await asyncio.sleep(CACHE_REFRESH_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                logger.info("Cache refresh task cancelled")
                break
            except Exception as e:
                logger.error("Cache refresh loop error: %s", e, exc_info=True)
                await asyncio.sleep(60)

    task = asyncio.create_task(_loop(), name="cache_refresh")
    logger.info("Cache refresh background task started (interval: 4h)")
    return task


# ---------------------------------------------------------------------------
# Warmup: prioritized UFs, specific combos, top params, startup+periodic
# ---------------------------------------------------------------------------

async def _get_prioritized_ufs(all_ufs: list[str]) -> list[str]:
    """CRIT-055 AC2: UFs ordered by search history popularity."""
    from cache.admin import get_popular_ufs_from_sessions
    from config import DEFAULT_UF_PRIORITY

    try:
        popular = await get_popular_ufs_from_sessions(days=7)
    except Exception:
        popular = []

    if not popular:
        ordered = [uf for uf in DEFAULT_UF_PRIORITY if uf in set(all_ufs)]
        return ordered + [uf for uf in all_ufs if uf not in set(ordered)]

    all_set = set(all_ufs)
    ordered = [uf for uf in popular if uf in all_set]
    return ordered + [uf for uf in all_ufs if uf not in set(ordered)]


async def warmup_specific_combinations(ufs: list[str], sectors: list[str]) -> dict:
    """CRIT-055 AC1/AC2/AC4: Pre-warm cache for sector+UF combinations."""
    from cache.swr import trigger_background_revalidation
    from config import (
        WARMUP_BATCH_DELAY_SECONDS, WARMUP_RATE_LIMIT_RPS,
        WARMUP_PNCP_DEGRADED_PAUSE_S, WARMUP_UF_BATCH_SIZE,
    )

    prioritized_ufs = await _get_prioritized_ufs(ufs)
    dispatched = skipped = failed = paused = 0
    total = len(sectors) * len(prioritized_ufs)
    ufs_covered: set[str] = set()
    rate_interval = 1.0 / WARMUP_RATE_LIMIT_RPS if WARMUP_RATE_LIMIT_RPS > 0 else 0.5

    logger.info(
        "CRIT-055 warmup: starting %d combinations (%d sectors x %d UFs, rate=%.1f rps, batch=%d)",
        total, len(sectors), len(prioritized_ufs), WARMUP_RATE_LIMIT_RPS, WARMUP_UF_BATCH_SIZE,
    )

    for sector_id in sectors:
        for i, uf in enumerate(prioritized_ufs):
            pncp_status = get_pncp_cron_status()
            if pncp_status.get("status") in ("degraded", "down"):
                logger.warning("CRIT-055 warmup: PNCP %s — pausing %.0fs", pncp_status["status"], WARMUP_PNCP_DEGRADED_PAUSE_S)
                paused += 1
                await asyncio.sleep(WARMUP_PNCP_DEGRADED_PAUSE_S)

            try:
                params = {"setor_id": sector_id, "ufs": [uf], "status": None, "modalidades": None, "modo_busca": None}
                request_data = {
                    "ufs": [uf],
                    "data_inicial": (date.today() - timedelta(days=10)).isoformat(),
                    "data_final": date.today().isoformat(),
                    "modalidades": None,
                }
                ok = await trigger_background_revalidation(
                    user_id="00000000-0000-0000-0000-000000000000", params=params, request_data=request_data,
                )
                if ok:
                    dispatched += 1
                    ufs_covered.add(uf)
                else:
                    skipped += 1
                await asyncio.sleep(rate_interval)
            except Exception as e:
                failed += 1
                logger.warning("CRIT-055 warmup: failed sector=%s uf=%s: %s", sector_id, uf, e)

            if (i + 1) % WARMUP_UF_BATCH_SIZE == 0 and i + 1 < len(prioritized_ufs):
                await asyncio.sleep(WARMUP_BATCH_DELAY_SECONDS)

    try:
        from metrics import WARMUP_COVERAGE_RATIO
        coverage = len(ufs_covered) / len(prioritized_ufs) if prioritized_ufs else 0
        WARMUP_COVERAGE_RATIO.set(coverage)
    except Exception:
        pass

    logger.info(
        "CRIT-055 warmup complete: %d/%d dispatched, %d failed, coverage: %d/%d UFs, paused %d times",
        dispatched, total, failed, len(ufs_covered), len(prioritized_ufs), paused,
    )
    return {
        "dispatched": dispatched, "skipped": skipped, "failed": failed,
        "paused": paused, "total": total,
        "ufs_covered": len(ufs_covered), "ufs_total": len(prioritized_ufs),
    }


async def warmup_top_params() -> dict:
    """GTM-ARCH-002 AC6/AC7: Pre-warm top 10 popular sector+UF combinations."""
    from cache.admin import get_top_popular_params
    from cache.swr import trigger_background_revalidation

    try:
        top_params = await get_top_popular_params(limit=30)

        def _combo_key(params: dict) -> tuple:
            return (params.get("setor_id", ""), tuple(sorted(params.get("ufs", []))))

        mandatory_keys = {_combo_key(c) for c in MANDATORY_WARMUP_COMBOS}
        popular_deduped = [p for p in top_params if _combo_key(p) not in mandatory_keys]
        all_params = list(MANDATORY_WARMUP_COMBOS) + popular_deduped

        if not all_params:
            logger.info("Warmup: no params found to pre-warm")
            return {"status": "no_params", "warmed": 0}

        logger.info(
            "Warmup: %d mandatory + %d popular combos (%d total, %d popular deduped)",
            len(MANDATORY_WARMUP_COMBOS), len(popular_deduped), len(all_params), len(top_params) - len(popular_deduped),
        )

        warmed = 0
        for params in all_params:
            try:
                dispatched = await trigger_background_revalidation(
                    user_id="00000000-0000-0000-0000-000000000000",
                    params=params,
                    request_data={
                        "ufs": params.get("ufs", []),
                        "data_inicial": (date.today() - timedelta(days=10)).isoformat(),
                        "data_final": date.today().isoformat(),
                        "modalidades": params.get("modalidades"),
                    },
                )
                if dispatched:
                    warmed += 1
                await asyncio.sleep(1)
            except Exception as e:
                logger.debug("Warmup dispatch failed: %s", e)

        logger.info("Warmup: %d/%d params enqueued", warmed, len(all_params))
        return {"status": "completed", "warmed": warmed, "total": len(all_params)}
    except Exception as e:
        logger.error("Warmup error: %s", e, exc_info=True)
        return {"status": "error", "error": str(e), "warmed": 0}


async def _warmup_startup_and_periodic(
    ufs: list[str], sectors: list[str], delay_seconds: int,
) -> None:
    """CRIT-055: Startup warmup + periodic re-warm loop."""
    from config import WARMUP_PERIODIC_INTERVAL_HOURS
    try:
        logger.info("CRIT-055 warmup: waiting %ds before startup warm-up", delay_seconds)
        await asyncio.sleep(delay_seconds)
        result = await warmup_specific_combinations(ufs, sectors)
        logger.info("CRIT-055 warmup: startup warm-up finished: %s", result)
        interval_seconds = WARMUP_PERIODIC_INTERVAL_HOURS * 3600
        while True:
            await asyncio.sleep(interval_seconds)
            logger.info("CRIT-055 warmup: periodic re-warm starting")
            periodic_result = await warmup_top_params()
            logger.info("CRIT-055 warmup: periodic re-warm finished: %s", periodic_result)
    except asyncio.CancelledError:
        logger.info("CRIT-055 warmup: task cancelled (shutdown)")
    except Exception as e:
        logger.error("CRIT-055 warmup: task failed: %s", e, exc_info=True)


async def start_warmup_task() -> asyncio.Task:
    """CRIT-055: Start startup + periodic cache warm-up."""
    from config import WARMUP_ENABLED, WARMUP_UFS, WARMUP_SECTORS, WARMUP_STARTUP_DELAY_SECONDS
    if not WARMUP_ENABLED:
        logger.info("CRIT-055 warmup: disabled via WARMUP_ENABLED=false — skipping")
        return asyncio.create_task(asyncio.sleep(0), name="warmup_noop")
    task = asyncio.create_task(
        _warmup_startup_and_periodic(WARMUP_UFS, WARMUP_SECTORS, WARMUP_STARTUP_DELAY_SECONDS),
        name="cache_warmup",
    )
    logger.info("CRIT-055 warmup: task started — delay=%ds, sectors=%s, ufs=%d total",
                WARMUP_STARTUP_DELAY_SECONDS, WARMUP_SECTORS, len(WARMUP_UFS))
    return task


# ---------------------------------------------------------------------------
# Coverage check (CRIT-081)
# ---------------------------------------------------------------------------

async def _get_cache_entry_age(sector_id: str, uf: str) -> float | None:
    """CRIT-081: Age in hours of most recent cache entry for sector+UF."""
    try:
        from supabase_client import get_supabase, sb_execute

        sb = get_supabase()
        resp = await sb_execute(
            sb.table("search_results_cache")
            .select("fetched_at, search_params")
            .eq("search_params->>setor_id", sector_id)
            .order("fetched_at", desc=True)
            .limit(50)
        )
        if not resp.data:
            return None

        now = datetime.now(timezone.utc)
        for row in resp.data:
            sp = row.get("search_params", {})
            if not isinstance(sp, dict):
                continue
            if uf not in (sp.get("ufs") or []):
                continue
            fetched_at_raw = row.get("fetched_at")
            if not fetched_at_raw:
                continue
            try:
                fetched_at = datetime.fromisoformat(str(fetched_at_raw).replace("Z", "+00:00"))
                if fetched_at.tzinfo is None:
                    fetched_at = fetched_at.replace(tzinfo=timezone.utc)
                return (now - fetched_at).total_seconds() / 3600
            except (ValueError, TypeError):
                continue
        return None
    except Exception as e:
        logger.debug("CRIT-081: _get_cache_entry_age error for %s:%s: %s", sector_id, uf, e)
        return None


async def ensure_minimum_cache_coverage() -> dict:
    """CRIT-081: Ensure all active sector*UF combos have fresh cache (<12h)."""
    from cache.swr import trigger_background_revalidation
    from sectors import SECTORS
    from config import ALL_BRAZILIAN_UFS, WARMUP_ENABLED

    if not WARMUP_ENABLED:
        return {"deficit": 0, "dispatched": 0, "skipped": True}

    deficit = dispatched = 0
    try:
        prioritized = await _get_prioritized_ufs(ALL_BRAZILIAN_UFS)
        top_ufs = prioritized[:5]
        all_sectors = list(SECTORS.values())

        for sector in all_sectors:
            for uf in top_ufs:
                age_hours = await _get_cache_entry_age(sector.id, uf)
                if age_hours is None or age_hours > 12:
                    deficit += 1
                    try:
                        params = {"setor_id": sector.id, "ufs": [uf], "status": None, "modalidades": None, "modo_busca": None}
                        request_data = {
                            "ufs": [uf],
                            "data_inicial": (date.today() - timedelta(days=10)).isoformat(),
                            "data_final": date.today().isoformat(),
                            "modalidades": None,
                        }
                        ok = await trigger_background_revalidation(
                            user_id="00000000-0000-0000-0000-000000000000", params=params, request_data=request_data,
                        )
                        if ok:
                            dispatched += 1
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.warning("CRIT-081: coverage revalidation failed for %s:%s: %s", sector.id, uf, e)

        logger.info("CRIT-081: coverage check complete: deficit=%d, dispatched=%d, sectors=%d, ufs=%d",
                     deficit, dispatched, len(all_sectors), len(top_ufs))
        try:
            from metrics import WARMUP_COVERAGE_RATIO
            total = len(all_sectors) * len(top_ufs)
            WARMUP_COVERAGE_RATIO.set((total - deficit) / total if total > 0 else 0)
        except Exception:
            pass
    except Exception as e:
        logger.error("CRIT-081: ensure_minimum_cache_coverage failed: %s", e, exc_info=True)

    return {"deficit": deficit, "dispatched": dispatched}


async def start_coverage_check_task() -> asyncio.Task:
    task = asyncio.create_task(
        cron_loop("CRIT-081 coverage", ensure_minimum_cache_coverage, COVERAGE_CHECK_INTERVAL, initial_delay=300),
        name="coverage_check",
    )
    logger.info("CRIT-081: Coverage check task started (interval: %ds)", COVERAGE_CHECK_INTERVAL)
    return task
