"""SEO-PLAYBOOK §7.4 + §Day-3 Activation — tests for the opt-in extensions
to the trial email sequence (activation_nudge, referral_invitation).

These tests assert:

1. The base `TRIAL_EMAIL_SEQUENCE` list is UNCHANGED (backward compatibility
   with the existing 6-email STORY-321 flow).
2. `_active_sequence()` appends extra entries only when the corresponding
   feature flag is on.
3. `activation_nudge` is skipped when the user has already searched
   (`stats.searches_count > 0`), sent otherwise.
4. `referral_invitation` renders with the user's real referral code.
5. The Day-3 activation template renders without error and contains the
   expected copy hooks.

Tests mock Supabase / email_service to avoid any real I/O.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# ============================================================================
# Sequence shape tests
# ============================================================================


class TestSequenceShape:
    def test_base_sequence_unchanged(self):
        """STORY-321 baseline must not regress."""
        from services.trial_email_sequence import TRIAL_EMAIL_SEQUENCE
        assert len(TRIAL_EMAIL_SEQUENCE) == 6
        assert [e["type"] for e in TRIAL_EMAIL_SEQUENCE] == [
            "welcome",
            "engagement",
            "paywall_alert",
            "value",
            "last_day",
            "expired",
        ]

    def test_active_sequence_default_flags_off(self):
        """With all optional flags false, _active_sequence == TRIAL_EMAIL_SEQUENCE."""
        with patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", False), \
             patch("config.REFERRAL_EMAIL_ENABLED", False), \
             patch("config.features.FEATURE_DISCOVERY_EMAILS_ENABLED", False):
            from services.trial_email_sequence import _active_sequence
            seq = _active_sequence()
            assert len(seq) == 6

    def test_active_sequence_day3_enabled(self):
        with patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", True), \
             patch("config.REFERRAL_EMAIL_ENABLED", False), \
             patch("config.features.FEATURE_DISCOVERY_EMAILS_ENABLED", False):
            from services.trial_email_sequence import _active_sequence
            seq = _active_sequence()
            assert len(seq) == 7
            types = [e["type"] for e in seq]
            assert "activation_nudge" in types

    def test_active_sequence_referral_enabled(self):
        with patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", False), \
             patch("config.REFERRAL_EMAIL_ENABLED", True), \
             patch("config.features.FEATURE_DISCOVERY_EMAILS_ENABLED", False):
            from services.trial_email_sequence import _active_sequence
            seq = _active_sequence()
            assert len(seq) == 7
            types = [e["type"] for e in seq]
            assert "referral_invitation" in types

    def test_active_sequence_both_enabled(self):
        with patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", True), \
             patch("config.REFERRAL_EMAIL_ENABLED", True), \
             patch("config.SHARE_ACTIVATION_EMAIL_ENABLED", False), \
             patch("config.features.FEATURE_DISCOVERY_EMAILS_ENABLED", False):
            from services.trial_email_sequence import _active_sequence
            seq = _active_sequence()
            assert len(seq) == 8

    def test_active_sequence_share_activation_enabled(self):
        with patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", False), \
             patch("config.REFERRAL_EMAIL_ENABLED", False), \
             patch("config.SHARE_ACTIVATION_EMAIL_ENABLED", True), \
             patch("config.features.FEATURE_DISCOVERY_EMAILS_ENABLED", False):
            from services.trial_email_sequence import _active_sequence
            seq = _active_sequence()
            assert len(seq) == 7
            types = [e["type"] for e in seq]
            assert "share_activation" in types

    def test_active_sequence_all_three_optional_enabled(self):
        with patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", True), \
             patch("config.REFERRAL_EMAIL_ENABLED", True), \
             patch("config.SHARE_ACTIVATION_EMAIL_ENABLED", True), \
             patch("config.features.FEATURE_DISCOVERY_EMAILS_ENABLED", False):
            from services.trial_email_sequence import _active_sequence
            seq = _active_sequence()
            assert len(seq) == 9
            types = [e["type"] for e in seq]
            assert set(["activation_nudge", "referral_invitation", "share_activation"]).issubset(types)

    def test_active_sequence_feature_discovery_enabled(self):
        """Feature discovery adds 3 emails (pipeline, excel, ai)."""
        with patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", False), \
             patch("config.REFERRAL_EMAIL_ENABLED", False), \
             patch("config.features.FEATURE_DISCOVERY_EMAILS_ENABLED", True):
            from services.trial_email_sequence import _active_sequence
            seq = _active_sequence()
            assert len(seq) == 9  # 6 base + 3 feature discovery
            types = [e["type"] for e in seq]
            assert "feature_pipeline" in types
            assert "feature_excel" in types
            assert "feature_ai" in types


# ============================================================================
# Template tests
# ============================================================================


class TestDay3ActivationTemplate:
    def test_renders_with_user_name(self):
        from templates.emails.day3_activation import render_day3_activation_email
        html = render_day3_activation_email(user_name="João", unsubscribe_url="https://u")
        assert "João" in html
        # Must contain primary CTA to /buscar (the aha moment entry point)
        assert "/buscar" in html
        # Must contain the headline hook copy
        assert "30 segundos" in html

    def test_renders_without_unsubscribe_url(self):
        from templates.emails.day3_activation import render_day3_activation_email
        html = render_day3_activation_email(user_name="Maria")
        assert "Maria" in html


class TestRenderEmailDispatch:
    def test_render_activation_nudge(self):
        from services.trial_email_sequence import _render_email
        subject, html = _render_email(
            email_type="activation_nudge",
            user_name="Teste",
            stats={"searches_count": 0},
            unsubscribe_url="https://u",
        )
        assert "30 segundos" in subject
        assert "/buscar" in html

    def test_render_referral_invitation_with_code(self):
        from services.trial_email_sequence import _render_email

        # Mock supabase lookup to return a known code
        fake_sb = MagicMock()
        fake_sb.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"code": "ABCD1234"}]
        )

        with patch("supabase_client.get_supabase", return_value=fake_sb):
            subject, html = _render_email(
                email_type="referral_invitation",
                user_name="Beta",
                stats={"user_id": "user-xyz"},
                unsubscribe_url="https://u",
            )
        assert "1 mês grátis" in subject
        assert "ABCD1234" in html

    def test_render_referral_invitation_without_code_fallback(self):
        """When the referral code lookup fails we still render a safe email."""
        from services.trial_email_sequence import _render_email

        with patch("supabase_client.get_supabase", side_effect=RuntimeError("db down")):
            subject, html = _render_email(
                email_type="referral_invitation",
                user_name="Gamma",
                stats={"user_id": "user-xyz"},
                unsubscribe_url="https://u",
            )
        # Fallback link should point at /indicar when code is missing
        assert "/indicar" in html


# ============================================================================
# Activation-nudge dispatch filter
# ============================================================================


class TestShareActivationTemplate:
    def test_renders_with_opps_plural(self):
        from templates.emails.share_activation import render_share_activation_email
        html = render_share_activation_email(
            user_name="Ana", opportunities_found=12, unsubscribe_url="https://u"
        )
        assert "Ana" in html
        assert "12" in html
        assert "oportunidades" in html
        # Primary CTA entry point
        assert "/buscar" in html

    def test_renders_with_opps_singular(self):
        from templates.emails.share_activation import render_share_activation_email
        html = render_share_activation_email(
            user_name="Beto", opportunities_found=1, unsubscribe_url=""
        )
        assert "1 oportunidade" in html

    def test_renders_with_zero_opps_graceful(self):
        from templates.emails.share_activation import render_share_activation_email
        # Even with zero opps the template must render (filter happens
        # upstream in process_trial_emails, not here).
        html = render_share_activation_email(user_name="Carla", opportunities_found=0)
        assert "Carla" in html
        assert "analisar" in html.lower()


class TestShareActivationDispatch:
    def test_render_share_activation(self):
        from services.trial_email_sequence import _render_email
        subject, html = _render_email(
            email_type="share_activation",
            user_name="Dani",
            stats={"opportunities_found": 3},
            unsubscribe_url="https://u",
        )
        assert "diretor" in subject
        assert "3" in html
        assert "/buscar" in html


class TestShareActivationFilter:
    """share_activation must skip users with 0 opps or with existing shares."""

    @pytest.mark.asyncio
    async def test_skips_user_with_zero_opportunities(self):
        from services import trial_email_sequence as svc

        fake_user = {
            "id": "u1",
            "email": "u1@test.com",
            "full_name": "User One",
            "plan_type": "free_trial",
            "marketing_emails_enabled": True,
        }

        sb_exec_mock = AsyncMock()
        sb_exec_mock.side_effect = [
            MagicMock(data=[fake_user]),  # profiles query
            MagicMock(data=[]),  # trial_email_log dedup
        ]

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", False), \
             patch("config.REFERRAL_EMAIL_ENABLED", False), \
             patch("config.SHARE_ACTIVATION_EMAIL_ENABLED", True), \
             patch("services.trial_email_sequence.get_trial_user_stats",
                   return_value={"searches_count": 5, "opportunities_found": 0,
                                 "total_value_estimated": 0}), \
             patch("supabase_client.get_supabase", return_value=MagicMock()), \
             patch("supabase_client.sb_execute", sb_exec_mock), \
             patch("email_service.send_email_async") as send_mock:
            await svc.process_trial_emails(batch_size=50)

        dispatched = [
            call.kwargs.get("tags", [])
            for call in send_mock.call_args_list
        ]
        share_sent = any(
            any(t.get("name") == "type" and t.get("value") == "share_activation" for t in tags)
            for tags in dispatched
        )
        assert share_sent is False

    @pytest.mark.asyncio
    async def test_skips_user_with_existing_share(self):
        from services import trial_email_sequence as svc

        fake_user = {
            "id": "u1",
            "email": "u1@test.com",
            "full_name": "User One",
            "plan_type": "free_trial",
            "marketing_emails_enabled": True,
        }

        sb_exec_mock = AsyncMock()
        sb_exec_mock.side_effect = [
            MagicMock(data=[fake_user]),  # profiles query
            MagicMock(data=[]),  # trial_email_log dedup
            MagicMock(data=[{"id": "share-1"}]),  # shared_analyses lookup
        ]

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", False), \
             patch("config.REFERRAL_EMAIL_ENABLED", False), \
             patch("config.SHARE_ACTIVATION_EMAIL_ENABLED", True), \
             patch("services.trial_email_sequence.get_trial_user_stats",
                   return_value={"searches_count": 5, "opportunities_found": 8,
                                 "total_value_estimated": 100000}), \
             patch("supabase_client.get_supabase", return_value=MagicMock()), \
             patch("supabase_client.sb_execute", sb_exec_mock), \
             patch("email_service.send_email_async") as send_mock:
            await svc.process_trial_emails(batch_size=50)

        dispatched = [
            call.kwargs.get("tags", [])
            for call in send_mock.call_args_list
        ]
        share_sent = any(
            any(t.get("name") == "type" and t.get("value") == "share_activation" for t in tags)
            for tags in dispatched
        )
        assert share_sent is False


class TestActivationNudgeFilter:
    """Users that already searched must NOT receive the activation nudge."""

    @pytest.mark.asyncio
    async def test_skips_user_with_searches(self):
        from services import trial_email_sequence as svc

        fake_user = {
            "id": "u1",
            "email": "u1@test.com",
            "full_name": "User One",
            "plan_type": "free_trial",
            "marketing_emails_enabled": True,
        }

        sb_exec_mock = AsyncMock()
        # Return our fake user for the profiles query, empty for the dedup check
        sb_exec_mock.side_effect = [
            MagicMock(data=[fake_user]),  # profiles query
            MagicMock(data=[]),  # trial_email_log dedup
        ]

        with patch("config.TRIAL_EMAILS_ENABLED", True), \
             patch("config.DAY3_ACTIVATION_EMAIL_ENABLED", True), \
             patch("config.REFERRAL_EMAIL_ENABLED", False), \
             patch("services.trial_email_sequence.get_trial_user_stats",
                   return_value={"searches_count": 5, "total_value_estimated": 0}), \
             patch("supabase_client.get_supabase", return_value=MagicMock()), \
             patch("supabase_client.sb_execute", sb_exec_mock), \
             patch("email_service.send_email_async") as send_mock:
            result = await svc.process_trial_emails(batch_size=50)

        # No email should have been dispatched for the nudge because the
        # user already has searches_count > 0
        dispatched_types = [
            call.kwargs.get("tags", [])
            for call in send_mock.call_args_list
        ]
        activation_sent = any(
            any(t.get("name") == "type" and t.get("value") == "activation_nudge" for t in tags)
            for tags in dispatched_types
        )
        assert activation_sent is False
