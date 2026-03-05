/**
 * TD-006 AC5: Isolated test suite for useTrialPhase hook.
 *
 * Covers:
 * - Active trial (full_access phase, days 1-7)
 * - Limited access trial (days 8-14)
 * - Expired / not_trial (paid user)
 * - No session (unauthenticated)
 * - Loading state
 * - API error fallback to full_access
 * - Non-OK response fallback
 * - SessionStorage caching
 * - Cache TTL expiration
 * - Cache corruption handling
 */

import { renderHook, act, waitFor } from "@testing-library/react";

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

// ---------------------------------------------------------------------------
// Setup / Teardown
// ---------------------------------------------------------------------------

beforeEach(() => {
  mockFetch.mockReset();
  currentSession = mockSession;
  // Clear sessionStorage
  if (typeof window !== "undefined") {
    sessionStorage.clear();
  }
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

    const { result } = renderHook(() => useTrialPhase());

    expect(result.current.loading).toBe(true);

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

    const { result } = renderHook(() => useTrialPhase());

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

    const { result } = renderHook(() => useTrialPhase());

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

    const { result } = renderHook(() => useTrialPhase());

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

    const { result } = renderHook(() => useTrialPhase());

    expect(result.current.loading).toBe(true);
    expect(result.current.phase).toBe("full_access");
  });

  // 6. API error fallback
  test("falls back to full_access on fetch error", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network failure"));

    const { result } = renderHook(() => useTrialPhase());

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

    const { result } = renderHook(() => useTrialPhase());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("full_access");
    expect(result.current.day).toBe(0);
  });

  // 8. SessionStorage caching - uses cached value
  test("uses sessionStorage cached value when fresh", async () => {
    const cached = {
      phase: "limited_access",
      day: 9,
      daysRemaining: 5,
      cachedAt: Date.now(), // fresh
    };
    sessionStorage.setItem("smartlic_trial_phase", JSON.stringify(cached));

    const { result } = renderHook(() => useTrialPhase());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("limited_access");
    expect(result.current.day).toBe(9);
    expect(result.current.daysRemaining).toBe(5);
    expect(mockFetch).not.toHaveBeenCalled();
  });

  // 9. Cache TTL expiration
  test("ignores expired cache and fetches from API", async () => {
    const cached = {
      phase: "limited_access",
      day: 9,
      daysRemaining: 5,
      cachedAt: Date.now() - 400_000, // > 5 min TTL
    };
    sessionStorage.setItem("smartlic_trial_phase", JSON.stringify(cached));

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "not_trial",
        trial_day: 0,
        days_remaining: 0,
      }),
    });

    const { result } = renderHook(() => useTrialPhase());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("not_trial");
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  // 10. Cache corruption handling
  test("handles corrupted cache gracefully", async () => {
    sessionStorage.setItem("smartlic_trial_phase", "not-valid-json{{");

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "full_access",
        trial_day: 1,
        days_remaining: 13,
      }),
    });

    const { result } = renderHook(() => useTrialPhase());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.phase).toBe("full_access");
    expect(result.current.day).toBe(1);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  // 11. Stores result in sessionStorage
  test("caches API response in sessionStorage", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "limited_access",
        trial_day: 8,
        days_remaining: 6,
      }),
    });

    renderHook(() => useTrialPhase());

    await waitFor(() => {
      const cached = sessionStorage.getItem("smartlic_trial_phase");
      expect(cached).not.toBeNull();
    });

    const cached = JSON.parse(sessionStorage.getItem("smartlic_trial_phase")!);
    expect(cached.phase).toBe("limited_access");
    expect(cached.day).toBe(8);
    expect(cached.daysRemaining).toBe(6);
    expect(cached.cachedAt).toBeDefined();
  });

  // 12. Passes authorization header
  test("sends Authorization header with session token", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        trial_phase: "full_access",
        trial_day: 1,
        days_remaining: 13,
      }),
    });

    renderHook(() => useTrialPhase());

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    expect(mockFetch).toHaveBeenCalledWith("/api/trial-status", {
      headers: { Authorization: "Bearer test-token-123" },
    });
  });
});
