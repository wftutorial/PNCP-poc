/**
 * CRIT-028 AC8-AC10: Dashboard skeletons / usePlan fallback tests.
 * Updated for CRIT-031: usePlan now uses useFetchWithBackoff with max 3 retries.
 *
 * Verifies:
 * - AC8: Dashboard with data shows cards correctly
 * - AC9: Dashboard with empty data shows empty state with CTA
 * - AC10: Zero regressions
 * - AC1-AC2: usePlan falls back to cached plan on fetch error
 * - AC6: console.error downgraded to console.warn
 */
import React from "react";
import { renderHook, act, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

// Mock AuthProvider before importing usePlan
const mockSession = { access_token: "test-token" };
const mockUser = { id: "user-123", email: "test@example.com" };

jest.mock("../app/components/AuthProvider", () => ({
  useAuth: () => ({
    session: mockSession,
    user: mockUser,
    loading: false,
    signOut: jest.fn(),
  }),
}));

import { usePlan } from "../hooks/usePlan";

describe("CRIT-028: usePlan fallback behavior", () => {
  let mockFetch: jest.Mock;

  beforeEach(() => {
    jest.useFakeTimers();
    mockFetch = jest.fn();
    global.fetch = mockFetch;
    localStorage.clear();
    jest.spyOn(console, "warn").mockImplementation(() => {});
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  // AC8: When fetch succeeds, planInfo is populated
  it("AC8: populates planInfo on successful fetch", async () => {
    const mockPlan = {
      user_id: "user-123",
      email: "test@example.com",
      plan_id: "smartlic_pro",
      plan_name: "SmartLic Pro",
      capabilities: {
        max_history_days: 1825,
        allow_excel: true,
        max_requests_per_month: 1000,
        max_requests_per_min: 10,
        max_summary_tokens: 500,
        priority: "NORMAL",
      },
      quota_used: 5,
      quota_remaining: 995,
      quota_reset_date: "2026-03-01",
      trial_expires_at: null,
      subscription_status: "active",
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockPlan,
    });

    const { result } = renderHook(() => usePlan());

    await act(async () => {
      jest.advanceTimersByTime(100);
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.planInfo).toEqual(mockPlan);
    expect(result.current.error).toBeNull();
  });

  // AC1-AC2: On fetch error, fall back to cached plan
  it("AC1-AC2: falls back to cached plan on fetch error", async () => {
    const cachedPlan = {
      user_id: "user-123",
      email: "test@example.com",
      plan_id: "smartlic_pro",
      plan_name: "SmartLic Pro",
      capabilities: {
        max_history_days: 1825,
        allow_excel: true,
        max_requests_per_month: 1000,
        max_requests_per_min: 10,
        max_summary_tokens: 500,
        priority: "NORMAL",
      },
      quota_used: 3,
      quota_remaining: 997,
      quota_reset_date: "2026-03-01",
      trial_expires_at: null,
      subscription_status: "active",
    };

    // Pre-populate cache
    localStorage.setItem(
      "smartlic_cached_plan",
      JSON.stringify({ data: cachedPlan, timestamp: Date.now() })
    );

    // Fetch always fails (all retries)
    mockFetch.mockRejectedValue(new TypeError("Failed to fetch"));

    const { result } = renderHook(() => usePlan());

    // Exhaust 3 retries (attempt 0 + 2 retries with backoff 2s, 4s)
    for (let i = 0; i < 4; i++) {
      await act(async () => {
        jest.advanceTimersByTime(i === 0 ? 100 : 10_000);
        await Promise.resolve();
        await Promise.resolve();
      });
    }

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should fall back to cached plan, NOT null
    expect(result.current.planInfo).not.toBeNull();
    expect(result.current.planInfo?.plan_id).toBe("smartlic_pro");
    expect(result.current.error).not.toBeNull();
  });

  // AC9: When no cache and fetch fails, planInfo is null
  it("AC9: planInfo is null when no cache and fetch fails", async () => {
    // No cache, fetch always fails
    mockFetch.mockRejectedValue(new TypeError("Failed to fetch"));

    const { result } = renderHook(() => usePlan());

    // Exhaust retries
    for (let i = 0; i < 4; i++) {
      await act(async () => {
        jest.advanceTimersByTime(i === 0 ? 100 : 10_000);
        await Promise.resolve();
        await Promise.resolve();
      });
    }

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.planInfo).toBeNull();
    expect(result.current.error).not.toBeNull();
  });

  // AC2: Expired cache is NOT used as fallback
  it("expired cache is not used as fallback", async () => {
    const cachedPlan = {
      user_id: "user-123",
      email: "test@example.com",
      plan_id: "smartlic_pro",
      plan_name: "SmartLic Pro",
      capabilities: {
        max_history_days: 1825,
        allow_excel: true,
        max_requests_per_month: 1000,
        max_requests_per_min: 10,
        max_summary_tokens: 500,
        priority: "NORMAL",
      },
      quota_used: 3,
      quota_remaining: 997,
      quota_reset_date: "2026-03-01",
      trial_expires_at: null,
      subscription_status: "active",
    };

    // Cache with expired timestamp (2 hours ago)
    localStorage.setItem(
      "smartlic_cached_plan",
      JSON.stringify({ data: cachedPlan, timestamp: Date.now() - 7200000 })
    );

    mockFetch.mockRejectedValue(new TypeError("Failed to fetch"));

    const { result } = renderHook(() => usePlan());

    // Exhaust retries
    for (let i = 0; i < 4; i++) {
      await act(async () => {
        jest.advanceTimersByTime(i === 0 ? 100 : 10_000);
        await Promise.resolve();
        await Promise.resolve();
      });
    }

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Expired cache should NOT be used
    expect(result.current.planInfo).toBeNull();
  });

  // AC6: console.error downgraded to console.warn
  it("AC6: uses console.warn instead of console.error for plan fetch failures", async () => {
    mockFetch.mockRejectedValue(new TypeError("Failed to fetch"));

    const warnSpy = jest.spyOn(console, "warn");

    renderHook(() => usePlan());

    // Exhaust retries
    for (let i = 0; i < 4; i++) {
      await act(async () => {
        jest.advanceTimersByTime(i === 0 ? 100 : 10_000);
        await Promise.resolve();
        await Promise.resolve();
      });
    }

    await waitFor(() => {
      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining("[usePlan] Failed to fetch plan info:"),
        expect.anything()
      );
    });
  });

  // Successful fetch caches the plan
  it("caches paid plan on successful fetch", async () => {
    const mockPlan = {
      user_id: "user-123",
      email: "test@example.com",
      plan_id: "smartlic_pro",
      plan_name: "SmartLic Pro",
      capabilities: {
        max_history_days: 1825,
        allow_excel: true,
        max_requests_per_month: 1000,
        max_requests_per_min: 10,
        max_summary_tokens: 500,
        priority: "NORMAL",
      },
      quota_used: 5,
      quota_remaining: 995,
      quota_reset_date: "2026-03-01",
      trial_expires_at: null,
      subscription_status: "active",
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockPlan,
    });

    renderHook(() => usePlan());

    await act(async () => {
      jest.advanceTimersByTime(100);
      await Promise.resolve();
    });

    await waitFor(() => {
      const cached = localStorage.getItem("smartlic_cached_plan");
      expect(cached).not.toBeNull();
      const parsed = JSON.parse(cached!);
      expect(parsed.data.plan_id).toBe("smartlic_pro");
    });
  });
});
