#!/usr/bin/env python3
"""Seed Stripe price IDs from environment variables into the database.

DEBT-DB-009: Stripe price IDs are hardcoded in SQL migrations (which cannot
read env vars). This script overwrites them with environment-specific values
for staging/dev environments.

Usage:
    # Set env vars in .env or export them, then:
    python scripts/seed_stripe_prices.py

    # Dry run (shows what would change):
    python scripts/seed_stripe_prices.py --dry-run

Required env vars (see .env.example):
    STRIPE_PRICE_PRO_MONTHLY
    STRIPE_PRICE_PRO_SEMIANNUAL
    STRIPE_PRICE_PRO_ANNUAL
    STRIPE_PRICE_CONSULTORIA_MONTHLY      (optional)
    STRIPE_PRICE_CONSULTORIA_SEMIANNUAL   (optional)
    STRIPE_PRICE_CONSULTORIA_ANNUAL       (optional)

Also requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
"""

import os
import sys
import argparse

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass  # dotenv not required if env vars are already set


PRICE_MAP = {
    "smartlic_pro": {
        "monthly": "STRIPE_PRICE_PRO_MONTHLY",
        "semiannual": "STRIPE_PRICE_PRO_SEMIANNUAL",
        "annual": "STRIPE_PRICE_PRO_ANNUAL",
    },
    "consultoria": {
        "monthly": "STRIPE_PRICE_CONSULTORIA_MONTHLY",
        "semiannual": "STRIPE_PRICE_CONSULTORIA_SEMIANNUAL",
        "annual": "STRIPE_PRICE_CONSULTORIA_ANNUAL",
    },
}

PERIOD_TO_COLUMN = {
    "monthly": "stripe_price_id_monthly",
    "semiannual": "stripe_price_id_semiannual",
    "annual": "stripe_price_id_annual",
}


def main():
    parser = argparse.ArgumentParser(description="Seed Stripe price IDs from env vars")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()

    # Collect price IDs from environment
    updates = []
    missing = []

    for plan_id, periods in PRICE_MAP.items():
        for period, env_var in periods.items():
            value = os.environ.get(env_var)
            if value:
                updates.append((plan_id, period, env_var, value))
            else:
                missing.append(env_var)

    if not updates:
        print("ERROR: No STRIPE_PRICE_* env vars found. Nothing to seed.")
        print(f"Missing: {', '.join(missing)}")
        print("See .env.example for required variables.")
        sys.exit(1)

    print(f"Found {len(updates)} price IDs to seed:")
    for plan_id, period, env_var, value in updates:
        print(f"  {plan_id}/{period}: {value} (from {env_var})")

    if missing:
        print(f"\nOptional vars not set: {', '.join(missing)}")

    if args.dry_run:
        print("\n[DRY RUN] No changes applied.")
        return

    # Connect to Supabase
    from supabase_client import get_supabase
    sb = get_supabase()

    # Update plan_billing_periods (source of truth)
    for plan_id, period, env_var, value in updates:
        result = (
            sb.table("plan_billing_periods")
            .update({"stripe_price_id": value})
            .eq("plan_id", plan_id)
            .eq("billing_period", period)
            .execute()
        )
        affected = len(result.data) if result.data else 0
        print(f"  plan_billing_periods [{plan_id}/{period}]: {affected} row(s) updated")

    # Update plans table (denormalized columns)
    for plan_id in PRICE_MAP:
        plan_updates = {}
        for period, env_var in PRICE_MAP[plan_id].items():
            value = os.environ.get(env_var)
            if value:
                plan_updates[PERIOD_TO_COLUMN[period]] = value

        if plan_updates:
            result = (
                sb.table("plans")
                .update(plan_updates)
                .eq("id", plan_id)
                .execute()
            )
            affected = len(result.data) if result.data else 0
            print(f"  plans [{plan_id}]: {affected} row(s) updated with {len(plan_updates)} columns")

    print("\nDone. Stripe price IDs seeded successfully.")


if __name__ == "__main__":
    main()
