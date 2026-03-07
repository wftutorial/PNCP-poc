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

- [ ] Decompose `search_pipeline.py` into per-stage modules: source_fetch, filtering, classification, viability, consolidation (SYS-002)
- [ ] Migrate progress tracker from asyncio.Queue to Redis Streams (prerequisite for horizontal scaling) (SYS-003)
- [ ] Eliminate sync PNCP client — keep only async httpx client, remove `requests` dependency (SYS-004)
- [ ] Decompose `main.py`: extract Sentry init, exception handlers, middleware config, router registration into separate modules (SYS-005)
- [ ] Split `config.py` into: `config/base.py`, `config/pncp.py`, `config/features.py`, `config/cors.py` (SYS-012)
- [ ] Create unified error response schema (replace mix of JSONResponse + HTTPException) (SYS-011)

## Acceptance Criteria

- [ ] AC1: `search_pipeline.py` < 200 lines (orchestrator only); stages in separate files
- [ ] AC2: Progress tracker works across multiple workers via Redis Streams
- [ ] AC3: No `requests` library in production dependencies; only `httpx` for HTTP
- [ ] AC4: `main.py` < 300 lines
- [ ] AC5: `config.py` split into 4+ focused modules
- [ ] AC6: All routes use unified error response schema
- [ ] AC7: Zero regressions in backend test suite (5800+ pass)

## Tests Required

- Search pipeline: end-to-end test with decomposed stages
- Progress tracker: multi-worker test with Redis Streams
- PNCP client: all existing tests pass with async-only client
- Error schema: verify all routes return consistent error format

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (backend 5800+ / 0 fail)
- [ ] No regressions
- [ ] Each decomposed module < 300 lines
- [ ] Code reviewed
