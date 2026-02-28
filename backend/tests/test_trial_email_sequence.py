"""
STORY-310 AC15-AC18: Tests for trial email sequence.

AC15: Tests for each email in the sequence (8 emails x scenarios).
AC16: Tests for cron job (scheduling, dedup, rate limit, skip converted).
AC17: Tests for stats query.
AC18: Zero regressions.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta


# ============================================================================
# AC15: Template rendering tests — 8 emails
# ============================================================================

from templates.emails.trial import (
    render_trial_welcome_email,
    render_trial_midpoint_email,
    render_trial_engagement_email,
    render_trial_tips_email,
    render_trial_urgency_email,
    render_trial_expiring_email,
    render_trial_last_day_email,
    render_trial_expired_email,
    _format_brl,
    _stats_block,
    _unsubscribe_block,
)


SAMPLE_STATS = {
    "searches_count": 12,
    "opportunities_found": 47,
    "total_value_estimated": 2_350_000,
    "pipeline_items_count": 8,
    "sectors_searched": ["software", "saude", "construcao"],
}

ZERO_STATS = {
    "searches_count": 0,
    "opportunities_found": 0,
    "total_value_estimated": 0,
    "pipeline_items_count": 0,
    "sectors_searched": [],
}

UNSUB_URL = "https://api.smartlic.tech/v1/trial-emails/unsubscribe?user_id=test&token=abc"


class TestUnsubscribeBlock:
    """Test unsubscribe block rendering."""

    def test_renders_when_url_provided(self):
        html = _unsubscribe_block(UNSUB_URL)
        assert "unsubscribe" in html
        assert "trial" in html.lower()

    def test_empty_when_no_url(self):
        html = _unsubscribe_block("")
        assert html == ""


class TestWelcomeEmail:
    """AC15: Email #1 — Day 0: Welcome."""

    def test_renders_without_error(self):
        html = render_trial_welcome_email("João")
        assert "<!DOCTYPE html>" in html

    def test_contains_user_name(self):
        html = render_trial_welcome_email("Maria Silva")
        assert "Maria Silva" in html

    def test_contains_welcome_message(self):
        html = render_trial_welcome_email("Test")
        assert "Bem-vindo" in html

    def test_contains_30_day_trial_mention(self):
        html = render_trial_welcome_email("Test")
        assert "30 dias" in html

    def test_contains_buscar_cta(self):
        html = render_trial_welcome_email("Test")
        assert "/buscar" in html
        assert "primeira busca" in html.lower()

    def test_contains_feature_list(self):
        html = render_trial_welcome_email("Test")
        assert "Pipeline" in html or "pipeline" in html
        assert "Excel" in html

    def test_contains_unsubscribe_link(self):
        html = render_trial_welcome_email("Test", unsubscribe_url=UNSUB_URL)
        assert "unsubscribe" in html

    def test_is_not_transactional(self):
        """Welcome email should include unsubscribe option."""
        html = render_trial_welcome_email("Test", unsubscribe_url=UNSUB_URL)
        assert "Cancelar inscrição" in html or "unsubscribe" in html


class TestMidpointEmail:
    """AC15: Email #2 — Day 3: Engagement Early."""

    def test_renders_with_stats(self):
        html = render_trial_midpoint_email("João", SAMPLE_STATS)
        assert "<!DOCTYPE html>" in html

    def test_shows_value_when_used(self):
        html = render_trial_midpoint_email("Test", SAMPLE_STATS)
        assert "2.4M" in html or "2.3M" in html  # _format_brl rounding

    def test_adapts_for_zero_usage(self):
        html = render_trial_midpoint_email("Test", ZERO_STATS)
        assert "27 dias" in html

    def test_contains_buscar_cta(self):
        html = render_trial_midpoint_email("Test", SAMPLE_STATS)
        assert "/buscar" in html

    def test_empty_stats_safe(self):
        html = render_trial_midpoint_email("Test", {})
        assert "<!DOCTYPE html>" in html

    def test_unsubscribe_url_passed(self):
        html = render_trial_midpoint_email("Test", SAMPLE_STATS, unsubscribe_url=UNSUB_URL)
        assert "unsubscribe" in html


