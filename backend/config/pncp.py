"""PNCP, PCP, ComprasGov source configuration: modalities, retry, timeouts, bulkheads."""

import os
from dataclasses import dataclass, field
from typing import List, Tuple, Type

from config.base import str_to_bool

# DEBT-107: httpx exceptions replace requests.exceptions
import httpx


# PNCP Modality Codes (codigoModalidadeContratacao)
MODALIDADES_PNCP = {
    1: "Leilão - Eletrônico",
    2: "Diálogo Competitivo",
    3: "Concurso",
    4: "Concorrência - Eletrônica",
    5: "Concorrência - Presencial",
    6: "Pregão - Eletrônico",
    7: "Pregão - Presencial",
    8: "Dispensa",
    9: "Inexigibilidade",
    10: "Manifestação de Interesse",
    11: "Pré-qualificação",
    12: "Credenciamento",
    13: "Leilão - Presencial",
    14: "Inaplicabilidade da Licitação",
    15: "Chamada pública",
}

DEFAULT_MODALIDADES: List[int] = [4, 5, 6, 7]

MODALIDADES_EXCLUIDAS: List[int] = [9, 14]


@dataclass
class RetryConfig:
    """Configuration for HTTP retry logic.

    STORY-282 AC1: Defaults use PNCP-specific env vars.
    """
    max_retries: int = int(os.getenv("PNCP_MAX_RETRIES", "1"))
    base_delay: float = 1.5
    max_delay: float = 15.0
    exponential_base: int = 2
    jitter: bool = True
    timeout: int = int(os.getenv("PNCP_READ_TIMEOUT", "15"))
    connect_timeout: float = float(os.getenv("PNCP_CONNECT_TIMEOUT", "10"))
    read_timeout: float = float(os.getenv("PNCP_READ_TIMEOUT", "15"))

    retryable_status_codes: Tuple[int, ...] = field(
        default_factory=lambda: (408, 422, 429, 500, 502, 503, 504)
    )

    # DEBT-107: httpx exceptions replace requests.exceptions (CRIT-038 original note preserved)
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (
            ConnectionError,
            TimeoutError,
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.ReadError,
        )
    )


# STORY-282: PNCP Timeout Resilience
PNCP_CONNECT_TIMEOUT: float = float(os.getenv("PNCP_CONNECT_TIMEOUT", "10"))
PNCP_READ_TIMEOUT: float = float(os.getenv("PNCP_READ_TIMEOUT", "15"))
PNCP_MAX_RETRIES: int = int(os.getenv("PNCP_MAX_RETRIES", "1"))
PNCP_MAX_PAGES: int = int(os.getenv("PNCP_MAX_PAGES", "5"))
# DEBT-102 AC6: PNCP API max page size (reduced from 500 to 50 by PNCP ~Feb 2026)
PNCP_MAX_PAGE_SIZE: int = 50
CACHE_FIRST_FRESH_TIMEOUT: int = int(os.getenv("CACHE_FIRST_FRESH_TIMEOUT", "60"))

# CRIT-052: Per-search PNCP canary adaptive timeout
PNCP_CANARY_TIMEOUT_S: float = float(os.getenv("PNCP_CANARY_TIMEOUT_S", "10"))
PNCP_CANARY_TIMEOUT_EXTENDED_S: float = float(os.getenv("PNCP_CANARY_TIMEOUT_EXTENDED_S", "15"))

# STORY-296: Bulkhead Per Source
PNCP_BULKHEAD_CONCURRENCY: int = int(os.getenv("PNCP_BULKHEAD_CONCURRENCY", "5"))
PCP_BULKHEAD_CONCURRENCY: int = int(os.getenv("PCP_BULKHEAD_CONCURRENCY", "3"))
COMPRASGOV_BULKHEAD_CONCURRENCY: int = int(os.getenv("COMPRASGOV_BULKHEAD_CONCURRENCY", "3"))
PNCP_SOURCE_TIMEOUT: float = float(os.getenv("PNCP_SOURCE_TIMEOUT", "80"))
PCP_SOURCE_TIMEOUT: float = float(os.getenv("PCP_SOURCE_TIMEOUT", "30"))
COMPRASGOV_SOURCE_TIMEOUT: float = float(os.getenv("COMPRASGOV_SOURCE_TIMEOUT", "30"))

# CRIT-047: PCP v2 Timeout Resilience
PCP_MAX_PAGES_V2: int = int(os.getenv("PCP_MAX_PAGES_V2", "20"))
PCP_RATE_LIMIT_DELAY: float = float(os.getenv("PCP_RATE_LIMIT_DELAY", "0.5"))
PCP_SLOW_PAGE_THRESHOLD_S: float = float(os.getenv("PCP_SLOW_PAGE_THRESHOLD_S", "10.0"))

# STORY-305: ComprasGov circuit breaker
COMPRASGOV_CB_ENABLED: bool = os.getenv("COMPRASGOV_CB_ENABLED", "true").lower() in ("true", "1", "yes")

# HARDEN-010: ComprasGov v3 master flag (API down since 2026-03-03)
COMPRASGOV_ENABLED: bool = str_to_bool(os.getenv("COMPRASGOV_ENABLED", "false"))

# GTM-STAB-003: Timeout Chain
PIPELINE_TIMEOUT: int = int(os.getenv("PIPELINE_TIMEOUT", "110"))
CONSOLIDATION_TIMEOUT: int = int(os.getenv("CONSOLIDATION_TIMEOUT", "100"))
PNCP_TIMEOUT_PER_SOURCE: int = int(os.getenv("PNCP_TIMEOUT_PER_SOURCE", "80"))
PNCP_TIMEOUT_PER_UF: int = int(os.getenv("PNCP_TIMEOUT_PER_UF", "30"))
PNCP_TIMEOUT_PER_UF_DEGRADED: int = int(os.getenv("PNCP_TIMEOUT_PER_UF_DEGRADED", "15"))
PIPELINE_SKIP_LLM_AFTER_S: int = int(os.getenv("PIPELINE_SKIP_LLM_AFTER_S", "90"))
PIPELINE_SKIP_VIABILITY_AFTER_S: int = int(os.getenv("PIPELINE_SKIP_VIABILITY_AFTER_S", "100"))

# GTM-STAB-003 AC3: Consolidation early return
EARLY_RETURN_THRESHOLD_PCT: float = float(os.getenv("EARLY_RETURN_THRESHOLD_PCT", "0.8"))
EARLY_RETURN_TIME_S: float = float(os.getenv("EARLY_RETURN_TIME_S", "80.0"))
