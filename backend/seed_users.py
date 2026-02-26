"""Seed script: create initial admin and first unlimited user.

Run once after Supabase project is configured:
    cd backend
    python seed_users.py

Credentials are read from environment variables or interactive prompt:
    SEED_ADMIN_PASSWORD  — password for the admin user
    SEED_MASTER_PASSWORD — password for the master user
"""

import os
import getpass


def main():
    from supabase_client import get_supabase

    sb = get_supabase()

    admin_password = os.environ.get("SEED_ADMIN_PASSWORD") or getpass.getpass(
        "Enter password for tiago.sasaki@gmail.com (admin): "
    )
    master_password = os.environ.get("SEED_MASTER_PASSWORD") or getpass.getpass(
        "Enter password for marinalvabaron@gmail.com (master): "
    )

    users_to_create = [
        {
            "email": "tiago.sasaki@gmail.com",
            "password": admin_password,
            "full_name": "TJ Sasaki",
            "plan_id": "master",
            "is_admin": True,
        },
        {
            "email": "marinalvabaron@gmail.com",
            "password": master_password,
            "full_name": "Mari Baron",
            "plan_id": "master",
            "is_admin": False,
        },
    ]

    admin_ids = []

    for u in users_to_create:
        print(f"Creating user: {u['email']}...")
        try:
            result = sb.auth.admin.create_user({
                "email": u["email"],
                "password": u["password"],
                "email_confirm": True,
                "user_metadata": {"full_name": u["full_name"]},
            })
            user_id = str(result.user.id)
            print(f"  Created with ID: {user_id}")

            # Update profile
            sb.table("profiles").update({
                "company": None,
                "plan_type": u["plan_id"],
            }).eq("id", user_id).execute()

            # Create master subscription (unlimited, no expiry)
            if u["plan_id"] == "master":
                sb.table("user_subscriptions").insert({
                    "user_id": user_id,
                    "plan_id": "master",
                    "credits_remaining": None,
                    "expires_at": None,
                    "is_active": True,
                }).execute()
                print("  Assigned master plan (unlimited)")

            if u["is_admin"]:
                admin_ids.append(user_id)
                print("  *** ADMIN USER ***")

        except Exception as e:
            print(f"  Error: {e}")
            # Try to continue with other users
            continue

    if admin_ids:
        print(f"\n{'='*60}")
        print("IMPORTANT: Add this to your .env file:")
        print(f"ADMIN_USER_IDS={','.join(admin_ids)}")
        print(f"{'='*60}")

    print("\nDone!")


if __name__ == "__main__":
    main()
