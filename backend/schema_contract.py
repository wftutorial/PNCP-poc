"""DEBT-208: Backward-compat re-export — will be removed after 1 sprint.

Canonical location: schemas/contract.py
"""
from schemas.contract import *  # noqa: F401,F403
from schemas.contract import (  # noqa: F401
    CRITICAL_SCHEMA,
    OPTIONAL_RPCS,
    validate_schema_contract,
    emit_degradation_warning,
)