class TestEngagementEmail:
    """AC15: Email #3 — Day 7: Engagement."""

    def test_renders_without_error(self):
        html = render_trial_engagement_email("João", SAMPLE_STATS)
        assert "<!DOCTYPE html>" in html

    def test_contains_feature_education(self):
        html = render_trial_engagement_email("Test", SAMPLE_STATS)
        assert "Pipeline" in html or "pipeline" in html
        assert "Excel" in html

    def test_shows_opportunities_count(self):
        html = render_trial_engagement_email("Test", SAMPLE_STATS)
        assert "47" in html

    def test_adapts_for_zero_usage(self):
        html = render_trial_engagement_email("Test", ZERO_STATS)
        assert "poder completo" in html.lower() or "descubra" in html.lower()

    def test_23_days_remaining(self):
        html = render_trial_engagement_email("Test", SAMPLE_STATS)
        assert "23 dias" in html

    def test_empty_stats_safe(self):
        html = render_trial_engagement_email("Test", {})
        assert "<!DOCTYPE html>" in html


class TestTipsEmail:
    """AC15: Email #4 — Day 14: Tips."""

    def test_renders_without_error(self):
        html = render_trial_tips_email("João", SAMPLE_STATS)
        assert "<!DOCTYPE html>" in html

    def test_contains_tips(self):
        html = render_trial_tips_email("Test", SAMPLE_STATS)
        assert "dica" in html.lower() or "Dica" in html

    def test_shows_value_in_headline(self):
        html = render_trial_tips_email("Test", SAMPLE_STATS)
        assert "2.4M" in html or "2.3M" in html or "Metade" in html

    def test_shows_sector_tips(self):
        html = render_trial_tips_email("Test", SAMPLE_STATS)
        assert "software" in html

    def test_adapts_for_zero_usage(self):
        html = render_trial_tips_email("Test", ZERO_STATS)
        assert "Metade" in html or "dica" in html.lower()

    def test_16_days_remaining(self):
        html = render_trial_tips_email("Test", SAMPLE_STATS)
        assert "16 dias" in html

    def test_empty_stats_safe(self):
        html = render_trial_tips_email("Test", {})
        assert "<!DOCTYPE html>" in html


class TestUrgencyEmail:
    """AC15: Email #5 — Day 21: Urgency Light."""

    def test_renders_without_error(self):
        html = render_trial_urgency_email("João", SAMPLE_STATS)
        assert "<!DOCTYPE html>" in html

    def test_shows_days_remaining(self):
        html = render_trial_urgency_email("Test", SAMPLE_STATS, days_remaining=9)
        assert "9 dias" in html

    def test_shows_value_in_headline(self):
        html = render_trial_urgency_email("Test", SAMPLE_STATS)
        assert "2.4M" in html or "2.3M" in html or "oportunidades" in html

    def test_mentions_smartlic_pro(self):
        html = render_trial_urgency_email("Test", SAMPLE_STATS)
        assert "SmartLic Pro" in html

    def test_planos_cta(self):
        html = render_trial_urgency_email("Test", SAMPLE_STATS)
        assert "/planos" in html

    def test_custom_days(self):
        html = render_trial_urgency_email("Test", ZERO_STATS, days_remaining=5)
        assert "5 dias" in html

    def test_empty_stats_safe(self):
        html = render_trial_urgency_email("Test", {})
        assert "<!DOCTYPE html>" in html


class TestExpiringEmail:
    """AC15: Email #6 — Day 25: Expiring."""

    def test_renders_without_error(self):
        html = render_trial_expiring_email("João", 5, SAMPLE_STATS)
        assert "<!DOCTYPE html>" in html

    def test_contains_days_remaining(self):
        html = render_trial_expiring_email("Test", 5, {})
        assert "5 dias" in html

    def test_contains_planos_cta(self):
        html = render_trial_expiring_email("Test", 5, {})
        assert "/planos" in html

    def test_shows_pipeline(self):
        html = render_trial_expiring_email("Test", 5, SAMPLE_STATS)
        assert "8" in html  # pipeline items

    def test_empty_stats_safe(self):
        html = render_trial_expiring_email("Test", 5, {})
        assert "<!DOCTYPE html>" in html


class TestLastDayEmail:
    """AC15: Email #7 — Day 29: Last Day."""

    def test_renders_without_error(self):
        html = render_trial_last_day_email("João", SAMPLE_STATS)
        assert "<!DOCTYPE html>" in html

    def test_urgency_styling(self):
        html = render_trial_last_day_email("Test", SAMPLE_STATS)
        assert "#d32f2f" in html

    def test_contains_price(self):
        html = render_trial_last_day_email("Test", SAMPLE_STATS)
        assert "397" in html

    def test_mentions_tomorrow(self):
        html = render_trial_last_day_email("Test", {})
        assert "Amanhã" in html

    def test_empty_stats_safe(self):
        html = render_trial_last_day_email("Test", {})
        assert "<!DOCTYPE html>" in html


