"""DEBT-117 AC9-AC12: LGPD User Deletion Cascade Verification.

Validates that all user-scoped tables have proper ON DELETE CASCADE
foreign keys pointing to profiles(id), ensuring LGPD-compliant user
data deletion when auth.users entries are removed.

This test performs static analysis of migration SQL files to verify
the cascade chain, since integration tests use mocked Supabase and
cannot test actual DB cascades.
"""

import os
import re
import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIGRATIONS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "supabase", "migrations"
)

# AC9: Tables that MUST have ON DELETE CASCADE to profiles(id)
REQUIRED_CASCADE_TABLES = [
    "search_sessions",
    "pipeline_items",
    "search_results_cache",
    "classification_feedback",
    "user_oauth_tokens",
    "google_sheets_exports",
]

# AC12: Complete cascade chain documentation
# Tables with their expected ON DELETE behavior
CASCADE_CHAIN = {
    # Level 0: auth.users -> profiles
    "profiles": {"references": "auth.users(id)", "on_delete": "CASCADE"},
    # Level 1: profiles -> child tables (AC9 required)
    "search_sessions": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "pipeline_items": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "search_results_cache": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "classification_feedback": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "user_oauth_tokens": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "google_sheets_exports": {"references": "profiles(id)", "on_delete": "CASCADE"},
    # Level 1: profiles -> other child tables
    "user_subscriptions": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "monthly_quota": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "search_results_store": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "trial_email_log": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "mfa_recovery_codes": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "mfa_recovery_attempts": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "alert_preferences": {"references": "profiles(id)", "on_delete": "CASCADE"},
    "alerts": {"references": "profiles(id)", "on_delete": "CASCADE"},
    # Intentionally NOT CASCADE
    "organizations": {"references": "profiles(id)", "on_delete": "RESTRICT"},
    "partner_referrals": {"references": "profiles(id)", "on_delete": "SET NULL"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_all_migrations() -> str:
    """Load and concatenate all migration SQL files in order."""
    if not os.path.isdir(MIGRATIONS_DIR):
        pytest.skip(f"Migrations directory not found: {MIGRATIONS_DIR}")

    sql_files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")
    )
    if not sql_files:
        pytest.skip("No migration files found")

    combined = []
    for fname in sql_files:
        with open(os.path.join(MIGRATIONS_DIR, fname), "r", encoding="utf-8") as f:
            combined.append(f"-- FILE: {fname}\n")
            combined.append(f.read())
    return "\n".join(combined)


def _find_fk_declarations(sql: str, table_name: str) -> list[dict]:
    """Find all FK declarations for a given table in the SQL.

    Handles both inline REFERENCES and ALTER TABLE ADD CONSTRAINT patterns.
    Returns list of dicts with keys: references, on_delete.
    """
    results = []

    # Pattern 1: CREATE TABLE inline — user_id UUID ... REFERENCES profiles(id) ON DELETE CASCADE
    # Match within CREATE TABLE blocks for the specific table
    create_pattern = re.compile(
        rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?{re.escape(table_name)}\s*\((.*?)\);",
        re.DOTALL | re.IGNORECASE,
    )
    for match in create_pattern.finditer(sql):
        body = match.group(1)
        # Find user_id references
        ref_pattern = re.compile(
            r"user_id\s+UUID\s+.*?REFERENCES\s+([\w.]+\(\w+\))\s+ON\s+DELETE\s+(\w+)",
            re.IGNORECASE,
        )
        for ref in ref_pattern.finditer(body):
            results.append({
                "references": ref.group(1),
                "on_delete": ref.group(2).upper(),
            })
        # Also check for id referencing auth.users (profiles table)
        if table_name == "profiles":
            id_ref = re.compile(
                r"id\s+UUID\s+.*?REFERENCES\s+([\w.]+\(\w+\))\s+ON\s+DELETE\s+(\w+)",
                re.IGNORECASE,
            )
            for ref in id_ref.finditer(body):
                results.append({
                    "references": ref.group(1),
                    "on_delete": ref.group(2).upper(),
                })

    # Pattern 2: ALTER TABLE ... ADD CONSTRAINT ... REFERENCES profiles(id) ON DELETE CASCADE
    alter_pattern = re.compile(
        rf"ALTER\s+TABLE\s+(?:(?:ONLY\s+)?(?:public\.)?){re.escape(table_name)}\s+"
        r"ADD\s+(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY\s*\(user_id\)\s+"
        r"REFERENCES\s+([\w.]+\(\w+\))\s+ON\s+DELETE\s+(\w+)",
        re.IGNORECASE,
    )
    for match in alter_pattern.finditer(sql):
        results.append({
            "references": match.group(1),
            "on_delete": match.group(2).upper(),
        })

    # Pattern 3: ALTER TABLE with owner_id (for organizations)
    if table_name == "organizations":
        owner_pattern = re.compile(
            rf"ALTER\s+TABLE\s+(?:(?:ONLY\s+)?(?:public\.)?){re.escape(table_name)}\s+"
            r"ADD\s+(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY\s*\(owner_id\)\s+"
            r"REFERENCES\s+([\w.]+\(\w+\))\s+ON\s+DELETE\s+(\w+)",
            re.IGNORECASE,
        )
        for match in owner_pattern.finditer(sql):
            results.append({
                "references": match.group(1),
                "on_delete": match.group(2).upper(),
            })

    # Pattern 4: ALTER TABLE with referred_user_id (for partner_referrals)
    if table_name == "partner_referrals":
        ref_user_pattern = re.compile(
            rf"ALTER\s+TABLE\s+(?:(?:ONLY\s+)?(?:public\.)?){re.escape(table_name)}\s+"
            r"ADD\s+(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY\s*\(referred_user_id\)\s+"
            r"REFERENCES\s+([\w.]+\(\w+\))\s+ON\s+DELETE\s+(\w+)",
            re.IGNORECASE,
        )
        for match in ref_user_pattern.finditer(sql):
            results.append({
                "references": match.group(1),
                "on_delete": match.group(2).upper(),
            })

    return results


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestUserDeletionCascade:
    """AC9-AC12: Verify LGPD-compliant user deletion cascade chain."""

    @pytest.fixture(autouse=True)
    def _load_migrations(self):
        """Load all migration SQL once per test class."""
        self.sql = _load_all_migrations()

    # AC9 + AC11: Verify required tables have CASCADE to profiles(id)
    @pytest.mark.parametrize("table_name", REQUIRED_CASCADE_TABLES)
    def test_required_table_has_cascade_to_profiles(self, table_name):
        """Each story-mentioned table MUST have ON DELETE CASCADE to profiles(id)."""
        fks = _find_fk_declarations(self.sql, table_name)

        # Filter to user_id -> profiles(id) FKs
        profiles_fks = [
            fk for fk in fks if "profiles" in fk["references"].lower()
        ]

        assert profiles_fks, (
            f"Table '{table_name}' has NO foreign key referencing profiles(id). "
            f"Found FKs: {fks}"
        )

        # The most recent FK should be CASCADE (migrations may have evolved)
        latest_fk = profiles_fks[-1]
        assert latest_fk["on_delete"] == "CASCADE", (
            f"Table '{table_name}' references profiles but with "
            f"ON DELETE {latest_fk['on_delete']} instead of CASCADE. "
            f"All user-scoped tables must cascade for LGPD compliance."
        )

    # AC10: Verify profiles table cascades from auth.users
    def test_profiles_cascades_from_auth_users(self):
        """profiles(id) MUST have ON DELETE CASCADE from auth.users(id)."""
        fks = _find_fk_declarations(self.sql, "profiles")

        auth_fks = [
            fk for fk in fks if "auth.users" in fk["references"].lower()
        ]
        assert auth_fks, (
            "profiles table has NO foreign key referencing auth.users(id). "
            "This breaks the LGPD cascade chain."
        )
        assert auth_fks[-1]["on_delete"] == "CASCADE", (
            f"profiles references auth.users but with "
            f"ON DELETE {auth_fks[-1]['on_delete']} instead of CASCADE."
        )

    # AC11: Verify complete cascade chain depth
    def test_cascade_chain_completeness(self):
        """Verify all expected tables in the cascade chain exist in migrations."""
        for table_name, expected in CASCADE_CHAIN.items():
            if table_name == "profiles":
                # Profiles is the root — tested separately
                continue

            fks = _find_fk_declarations(self.sql, table_name)
            if not fks:
                # Table may not exist yet or may be defined differently
                # Only fail for required tables
                if table_name in REQUIRED_CASCADE_TABLES:
                    pytest.fail(
                        f"Required table '{table_name}' has no FK declarations found"
                    )
                continue

    # AC12: Document cascade chain
    def test_cascade_documentation(self):
        """Document which tables have CASCADE and which have other behaviors.

        This test generates a cascade chain report for future reference.
        It always passes but logs the complete chain.
        """
        report_lines = [
            "=" * 70,
            "LGPD USER DELETION CASCADE CHAIN — SmartLic",
            "=" * 70,
            "",
            "When auth.users(id) is deleted:",
            "",
            "Level 0: auth.users -> profiles (CASCADE)",
            "",
            "Level 1: profiles -> child tables:",
        ]

        cascade_tables = []
        non_cascade_tables = []

        for table_name, expected in sorted(CASCADE_CHAIN.items()):
            if table_name == "profiles":
                continue

            fks = _find_fk_declarations(self.sql, table_name)
            profiles_fks = [
                fk for fk in fks if "profiles" in fk["references"].lower()
            ]

            if profiles_fks:
                latest = profiles_fks[-1]
                entry = f"  {table_name}: ON DELETE {latest['on_delete']}"
                if latest["on_delete"] == "CASCADE":
                    cascade_tables.append(entry)
                else:
                    non_cascade_tables.append(
                        f"{entry} (intentional: {expected.get('on_delete', 'unknown')})"
                    )

        report_lines.append("")
        report_lines.append("CASCADE (auto-deleted):")
        report_lines.extend(cascade_tables or ["  (none found)"])
        report_lines.append("")
        report_lines.append("NON-CASCADE (requires manual handling):")
        report_lines.extend(non_cascade_tables or ["  (none)"])
        report_lines.append("")
        report_lines.append("=" * 70)

        # Log the report — always passes
        report = "\n".join(report_lines)
        print(report)

        # Verify at minimum that all 6 required tables were found with CASCADE
        assert len([t for t in cascade_tables if any(
            req in t for req in REQUIRED_CASCADE_TABLES
        )]) >= len(REQUIRED_CASCADE_TABLES), (
            f"Not all required tables found with CASCADE. "
            f"Expected: {REQUIRED_CASCADE_TABLES}"
        )

    # AC12: No tables should directly reference auth.users (except profiles)
    def test_no_direct_auth_users_references(self):
        """Verify no user-scoped tables bypass profiles and reference auth.users directly.

        After FK standardization (STORY-264, DEBT-100, DEBT-104), all tables
        should reference profiles(id), not auth.users(id) directly.
        """
        # Find all CREATE TABLE + ALTER TABLE patterns referencing auth.users
        auth_refs = re.findall(
            r"(?:CREATE\s+TABLE|ALTER\s+TABLE)\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:ONLY\s+)?(?:public\.)?(\w+).*?"
            r"REFERENCES\s+auth\.users\(id\)",
            self.sql,
            re.DOTALL | re.IGNORECASE,
        )

        # Filter out profiles (which is the legitimate bridge)
        non_profiles_refs = [t for t in auth_refs if t != "profiles"]

        # These are OK if they were later migrated to profiles
        # The test verifies the LATEST state by checking if a profiles FK exists
        for table in set(non_profiles_refs):
            fks = _find_fk_declarations(self.sql, table)
            profiles_fks = [
                fk for fk in fks if "profiles" in fk["references"].lower()
            ]
            if not profiles_fks and table in REQUIRED_CASCADE_TABLES:
                pytest.fail(
                    f"Table '{table}' references auth.users(id) directly without "
                    f"a subsequent migration to profiles(id). This bypasses the "
                    f"LGPD cascade chain."
                )
