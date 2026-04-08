"""Per-source fetch pipeline helpers.

TD-008: Extracted from source_merger.py as part of DEBT-07 module split.
Contains SourceFetcher — wraps per-source fetch with timeout, bulkhead,
and error handling. ConsolidationService delegates to this class.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Set

from utils.error_reporting import report_error
from clients.base import SourceAdapter, UnifiedProcurement, SourceError
from metrics import FETCH_DURATION, API_ERRORS
from telemetry import get_tracer, optional_span
from bulkhead import BulkheadAcquireTimeoutError, get_bulkhead

logger = logging.getLogger(__name__)

_tracer = get_tracer("consolidation")


class SourceFetcher:
    """Wraps per-source adapter fetches with timeout, bulkhead, and error handling."""

    def __init__(
        self,
        timeout_per_source: int,
        bulkheads: Dict,
    ) -> None:
        self._timeout_per_source = timeout_per_source
        self._bulkheads = bulkheads

    async def fetch_source(
        self,
        adapter: SourceAdapter,
        data_inicial: str,
        data_final: str,
        ufs: Optional[Set[str]],
        partial_collector: Optional[List] = None,
    ) -> List[UnifiedProcurement]:
        """Fetch all records from a single source."""
        records = [] if partial_collector is None else partial_collector
        async for record in adapter.fetch(data_inicial, data_final, ufs):
            records.append(record)
        return records

    async def wrap_source(
        self, code: str, adapter: SourceAdapter,
        data_inicial: str, data_final: str,
        ufs: Optional[Set[str]] = None,
        timeout: Optional[int] = None,
        partial_collector_out: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        Wrap a source fetch with timeout and error handling.

        Preserves partial results on timeout: records that were already
        yielded by the adapter before the timeout fires are returned
        with status ``"partial"`` instead of being discarded.
        """
        effective_timeout = timeout if timeout is not None else self._timeout_per_source
        start = time.time()
        partial_records: List[UnifiedProcurement] = (
            partial_collector_out if partial_collector_out is not None else []
        )
        source_span_name = f"fetch.{code.lower()}"
        with optional_span(_tracer, source_span_name, {"source.code": code}) as src_span:
            return await self._wrap_source_inner(
                code, adapter, data_inicial, data_final, ufs,
                effective_timeout, start, partial_records, src_span,
            )

    async def _wrap_source_inner(
        self, code, adapter, data_inicial, data_final, ufs,
        effective_timeout, start, partial_records, src_span,
    ):
        try:
            fetch_coro = self.fetch_source(
                adapter, data_inicial, data_final, ufs,
                partial_collector=partial_records,
            )
            bulkhead = self._bulkheads.get(code) or get_bulkhead(code)
            if bulkhead:
                fetch_coro = bulkhead.execute(fetch_coro)
            await asyncio.wait_for(fetch_coro, timeout=effective_timeout)
            duration = int((time.time() - start) * 1000)
            FETCH_DURATION.labels(source=code).observe(duration / 1000.0)
            src_span.set_attribute("duration_ms", duration)
            src_span.set_attribute("items_out", len(partial_records))
            src_span.set_attribute("status", "success")
            logger.debug(
                f"[CONSOLIDATION] {code}: {len(partial_records)} records in {duration}ms"
            )
            return {
                "code": code,
                "status": "success",
                "records": partial_records,
                "duration_ms": duration,
            }
        except BulkheadAcquireTimeoutError as bae:
            duration = int((time.time() - start) * 1000)
            FETCH_DURATION.labels(source=code).observe(duration / 1000.0)
            logger.warning(
                f"[CONSOLIDATION] {code}: bulkhead acquire timeout after {duration}ms — skipped"
            )
            return {
                "code": code,
                "status": "skipped",
                "records": [],
                "duration_ms": duration,
                "error": str(bae),
            }
        except asyncio.TimeoutError:
            duration = int((time.time() - start) * 1000)
            FETCH_DURATION.labels(source=code).observe(duration / 1000.0)
            API_ERRORS.labels(source=code, error_type="timeout").inc()
            salvaged = len(partial_records)
            if salvaged > 0:
                logger.warning(
                    f"[CONSOLIDATION] {code}: timeout after {duration}ms — "
                    f"salvaged {salvaged} partial records"
                )
                return {
                    "code": code,
                    "status": "partial",
                    "records": partial_records,
                    "duration_ms": duration,
                    "error": f"Timeout after {effective_timeout}s (salvaged {salvaged} records)",
                }
            else:
                logger.info(
                    f"[CONSOLIDATION] {code}: timeout after {duration}ms — no records"
                )
                return {
                    "code": code,
                    "status": "timeout",
                    "records": [],
                    "duration_ms": duration,
                    "error": f"Timeout after {effective_timeout}s",
                }
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            FETCH_DURATION.labels(source=code).observe(duration / 1000.0)
            _err_type = "unknown"
            if "429" in str(e):
                _err_type = "429"
            elif "422" in str(e):
                _err_type = "422"
            elif "500" in str(e) or "502" in str(e) or "503" in str(e) or "504" in str(e):
                _err_type = "500"
            elif "timeout" in str(e).lower() or "Timeout" in type(e).__name__:
                _err_type = "timeout"
            elif "connect" in str(e).lower() or "Connection" in type(e).__name__:
                _err_type = "connection"
            API_ERRORS.labels(source=code, error_type=_err_type).inc()
            salvaged = len(partial_records)

            source_code = code
            if isinstance(e, SourceError):
                source_code = e.source_code

            if salvaged > 0:
                report_error(
                    e, f"[CONSOLIDATION] {code}: PARTIAL after {duration}ms — salvaged {salvaged} records",
                    expected=True, tags={"data_source": source_code}, log=logger,
                )
                return {
                    "code": code,
                    "status": "partial",
                    "records": partial_records,
                    "duration_ms": duration,
                    "error": f"{e} (salvaged {salvaged} records)",
                }
            report_error(
                e, f"[CONSOLIDATION] {code}: FAILED after {duration}ms",
                expected=True, tags={"data_source": source_code}, log=logger,
            )
            return {
                "code": code,
                "status": "error",
                "records": [],
                "duration_ms": duration,
                "error": str(e),
            }
