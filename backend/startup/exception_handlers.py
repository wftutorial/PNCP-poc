"""startup/exception_handlers.py — Global exception handlers (DEBT-107).

Extracted from main.py.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to *app*."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """AC9: Validation errors in Portuguese."""
        logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": "Dados inválidos. Verifique os campos e tente novamente."},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """STORY-300 AC5-AC7: Catch-all — NEVER returns stack traces."""
        import sentry_sdk
        from middleware import correlation_id_var, request_id_var

        error_msg = str(exc).lower()
        corr_id = correlation_id_var.get("-")
        req_id = request_id_var.get("-")

        if "rls" in error_msg or "row-level security" in error_msg or (
            "policy" in error_msg and "permission" in error_msg
        ):
            logger.error(f"RLS error on {request.url.path}: {exc}")
            sentry_sdk.capture_exception(exc)
            return JSONResponse(
                status_code=403,
                content={"detail": "Erro de permissão. Faça login novamente.", "correlation_id": corr_id},
            )

        if "stripe" in error_msg or "stripeerror" in type(exc).__name__.lower():
            logger.error(f"Unhandled Stripe error on {request.url.path}: {exc}")
            sentry_sdk.capture_exception(exc)
            return JSONResponse(
                status_code=500,
                content={"detail": "Erro ao processar pagamento. Tente novamente.", "correlation_id": corr_id},
            )

        logger.exception(f"Unhandled error on {request.url.path}")
        sentry_sdk.capture_exception(exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Erro interno do servidor. Tente novamente.",
                "correlation_id": corr_id,
                "request_id": req_id,
            },
        )
