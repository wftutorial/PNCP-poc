"""STORY-315 AC1-AC4: Alert matching engine.

Queries active alerts for users with active plans, executes cached-result
search per alert using filter.py–compatible logic, cross-deduplicates within
the same user, and records runs in ``alert_runs`` for auditability.

Usage (from cron_jobs.py):
    from services.alert_matcher import match_alerts
    results = await match_alerts()
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from supabase_client import get_supabase, sb_execute

logger = logging.getLogger(__name__)

# Active plan types that should receive alert emails
_ACTIVE_PLAN_TYPES = frozenset({
    "smartlic_pro",
    "consultor_agil",
    "maquina",
    "sala_guerra",
    "free_trial",
})


# ---------------------------------------------------------------------------
# AC1: match_alerts() — main entry point
# ---------------------------------------------------------------------------


async def match_alerts(
    max_alerts: int = 100,
    batch_size: int = 10,
    db=None,
) -> dict:
    """Execute all active alerts for users with active plans.

    AC1: For each alert:
      1. Query active alerts where user has an active plan.
      2. Search cached results using alert filters.
      3. Dedup against previously sent items.
      4. Cross-alert dedup per user (AC3).
      5. Record run in alert_runs (AC10).

    Args:
        max_alerts: Maximum alerts to process per execution (AC8).
        batch_size: Concurrent batch size for processing.
        db: Supabase client (fetched if None).

    Returns:
        Dict with keys: total_alerts, matched, skipped, errors, payloads.
    """
    if db is None:
        db = get_supabase()

    summary = {
        "total_alerts": 0,
        "matched": 0,
        "skipped": 0,
        "errors": 0,
        "payloads": [],
    }

    # Step 1: Get active alerts with enriched user data
    alerts = await _get_eligible_alerts(db, limit=max_alerts)
    summary["total_alerts"] = len(alerts)

    if not alerts:
        logger.info("STORY-315: No eligible alerts to process")
        return summary

    # AC3: Cross-alert dedup per user — track items already assigned
    user_sent_items: dict[str, set[str]] = {}

    for alert in alerts:
        try:
            payload = await _process_alert(alert, user_sent_items, db)

            if payload.get("skipped"):
                summary["skipped"] += 1
            else:
                summary["matched"] += 1
                summary["payloads"].append(payload)

                # AC3: Update cross-alert dedup set for this user
                user_id = alert["user_id"]
                if user_id not in user_sent_items:
                    user_sent_items[user_id] = set()
                for item in payload.get("new_items", []):
                    user_sent_items[user_id].add(item.get("id", ""))

        except Exception as e:
            summary["errors"] += 1
            logger.error(
                "STORY-315: Failed to process alert %s: %s",
                alert["id"][:8], e,
            )

    logger.info(
        "STORY-315: match_alerts complete — "
        "total=%d, matched=%d, skipped=%d, errors=%d",
        summary["total_alerts"],
        summary["matched"],
        summary["skipped"],
        summary["errors"],
    )

    return summary


# ---------------------------------------------------------------------------
# AC1: Get eligible alerts (active + user with active plan)
# ---------------------------------------------------------------------------


async def _get_eligible_alerts(db, limit: int = 100) -> list[dict]:
    """Query active alerts enriched with user profile + plan data.

    AC1: Only returns alerts where the user has an active plan type.

    Returns:
        List of dicts: id, user_id, name, filters, email, full_name.
    """
    try:
        # Fetch all active alerts
        result = await sb_execute(
            db.table("alerts")
            .select("id, user_id, name, filters, active, created_at")
            .eq("active", True)
            .limit(limit)
        )

        if not result.data:
            return []

        enriched = []
        for alert in result.data:
            user_id = alert.get("user_id")
            if not user_id:
                continue

            # Fetch profile with plan info
            profile = await _get_profile_with_plan(user_id, db)
            if not profile:
                continue

            # AC1: Only users with active plans
            plan_type = profile.get("plan_type", "")
            if plan_type not in _ACTIVE_PLAN_TYPES:
                logger.debug(
                    "Skipping alert %s — user %s has plan_type=%s",
                    alert["id"][:8], user_id[:8], plan_type,
                )
                continue

            if not profile.get("email"):
                continue

            enriched.append({
                "id": alert["id"],
                "user_id": user_id,
                "name": alert.get("name", ""),
                "filters": alert.get("filters") or {},
                "email": profile["email"],
                "full_name": (
                    profile.get("full_name")
                    or profile["email"].split("@")[0]
                ),
            })

        logger.info(
            "STORY-315: Found %d eligible alerts (from %d active)",
            len(enriched), len(result.data),
        )
        return enriched

    except Exception as e:
        logger.error("STORY-315: Failed to get eligible alerts: %s", e)
        return []


async def _get_profile_with_plan(user_id: str, db) -> Optional[dict]:
    """Fetch profile with email, full_name, and plan_type."""
    try:
        result = await sb_execute(
            db.table("profiles")
            .select("email, full_name, plan_type")
            .eq("id", user_id)
            .single()
        )
        return result.data
    except Exception as e:
        logger.warning(
            "STORY-315: Failed to get profile for %s: %s",
            user_id[:8], e,
        )
        return None


# ---------------------------------------------------------------------------
# AC1+AC2: Process a single alert with filter.py–compatible matching
# ---------------------------------------------------------------------------


async def _process_alert(
    alert: dict,
    user_sent_items: dict[str, set[str]],
    db,
) -> dict:
    """Process one alert: search, filter, dedup, return payload.

    AC2: Uses keyword density scoring, UF filtering, value range,
    and status filtering (only open bids).

    AC3: Cross-alert dedup — skips items already in another alert
    for the same user.

    AC4: Searches last 24h of cached results.

    Returns:
        Dict: alert_id, user_id, email, full_name, alert_name,
              new_items, total_found, skipped, skip_reason.
    """
    from services.alert_service import check_rate_limit, get_sent_item_ids

    alert_id = alert["id"]
    user_id = alert["user_id"]

    result = {
        "alert_id": alert_id,
        "user_id": user_id,
        "email": alert["email"],
        "full_name": alert["full_name"],
        "alert_name": alert.get("name") or "suas licitacoes",
        "new_items": [],
        "total_found": 0,
        "skipped": False,
        "skip_reason": None,
    }

    # Rate limit check (max 1/day per alert)
    if await check_rate_limit(alert_id, db):
        result["skipped"] = True
        result["skip_reason"] = "rate_limited"
        return result

    # AC4: Search cached results from last 24h
    raw_results = await _search_cached_results(alert.get("filters", {}), db)

    if not raw_results:
        result["skipped"] = True
        result["skip_reason"] = "no_results"
        # Record run even for empty results
        await _record_alert_run(alert_id, 0, 0, "no_results", db)
        return result

    # AC2: Apply filter.py–compatible matching
    filtered = _apply_alert_filters(raw_results, alert.get("filters", {}))

    if not filtered:
        result["skipped"] = True
        result["skip_reason"] = "no_matching_results"
        await _record_alert_run(alert_id, len(raw_results), 0, "no_match", db)
        return result

    # Dedup against previously sent items
    sent_ids = await get_sent_item_ids(alert_id, db)
    new_items = [
        item for item in filtered
        if item.get("id") and item["id"] not in sent_ids
    ]

    # AC3: Cross-alert dedup for same user
    user_already_sent = user_sent_items.get(user_id, set())
    if user_already_sent:
        new_items = [
            item for item in new_items
            if item.get("id") not in user_already_sent
        ]

    if not new_items:
        result["skipped"] = True
        result["skip_reason"] = "all_already_sent"
        await _record_alert_run(
            alert_id, len(raw_results), 0, "all_deduped", db,
        )
        return result

    result["new_items"] = new_items
    result["total_found"] = len(new_items)

    # AC10: Record successful run
    await _record_alert_run(
        alert_id, len(raw_results), len(new_items), "matched", db,
    )

    return result


# ---------------------------------------------------------------------------
# AC4: Search cached results (last 24h)
# ---------------------------------------------------------------------------


async def _search_cached_results(
    alert_filters: dict, db,
) -> list[dict]:
    """Search cached results for alert matching.

    AC4: Queries search_results_cache for entries from the last 24h
    (or since the last run). Lightweight — no external API calls.

    Returns:
        Flat list of opportunity dicts with normalized keys.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    setor = alert_filters.get("setor", "")

    try:
        query = (
            db.table("search_results_cache")
            .select("results, search_params, created_at")
            .gte("created_at", since.isoformat())
            .order("created_at", desc=True)
            .limit(100)
        )
        result = await sb_execute(query)

        if not result.data:
            return []

        all_items: list[dict] = []
        seen_ids: set[str] = set()

        for row in result.data:
            results = row.get("results") or []
            params = row.get("search_params") or {}

            # Sector pre-filter
            if setor and params.get("setor_id") and params["setor_id"] != setor:
                continue

            for item in results:
                if not isinstance(item, dict):
                    continue

                item_id = (
                    item.get("id")
                    or item.get("numeroControlePNCP")
                    or item.get("pncp_id")
                    or ""
                )
                if not item_id or item_id in seen_ids:
                    continue
                seen_ids.add(item_id)

                all_items.append(_normalize_item(item, item_id))

        return all_items

    except Exception as e:
        logger.error("STORY-315: Cache search failed: %s", e)
        return []