class TestExpiredEmail:
    """AC15: Email #8 — Day 32: Expired."""

    def test_renders_without_error(self):
        html = render_trial_expired_email("João", SAMPLE_STATS)
        assert "<!DOCTYPE html>" in html

    def test_mentions_data_saved(self):
        html = render_trial_expired_email("Test", SAMPLE_STATS)
        assert "30 dias" in html

    def test_reactivation_cta(self):
        html = render_trial_expired_email("Test", SAMPLE_STATS)
        assert "/planos" in html
        assert "Reativar" in html

    def test_adapts_headline_pipeline(self):
        html = render_trial_expired_email("Test", {
            "opportunities_found": 30,
            "pipeline_items_count": 5,
        })
        assert "5 oportunidades" in html

    def test_adapts_headline_opps(self):
        html = render_trial_expired_email("Test", {
            "opportunities_found": 30,
            "pipeline_items_count": 0,
        })
        assert "30 oportunidades" in html

    def test_zero_usage_generic(self):
        html = render_trial_expired_email("Test", ZERO_STATS)
        assert "continuam surgindo" in html.lower()

    def test_empty_stats_safe(self):
        html = render_trial_expired_email("Test", {})
        assert "<!DOCTYPE html>" in html


# ============================================================================
# AC17: Stats query tests
# ============================================================================

class TestGetTrialUserStats:
    """AC17: Test get_trial_user_stats function."""

    def test_returns_dict_with_required_keys(self):
        """AC12: Returns all required fields."""
        mock_base_stats = MagicMock()
        mock_base_stats.model_dump.return_value = {
            "searches_count": 5,
            "opportunities_found": 20,
            "total_value_estimated": 500_000,
            "pipeline_items_count": 3,
            "sectors_searched": ["software"],
        }

        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()}]
        )

        with patch("services.trial_stats.get_trial_usage_stats", return_value=mock_base_stats), \
             patch("supabase_client.get_supabase", return_value=mock_sb):
            from services.trial_email_sequence import get_trial_user_stats
            result = get_trial_user_stats("user-123")

        assert "searches_executed" in result
        assert "opportunities_found" in result
        assert "total_value_analyzed" in result
        assert "pipeline_items" in result
        assert "days_remaining" in result
        assert result["searches_executed"] == 5
        assert result["days_remaining"] in (19, 20)  # 30 - 10, +/- 1 due to time-of-day

    def test_days_remaining_zero_when_expired(self):
        """Days remaining is 0 when trial has expired."""
        mock_base_stats = MagicMock()
        mock_base_stats.model_dump.return_value = {
            "searches_count": 0,
            "opportunities_found": 0,
            "total_value_estimated": 0,
            "pipeline_items_count": 0,
            "sectors_searched": [],
        }

        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()}]
        )

        with patch("services.trial_stats.get_trial_usage_stats", return_value=mock_base_stats), \
             patch("supabase_client.get_supabase", return_value=mock_sb):
            from services.trial_email_sequence import get_trial_user_stats
            result = get_trial_user_stats("user-456")

        assert result["days_remaining"] == 0

    def test_handles_missing_profile(self):
        """Returns 0 days_remaining when profile not found."""
        mock_base_stats = MagicMock()
        mock_base_stats.model_dump.return_value = {
            "searches_count": 0,
            "opportunities_found": 0,
            "total_value_estimated": 0,
            "pipeline_items_count": 0,
            "sectors_searched": [],
        }

        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

        with patch("services.trial_stats.get_trial_usage_stats", return_value=mock_base_stats), \
             patch("supabase_client.get_supabase", return_value=mock_sb):
            from services.trial_email_sequence import get_trial_user_stats
            result = get_trial_user_stats("user-missing")

        assert result["days_remaining"] == 0

    def test_handles_db_error_gracefully(self):
        """Returns 0 days_remaining on DB error."""
        mock_base_stats = MagicMock()
        mock_base_stats.model_dump.return_value = {
            "searches_count": 0,
            "opportunities_found": 0,
            "total_value_estimated": 0,
            "pipeline_items_count": 0,
            "sectors_searched": [],
        }

        mock_sb = MagicMock()
        mock_sb.table.side_effect = Exception("DB unavailable")

        with patch("services.trial_stats.get_trial_usage_stats", return_value=mock_base_stats), \
             patch("supabase_client.get_supabase", return_value=mock_sb):
            from services.trial_email_sequence import get_trial_user_stats
            result = get_trial_user_stats("user-err")

        assert result["days_remaining"] == 0
        assert result["searches_executed"] == 0


