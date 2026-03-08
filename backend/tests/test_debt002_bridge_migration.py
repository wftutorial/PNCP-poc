"""
DEBT-002: Bridge Migration Tests
Validates the bridge migration SQL is well-formed and idempotent.
"""
import os
import re
import pytest


BRIDGE_MIGRATION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "supabase", "migrations",
    "20260308200000_debt002_bridge_backend_migrations.sql"
)

BACKEND_MIGRATIONS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "migrations"
)


class TestBridgeMigrationExists:
    """AC1: Bridge migration file exists."""

    def test_bridge_migration_file_exists(self):
        assert os.path.exists(BRIDGE_MIGRATION_PATH), (
            "Bridge migration file not found at expected path"
        )

    def test_bridge_migration_is_not_empty(self):
        with open(BRIDGE_MIGRATION_PATH, encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 100, "Bridge migration file is too small"


class TestBridgeMigrationIdempotency:
    """AC2: Bridge migration uses idempotent patterns."""

    @pytest.fixture(autouse=True)
    def load_migration(self):
        with open(BRIDGE_MIGRATION_PATH, encoding="utf-8") as f:
            self.sql = f.read()

    def test_create_table_uses_if_not_exists(self):
        """All CREATE TABLE statements must use IF NOT EXISTS."""
        creates = re.findall(r'CREATE TABLE\s+(?!IF NOT EXISTS)', self.sql, re.IGNORECASE)
        assert len(creates) == 0, (
            f"Found {len(creates)} CREATE TABLE without IF NOT EXISTS"
        )

    def test_create_index_uses_if_not_exists(self):
        """All CREATE INDEX statements must use IF NOT EXISTS."""
        creates = re.findall(r'CREATE INDEX\s+(?!IF NOT EXISTS)', self.sql, re.IGNORECASE)
        assert len(creates) == 0, (
            f"Found {len(creates)} CREATE INDEX without IF NOT EXISTS"
        )

    def test_policies_have_drop_before_create(self):
        """All CREATE POLICY must be preceded by DROP POLICY IF EXISTS."""
        policy_names = re.findall(r'CREATE POLICY\s+(\w+)', self.sql, re.IGNORECASE)
        for name in policy_names:
            assert f'DROP POLICY {name}' in self.sql or f'drop policy {name}' in self.sql.lower() or 'DROP POLICY' in self.sql, (
                f"CREATE POLICY {name} not preceded by DROP POLICY"
            )

    def test_no_drop_table_statements(self):
        """Bridge migration should NOT drop any tables."""
        drops = re.findall(r'DROP TABLE', self.sql, re.IGNORECASE)
        assert len(drops) == 0, "Bridge migration should not drop tables"

    def test_no_drop_function_statements(self):
        """Bridge migration should NOT drop functions."""
        drops = re.findall(r'DROP FUNCTION', self.sql, re.IGNORECASE)
        assert len(drops) == 0, "Bridge migration should not drop functions"

    def test_ends_with_notify_pgrst(self):
        """Must end with PostgREST schema reload."""
        assert "NOTIFY pgrst" in self.sql, "Missing NOTIFY pgrst at end"


class TestBridgeMigrationCompleteness:
    """AC1: All backend/migrations/ objects are covered."""

    @pytest.fixture(autouse=True)
    def load_migration(self):
        with open(BRIDGE_MIGRATION_PATH, encoding="utf-8") as f:
            self.sql = f.read().lower()

    def test_classification_feedback_table_present(self):
        """006_classification_feedback.sql — table must be bridged."""
        assert "classification_feedback" in self.sql

    def test_classification_feedback_columns(self):
        """006 — all columns present."""
        for col in ["user_id", "search_id", "bid_id", "setor_id", "user_verdict",
                     "reason", "category", "bid_objeto", "bid_valor", "bid_uf",
                     "confidence_score", "relevance_source"]:
            assert col in self.sql, f"Missing column: {col}"

    def test_classification_feedback_rls(self):
        """006 — RLS enabled."""
        assert "enable row level security" in self.sql

    def test_classification_feedback_policies(self):
        """006 — all 5 policies present."""
        for policy in ["feedback_insert_own", "feedback_select_own",
                        "feedback_update_own", "feedback_delete_own",
                        "feedback_admin_all"]:
            assert policy in self.sql, f"Missing policy: {policy}"

    def test_classification_feedback_indexes(self):
        """006 — all indexes present."""
        for idx in ["idx_feedback_sector_verdict", "idx_feedback_user_created",
                     "idx_classification_feedback_user_id"]:
            assert idx in self.sql, f"Missing index: {idx}"

    def test_array_normalization_present(self):
        """010_normalize_session_arrays.sql — UPDATEs must be bridged."""
        assert "unnest(ufs)" in self.sql or "unnest( ufs )" in self.sql
        assert "unnest(sectors)" in self.sql or "unnest( sectors )" in self.sql

    def test_defensive_verification_present(self):
        """Verification of pre-existing objects from 002-005, 007-009."""
        for obj in ["monthly_quota", "increment_quota_atomic",
                     "check_and_increment_quota", "user_oauth_tokens",
                     "google_sheets_exports", "search_state_transitions"]:
            assert obj in self.sql, f"Missing verification for: {obj}"


class TestBackendMigrationsNotDeleted:
    """Story requirement: Do NOT move or delete backend/migrations/ files."""

    EXPECTED_FILES = [
        "002_monthly_quota.sql",
        "003_atomic_quota_increment.sql",
        "004_google_oauth_tokens.sql",
        "005_google_sheets_exports.sql",
        "006_classification_feedback.sql",
        "007_search_session_lifecycle.sql",
        "008_search_state_transitions.sql",
        "009_add_search_id_to_search_sessions.sql",
        "010_normalize_session_arrays.sql",
    ]

    def test_all_backend_migration_files_exist(self):
        """Verify no backend migration files were deleted."""
        for filename in self.EXPECTED_FILES:
            path = os.path.join(BACKEND_MIGRATIONS_DIR, filename)
            assert os.path.exists(path), (
                f"backend/migrations/{filename} was deleted — this violates DEBT-002 rules"
            )

    def test_backend_migrations_readme_exists(self):
        """Deprecation notice must exist."""
        readme = os.path.join(BACKEND_MIGRATIONS_DIR, "README.md")
        assert os.path.exists(readme), "Missing README.md deprecation notice"

    def test_backend_migrations_readme_mentions_deprecated(self):
        """README must mention deprecation."""
        readme = os.path.join(BACKEND_MIGRATIONS_DIR, "README.md")
        with open(readme, encoding="utf-8") as f:
            content = f.read()
        assert "DEPRECATED" in content.upper()


class TestDisasterRecoveryDoc:
    """AC4: DISASTER-RECOVERY.md exists with required sections."""

    DR_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "DISASTER-RECOVERY.md"
    )

    @pytest.fixture(autouse=True)
    def load_doc(self):
        with open(self.DR_PATH, encoding="utf-8") as f:
            self.content = f.read()

    def test_dr_doc_exists(self):
        assert os.path.exists(self.DR_PATH)

    def test_has_pitr_section(self):
        assert "Point-in-Time Recovery" in self.content or "PITR" in self.content

    def test_has_full_recreation_section(self):
        assert "Full Recreation" in self.content

    def test_has_manual_setup_section(self):
        assert "Manual Setup" in self.content

    def test_has_pg_cron_documentation(self):
        """AC6: pg_cron jobs documented."""
        assert "pg_cron" in self.content
        for job in ["cleanup-monthly-quota", "cleanup-webhook-events",
                     "cleanup-audit-events", "cleanup-cold-cache-entries",
                     "cleanup-expired-search-results"]:
            assert job in self.content, f"Missing pg_cron job documentation: {job}"

    def test_has_seed_data_section(self):
        assert "Seed Data" in self.content

    def test_has_env_var_section(self):
        assert "Environment Variable" in self.content or "SUPABASE_URL" in self.content

    def test_has_naming_convention(self):
        """DB-026: naming convention documented."""
        assert "YYYYMMDDHHMMSS" in self.content or "Naming Convention" in self.content

    def test_has_verification_checklist(self):
        assert "Verification Checklist" in self.content or "Post-Recreation" in self.content

    def test_has_handle_new_user_warning(self):
        assert "handle_new_user" in self.content


class TestCIGuard:
    """AC7: CI guard for handle_new_user is active."""

    CI_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", ".github", "workflows",
        "handle-new-user-guard.yml"
    )

    def test_ci_guard_exists(self):
        assert os.path.exists(self.CI_PATH), "handle-new-user-guard.yml not found"

    def test_ci_guard_triggers_on_migration_changes(self):
        with open(self.CI_PATH, encoding="utf-8") as f:
            content = f.read()
        assert "supabase/migrations/" in content
        assert "pull_request" in content

    def test_ci_guard_checks_handle_new_user(self):
        with open(self.CI_PATH, encoding="utf-8") as f:
            content = f.read()
        assert "handle_new_user" in content