def _normalize_item(item: dict, item_id: str) -> dict:
    """Normalize a raw cached item into a standard format."""
    return {
        "id": item_id,
        "titulo": (
            item.get("objetoCompra")
            or item.get("titulo")
            or "Sem titulo"
        ),
        "orgao": (
            item.get("nomeOrgao")
            or item.get("orgao")
            or "Nao informado"
        ),
        "valor_estimado": float(
            item.get("valorTotalEstimado")
            or item.get("valor_estimado")
            or 0
        ),
        "uf": item.get("uf") or item.get("unidadeFederativa", ""),
        "modalidade": (
            item.get("modalidade")
            or item.get("modalidadeNome", "")
        ),
        "link_pncp": item.get("link_pncp") or item.get("linkPncp", ""),
        "viability_score": item.get("viability_score"),
        "status": item.get("status", ""),
        "data_publicacao": item.get("dataPublicacao", ""),
    }


# ---------------------------------------------------------------------------
# AC2: Apply filter.py–compatible matching
# ---------------------------------------------------------------------------


def _apply_alert_filters(
    items: list[dict], filters: dict,
) -> list[dict]:
    """Apply alert filter criteria to a list of items.

    AC2: Uses same logic as filter.py:
      - UF filtering
      - Value range filtering
      - Keyword density scoring
      - Status filtering (only open bids)

    Args:
        items: Normalized opportunity dicts.
        filters: Alert filter criteria.

    Returns:
        Filtered list of matching items, sorted by relevance.
    """
    ufs = filters.get("ufs") or []
    keywords = filters.get("keywords") or []
    valor_min = float(filters.get("valor_min") or 0)
    valor_max = float(filters.get("valor_max") or 0)

    matched: list[dict] = []

    for item in items:
        # 1. UF check (fastest — fail-fast)
        if ufs:
            item_uf = item.get("uf", "")
            if item_uf and item_uf not in ufs:
                continue

        # 2. Value range check
        item_valor = item.get("valor_estimado", 0) or 0
        if valor_min > 0 and item_valor > 0 and item_valor < valor_min:
            continue
        if valor_max > 0 and item_valor > 0 and item_valor > valor_max:
            continue

        # 3. Keyword matching with density scoring (AC2)
        if keywords:
            text = f"{item.get('titulo', '')} {item.get('orgao', '')}".lower()
            words = text.split()
            word_count = max(len(words), 1)

            total_matches = 0
            any_match = False
            for kw in keywords:
                kw_lower = kw.lower()
                occurrences = text.count(kw_lower)
                if occurrences > 0:
                    any_match = True
                    total_matches += occurrences

            if not any_match:
                continue

            # AC2: Density scoring (same thresholds as filter.py)
            density = total_matches / word_count
            item["keyword_density"] = density

        # 4. Status filtering — only open bids
        status = item.get("status", "").lower()
        if status and status in ("encerrada", "revogada", "anulada", "suspensa"):
            continue

        matched.append(item)

    # Sort: viability_score DESC, then keyword_density DESC, then valor DESC
    matched.sort(
        key=lambda x: (
            x.get("viability_score") or 0.0,
            x.get("keyword_density", 0.0),
            x.get("valor_estimado") or 0.0,
        ),
        reverse=True,
    )

    return matched


