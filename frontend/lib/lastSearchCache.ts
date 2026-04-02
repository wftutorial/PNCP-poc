/**
 * GTM-UX-004 AC5-AC7: Last Search Cache
 *
 * Persists the most recent search result in localStorage so the
 * "Ver ultima busca" button in SourcesUnavailable can restore it
 * when all sources are down.
 */

import { safeSetItem, safeGetItem, safeRemoveItem } from "./storage";
import type { SearchFormState } from "./searchStatePersistence";

const LAST_SEARCH_KEY = "smartlic_last_search";
const LAST_SEARCH_TTL = 24 * 60 * 60 * 1000; // 24 hours

export interface LastSearchData {
  result: unknown; // BuscaResult
  timestamp: number;
  formState?: SearchFormState; // ISSUE-060: params used in this search
}

/** Save the most recent successful search result to localStorage */
export function saveLastSearch(result: unknown, formState?: SearchFormState): void {
  const data: LastSearchData = { result, timestamp: Date.now(), formState };
  safeSetItem(LAST_SEARCH_KEY, JSON.stringify(data));
}

/** Load the last search result (returns null if missing or expired) */
export function getLastSearch(): LastSearchData | null {
  try {
    const raw = safeGetItem(LAST_SEARCH_KEY);
    if (!raw) return null;
    const data: LastSearchData = JSON.parse(raw);
    if (Date.now() - data.timestamp > LAST_SEARCH_TTL) {
      safeRemoveItem(LAST_SEARCH_KEY);
      return null;
    }
    return data;
  } catch {
    return null;
  }
}

/** Check if a last search exists without consuming it */
export function checkHasLastSearch(): boolean {
  return getLastSearch() !== null;
}
