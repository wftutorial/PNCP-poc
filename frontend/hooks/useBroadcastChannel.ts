"use client";

import { useEffect, useRef, useCallback } from "react";
import type { BuscaResult } from "../app/types";

// ── Types ───────────────────────────────────────────────────────────────

export interface SearchCompleteMessage {
  type: "search_complete";
  result: BuscaResult;
  searchId: string | null;
  timestamp: number;
  tabId: string;
}

type BroadcastMessage = SearchCompleteMessage;

interface UseBroadcastChannelOptions {
  /** Called when another tab completes a search */
  onSearchComplete?: (result: BuscaResult, searchId: string | null) => void;
  /** Whether the hook is enabled (default: true) */
  enabled?: boolean;
}

interface UseBroadcastChannelReturn {
  /** Broadcast search completion to other tabs */
  broadcastSearchComplete: (result: BuscaResult, searchId: string | null) => void;
  /** Whether BroadcastChannel is supported in this browser */
  isSupported: boolean;
}

// ── Stable tab ID (unique per tab, survives re-renders) ─────────────────

const TAB_ID = typeof crypto !== "undefined" && crypto.randomUUID
  ? crypto.randomUUID()
  : Math.random().toString(36).slice(2);

// ── Hook ────────────────────────────────────────────────────────────────

export function useBroadcastChannel(
  options: UseBroadcastChannelOptions = {}
): UseBroadcastChannelReturn {
  const { onSearchComplete, enabled = true } = options;
  const channelRef = useRef<BroadcastChannel | null>(null);
  const callbackRef = useRef(onSearchComplete);
  callbackRef.current = onSearchComplete;

  const isSupported = typeof BroadcastChannel !== "undefined";

  // Setup / teardown channel
  useEffect(() => {
    if (!isSupported || !enabled) return;

    const channel = new BroadcastChannel("smartlic-search");
    channelRef.current = channel;

    channel.onmessage = (event: MessageEvent<BroadcastMessage>) => {
      const data = event.data;
      // Ignore messages from this tab
      if (data.tabId === TAB_ID) return;

      if (data.type === "search_complete" && callbackRef.current) {
        callbackRef.current(data.result, data.searchId);
      }
    };

    return () => {
      channel.close();
      channelRef.current = null;
    };
  }, [isSupported, enabled]);

  const broadcastSearchComplete = useCallback(
    (result: BuscaResult, searchId: string | null) => {
      if (!channelRef.current) return;
      const message: SearchCompleteMessage = {
        type: "search_complete",
        result,
        searchId,
        timestamp: Date.now(),
        tabId: TAB_ID,
      };
      try {
        channelRef.current.postMessage(message);
      } catch {
        // AC4: Graceful degradation — silently ignore serialization errors
      }
    },
    []
  );

  return { broadcastSearchComplete, isSupported };
}
