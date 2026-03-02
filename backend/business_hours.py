"""STORY-353 AC8: Business hours calculation for support SLA.

Defines "business hours" as Mon-Fri 8h-18h BRT (UTC-3).
Configurable via env vars BUSINESS_HOURS_START and BUSINESS_HOURS_END.
"""

from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))


def calculate_business_hours(start: datetime, end: datetime) -> float:
    """Calculate elapsed business hours between two datetimes.

    Business hours: Mon-Fri, BUSINESS_HOURS_START to BUSINESS_HOURS_END (BRT).
    Both start and end are converted to BRT before calculation.

    Args:
        start: Start datetime (timezone-aware or naive UTC assumed).
        end: End datetime (timezone-aware or naive UTC assumed).

    Returns:
        Float number of business hours elapsed.
    """
    from config import BUSINESS_HOURS_START, BUSINESS_HOURS_END

    hours_per_day = BUSINESS_HOURS_END - BUSINESS_HOURS_START
    if hours_per_day <= 0:
        return 0.0

    # Convert to BRT
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    start_brt = start.astimezone(BRT)
    end_brt = end.astimezone(BRT)

    if end_brt <= start_brt:
        return 0.0

    total_hours = 0.0
    current = start_brt

    while current < end_brt:
        # Skip weekends
        if current.weekday() >= 5:  # Saturday=5, Sunday=6
            # Jump to next Monday 00:00
            days_until_monday = 7 - current.weekday()
            current = current.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=days_until_monday)
            continue

        day_start = current.replace(
            hour=BUSINESS_HOURS_START, minute=0, second=0, microsecond=0
        )
        day_end = current.replace(
            hour=BUSINESS_HOURS_END, minute=0, second=0, microsecond=0
        )

        # Effective window for this day
        effective_start = max(current, day_start)
        effective_end = min(end_brt, day_end)

        if effective_start < effective_end:
            delta = (effective_end - effective_start).total_seconds() / 3600
            total_hours += delta

        # Move to next day start
        current = current.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

    return round(total_hours, 2)


def is_within_business_hours(dt: datetime) -> bool:
    """Check if a datetime falls within business hours.

    Args:
        dt: Datetime to check (timezone-aware or naive UTC assumed).

    Returns:
        True if within Mon-Fri BUSINESS_HOURS_START-BUSINESS_HOURS_END BRT.
    """
    from config import BUSINESS_HOURS_START, BUSINESS_HOURS_END

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    dt_brt = dt.astimezone(BRT)

    # Weekday check (Mon=0 .. Fri=4)
    if dt_brt.weekday() >= 5:
        return False

    return BUSINESS_HOURS_START <= dt_brt.hour < BUSINESS_HOURS_END
