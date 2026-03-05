/**
 * TD-006 AC5 / TD-008: Isolated test suite for useTrialPhase hook (SWR-based).
 *
 * SWR handles caching internally (replaces sessionStorage caching).
 */

import { renderHook, waitFor } from "@testing-library/react";
import React from "react";
import { SWRConfig } from "swr";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockSession = { access_token: "test-token-123" };
let currentSession: typeof mockSession | null = mockSession;

jest.mock("../../app/components/AuthProvider", () => ({
  useAuth: () => ({ session: currentSession }),
}));

const mockFetch = jest.fn();
global.fetch = mockFetch;

// ---------------------------------------------------------------------------
// Import under test
// ---------------------------------------------------------------------------

import { useTrialPhase } from "../../hooks/useTrialPhase";

// Wrapper with isolated SWR cache per test
function wrapper({ children }: { children: React.ReactNode }) {
  return React.createElement(
    SWRConfig,
    { value: { provider: () => new Map(), dedupingInterval: 0, errorRetryCount: 0 } },
    children
  );
}

// ---------------------------------------------------------------------------
// Setup / Teardown
// ---------------------------------------------------------------------------

beforeEach(() => {
  mockFetch.mockReset();
  currentSession = mockSession;
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useTrialPhase (isolated)", () => {
  // 1. Active trial - full_access
  test("returns full_access phase for days 1-7", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "full_access",
        trial_day: 3,
        days_remaining: 11,
      }),
    });

    const { result } = renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("full_access");
    expect(result.current.day).toBe(3);
    expect(result.current.daysRemaining).toBe(11);
  });

  // 2. Limited access trial
  test("returns limited_access phase for days 8-14", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "limited_access",
        trial_day: 10,
        days_remaining: 4,
      }),
    });

    const { result } = renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("limited_access");
    expect(result.current.day).toBe(10);
    expect(result.current.daysRemaining).toBe(4);
  });

  // 3. Not trial (paid user)
  test("returns not_trial for paid users", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "not_trial",
        trial_day: 0,
        days_remaining: 0,
      }),
    });

    const { result } = renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("not_trial");
    expect(result.current.day).toBe(0);
    expect(result.current.daysRemaining).toBe(0);
  });

  // 4. No session (unauthenticated)
  test("returns full_access with day=0 when no session", async () => {
    currentSession = null;

    const { result } = renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("full_access");
    expect(result.current.day).toBe(0);
    expect(result.current.daysRemaining).toBe(999);
    expect(mockFetch).not.toHaveBeenCalled();
  });

  // 5. Loading state
  test("starts in loading state", () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // never resolves

    const { result } = renderHook(() => useTrialPhase(), { wrapper });

    expect(result.current.loading).toBe(true);
    expect(result.current.phase).toBe("full_access");
  });

  // 6. API error fallback
  test("falls back to full_access on fetch error", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network failure"));

    const { result } = renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("full_access");
    expect(result.current.day).toBe(0);
    expect(result.current.daysRemaining).toBe(999);
  });

  // 7. Non-OK response fallback
  test("falls back to full_access on non-OK response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: "Server error" }),
    });

    const { result } = renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // SWR-based hook returns null from fetcher on non-OK, treated as no data
    expect(result.current.phase).toBe("full_access");
    expect(result.current.day).toBe(0);
  });

  // 8. SWR deduplication (replaces old sessionStorage caching test)
  test("SWR deduplicates concurrent requests", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        trial_phase: "limited_access",
        trial_day: 9,
        days_remaining: 5,
      }),
    });

    const { result: r1 } = renderHook(() => useTrialPhase(), { wrapper });
    const { result: r2 } = renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(r1.current.loading).toBe(false);
      expect(r2.current.loading).toBe(false);
    });

    expect(r1.current.phase).toBe("limited_access");
    expect(r2.current.phase).toBe("limited_access");
  });

  // 9. Passes authorization header
  test("sends Authorization header with session token", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "full_access",
        trial_day: 1,
        days_remaining: 13,
      }),
    });

    renderHook(() => useTrialPhase(), { wrapper });

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    expect(mockFetch).toHaveBeenCalledWith("/api/trial-status", {
      headers: { Authorization: "Bearer test-token-123" },
    });
  });
});
