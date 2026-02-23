-- CRIT-029: Normalize existing search_sessions arrays to sorted order.
-- Ensures dedup query (.filter with sorted PG array literals) matches
-- sessions created before this fix was deployed.

UPDATE search_sessions
SET ufs = (SELECT array_agg(u ORDER BY u) FROM unnest(ufs) u)
WHERE ufs IS NOT NULL;

UPDATE search_sessions
SET sectors = (SELECT array_agg(s ORDER BY s) FROM unnest(sectors) s)
WHERE sectors IS NOT NULL;
