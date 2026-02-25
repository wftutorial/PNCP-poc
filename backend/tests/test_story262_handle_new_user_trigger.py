"""
STORY-262: handle_new_user() trigger fix — static analysis tests.

Validates migration 20260225110000 restores all 10 profile fields,
adds ON CONFLICT (id) DO NOTHING, and preserves phone normalization.

Test categories:
  AC1: Email signup with metadata (company, sector, whatsapp_consent)
  AC2: Google OAuth signup (full_name, avatar_url)
  AC3: Re-signup safety (ON CONFLICT DO NOTHING)
  AC4: Phone normalization (+55 strip, leading 0 strip)
  AC5: Invalid phone → NULL
  AC6: plan_type default 'free_trial'
  AC7: context_data default '{}'::jsonb
"""

import os
import re

import pytest


@pytest.fixture
def migration_262_sql():
    """Load the STORY-262 migration SQL."""
    migration_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "supabase",
        "migrations",
        "20260225110000_fix_handle_new_user_trigger.sql",
    )
    with open(migration_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def regression_migration_sql():
    """Load the regression migration (20260224000000) for comparison."""
    migration_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "supabase",
        "migrations",
        "20260224000000_phone_email_unique.sql",
    )
    with open(migration_path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# AC1: Email signup — all metadata fields propagated
# ============================================================================


class TestAC1EmailSignupMetadata:
    """AC1: company, sector, whatsapp_consent must be in the INSERT."""

    def test_insert_includes_company(self, migration_262_sql):
        assert "company" in migration_262_sql.lower(), (
            "INSERT must include 'company' column for email signup metadata"
        )

    def test_insert_includes_sector(self, migration_262_sql):
        assert "sector" in migration_262_sql.lower(), (
            "INSERT must include 'sector' column for email signup metadata"
        )

    def test_insert_includes_whatsapp_consent(self, migration_262_sql):
        assert "whatsapp_consent" in migration_262_sql.lower(), (
            "INSERT must include 'whatsapp_consent' column for email signup metadata"
        )

    def test_company_reads_from_metadata(self, migration_262_sql):
        assert "raw_user_meta_data->>'company'" in migration_262_sql, (
            "company must be read from raw_user_meta_data"
        )

    def test_sector_reads_from_metadata(self, migration_262_sql):
        assert "raw_user_meta_data->>'sector'" in migration_262_sql, (
            "sector must be read from raw_user_meta_data"
        )

    def test_whatsapp_consent_reads_from_metadata(self, migration_262_sql):
        assert "raw_user_meta_data->>'whatsapp_consent'" in migration_262_sql, (
            "whatsapp_consent must be read from raw_user_meta_data"
        )

    def test_company_has_coalesce_default(self, migration_262_sql):
        """company should COALESCE to empty string."""
        assert re.search(
            r"COALESCE\(NEW\.raw_user_meta_data->>'company',\s*''\)", migration_262_sql
        ), "company must use COALESCE with '' default"

    def test_sector_has_coalesce_default(self, migration_262_sql):
        """sector should COALESCE to empty string."""
        assert re.search(
            r"COALESCE\(NEW\.raw_user_meta_data->>'sector',\s*''\)", migration_262_sql
        ), "sector must use COALESCE with '' default"

    def test_whatsapp_consent_coalesces_to_false(self, migration_262_sql):
        """whatsapp_consent should COALESCE to FALSE."""
        assert re.search(
            r"COALESCE\(\(NEW\.raw_user_meta_data->>'whatsapp_consent'\)::boolean,\s*FALSE\)",
            migration_262_sql,
        ), "whatsapp_consent must COALESCE to FALSE"


# ============================================================================
# AC2: Google OAuth signup — full_name and avatar_url propagated
# ============================================================================


class TestAC2GoogleOAuthSignup:
    """AC2: full_name and avatar_url must be in the INSERT."""

    def test_insert_includes_full_name(self, migration_262_sql):
        assert "full_name" in migration_262_sql, (
            "INSERT must include 'full_name' for OAuth signup"
        )

    def test_full_name_reads_from_metadata(self, migration_262_sql):
        assert "raw_user_meta_data->>'full_name'" in migration_262_sql, (
            "full_name must be read from raw_user_meta_data"
        )

    def test_insert_includes_avatar_url(self, migration_262_sql):
        assert "avatar_url" in migration_262_sql, (
            "INSERT must include 'avatar_url' for OAuth signup"
        )

    def test_avatar_url_reads_from_metadata(self, migration_262_sql):
        assert "raw_user_meta_data->>'avatar_url'" in migration_262_sql, (
            "avatar_url must be read from raw_user_meta_data"
        )


# ============================================================================
# AC3: Re-signup safety — ON CONFLICT (id) DO NOTHING
# ============================================================================


class TestAC3ReSignupSafety:
    """AC3: ON CONFLICT (id) DO NOTHING prevents unique violation on re-signup."""

    def test_on_conflict_present(self, migration_262_sql):
        assert "ON CONFLICT" in migration_262_sql, (
            "INSERT must have ON CONFLICT clause for re-signup safety"
        )

    def test_on_conflict_targets_id(self, migration_262_sql):
        assert re.search(r"ON\s+CONFLICT\s*\(id\)", migration_262_sql), (
            "ON CONFLICT must target (id) column"
        )

    def test_on_conflict_does_nothing(self, migration_262_sql):
        assert re.search(r"ON\s+CONFLICT\s*\(id\)\s+DO\s+NOTHING", migration_262_sql), (
            "ON CONFLICT (id) must DO NOTHING (not UPDATE)"
        )

    def test_regression_migration_lacks_on_conflict(self, regression_migration_sql):
        """Confirm the regression migration (20260224000000) does NOT have ON CONFLICT."""
        assert "ON CONFLICT" not in regression_migration_sql, (
            "Regression migration should NOT have ON CONFLICT — that's the bug this fixes"
        )


# ============================================================================
# AC4: Phone normalization — +55 strip, leading 0 strip
# ============================================================================


class TestAC4PhoneNormalization:
    """AC4: Phone normalization logic is preserved."""

    def test_strips_non_digits(self, migration_262_sql):
        """regexp_replace must strip non-digit chars."""
        assert "regexp_replace" in migration_262_sql, (
            "Phone normalization must use regexp_replace"
        )
        assert "'[^0-9]'" in migration_262_sql, (
            "regexp_replace must strip non-digit characters with [^0-9]"
        )

    def test_strips_country_code_55(self, migration_262_sql):
        """Must strip leading '55' country code when length > 11."""
        assert "left(_phone, 2) = '55'" in migration_262_sql, (
            "Must check for leading '55' country code"
        )
        assert "substring(_phone from 3)" in migration_262_sql, (
            "Must strip '55' prefix via substring from 3"
        )

    def test_strips_leading_zero(self, migration_262_sql):
        """Must strip leading '0' from phone."""
        assert "left(_phone, 1) = '0'" in migration_262_sql, (
            "Must check for leading '0'"
        )
        assert "substring(_phone from 2)" in migration_262_sql, (
            "Must strip leading '0' via substring from 2"
        )


# ============================================================================
# AC5: Invalid phone → NULL
# ============================================================================


class TestAC5InvalidPhoneNull:
    """AC5: Phones not 10 or 11 digits should be set to NULL."""

    def test_validates_phone_length(self, migration_262_sql):
        """Must validate length is 10 or 11."""
        assert re.search(r"length\(_phone\)\s+NOT\s+IN\s*\(10,\s*11\)", migration_262_sql), (
            "Must check length NOT IN (10, 11)"
        )

    def test_sets_null_for_invalid(self, migration_262_sql):
        """Invalid phone must be set to NULL."""
        assert "_phone := NULL" in migration_262_sql, (
            "Invalid phone must be set to NULL"
        )


# ============================================================================
# AC6: plan_type default 'free_trial'
# ============================================================================


class TestAC6PlanTypeDefault:
    """AC6: plan_type must default to 'free_trial'."""

    def test_plan_type_in_insert(self, migration_262_sql):
        assert "plan_type" in migration_262_sql, (
            "INSERT must include plan_type column"
        )

    def test_plan_type_value_free_trial(self, migration_262_sql):
        assert "'free_trial'" in migration_262_sql, (
            "plan_type must be set to 'free_trial'"
        )

    def test_no_legacy_free_plan(self, migration_262_sql):
        """Ensure no legacy 'free' plan type (must be 'free_trial')."""
        lines = migration_262_sql.split("\n")
        for line in lines:
            if line.strip().startswith("--"):
                continue
            if "plan_type" in line.lower() and "'free'" in line and "'free_trial'" not in line:
                pytest.fail(
                    f"Found legacy 'free' plan_type (not 'free_trial'): {line.strip()}"
                )

    def test_regression_migration_lacks_plan_type(self, regression_migration_sql):
        """Confirm regression migration (20260224000000) INSERT doesn't set plan_type."""
        # Find the INSERT statement in the regression migration
        insert_match = re.search(
            r"INSERT\s+INTO\s+public\.profiles\s*\((.*?)\)", regression_migration_sql, re.DOTALL
        )
        assert insert_match, "Regression migration should have an INSERT INTO profiles"
        insert_columns = insert_match.group(1)
        assert "plan_type" not in insert_columns, (
            "Regression migration INSERT should NOT include plan_type — that's the bug"
        )


# ============================================================================
# AC7: context_data default '{}'::jsonb
# ============================================================================


class TestAC7ContextDataDefault:
    """AC7: context_data must default to '{}'::jsonb."""

    def test_context_data_in_insert(self, migration_262_sql):
        assert "context_data" in migration_262_sql, (
            "INSERT must include context_data column"
        )

    def test_context_data_jsonb_default(self, migration_262_sql):
        assert "'{}'::jsonb" in migration_262_sql, (
            "context_data must default to '{}'::jsonb"
        )


# ============================================================================
# Structural integrity — INSERT has all 10 columns
# ============================================================================


class TestInsertStructuralIntegrity:
    """Verify the INSERT statement includes all 10 required columns."""

    REQUIRED_COLUMNS = [
        "id",
        "email",
        "full_name",
        "company",
        "sector",
        "phone_whatsapp",
        "whatsapp_consent",
        "plan_type",
        "avatar_url",
        "context_data",
    ]

    def test_all_10_columns_in_insert(self, migration_262_sql):
        """INSERT INTO profiles must list all 10 columns."""
        insert_match = re.search(
            r"INSERT\s+INTO\s+public\.profiles\s*\((.*?)\)",
            migration_262_sql,
            re.DOTALL,
        )
        assert insert_match, "Migration must contain INSERT INTO public.profiles"
        insert_columns = insert_match.group(1)

        missing = [
            col for col in self.REQUIRED_COLUMNS if col not in insert_columns
        ]
        assert not missing, (
            f"INSERT is missing columns: {missing}. "
            f"All 10 columns required: {self.REQUIRED_COLUMNS}"
        )

    def test_regression_only_had_4_columns(self, regression_migration_sql):
        """Confirm regression migration only inserted 4 columns (the bug)."""
        insert_match = re.search(
            r"INSERT\s+INTO\s+public\.profiles\s*\((.*?)\)",
            regression_migration_sql,
            re.DOTALL,
        )
        assert insert_match, "Regression migration should have an INSERT INTO profiles"
        insert_columns = insert_match.group(1)

        present = [
            col for col in self.REQUIRED_COLUMNS if col in insert_columns
        ]
        assert len(present) == 4, (
            f"Regression migration should only have 4 columns in INSERT, "
            f"found {len(present)}: {present}"
        )

    def test_values_count_matches_columns(self, migration_262_sql):
        """Number of VALUES entries should match number of columns (10)."""
        # Extract the VALUES clause
        values_match = re.search(
            r"VALUES\s*\((.*?)\)\s*ON\s+CONFLICT",
            migration_262_sql,
            re.DOTALL,
        )
        assert values_match, "Migration must have a VALUES clause before ON CONFLICT"
        values_str = values_match.group(1)

        # Count top-level comma-separated entries (accounting for nested parens/functions)
        depth = 0
        count = 1
        for ch in values_str:
            if ch in ("(", ):
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                count += 1

        assert count == 10, (
            f"VALUES has {count} entries but INSERT has 10 columns. "
            "Column/value count mismatch."
        )


# ============================================================================
# Idempotency & safety
# ============================================================================


class TestIdempotencyAndSafety:
    """Trigger uses CREATE OR REPLACE and is SECURITY DEFINER."""

    def test_uses_create_or_replace(self, migration_262_sql):
        assert "CREATE OR REPLACE FUNCTION" in migration_262_sql, (
            "Must use CREATE OR REPLACE for safe re-application"
        )

    def test_security_definer(self, migration_262_sql):
        assert "SECURITY DEFINER" in migration_262_sql, (
            "Trigger must be SECURITY DEFINER to write to profiles from auth schema"
        )

    def test_plpgsql_language(self, migration_262_sql):
        assert "plpgsql" in migration_262_sql.lower(), (
            "Function must use PL/pgSQL language"
        )

    def test_returns_trigger(self, migration_262_sql):
        assert "RETURNS trigger" in migration_262_sql, (
            "Function must RETURN trigger type"
        )

    def test_returns_new(self, migration_262_sql):
        assert "RETURN NEW;" in migration_262_sql, (
            "Trigger must RETURN NEW for the auth.users insert to proceed"
        )
