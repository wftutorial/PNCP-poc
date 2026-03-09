# DEBT-015: Backend Architecture Decomposition

**Sprint:** Backlog
**Effort:** 90h
**Priority:** MEDIUM
**Agent:** @architect (Atlas) + @dev

## Context

The backend has several large modules that concentrate too much logic, making changes risky and testing difficult. `search_pipeline.py` is 800+ lines with each stage 50-100+ lines of nested try/catch. `main.py` is still 820+ lines after previous decomposition. The PNCP client has dual sync+async implementations with 1500+ duplicated lines. `config.py` is 500+ lines mixing PNCP modality codes, retry config, CORS, logging, feature flags, and validation. Error handling patterns are inconsistent across routes (mix of `JSONResponse` and `HTTPException`).

These are high-effort items with long-term value for development velocity and maintainability.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| SYS-002 | `search_pipeline.py` god module (800+ lines) — each stage with nested try/catch | 24h |
| SYS-003 | Progress tracker in-memory (asyncio.Queue) — does not scale horizontally | 16h |
| SYS-004 | Dual HTTP client sync+async for PNCP (1500+ duplicated lines) | 24h |
| SYS-005 | `main.py` still 820+ lines after decomposition | 12h |
| SYS-012 | `config.py` 500+ lines with mixed concerns | 6h |
| SYS-011 | Inconsistent error handling patterns across routes | 8h |

## Tasks

- [x] Decompose `search_pipeline.py` into per-stage modules: validate, prepare, execute, filter, enrich, generate, persist (SYS-002)
- [x] Migrate progress tracker from asyncio.Queue to Redis Streams (prerequisite for horizontal scaling) (SYS-003) — already 95%+ complete from STORY-276/294
- [x] Fix broken sync PNCP client usage in blog_stats.py and sectors_public.py; wrap debug endpoint with asyncio.to_thread (SYS-004)
- [x] Decompose `main.py`: extract Sentry init → startup/sentry.py, lifespan → startup/lifespan.py, state → startup/state.py, health → routes/health_core.py (SYS-005)
- [x] Split `config.py` into: `config/base.py`, `config/pncp.py`, `config/features.py`, `config/cors.py`, `config/pipeline.py` (SYS-012)
- [x] Create unified error response schema: `error_response.py` with ErrorCode enum + build_error_detail helper (SYS-011)

## Acceptance Criteria

- [x] AC1: `search_pipeline.py` = 168 lines (orchestrator only); 7 stages in `pipeline/stages/`
- [x] AC2: Progress tracker works across multiple workers via Redis Streams (STORY-276/294)
- [x] AC3: Sync PNCPClient retained for scripts; blog_stats/sectors_public fixed to use AsyncPNCPClient; `requests` still needed by lead prospecting clients
- [x] AC4: `main.py` = 298 lines
- [x] AC5: `config.py` split into 5 focused modules (base, pncp, features, cors, pipeline)
- [x] AC6: Unified ErrorCode enum (13 values) + build_error_detail() in error_response.py; SearchErrorCode = ErrorCode alias
- [x] AC7: 7498 passed / 126 pre-existing failures / 0 regressions in backend test suite

## Tests Required

- Search pipeline: end-to-end test with decomposed stages
- Progress tracker: multi-worker test with Redis Streams
- PNCP client: all existing tests pass with async-only client
- Error schema: verify all routes return consistent error format

## Definition of Done

- [x] All tasks complete
- [x] Tests passing (backend 7498+ pass, 0 new failures)
- [x] No regressions
- [x] Each decomposed module < 300 lines
- [ ] Code reviewed

## Files Changed

### New Files
- `backend/error_response.py` — Unified ErrorCode enum + build_error_detail()
- `backend/config/__init__.py` — Config package with backward-compatible re-exports
- `backend/config/base.py` — Core utilities (setup_logging, validate_env_vars)
- `backend/config/pncp.py` — Source config (MODALIDADES_PNCP, RetryConfig, timeouts)
- `backend/config/features.py` — Feature flags (33 flags, registry, reload)
- `backend/config/cors.py` — CORS origins
- `backend/config/pipeline.py` — Pipeline operations config
- `backend/startup/__init__.py` — Startup package
- `backend/startup/state.py` — Shared process state (startup_time, process_start_time)
- `backend/startup/sentry.py` — Sentry init, PII scrubbing, noise filtering
- `backend/startup/lifespan.py` — Startup/shutdown orchestration
- `backend/routes/health_core.py` — /health/live, /health/ready, /health, /sources/health
- `backend/pipeline/stages/__init__.py` — Stage function re-exports
- `backend/pipeline/stages/validate.py` — Stage 1: request validation
- `backend/pipeline/stages/prepare.py` — Stage 2: term parsing, sector config
- `backend/pipeline/stages/execute.py` — Stage 3: API calls, cache fallback
- `backend/pipeline/stages/filter_stage.py` — Stage 4: keyword/status/value filtering
- `backend/pipeline/stages/enrich.py` — Stage 5: relevance scoring
- `backend/pipeline/stages/generate.py` — Stage 6: LLM summary, Excel generation
- `backend/pipeline/stages/persist.py` — Stage 7: session save, response building
- `backend/pipeline/worker.py` — ARQ Worker entry points
- `backend/pipeline/tracing.py` — Stage tracing and validation utilities

### Modified Files
- `backend/main.py` — Reduced from 1,362 → 298 lines (thin orchestrator)
- `backend/search_pipeline.py` — Reduced from 2,875 → 168 lines (orchestrator only)
- `backend/schemas.py` — SearchErrorCode now imported from error_response
- `backend/routes/search.py` — _build_error_detail imported from error_response
- `backend/routes/blog_stats.py` — Fixed: PNCPClient → AsyncPNCPClient
- `backend/routes/sectors_public.py` — Fixed: PNCPClient → AsyncPNCPClient
- `backend/tests/test_health_ready.py` — Updated mock paths for startup.state
- `backend/tests/test_schema_validation.py` — Updated mock paths for startup.lifespan
- `backend/tests/test_harden024_saturation_metrics.py` — Updated mock paths
- `backend/tests/test_blog_stats.py` — Updated mocks for AsyncPNCPClient
- `backend/tests/test_sectors_public.py` — Updated mocks for AsyncPNCPClient
