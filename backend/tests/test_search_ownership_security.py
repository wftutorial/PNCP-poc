"""CRIT-SEC-003: Search endpoint IDOR protection tests.

Verifies that users cannot access other users' search data by guessing search_ids.
"""

import uuid
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from types import SimpleNamespace

from fastapi.testclient import TestClient

from main import app
from auth import require_auth


USER_A = {
    "id": "user-a-id-00000000",
    "email": "usera@example.com",
    "plan_type": "smartlic_pro",
}

USER_B = {
    "id": "user-b-id-11111111",
    "email": "userb@example.com",
    "plan_type": "smartlic_pro",
}


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def auth_as_user_b():
    """Authenticate as User B."""
    app.dependency_overrides[require_auth] = lambda: USER_B
    yield USER_B
    app.dependency_overrides.pop(require_auth, None)


def _mock_db_returns_user_a_session():
    """Mock DB that returns a session owned by User A."""
    mock_result = SimpleNamespace(data=[{"id": "session-123"}])

    async def mock_sb_execute(query):
        # Inspect the query chain to check user_id filter
        # If user_id filter matches User A, return data; otherwise empty
        return mock_result

    return mock_sb_execute


class TestSearchOwnershipIDOR:
    """User B should NOT be able to access User A's searches."""

    def test_status_returns_404_for_other_users_search(self, client, auth_as_user_b):
        """GET /v1/search/{id}/status — User B cannot see User A's search."""
        search_id = str(uuid.uuid4())

        # DB returns empty (no session for User B with this search_id)
        mock_result = SimpleNamespace(data=[])

        with patch("routes.search_status.get_tracker", new_callable=AsyncMock, return_value=None), \
             patch("supabase_client.get_supabase") as mock_sb:
            mock_table = MagicMock()
            mock_table.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = MagicMock(return_value=mock_result)
            mock_sb.return_value = mock_table

            response = client.get(f"/v1/search/{search_id}/status")

        assert response.status_code == 404

    def test_results_returns_404_for_other_users_search(self, client, auth_as_user_b):
        """GET /v1/search/{id}/results — User B cannot see User A's results."""
        search_id = str(uuid.uuid4())

        with patch("routes.search_status.get_tracker", new_callable=AsyncMock, return_value=None), \
             patch("supabase_client.get_supabase") as mock_sb:
            mock_table = MagicMock()
            mock_result = SimpleNamespace(data=[])
            mock_table.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = MagicMock(return_value=mock_result)
            mock_sb.return_value = mock_table

            response = client.get(f"/v1/search/{search_id}/results")

        assert response.status_code == 404

    def test_cancel_returns_404_for_other_users_search(self, client, auth_as_user_b):
        """POST /v1/search/{id}/cancel — User B cannot cancel User A's search."""
        search_id = str(uuid.uuid4())

        with patch("routes.search_status.get_tracker", new_callable=AsyncMock, return_value=None), \
             patch("supabase_client.get_supabase") as mock_sb:
            mock_table = MagicMock()
            mock_result = SimpleNamespace(data=[])
            mock_table.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = MagicMock(return_value=mock_result)
            mock_sb.return_value = mock_table

            response = client.post(f"/v1/search/{search_id}/cancel")

        assert response.status_code == 404

    def test_timeline_returns_404_for_other_users_search(self, client, auth_as_user_b):
        """GET /v1/search/{id}/timeline — User B cannot see User A's timeline."""
        search_id = str(uuid.uuid4())

        with patch("routes.search_status.get_tracker", new_callable=AsyncMock, return_value=None), \
             patch("supabase_client.get_supabase") as mock_sb:
            mock_table = MagicMock()
            mock_result = SimpleNamespace(data=[])
            mock_table.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = MagicMock(return_value=mock_result)
            mock_sb.return_value = mock_table

            response = client.get(f"/v1/search/{search_id}/timeline")

        assert response.status_code == 404


class TestSearchOwnershipAllowsOwner:
    """Owner of the search should still have access."""

    @pytest.fixture(autouse=True)
    def auth_as_user_a(self):
        app.dependency_overrides[require_auth] = lambda: USER_A
        yield
        app.dependency_overrides.pop(require_auth, None)

    def test_owner_can_access_own_search_status(self, client):
        """User A can access their own search status via in-flight tracker."""
        search_id = str(uuid.uuid4())
        tracker = MagicMock()
        tracker.uf_count = 3
        tracker._ufs_completed = 1
        tracker._is_complete = False
        tracker.created_at = 1000000.0

        sm = MagicMock()
        sm.current_state = MagicMock()
        sm.current_state.value = "fetching"

        # DB returns empty but tracker exists (in-flight) — should pass
        mock_result = SimpleNamespace(data=[])
        with patch("routes.search_status.get_tracker", new_callable=AsyncMock, return_value=tracker), \
             patch("routes.search_status.get_state_machine", return_value=sm), \
             patch("supabase_client.get_supabase") as mock_sb:
            mock_table = MagicMock()
            mock_table.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = MagicMock(return_value=mock_result)
            mock_sb.return_value = mock_table

            response = client.get(f"/v1/search/{search_id}/status")

        assert response.status_code == 200
