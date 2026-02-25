"""GTM-STAB-009: Async search architecture tests.

Tests the async search flow:
- POST /buscar returns 202 when SEARCH_ASYNC_ENABLED=true
- 202 response includes status_url, progress_url, estimated_duration_s
- X-Sync: true forces synchronous mode
- GET /v1/search/{id}/results returns 202 when processing, 200 when ready
- Backward compatibility: flag=false keeps sync behavior
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from main import app


def _make_mock_tracker():
    """Create a mock tracker with async-compatible methods."""
    tracker = Mock()
    tracker.emit = AsyncMock()
    tracker.emit_error = AsyncMock()
    tracker.emit_complete = AsyncMock()
    tracker.emit_degraded = AsyncMock()
    return tracker


def _make_mock_state_machine():
    """Create a mock state machine with async-compatible methods."""
    sm = Mock()
    sm.fail = AsyncMock()
    sm.transition = AsyncMock()
    sm.complete = AsyncMock()
    return sm


def _make_sync_response():
    """Build a minimal valid BuscaResponse for sync path tests."""
    from schemas import BuscaResponse

    return BuscaResponse(
        resumo={
            "resumo_executivo": "Teste",
            "total_oportunidades": 0,
            "valor_total": 0.0,
            "destaques": [],
        },
        licitacoes=[],
        excel_available=False,
        quota_used=1,
        quota_remaining=999,
        total_raw=0,
        total_filtrado=0,
    )


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Override require_auth dependency."""
    from auth import require_auth

    mock_user = {
        "id": "test-user-id",
        "email": "test@example.com",
        "plan_type": "smartlic_pro",
    }
    app.dependency_overrides[require_auth] = lambda: mock_user
    yield mock_user
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def mock_quota():
    """Mock quota check to always allow."""
    mock_info = Mock()
    mock_info.allowed = True
    mock_info.error_message = ""
    mock_info.capabilities = {"max_requests_per_month": 1000}

    with patch("quota.check_quota", return_value=mock_info):
        with patch("quota.check_and_increment_quota_atomic", return_value=(True, 1, 999)):
            yield


@pytest.fixture
def mock_rate_limit():
    """Mock rate limiting to always pass."""
    from routes.search import require_rate_limit
    # Rate limit returns a dependency function; override the outer dependency
    with patch("routes.search.require_rate_limit", return_value=lambda: None):
        yield


@pytest.fixture
def mock_active_plan():
    """Mock require_active_plan to pass."""
    with patch("quota.require_active_plan", new_callable=AsyncMock):
        yield


