"""ISSUE-022: Value sanitization for procurement aggregations.

TCU methodology: CV > 25% -> sanitized sum excluding IQR outliers.
Hard cap at R$ 10B per individual procurement.
"""
import math
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# Hard cap: no single Brazilian municipal/state procurement exceeds R$ 10B
VALUE_HARD_CAP: float = 10_000_000_000.0  # R$ 10 bilhões


def sanitize_valor(valor) -> float:
    """Sanitize a single valor: clamp to [0, VALUE_HARD_CAP].

    Values exceeding the hard cap are treated as data quality issues
    and returned as 0.0 (excluded from aggregations).
    """
    if valor is None:
        return 0.0
    try:
        v = float(valor)
    except (ValueError, TypeError):
        return 0.0
    if v <= 0:
        return 0.0
    if v > VALUE_HARD_CAP:
        logger.warning(
            f"Value R$ {v:,.2f} exceeds hard cap R$ {VALUE_HARD_CAP:,.2f} — "
            f"treating as data quality issue"
        )
        return 0.0
    return v


def compute_robust_total(
    values: List[float],
) -> Tuple[float, float, int, bool]:
    """Compute robust total using TCU methodology.

    When coefficient of variation > 25%, excludes IQR outliers
    from the sum (TCU "média saneada" approach).

    Args:
        values: List of sanitized (post-cap) values.

    Returns:
        Tuple of (total, median, outlier_count, used_sanitized_sum)
    """
    valid = [v for v in values if v > 0]
    if not valid:
        return 0.0, 0.0, 0, False

    n = len(valid)
    total = sum(valid)
    mean = total / n
    sorted_vals = sorted(valid)
    median = sorted_vals[n // 2]

    if n < 3:
        return total, median, 0, False

    # Coefficient of Variation
    variance = sum((v - mean) ** 2 for v in valid) / n
    std_dev = math.sqrt(variance)
    cv = std_dev / mean if mean > 0 else 0.0

    # IQR-based outlier detection
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1

    if iqr > 0:
        upper_fence = q3 + 1.5 * iqr
    else:
        upper_fence = float("inf")

    outliers = [v for v in valid if v > upper_fence]
    outlier_count = len(outliers)

    # TCU: CV > 25% -> use sanitized sum (exclude outliers)
    if cv > 0.25 and outlier_count > 0:
        sanitized = [v for v in valid if v <= upper_fence]
        sanitized_total = sum(sanitized) if sanitized else total
        logger.info(
            f"TCU sanitization applied: CV={cv:.1%}, "
            f"{outlier_count} outlier(s) excluded, "
            f"total R$ {total:,.2f} -> R$ {sanitized_total:,.2f}"
        )
        return sanitized_total, median, outlier_count, True

    return total, median, outlier_count, False