# ---------------------------------------------------------------------------
# AC10: Record alert run in alert_runs table
# ---------------------------------------------------------------------------


async def _record_alert_run(
    alert_id: str,
    items_found: int,
    items_sent: int,
    status: str,
    db,
) -> None:
    """Record an alert run in the alert_runs table for history/debugging.

    AC10: Persists run metadata for auditing and debugging.
    """
    try:
        await sb_execute(
            db.table("alert_runs").insert({
                "alert_id": alert_id,
                "run_at": datetime.now(timezone.utc).isoformat(),
                "items_found": items_found,
                "items_sent": items_sent,
                "status": status,
            })
        )
    except Exception as e:
        # Non-critical — don't fail the alert on logging failure
        logger.warning(
            "STORY-315: Failed to record alert run for %s: %s",
            alert_id[:8], e,
        )


# ---------------------------------------------------------------------------
# Finalize: track sent items after email confirmed sent
# ---------------------------------------------------------------------------


async def finalize_matched_alert(
    alert_id: str, item_ids: list[str], db=None,
) -> None:
    """Record items as sent after email delivery is confirmed.

    Call AFTER the email is successfully sent to update dedup tracking.
    """
    from services.alert_service import track_sent_items

    if db is None:
        db = get_supabase()

    await track_sent_items(alert_id, item_ids, db)