class TestAsyncSearchEnabled:
    """Test POST /buscar with SEARCH_ASYNC_ENABLED=true."""

    def test_returns_202_when_async_enabled_and_queue_available(
        self, client, mock_auth, mock_quota, mock_active_plan
    ):
        """AC1: POST /buscar returns 202 Accepted with enriched response."""
        mock_job = Mock()
        mock_job.job_id = "job-123"

        with patch("config.get_feature_flag", return_value=True):
            with patch("job_queue.is_queue_available", new_callable=AsyncMock, return_value=True):
                with patch("job_queue.enqueue_job", new_callable=AsyncMock, return_value=mock_job):
                    with patch("routes.search.check_user_roles", new_callable=AsyncMock, return_value=(False, False)):
                        with patch("routes.search.create_tracker", new_callable=AsyncMock, return_value=_make_mock_tracker()):
                            with patch("routes.search.create_state_machine", new_callable=AsyncMock, return_value=_make_mock_state_machine()):
                                response = client.post("/buscar", json={
                                    "ufs": ["SP", "RJ"],
                                    "data_inicial": "2026-02-14",
                                    "data_final": "2026-02-24",
                                    "setor_id": "vestuario",
                                })

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"
        assert "search_id" in data
        assert "status_url" in data
        assert "progress_url" in data
        assert "estimated_duration_s" in data
        assert data["status_url"].startswith("/v1/search/")
        assert data["progress_url"].startswith("/buscar-progress/")
        assert isinstance(data["estimated_duration_s"], int)

    def test_x_sync_header_forces_sync_mode(
        self, client, mock_auth, mock_quota, mock_active_plan
    ):
        """AC6: X-Sync: true bypasses async — enqueue_job is never called."""
        with patch("config.get_feature_flag", return_value=True), \
             patch("job_queue.is_queue_available", new_callable=AsyncMock, return_value=True), \
             patch("job_queue.enqueue_job", new_callable=AsyncMock) as mock_enqueue, \
             patch("routes.search.create_tracker", new_callable=AsyncMock, return_value=_make_mock_tracker()), \
             patch("routes.search.create_state_machine", new_callable=AsyncMock, return_value=_make_mock_state_machine()), \
             patch("routes.search.remove_tracker", new_callable=AsyncMock), \
             patch("routes.search.remove_state_machine"), \
             patch("routes.search.SearchPipeline") as MockPipeline, \
             patch("search_cache.get_from_cache_cascade", new_callable=AsyncMock, return_value=None):
            mock_pipe = MockPipeline.return_value
            mock_pipe.run = AsyncMock(return_value=_make_sync_response())
            response = client.post(
                "/buscar",
                json={
                    "ufs": ["SP"],
                    "data_inicial": "2026-02-14",
                    "data_final": "2026-02-24",
                    "setor_id": "vestuario",
                },
                headers={"X-Sync": "true"},
            )

        assert response.status_code != 202
        mock_enqueue.assert_not_called()

    def test_sync_query_param_forces_sync_mode(
        self, client, mock_auth, mock_quota, mock_active_plan
    ):
        """AC6: ?sync=true bypasses async — enqueue_job is never called."""
        with patch("config.get_feature_flag", return_value=True), \
             patch("job_queue.is_queue_available", new_callable=AsyncMock, return_value=True), \
             patch("job_queue.enqueue_job", new_callable=AsyncMock) as mock_enqueue, \
             patch("routes.search.create_tracker", new_callable=AsyncMock, return_value=_make_mock_tracker()), \
             patch("routes.search.create_state_machine", new_callable=AsyncMock, return_value=_make_mock_state_machine()), \
             patch("routes.search.remove_tracker", new_callable=AsyncMock), \
             patch("routes.search.remove_state_machine"), \
             patch("routes.search.SearchPipeline") as MockPipeline, \
             patch("search_cache.get_from_cache_cascade", new_callable=AsyncMock, return_value=None):
            mock_pipe = MockPipeline.return_value
            mock_pipe.run = AsyncMock(return_value=_make_sync_response())
            response = client.post(
                "/buscar?sync=true",
                json={
                    "ufs": ["SP"],
                    "data_inicial": "2026-02-14",
                    "data_final": "2026-02-24",
                    "setor_id": "vestuario",
                },
            )

        assert response.status_code != 202
        mock_enqueue.assert_not_called()

    def test_falls_back_to_sync_when_queue_unavailable(
        self, client, mock_auth, mock_quota, mock_active_plan
    ):
        """AC2: When ARQ/Redis down, falls back to sync pipeline (200, not 202)."""
        with patch("config.get_feature_flag", return_value=True), \
             patch("job_queue.is_queue_available", new_callable=AsyncMock, return_value=False), \
             patch("job_queue.enqueue_job", new_callable=AsyncMock) as mock_enqueue, \
             patch("routes.search.create_tracker", new_callable=AsyncMock, return_value=_make_mock_tracker()), \
             patch("routes.search.create_state_machine", new_callable=AsyncMock, return_value=_make_mock_state_machine()), \
             patch("routes.search.remove_tracker", new_callable=AsyncMock), \
             patch("routes.search.remove_state_machine"), \
             patch("routes.search.SearchPipeline") as MockPipeline, \
             patch("search_cache.get_from_cache_cascade", new_callable=AsyncMock, return_value=None):
            mock_pipe = MockPipeline.return_value
            mock_pipe.run = AsyncMock(return_value=_make_sync_response())
            response = client.post("/buscar", json={
                "ufs": ["SP"],
                "data_inicial": "2026-02-14",
                "data_final": "2026-02-24",
                "setor_id": "vestuario",
            })

        assert response.status_code == 200
        mock_enqueue.assert_not_called()


