"""Tests for SYS-023: Per-user Supabase tokens for user-scoped operations.

Tests the get_user_supabase() function and get_user_db() FastAPI dependency.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, PropertyMock


# ---------------------------------------------------------------------------
# Helper: mock the supabase module's create_client (lazy import)
# ---------------------------------------------------------------------------

def _mock_supabase_module():
    """Ensure supabase module is mockable for tests (not installed locally)."""
    mock_supabase = MagicMock()
    mock_session = MagicMock()
    mock_session.headers = {}
    mock_postgrest = MagicMock()
    mock_postgrest.session = mock_session
    mock_client = MagicMock()
    mock_client.postgrest = mock_postgrest
    mock_supabase.create_client.return_value = mock_client
    return mock_supabase, mock_client, mock_session


# Valid PerfilContexto payload for PUT /v1/profile/context
_VALID_PROFILE_CONTEXT = {
    "ufs_atuacao": ["SP", "RJ"],
    "porte_empresa": "GRANDE",
    "experiencia_licitacoes": "EXPERIENTE",
}


# ---------------------------------------------------------------------------
# get_user_supabase() unit tests
# ---------------------------------------------------------------------------

class TestGetUserSupabase:
    """Tests for supabase_client.get_user_supabase()."""

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "anon-key-123",
    })
    def test_creates_client_with_anon_key(self):
        """Should create a Supabase client using anon key (not service role)."""
        mock_mod, mock_client, mock_session = _mock_supabase_module()

        with patch.dict(sys.modules, {"supabase": mock_mod}):
            from supabase_client import get_user_supabase
            result = get_user_supabase("user-jwt-token-abc")

        mock_mod.create_client.assert_called_once_with("https://test.supabase.co", "anon-key-123")
        assert result is mock_client

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "anon-key-123",
    })
    def test_sets_user_jwt_on_authorization_header(self):
        """Should override the Authorization header with user's Bearer token."""
        mock_mod, mock_client, mock_session = _mock_supabase_module()

        with patch.dict(sys.modules, {"supabase": mock_mod}):
            from supabase_client import get_user_supabase
            get_user_supabase("my-user-jwt-token")

        assert mock_session.headers["Authorization"] == "Bearer my-user-jwt-token"
        assert mock_session.headers["apikey"] == "anon-key-123"

    @patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_ANON_KEY": ""}, clear=False)
    def test_raises_runtime_error_without_config(self):
        """Should raise RuntimeError if SUPABASE_URL or SUPABASE_ANON_KEY not set."""
        from supabase_client import get_user_supabase

        with pytest.raises(RuntimeError, match="SUPABASE_URL and SUPABASE_ANON_KEY must be set"):
            get_user_supabase("some-token")

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "anon-key-123",
    })
    def test_each_call_creates_new_client(self):
        """Should NOT cache/pool user clients -- each call creates a new one."""
        mock_mod, _, _ = _mock_supabase_module()

        with patch.dict(sys.modules, {"supabase": mock_mod}):
            from supabase_client import get_user_supabase
            get_user_supabase("token-a")
            get_user_supabase("token-b")

        assert mock_mod.create_client.call_count == 2

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "anon-key-123",
    })
    def test_handles_postgrest_access_error_gracefully(self):
        """Should not crash if postgrest attribute is inaccessible."""
        mock_mod = MagicMock()
        mock_client = MagicMock()
        type(mock_client).postgrest = PropertyMock(side_effect=AttributeError("no postgrest"))
        mock_mod.create_client.return_value = mock_client

        with patch.dict(sys.modules, {"supabase": mock_mod}):
            from supabase_client import get_user_supabase
            result = get_user_supabase("some-token")

        assert result is mock_client

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "anon-key-123",
    })
    def test_different_tokens_get_different_headers(self):
        """Each client should have the specific user's token, not a shared one."""
        sessions = []

        for token in ["token-alice", "token-bob"]:
            mock_mod = MagicMock()
            mock_session = MagicMock()
            mock_session.headers = {}
            mock_postgrest = MagicMock()
            mock_postgrest.session = mock_session
            mock_client = MagicMock()
            mock_client.postgrest = mock_postgrest
            mock_mod.create_client.return_value = mock_client

            with patch.dict(sys.modules, {"supabase": mock_mod}):
                from supabase_client import get_user_supabase
                get_user_supabase(token)
                sessions.append(mock_session)

        assert sessions[0].headers["Authorization"] == "Bearer token-alice"
        assert sessions[1].headers["Authorization"] == "Bearer token-bob"


# ---------------------------------------------------------------------------
# get_user_db() dependency tests
# ---------------------------------------------------------------------------