# ============================================================================
# AC16: Cron job / process_trial_emails tests
# ============================================================================

class TestProcessTrialEmails:
    """AC16: Test the process_trial_emails dispatch function."""

    @pytest.mark.asyncio
    async def test_disabled_flag_skips(self):
        """AC3: When TRIAL_EMAILS_ENABLED=false, does nothing."""
        with patch("config.TRIAL_EMAILS_ENABLED", False):
            from services.trial_email_sequence import process_trial_emails
            result = await process_trial_emails()
            assert result.get("disabled") is True
            assert result["sent"] == 0

    @pytest.mark.asyncio
    async def test_sends_welcome_email_day_0(self):
        """AC1: Day 0 users receive welcome email."""
        from services.trial_email_sequence import process_trial_emails

        mock_sb = MagicMock()

        # Track table calls
        def table_side_effect(name):
            if name == "profiles":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.gte.return_value = chain
                chain.lt.return_value = chain

                call_count = [0]
                def execute():
                    call_count[0] += 1
                    if call_count[0] == 1:  # First call is for day 0 (welcome)
                        return MagicMock(data=[{
                            "id": "user-welcome-uuid",
                            "email": "new@example.com",
                            "full_name": "Novo Usuario",
                            "plan_type": "free_trial",
                            "marketing_emails_enabled": True,
                        }])
                    return MagicMock(data=[])
                chain.execute = AsyncMock(side_effect=execute)
                return chain
            elif name == "trial_email_log":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.limit.return_value = chain
                chain.execute = AsyncMock(return_value=MagicMock(data=[]))
                chain.insert.return_value = chain
                return chain
            return MagicMock()

        mock_sb.table.side_effect = table_side_effect

        mock_stats = {
            "searches_count": 0,
            "opportunities_found": 0,
            "total_value_estimated": 0,
            "pipeline_items_count": 0,
            "sectors_searched": [],
            "searches_executed": 0,
            "total_value_analyzed": 0,
            "pipeline_items": 0,
            "days_remaining": 30,
        }

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect), \
             patch("services.trial_email_sequence.get_trial_user_stats", return_value=mock_stats), \
             patch("email_service.send_email_async") as mock_send, \
             patch("metrics.TRIAL_EMAILS_SENT"):

            result = await process_trial_emails()

            assert result["sent"] >= 1
            mock_send.assert_called()
            # Verify welcome email was among the calls (first call)
            first_call = mock_send.call_args_list[0]
            assert "Bem-vindo" in first_call.kwargs.get("subject", "") or "Bem-vindo" in str(first_call)

    @pytest.mark.asyncio
    async def test_skips_converted_users(self):
        """AC4: Users who converted to paid are skipped."""
        from services.trial_email_sequence import process_trial_emails

        mock_sb = MagicMock()

        def table_side_effect(name):
            if name == "profiles":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.gte.return_value = chain
                chain.lt.return_value = chain
                # Return user with paid plan (shouldn't happen since we query free_trial,
                # but double-check in code)
                chain.execute = AsyncMock(return_value=MagicMock(data=[{
                    "id": "user-paid-uuid",
                    "email": "paid@example.com",
                    "full_name": "Paid User",
                    "plan_type": "smartlic_pro",  # Already converted!
                    "marketing_emails_enabled": True,
                }]))
                return chain
            return MagicMock()

        mock_sb.table.side_effect = table_side_effect

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect), \
             patch("email_service.send_email_async") as mock_send, \
             patch("metrics.TRIAL_EMAILS_SENT"):

            result = await process_trial_emails()

            assert result["converted_skipped"] >= 1
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_unsubscribed_users(self):
        """AC5: Users who opted out of marketing emails are skipped."""
        from services.trial_email_sequence import process_trial_emails

        mock_sb = MagicMock()

        def table_side_effect(name):
            if name == "profiles":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.gte.return_value = chain
                chain.lt.return_value = chain
                chain.execute = AsyncMock(return_value=MagicMock(data=[{
                    "id": "user-unsub-uuid",
                    "email": "unsub@example.com",
                    "full_name": "Unsub User",
                    "plan_type": "free_trial",
                    "marketing_emails_enabled": False,  # Unsubscribed!
                }]))
                return chain
            return MagicMock()

        mock_sb.table.side_effect = table_side_effect

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect), \
             patch("email_service.send_email_async") as mock_send, \
             patch("metrics.TRIAL_EMAILS_SENT"):

            result = await process_trial_emails()

            assert result["unsubscribed_skipped"] >= 1
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_idempotency_skips_already_sent(self):
        """AC16: Running job twice doesn't send duplicate emails."""
        from services.trial_email_sequence import process_trial_emails

        mock_sb = MagicMock()

        def table_side_effect(name):
            if name == "profiles":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.gte.return_value = chain
                chain.lt.return_value = chain

                call_count = [0]
                def execute():
                    call_count[0] += 1
                    if call_count[0] == 1:
                        return MagicMock(data=[{
                            "id": "user-dup-uuid",
                            "email": "dup@example.com",
                            "full_name": "Dup User",
                            "plan_type": "free_trial",
                            "marketing_emails_enabled": True,
                        }])
                    return MagicMock(data=[])
                chain.execute = AsyncMock(side_effect=execute)
                return chain
            elif name == "trial_email_log":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.limit.return_value = chain
                # Return existing log = already sent!
                chain.execute = AsyncMock(return_value=MagicMock(data=[{"id": "existing-log"}]))
                return chain
            return MagicMock()

        mock_sb.table.side_effect = table_side_effect

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect), \
             patch("email_service.send_email_async") as mock_send, \
             patch("metrics.TRIAL_EMAILS_SENT"):

            result = await process_trial_emails()

            assert result["skipped"] >= 1
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_batch_limit_respected(self):
        """AC9: Batch limit stops processing after max emails."""
        from services.trial_email_sequence import process_trial_emails

        mock_sb = MagicMock()

        # Return many users for every milestone
        def table_side_effect(name):
            if name == "profiles":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.gte.return_value = chain
                chain.lt.return_value = chain
                # Return 10 users per milestone
                chain.execute = AsyncMock(return_value=MagicMock(data=[
                    {
                        "id": f"user-batch-{i}",
                        "email": f"batch{i}@example.com",
                        "full_name": f"Batch User {i}",
                        "plan_type": "free_trial",
                        "marketing_emails_enabled": True,
                    }
                    for i in range(10)
                ]))
                return chain
            elif name == "trial_email_log":
                chain = MagicMock()
                chain.select.return_value = chain
                chain.eq.return_value = chain
                chain.limit.return_value = chain
                chain.execute = AsyncMock(return_value=MagicMock(data=[]))
                chain.insert.return_value = chain
                return chain
            return MagicMock()

        mock_sb.table.side_effect = table_side_effect

        mock_stats_dict = {
            **ZERO_STATS,
            "searches_executed": 0,
            "total_value_analyzed": 0,
            "pipeline_items": 0,
            "days_remaining": 30,
        }

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect), \
             patch("services.trial_email_sequence.get_trial_user_stats", return_value=mock_stats_dict), \
             patch("email_service.send_email_async"), \
             patch("metrics.TRIAL_EMAILS_SENT"):

            result = await process_trial_emails(batch_size=5)

            # Should stop at 5 despite many more users available
            assert result["sent"] <= 5

    @pytest.mark.asyncio
    async def test_no_users_at_milestone(self):
        """No users at any milestone = zero sent."""
        from services.trial_email_sequence import process_trial_emails

        mock_sb = MagicMock()
        empty_chain = MagicMock()
        empty_chain.select.return_value = empty_chain
        empty_chain.eq.return_value = empty_chain
        empty_chain.gte.return_value = empty_chain
        empty_chain.lt.return_value = empty_chain
        empty_chain.execute = AsyncMock(return_value=MagicMock(data=[]))

        mock_sb.table.return_value = empty_chain

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect):

            result = await process_trial_emails()
            assert result["sent"] == 0
            assert result["errors"] == 0


