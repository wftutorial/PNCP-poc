"""CORS configuration: allowed origins for development and production."""

import logging
import os

logger = logging.getLogger("config")

DEFAULT_CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

PRODUCTION_ORIGINS: list[str] = [
    "https://smartlic.tech",
    "https://www.smartlic.tech",
    "https://smartlic-frontend-production.up.railway.app",
    "https://smartlic-backend-production.up.railway.app",
]


def get_cors_origins() -> list[str]:
    """Get allowed CORS origins from environment variable.

    Security: Never allows '*' wildcard in production.
    Always includes production domains in Railway/production environments.
    """
    cors_env = os.getenv("CORS_ORIGINS", "").strip()

    is_production = (
        os.getenv("RAILWAY_ENVIRONMENT") is not None or
        os.getenv("RAILWAY_PROJECT_ID") is not None or
        os.getenv("ENVIRONMENT", "").lower() in ("production", "prod") or
        os.getenv("ENV", "").lower() in ("production", "prod")
    )

    if not cors_env:
        origins = DEFAULT_CORS_ORIGINS.copy()
        if is_production:
            logger.info("Production environment detected, including production origins")
            for prod_origin in PRODUCTION_ORIGINS:
                if prod_origin not in origins:
                    origins.append(prod_origin)
        else:
            logger.info("CORS_ORIGINS not set, using development defaults only")
        return origins

    origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

    if "*" in origins:
        logger.warning(
            "SECURITY WARNING: Wildcard '*' in CORS_ORIGINS is not recommended. "
            "Replacing with production defaults for security."
        )
        origins = [o for o in origins if o != "*"]

    for prod_origin in PRODUCTION_ORIGINS:
        if prod_origin not in origins:
            origins.append(prod_origin)

    seen = set()
    unique_origins = []
    for origin in origins:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)

    logger.info(f"CORS origins configured: {unique_origins}")
    return unique_origins
