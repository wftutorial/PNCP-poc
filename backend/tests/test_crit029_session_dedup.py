"""CRIT-029: Histórico dedup — prevent duplicate session entries on cache hits.

AC1: Same params within 5min → single history entry (not duplicate)
AC2: Cache hits (duration < 2s) merged with original session (update, not insert)
AC3: Dedup checks (user_id + sectors + ufs + data_range) not just search_id
AC4: Integration test: busca + retry → 1 history entry
AC5: Unit test: cache hit same params → update instead of insert
AC6: Zero regression
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_sb():
    """Create a mock Supabase client with chained method returns."""
    sb = MagicMock()

    # Default: insert returns a new session ID
    sb.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": "new-session-id"}]
    )

    # Default: select for search_id dedup returns empty
    sb.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[]
    )

    # Default: select for param dedup returns empty
    sb.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[]
    )

    # Default: update returns success
    sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{}]
    )

    return sb


@pytest.fixture
def base_args():
    return {
        "user_id": "user-crit029-test",
        "sectors": ["informatica"],
        "ufs": ["SP", "RJ"],
        "data_inicial": "2026-02-01",
        "data_final": "2026-02-10",
        "custom_keywords": None,
        "search_id": "search-crit029-001",
    }


# ===========================================================================
# AC1: Same params within 5min → single history entry
# ===========================================================================

class TestParameterBasedDedup:
    """CRIT-029 AC1+AC3: Parameter-based dedup prevents duplicates."""

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_no_dedup_match_creates_new_session(self, mock_get_sb, mock_profile, mock_sb, base_args):
        """When no recent session with same params exists, create new one."""
        mock_get_sb.return_value = mock_sb

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "new-session-id"
        mock_sb.table.return_value.insert.assert_called_once()

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_param_dedup_returns_existing_session(self, mock_get_sb, mock_profile, base_args):
        """When session with same params exists within 5min, reuse it."""
        # Use sequential table calls to handle multiple query chains
        call_count = 0
        recent_time = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                # First: search_id dedup check → no match
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[]
                )
            elif call_count == 2:
                # Second: parameter-based dedup check → match found
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[{"id": "existing-param-session", "created_at": recent_time}]
                )
            else:
                # Insert (should not be called)
                mock_table.insert.return_value.execute.return_value = MagicMock(
                    data=[{"id": "should-not-reach"}]
                )
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "existing-param-session"
        # Insert should NOT have been called
        assert call_count == 2  # Only search_id check + param check

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_param_dedup_failure_falls_through_to_insert(self, mock_get_sb, mock_profile, base_args):
        """If param dedup check fails (DB error), fall through to insert."""
        call_count = 0

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                # search_id check → no match
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[]
                )
            elif call_count == 2:
                # param dedup check → DB error
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.side_effect = Exception("DB timeout")
            else:
                # Insert succeeds
                mock_table.insert.return_value.execute.return_value = MagicMock(
                    data=[{"id": "fallback-insert-id"}]
                )
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "fallback-insert-id"


# ===========================================================================
# AC2: Cache hits merged with original session
# ===========================================================================

class TestCacheHitMerge:
    """CRIT-029 AC2: Cache hits (fast responses) update existing session."""

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_second_search_same_params_reuses_session(self, mock_get_sb, mock_profile, base_args):
        """Simulates: search A (183s) creates session, search B (0.5s cache) reuses it."""
        call_count = 0
        original_session_time = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                # search_id check for second search → no match (different search_id)
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[]
                )
            elif call_count == 2:
                # param dedup → finds original session from 1 minute ago
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[{"id": "original-session-from-search-A", "created_at": original_session_time}]
                )
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        # Second search has a different search_id (as frontend generates new one each time)
        base_args["search_id"] = "search-crit029-002-different"

        from quota import register_search_session
        result = await register_search_session(**base_args)

        # Should reuse the existing session, not create new
        assert result == "original-session-from-search-A"

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_different_params_creates_new_session(self, mock_get_sb, mock_profile, base_args):
        """Different sector → should NOT match dedup → new session."""
        call_count = 0

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                # search_id check → no match
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[]
                )
            elif call_count == 2:
                # param dedup → no match (different sector)
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[]
                )
            else:
                # Insert new session
                mock_table.insert.return_value.execute.return_value = MagicMock(
                    data=[{"id": "new-sector-session"}]
                )
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        # Different sector
        base_args["sectors"] = ["vestuario"]

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "new-sector-session"


# ===========================================================================
# AC3: Dedup uses composite key (user + sectors + ufs + date_range)
# ===========================================================================

class TestCompositeKeyDedup:
    """CRIT-029 AC3: Dedup verifies full composite key."""

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_different_ufs_creates_new_session(self, mock_get_sb, mock_profile, base_args):
        """Different UFs → not a duplicate → new session."""
        call_count = 0

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            elif call_count == 2:
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            else:
                mock_table.insert.return_value.execute.return_value = MagicMock(data=[{"id": "new-ufs-session"}])
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        base_args["ufs"] = ["MG", "BA"]  # Different UFs

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "new-ufs-session"

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_different_dates_creates_new_session(self, mock_get_sb, mock_profile, base_args):
        """Different date range → not a duplicate → new session."""
        call_count = 0

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            elif call_count == 2:
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            else:
                mock_table.insert.return_value.execute.return_value = MagicMock(data=[{"id": "new-dates-session"}])
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        base_args["data_final"] = "2026-02-20"  # Different end date

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "new-dates-session"

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_ufs_sorted_for_consistent_matching(self, mock_get_sb, mock_profile, base_args):
        """UFs should be sorted before comparison to ensure RJ,SP matches SP,RJ."""
        call_count = 0
        recent_time = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            elif call_count == 2:
                # Param dedup finds match
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[{"id": "sorted-match-session", "created_at": recent_time}]
                )
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        # UFs in reverse order (RJ, SP instead of SP, RJ)
        base_args["ufs"] = ["RJ", "SP"]

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "sorted-match-session"

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_no_search_id_still_does_param_dedup(self, mock_get_sb, mock_profile, base_args):
        """Even without search_id, param-based dedup still works."""
        call_count = 0
        recent_time = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count == 1:
                # First call is param dedup (search_id check skipped)
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[{"id": "param-match-no-sid", "created_at": recent_time}]
                )
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        base_args["search_id"] = None

        from quota import register_search_session
        result = await register_search_session(**base_args)

        assert result == "param-match-no-sid"


# ===========================================================================
# AC4: Integration-level test: search + cache-hit retry → 1 entry
# ===========================================================================

class TestSearchRetryDedup:
    """CRIT-029 AC4: Search + immediate retry produces only 1 history entry."""

    @pytest.mark.asyncio
    @patch("quota._ensure_profile_exists", return_value=True)
    @patch("supabase_client.get_supabase")
    async def test_search_then_retry_produces_single_session(self, mock_get_sb, mock_profile, base_args):
        """First call creates session, second call (retry) reuses it."""
        first_session_id = "session-first-call"
        call_count = 0
        creation_time = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()

        def table_side_effect(table_name):
            nonlocal call_count
            call_count += 1
            mock_table = MagicMock()

            if call_count <= 2:
                # First register_search_session call:
                # 1. search_id check → no match
                # 2. param dedup → no match
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            elif call_count == 3:
                # Insert for first call
                mock_table.insert.return_value.execute.return_value = MagicMock(
                    data=[{"id": first_session_id}]
                )
            elif call_count == 4:
                # Second register_search_session call: search_id check → no match
                mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            elif call_count == 5:
                # Second call: param dedup → match (first session)
                mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[{"id": first_session_id, "created_at": creation_time}]
                )
            return mock_table

        sb = MagicMock()
        sb.table.side_effect = table_side_effect
        mock_get_sb.return_value = sb

        from quota import register_search_session

        # First search
        result1 = await register_search_session(**base_args)
        assert result1 == first_session_id

        # Retry (different search_id, same params)
        base_args["search_id"] = "search-crit029-retry"
        result2 = await register_search_session(**base_args)
        assert result2 == first_session_id

        # Both calls return the same session ID → only 1 history entry
        assert result1 == result2