# ============================================================================
# Unsubscribe + Webhook tests
# ============================================================================

class TestUnsubscribe:
    """Test unsubscribe token generation and verification."""

    def test_token_roundtrip(self):
        from services.trial_email_sequence import _generate_unsubscribe_token, verify_unsubscribe_token
        user_id = "test-user-123"
        token = _generate_unsubscribe_token(user_id)
        assert verify_unsubscribe_token(user_id, token) is True

    def test_invalid_token_rejected(self):
        from services.trial_email_sequence import verify_unsubscribe_token
        assert verify_unsubscribe_token("test-user-123", "invalid-token") is False

    def test_different_user_rejected(self):
        from services.trial_email_sequence import _generate_unsubscribe_token, verify_unsubscribe_token
        token = _generate_unsubscribe_token("user-1")
        assert verify_unsubscribe_token("user-2", token) is False

    def test_url_generation(self):
        from services.trial_email_sequence import get_unsubscribe_url
        url = get_unsubscribe_url("user-123")
        assert "user_id=user-123" in url
        assert "token=" in url


class TestRenderEmail:
    """Test _render_email dispatcher."""

    def test_all_types_render(self):
        """All 8 email types render without error."""
        from services.trial_email_sequence import _render_email

        for email_type in [
            "welcome", "engagement_early", "engagement", "tips",
            "urgency", "expiring", "last_day", "expired",
        ]:
            subject, html = _render_email(
                email_type=email_type,
                user_name="Test User",
                stats=SAMPLE_STATS,
                unsubscribe_url=UNSUB_URL,
            )
            assert subject, f"Empty subject for {email_type}"
            assert "<!DOCTYPE html>" in html, f"Invalid HTML for {email_type}"

    def test_unknown_type_raises(self):
        from services.trial_email_sequence import _render_email
        with pytest.raises(ValueError, match="Unknown email type"):
            _render_email(email_type="nonexistent", user_name="T", stats={})


