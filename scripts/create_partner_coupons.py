#!/usr/bin/env python3
"""STORY-323 AC15: Create Stripe coupons for partner consultancies.

Usage:
    python scripts/create_partner_coupons.py

Creates coupons for each active partner in the database.
Coupon format: {SLUG_UPPER}_25 (e.g., TRIUNFO_LEGIS_25)
Type: percentage, 25% off, duration: forever
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv()


def main():
    import stripe

    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_key:
        print("ERROR: STRIPE_SECRET_KEY not set")
        sys.exit(1)

    # Use sync Supabase client for script
    from supabase_client import get_supabase
    sb = get_supabase()

    # Get all active partners
    result = sb.table("partners").select("id, name, slug, stripe_coupon_id").eq("status", "active").execute()
    partners = result.data or []

    if not partners:
        print("No active partners found.")
        return

    print(f"Found {len(partners)} active partners\n")

    for partner in partners:
        slug = partner["slug"]
        coupon_id = slug.upper().replace("-", "_") + "_25"

        # Skip if already has a coupon
        if partner.get("stripe_coupon_id"):
            print(f"  SKIP {slug} — already has coupon {partner['stripe_coupon_id']}")
            continue

        try:
            # Create Stripe coupon
            coupon = stripe.Coupon.create(
                id=coupon_id,
                percent_off=25,
                duration="forever",
                name=f"Parceiro {partner['name']} — 25% off",
                metadata={"partner_slug": slug, "partner_id": partner["id"]},
                api_key=stripe_key,
            )

            # Also create a promotion code for the coupon (user-facing code)
            promo = stripe.PromotionCode.create(
                coupon=coupon.id,
                code=coupon_id,
                active=True,
                api_key=stripe_key,
            )

            # Update partner with coupon ID
            sb.table("partners").update(
                {"stripe_coupon_id": coupon.id}
            ).eq("id", partner["id"]).execute()

            print(f"  OK   {slug} — coupon={coupon.id}, promo_code={promo.code}")

        except stripe.error.InvalidRequestError as e:
            if "already exists" in str(e):
                # Coupon exists in Stripe, just link it
                sb.table("partners").update(
                    {"stripe_coupon_id": coupon_id}
                ).eq("id", partner["id"]).execute()
                print(f"  LINK {slug} — coupon already exists, linked {coupon_id}")
            else:
                print(f"  ERR  {slug} — {e}")
        except Exception as e:
            print(f"  ERR  {slug} — {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
