"""Multi-source consolidation orchestrator.

TD-008: Extracted from consolidation.py as part of DEBT-07 module split.
Contains ConsolidationService — orchestrates parallel fetching, deduplication
(delegated to DeduplicationEngine), and result assembly.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set

from utils.error_reporting import report_error
from clients.base import SourceAdapter, SourceStatus, UnifiedProcurement, SourceError
from source_config.sources import source_health_registry
from metrics import FETCH_DURATION, API_ERRORS, SOURCES_BIDS_FETCHED
from telemetry import get_tracer, optional_span
from bulkhead import BulkheadAcquireTimeoutError, SourceBulkhead, get_bulkhead

from consolidation.priority_resolver import (
    AllSourcesFailedError,
    ConsolidationResult,
    SourceResult,
)
from consolidation.dedup import DeduplicationEngine
from consolidation.source_pipeline import SourceFetcher

logger = logging.getLogger(__name__)

# F-02 AC13: Tracer for per-source fetch spans
_tracer = get_tracer("consolidation")


class ConsolidationService:
    """
    Orchestrates parallel fetching from multiple procurement sources.

    Features:
    - Parallel fetch via asyncio.gather
    - Per-source and global timeouts
    - Deduplication by dedup_key (keeps highest-priority source) via DeduplicationEngine
    - Automatic conversion to legacy format
    - Graceful degradation (partial results on partial failure)
    - Progress callback support
    """

    # GTM-STAB: Failover timeout reduced from 120→80 — tighter per-source budget
    FAILOVER_TIMEOUT_PER_SOURCE = 80
    # STORY-271 AC2: Degraded global timeout 110→100 — 15s buffer before GUNICORN_TIMEOUT=115s
    DEGRADED_GLOBAL_TIMEOUT = 100
    # Timeout for ComprasGov last-resort fallback (AC15)
    FALLBACK_TIMEOUT = 40

    def __init__(
        self,
        adapters: Dict[str, SourceAdapter],
        timeout_per_source: int = 25,
        timeout_global: int = 60,
        fail_on_all_errors: bool = True,
        fallback_adapter: Optional[SourceAdapter] = None,
        bulkheads: Optional[Dict[str, SourceBulkhead]] = None,
    ):
        """
        Initialize ConsolidationService.

        Args:
            adapters: Dict mapping source code to SourceAdapter instance
            timeout_per_source: Max seconds per source fetch
            timeout_global: Max seconds for entire consolidation
            fail_on_all_errors: Raise if all sources fail
            fallback_adapter: Optional ComprasGov adapter used as last-resort
                fallback when all other sources fail (AC15).
            bulkheads: Optional dict mapping source code to SourceBulkhead.
                When provided, each source fetch is wrapped with the
                bulkhead's semaphore for concurrency isolation (STORY-296).
        """
        # GTM-FIX-024 T5: Fail-fast contract validation
        required_attrs = ("code", "metadata", "fetch", "health_check", "close")
        for adapter_key, adapter in adapters.items():
            missing = [attr for attr in required_attrs if not hasattr(adapter, attr)]
            if missing:
                raise TypeError(
                    f"Adapter '{adapter_key}' ({type(adapter).__name__}) missing required "
                    f"attributes: {', '.join(missing)}. Must implement SourceAdapter interface."
                )
        if fallback_adapter is not None:
            missing = [attr for attr in required_attrs if not hasattr(fallback_adapter, attr)]
            if missing:
                raise TypeError(
                    f"Fallback adapter ({type(fallback_adapter).__name__}) missing required "
                    f"attributes: {', '.join(missing)}. Must implement SourceAdapter interface."
                )

        self._adapters = adapters
        self._timeout_per_source = timeout_per_source
        self._timeout_global = timeout_global
        self._fail_on_all_errors = fail_on_all_errors
        self._fallback_adapter = fallback_adapter
        self._bulkheads = bulkheads or {}
        self._last_effective_global_timeout: Optional[int] = None
        self._fetcher = SourceFetcher(
            timeout_per_source=self._timeout_per_source,
            bulkheads=self._bulkheads,
        )

        if timeout_per_source > timeout_global * 0.8:
            logger.warning(
                f"Timeout near-inversion: timeout_per_source ({timeout_per_source}s) > "
                f"80% of timeout_global ({timeout_global}s). Sources may starve each other."
            )

    async def fetch_all(
        self,
        data_inicial: str,
        data_final: str,
        ufs: Optional[Set[str]] = None,
        on_source_complete: Optional[Callable] = None,
        on_early_return: Optional[Callable] = None,
        on_source_done: Optional[Callable] = None,
    ) -> ConsolidationResult:
        """
        Fetch from all enabled sources in parallel, deduplicate, and return.

        Implements multi-source orchestration with:
        - Health-aware timeout adjustments (AC13, AC17)
        - Degraded mode with partial results (AC14)
        - ComprasGov last-resort fallback (AC15)
        - Detailed per-source status reporting (AC16)
        - GTM-STAB-003 AC3: Early return when >=80% UFs responded and elapsed >80s
        """
        start_time = time.time()
        requested_ufs = set(ufs) if ufs else set()

        from middleware import search_id_var
        _search_id = search_id_var.get("-")
        logger.info(f"Consolidation started [search={_search_id}] sources={list(self._adapters.keys())}")

        if not self._adapters:
            return ConsolidationResult(
                records=[],
                total_before_dedup=0,
                total_after_dedup=0,
                duplicates_removed=0,
                source_results=[],
                elapsed_ms=0,
            )

        # AC12/AC17: Check PNCP health to determine effective timeouts
        pncp_status = source_health_registry.get_status("PNCP")
        pncp_is_degraded = pncp_status in ("degraded", "down")

        effective_global_timeout = self._timeout_global
        if pncp_is_degraded:
            effective_global_timeout = max(
                self._timeout_global, self.DEGRADED_GLOBAL_TIMEOUT
            )
            logger.debug(
                f"[CONSOLIDATION] PNCP is {pncp_status} — "
                f"global timeout increased to {effective_global_timeout}s"
            )
        self._last_effective_global_timeout = effective_global_timeout

        # Build per-source timeouts with health-aware adjustments (AC13)
        source_timeouts: Dict[str, int] = {}
        for code in self._adapters:
            if pncp_is_degraded and code != "PNCP":
                source_timeouts[code] = self.FAILOVER_TIMEOUT_PER_SOURCE
            else:
                source_timeouts[code] = self._timeout_per_source

        from config import EARLY_RETURN_THRESHOLD_PCT, EARLY_RETURN_TIME_S

        source_partial_collectors: Dict[str, List[UnifiedProcurement]] = {
            code: [] for code in self._adapters
        }

        source_results_map: Dict[str, dict] = {}
        early_return_triggered = False

        source_tasks: Dict[str, asyncio.Task] = {}
        for code, adapter in self._adapters.items():
            task = asyncio.create_task(
                self._fetcher.wrap_source(
                    code, adapter,
                    data_inicial=data_inicial,
                    data_final=data_final,
                    ufs=ufs,
                    timeout=source_timeouts[code],
                    partial_collector_out=source_partial_collectors[code],
                ),
                name=f"source_{code}",
            )
            source_tasks[code] = task

        pending_tasks = set(source_tasks.values())
        deadline = start_time + effective_global_timeout

        while pending_tasks:
            remaining_time = deadline - time.time()
            if remaining_time <= 0:
                logger.warning(
                    f"[CONSOLIDATION] Global timeout ({effective_global_timeout}s) reached — collecting partial results"
                )
                for task in pending_tasks:
                    task.cancel()
                await asyncio.gather(*pending_tasks, return_exceptions=True)
                break

            check_interval = min(2.0, remaining_time)
            done, pending_tasks = await asyncio.wait(
                pending_tasks, timeout=check_interval, return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                try:
                    result = task.result()
                except (asyncio.CancelledError, Exception):
                    result = None
                if isinstance(result, dict):
                    code = result["code"]
                    source_results_map[code] = result

                    if on_source_done:
                        try:
                            _status = result.get("status", "error")
                            _records = result.get("records", [])
                            _legacy = [r.to_legacy_format() for r in _records if hasattr(r, "to_legacy_format")]
                            _duration = result.get("duration_ms", 0)
                            _error = result.get("error")

                            cb_result = on_source_done(
                                code, _status, _legacy, _duration, _error,
                            )
                            if asyncio.iscoroutine(cb_result):
                                await cb_result
                        except Exception as cb_err:
                            logger.warning(
                                f"[CONSOLIDATION] on_source_done callback error for {code}: {cb_err}"
                            )
                elif result is not None:
                    logger.warning(
                        f"[CONSOLIDATION] Unexpected non-dict result from task: "
                        f"type={type(result).__name__} value={str(result)[:200]}"
                    )

            # GTM-STAB-003 AC3: Check early return condition
            if pending_tasks and requested_ufs and not early_return_triggered:
                elapsed_s = time.time() - start_time
                if elapsed_s >= EARLY_RETURN_TIME_S:
                    seen_ufs = set()
                    for collector in source_partial_collectors.values():
                        for record in collector:
                            uf = getattr(record, "uf", None) or ""
                            if uf:
                                seen_ufs.add(uf)
                    for sr_data in source_results_map.values():
                        for record in sr_data.get("records", []):
                            uf = getattr(record, "uf", None) or ""
                            if uf:
                                seen_ufs.add(uf)

                    completed_ufs = seen_ufs & requested_ufs
                    total_requested = len(requested_ufs)
                    completion_pct = len(completed_ufs) / total_requested if total_requested > 0 else 0

                    if completion_pct >= EARLY_RETURN_THRESHOLD_PCT and completion_pct < 1.0:
                        pending_uf_list = sorted(requested_ufs - completed_ufs)
                        completed_uf_list = sorted(completed_ufs)
                        early_return_triggered = True

                        logger.info(
                            "early_return_triggered",
                            extra={
                                "ufs_completed": completed_uf_list,
                                "ufs_pending": pending_uf_list,
                                "elapsed_s": round(elapsed_s, 1),
                                "completion_pct": round(completion_pct * 100, 1),
                            },
                        )

                        for task in pending_tasks:
                            task.cancel()
                        await asyncio.gather(*pending_tasks, return_exceptions=True)

                        if on_early_return:
                            try:
                                cb_result = on_early_return(completed_uf_list, pending_uf_list)
                                if asyncio.iscoroutine(cb_result):
                                    await cb_result
                            except Exception as e:
                                logger.warning(f"on_early_return callback error: {e}")
                        break

        # For any source without a result (timed out or cancelled), mark as timeout
        for code in self._adapters:
            if code not in source_results_map:
                source_results_map[code] = {
                    "code": code,
                    "records": [],
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "status": "timeout",
                    "error": (
                        f"Early return (elapsed {time.time() - start_time:.0f}s)"
                        if early_return_triggered
                        else f"Global timeout ({effective_global_timeout}s)"
                    ),
                }

        # Collect results and metrics, update health registry (AC12)
        all_records: List[UnifiedProcurement] = []
        source_results: List[SourceResult] = []
        source_errors: Dict[str, str] = {}
        failed_sources: List[str] = []

        for code in self._adapters:
            result = source_results_map.get(code)
            result_status = result.get("status") if result else None
            has_records = result_status in ("success", "partial")

            if result and has_records:
                records = result["records"]
                all_records.extend(records)
                if result_status == "success":
                    source_health_registry.record_success(code)
                else:
                    source_health_registry.record_failure(code)
                    failed_sources.append(code)
                    source_errors[code] = result.get("error", "Partial timeout")
                sr = SourceResult(
                    source_code=code,
                    record_count=len(records),
                    duration_ms=result["duration_ms"],
                    error=result.get("error"),
                    status=result_status,
                )
                source_results.append(sr)
                if on_source_complete:
                    try:
                        on_source_complete(code, len(records), None)
                    except Exception as e:
                        logger.warning(f"on_source_complete callback error for {code}: {e}")
            else:
                error_msg = "Global timeout"
                status = "timeout"
                if result:
                    error_msg = result.get("error", "Unknown error")
                    status = result.get("status", "error")
                source_errors[code] = error_msg
                failed_sources.append(code)
                source_health_registry.record_failure(code)
                sr = SourceResult(
                    source_code=code,
                    record_count=0,
                    duration_ms=result["duration_ms"] if result else 0,
                    error=error_msg,
                    status=status,
                )
                source_results.append(sr)
                if on_source_complete:
                    try:
                        on_source_complete(code, 0, error_msg)
                    except Exception as e:
                        logger.warning(f"on_source_complete callback error for {code}: {e}")

        # AC15: ComprasGov last-resort fallback when ALL sources fail
        fallback_used = False
        if not all_records and source_errors and self._fallback_adapter is not None:
            fallback_code = getattr(self._fallback_adapter, "code", "unknown_fallback")
            already_tried = fallback_code in self._adapters
            if not already_tried:
                logger.debug(
                    f"[CONSOLIDATION] All sources failed — attempting {fallback_code} "
                    f"as last-resort fallback (timeout={self.FALLBACK_TIMEOUT}s)"
                )
                fallback_result = await self._fetcher.wrap_source(
                    fallback_code,
                    self._fallback_adapter,
                    data_inicial=data_inicial,
                    data_final=data_final,
                    ufs=ufs,
                    timeout=self.FALLBACK_TIMEOUT,
                )
                if fallback_result.get("status") == "success":
                    fb_records = fallback_result["records"]
                    all_records.extend(fb_records)
                    source_health_registry.record_success(fallback_code)
                    sr = SourceResult(
                        source_code=fallback_code,
                        record_count=len(fb_records),
                        duration_ms=fallback_result["duration_ms"],
                        status="success",
                    )
                    source_results.append(sr)
                    fallback_used = True
                    logger.debug(
                        f"[CONSOLIDATION] Fallback {fallback_code} returned "
                        f"{len(fb_records)} records"
                    )
                    if on_source_complete:
                        try:
                            on_source_complete(fallback_code, len(fb_records), None)
                        except Exception as e:
                            logger.warning(f"on_source_complete callback error for {fallback_code}: {e}")
                else:
                    fb_error = fallback_result.get("error", "Unknown error")
                    source_errors[fallback_code] = fb_error
                    source_health_registry.record_failure(fallback_code)
                    sr = SourceResult(
                        source_code=fallback_code,
                        record_count=0,
                        duration_ms=fallback_result.get("duration_ms", 0),
                        error=fb_error,
                        status=fallback_result.get("status", "error"),
                    )
                    source_results.append(sr)
                    logger.warning(
                        f"[CONSOLIDATION] Fallback {fallback_code} also failed: "
                        f"{fb_error}"
                    )

        # AC14: Determine partial/degradation state
        has_data = len(all_records) > 0
        has_failures = len(failed_sources) > 0
        is_partial = has_data and has_failures

        if early_return_triggered and has_data:
            is_partial = True

        degradation_reason: Optional[str] = None

        if early_return_triggered:
            degradation_reason = "early_return_timeout"
        elif is_partial:
            degradation_reason = (
                f"Partial results: sources failed: {', '.join(failed_sources)}"
            )

        if is_partial:
            logger.info(
                f"[CONSOLIDATION] Degraded mode — {degradation_reason}"
            )

        if not has_data and source_errors and self._fail_on_all_errors:
            raise AllSourcesFailedError(source_errors)

        # Deduplicate via DeduplicationEngine
        total_before = len(all_records)
        dedup_engine = DeduplicationEngine(self._adapters)
        deduped = dedup_engine.run(all_records)
        total_after = len(deduped)

        # Convert to legacy format
        legacy_records = [r.to_legacy_format() for r in deduped]

        elapsed = int((time.time() - start_time) * 1000)

        # GTM-STAB-003 AC3: Build UF completion lists
        seen_ufs_in_results = set()
        for record in all_records:
            uf = getattr(record, "uf", None) or ""
            if uf:
                seen_ufs_in_results.add(uf)
        completed_ufs_list = sorted(seen_ufs_in_results & requested_ufs) if requested_ufs else sorted(seen_ufs_in_results)
        pending_ufs_list = sorted(requested_ufs - seen_ufs_in_results) if requested_ufs else []

        # STORY-350 AC3: Increment per-source bids fetched counter
        for sr in source_results:
            if sr.record_count > 0:
                uf_counts: Dict[str, int] = {}
                for record in all_records:
                    src = getattr(record, "source_code", None) or getattr(record, "fonte", "")
                    if str(src).lower() == sr.source_code.lower():
                        uf = getattr(record, "uf", "") or "unknown"
                        uf_counts[uf] = uf_counts.get(uf, 0) + 1
                if uf_counts:
                    for uf, count in uf_counts.items():
                        SOURCES_BIDS_FETCHED.labels(source=sr.source_code, uf=uf).inc(count)
                else:
                    SOURCES_BIDS_FETCHED.labels(source=sr.source_code, uf="all").inc(sr.record_count)

        logger.info(
            f"[CONSOLIDATION] Complete: {total_before} raw -> {total_after} deduped "
            f"({total_before - total_after} duplicates removed) in {elapsed}ms"
            f"{' [PARTIAL]' if is_partial else ''}"
            f"{' [EARLY_RETURN]' if early_return_triggered else ''}"
            f"{' [FALLBACK]' if fallback_used else ''}"
        )

        return ConsolidationResult(
            records=legacy_records,
            total_before_dedup=total_before,
            total_after_dedup=total_after,
            duplicates_removed=total_before - total_after,
            source_results=source_results,
            elapsed_ms=elapsed,
            is_partial=is_partial,
            degradation_reason=degradation_reason,
            ufs_completed=completed_ufs_list,
            ufs_pending=pending_ufs_list,
        )


    # _fetch_source, _wrap_source, _wrap_source_inner
    # moved to consolidation.source_pipeline.SourceFetcher (TD-008 DEBT-07 split)

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Run health checks on all adapters in parallel.

        Returns:
            Dict mapping source code to health status info
        """
        results = {}

        async def check_one(code: str, adapter: SourceAdapter):
            start = time.time()
            try:
                status = await asyncio.wait_for(adapter.health_check(), timeout=5.0)
                duration = int((time.time() - start) * 1000)
                return code, {
                    "status": status.value,
                    "response_ms": duration,
                    "priority": adapter.metadata.priority,
                }
            except asyncio.TimeoutError:
                return code, {
                    "status": SourceStatus.UNAVAILABLE.value,
                    "response_ms": 5000,
                    "priority": adapter.metadata.priority,
                }
            except Exception:
                return code, {
                    "status": SourceStatus.UNAVAILABLE.value,
                    "response_ms": int((time.time() - start) * 1000),
                    "priority": adapter.metadata.priority,
                }

        checks = [check_one(code, adapter) for code, adapter in self._adapters.items()]
        done = await asyncio.gather(*checks, return_exceptions=True)

        for item in done:
            if isinstance(item, tuple):
                code, info = item
                results[code] = info

        return results

    async def close(self) -> None:
        """Close all adapters including fallback (STORY-257A AC12)."""
        for adapter in self._adapters.values():
            try:
                await adapter.close()
            except Exception as e:
                logger.debug(f"Adapter close error (non-critical): {e}")
        if self._fallback_adapter is not None:
            try:
                await self._fallback_adapter.close()
            except Exception as e:
                logger.debug(f"Fallback adapter close error (non-critical): {e}")