class TestGetUserDbDependency:
    """Tests for database.get_user_db() FastAPI dependency."""

    @patch("database.get_user_supabase")
    def test_extracts_token_from_credentials(self, mock_get_user):
        """Should pass credentials.credentials to get_user_supabase."""
        from database import get_user_db

        mock_creds = MagicMock()
        mock_creds.credentials = "jwt-token-xyz"
        mock_get_user.return_value = MagicMock()

        get_user_db(credentials=mock_creds)

        mock_get_user.assert_called_once_with("jwt-token-xyz")

    def test_raises_401_without_credentials(self):
        """Should raise HTTPException 401 when no Authorization header."""
        from database import get_user_db
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            get_user_db(credentials=None)

        assert exc_info.value.status_code == 401

    @patch("database.get_user_supabase")
    def test_returns_user_scoped_client(self, mock_get_user):
        """Should return the client from get_user_supabase."""
        from database import get_user_db

        expected_client = MagicMock()
        mock_get_user.return_value = expected_client

        mock_creds = MagicMock()
        mock_creds.credentials = "some-token"

        result = get_user_db(credentials=mock_creds)
        assert result is expected_client


# ---------------------------------------------------------------------------
# get_db() still returns admin client (backward compat)
# ---------------------------------------------------------------------------

class TestGetDbBackwardCompat:
    """Ensure get_db() still returns the admin (service-role) client."""

    @patch("database.get_supabase")
    def test_get_db_returns_admin_client(self, mock_get_sb):
        """get_db() should still call get_supabase() (admin)."""
        from database import get_db

        mock_admin = MagicMock()
        mock_get_sb.return_value = mock_admin

        result = get_db()

        mock_get_sb.assert_called_once()
        assert result is mock_admin


# ---------------------------------------------------------------------------
# Route integration: profile context uses user-scoped client
# ---------------------------------------------------------------------------

class TestProfileContextUserScoped:
    """Verify that profile context endpoints receive user-scoped client."""

    def _setup_client(self, mock_user_db=None):
        """Create test client with auth and user_db overrides."""
        from fastapi.testclient import TestClient
        from main import app
        from auth import require_auth
        from database import get_user_db, get_db

        mock_user = {"id": "user-123", "email": "test@example.com", "role": "authenticated"}
        app.dependency_overrides[require_auth] = lambda: mock_user

        if mock_user_db is not None:
            app.dependency_overrides[get_user_db] = lambda: mock_user_db

        # Override get_db to prevent service role initialization
        mock_admin_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_admin_db

        client = TestClient(app)
        return client

    def _cleanup(self):
        from main import app
        app.dependency_overrides.clear()

    def test_get_profile_context_uses_user_db(self):
        """GET /v1/profile/context should receive the user-scoped client."""
        mock_user_db = MagicMock()
        mock_result = MagicMock()
        mock_result.data = {"context_data": {"porte_empresa": "medio"}}

        client = self._setup_client(mock_user_db=mock_user_db)
        try:
            with patch("routes.user.sb_execute") as mock_sb:
                mock_sb.return_value = mock_result
                resp = client.get("/v1/profile/context")

            assert resp.status_code == 200
            # Verify user_db.table("profiles") was called (not admin db)
            mock_user_db.table.assert_called_with("profiles")
        finally:
            self._cleanup()

    def test_put_profile_context_uses_user_db(self):
        """PUT /v1/profile/context should receive the user-scoped client."""
        mock_user_db = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "user-123"}]

        client = self._setup_client(mock_user_db=mock_user_db)
        try:
            with patch("routes.user.sb_execute") as mock_sb:
                mock_sb.return_value = mock_result
                resp = client.put(
                    "/v1/profile/context",
                    json=_VALID_PROFILE_CONTEXT,
                )

            assert resp.status_code == 200
            mock_user_db.table.assert_called_with("profiles")
        finally:
            self._cleanup()


# ---------------------------------------------------------------------------
# Route integration: GET /pipeline uses user-scoped client
# ---------------------------------------------------------------------------

class TestPipelineListUserScoped:
    """Verify that GET /v1/pipeline receives user-scoped client."""

    def _setup_client(self, mock_user_db=None):
        """Create test client with auth and user_db overrides."""
        from fastapi.testclient import TestClient
        from main import app
        from auth import require_auth
        from database import get_user_db, get_db

        mock_user = {"id": "user-456", "email": "pipe@example.com", "role": "authenticated"}
        app.dependency_overrides[require_auth] = lambda: mock_user

        if mock_user_db is not None:
            app.dependency_overrides[get_user_db] = lambda: mock_user_db

        mock_admin_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_admin_db

        return TestClient(app)

    def _cleanup(self):
        from main import app
        app.dependency_overrides.clear()

    @patch("routes.pipeline._check_pipeline_read_access")
    def test_get_pipeline_uses_user_db(self, mock_access):
        """GET /v1/pipeline should use user-scoped client for the query."""
        mock_access.return_value = None

        mock_user_db = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_result.count = 0

        client = self._setup_client(mock_user_db=mock_user_db)
        try:
            with patch("routes.pipeline.sb_execute") as mock_sb:
                mock_sb.return_value = mock_result
                resp = client.get("/v1/pipeline")

            assert resp.status_code == 200
            mock_user_db.table.assert_called_with("pipeline_items")
        finally:
            self._cleanup()