class TestAsyncSearchDisabled:
    """Test POST /buscar with SEARCH_ASYNC_ENABLED=false (default)."""

    def test_sync_mode_when_flag_disabled(
        self, client, mock_auth, mock_quota, mock_active_plan
    ):
        """AC6: Default behavior unchanged when flag is off — sync pipeline runs."""
        with patch("config.get_feature_flag", return_value=False), \
             patch("job_queue.enqueue_job", new_callable=AsyncMock) as mock_enqueue, \
             patch("routes.search.create_tracker", new_callable=AsyncMock, return_value=_make_mock_tracker()), \
             patch("routes.search.create_state_machine", new_callable=AsyncMock, return_value=_make_mock_state_machine()), \
             patch("routes.search.remove_tracker", new_callable=AsyncMock), \
             patch("routes.search.remove_state_machine"), \
             patch("routes.search.SearchPipeline") as MockPipeline, \
             patch("search_cache.get_from_cache_cascade", new_callable=AsyncMock, return_value=None):
            mock_pipe = MockPipeline.return_value
            mock_pipe.run = AsyncMock(return_value=_make_sync_response())
            response = client.post("/buscar", json={
                "ufs": ["SP"],
                "data_inicial": "2026-02-14",
                "data_final": "2026-02-24",
                "setor_id": "vestuario",
            })

        assert response.status_code == 200
        mock_enqueue.assert_not_called()


class TestSearchResultsEndpoint:
    """Test GET /v1/search/{id}/results."""

    def test_returns_200_when_results_ready(self, client, mock_auth):
        """AC4: Returns full result when available."""
        mock_result = {"total_filtrado": 10, "licitacoes": []}

        with patch("routes.search.get_background_results_async", new_callable=AsyncMock, return_value=mock_result):
            response = client.get("/v1/search/test-search-id/results")

        assert response.status_code == 200
        data = response.json()
        assert data["total_filtrado"] == 10
        assert response.headers.get("cache-control") == "max-age=300"

    def test_returns_202_when_still_processing(self, client, mock_auth):
        """AC4: Returns 202 with status when not ready yet."""
        mock_status = {
            "search_id": "test-search-id",
            "status": "fetching",
            "progress": 30,
        }

        with patch("routes.search.get_background_results_async", new_callable=AsyncMock, return_value=None):
            with patch("routes.search.get_search_status", new_callable=AsyncMock, return_value=mock_status):
                response = client.get("/v1/search/test-search-id/results")

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "fetching"
        assert data["progress"] == 30

    def test_returns_404_when_not_found(self, client, mock_auth):
        """AC4: Returns 404 when search_id not found."""
        with patch("routes.search.get_background_results_async", new_callable=AsyncMock, return_value=None):
            with patch("routes.search.get_search_status", new_callable=AsyncMock, return_value=None):
                response = client.get("/v1/search/nonexistent-id/results")

        assert response.status_code == 404


class TestSearchQueuedResponseSchema:
    """Test the enriched 202 response schema."""

    def test_schema_has_required_fields(self):
        """AC1: Schema includes all required fields."""
        from schemas import SearchQueuedResponse

        resp = SearchQueuedResponse(
            search_id="abc-123",
            status_url="/v1/search/abc-123/status",
            progress_url="/buscar-progress/abc-123",
            estimated_duration_s=45,
        )
        assert resp.search_id == "abc-123"
        assert resp.status == "queued"
        assert resp.status_url == "/v1/search/abc-123/status"
        assert resp.progress_url == "/buscar-progress/abc-123"
        assert resp.estimated_duration_s == 45

    def test_estimated_duration_default(self):
        """Default estimated duration is 45s."""
        from schemas import SearchQueuedResponse

        resp = SearchQueuedResponse(
            search_id="abc-123",
            status_url="/v1/search/abc-123/status",
            progress_url="/buscar-progress/abc-123",
        )
        assert resp.estimated_duration_s == 45