class TestResendWebhook:
    """AC11: Test Resend webhook handler."""

    @pytest.mark.asyncio
    async def test_handles_opened_event(self):
        from services.trial_email_sequence import handle_resend_webhook

        mock_sb = MagicMock()
        mock_chain = MagicMock()
        mock_chain.update.return_value = mock_chain
        mock_chain.eq.return_value = mock_chain
        mock_chain.is_.return_value = mock_chain
        mock_chain.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_sb.table.return_value = mock_chain

        with patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect):
            result = await handle_resend_webhook("email.opened", {"email_id": "res-123"})
            assert result is True

    @pytest.mark.asyncio
    async def test_handles_clicked_event(self):
        from services.trial_email_sequence import handle_resend_webhook

        mock_sb = MagicMock()
        mock_chain = MagicMock()
        mock_chain.update.return_value = mock_chain
        mock_chain.eq.return_value = mock_chain
        mock_chain.is_.return_value = mock_chain
        mock_chain.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_sb.table.return_value = mock_chain

        with patch("supabase_client.get_supabase", return_value=mock_sb), \
             patch("supabase_client.sb_execute", side_effect=_sb_execute_side_effect):
            result = await handle_resend_webhook("email.clicked", {"email_id": "res-456"})
            assert result is True

    @pytest.mark.asyncio
    async def test_ignores_unknown_event(self):
        from services.trial_email_sequence import handle_resend_webhook
        result = await handle_resend_webhook("email.bounced", {"email_id": "res-789"})
        assert result is False

    @pytest.mark.asyncio
    async def test_skips_missing_email_id(self):
        from services.trial_email_sequence import handle_resend_webhook
        result = await handle_resend_webhook("email.opened", {})
        assert result is False


# ============================================================================
# STORY-310 Cron Integration tests
# ============================================================================

class TestCronJobIntegration:
    """Test cron_jobs.py integration with trial email sequence."""

    def test_trial_sequence_constants_exist(self):
        """STORY-310 constants are defined in cron_jobs."""
        from cron_jobs import TRIAL_SEQUENCE_INTERVAL_SECONDS, TRIAL_SEQUENCE_BATCH_SIZE
        assert TRIAL_SEQUENCE_INTERVAL_SECONDS == 86400  # 24h
        assert TRIAL_SEQUENCE_BATCH_SIZE == 50

    @pytest.mark.asyncio
    async def test_start_trial_sequence_task_returns_task(self):
        """start_trial_sequence_task returns an asyncio.Task."""
        import asyncio
        from cron_jobs import start_trial_sequence_task
        task = await start_trial_sequence_task()
        assert isinstance(task, asyncio.Task)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# ============================================================================
# Helpers
# ============================================================================

async def _sb_execute_side_effect(query):
    """Mock sb_execute: call .execute() on the query chain."""
    if hasattr(query, 'execute'):
        result = query.execute
        if callable(result):
            ret = result()
            if hasattr(ret, '__await__'):
                return await ret
            return ret
        return result
    return query


_mock_sb_execute = AsyncMock(side_effect=_sb_execute_side_effect)
