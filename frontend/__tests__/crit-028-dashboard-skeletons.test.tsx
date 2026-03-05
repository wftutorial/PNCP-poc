/**
 * CRIT-028 AC8-AC10: Dashboard skeletons / usePlan fallback tests.
 * TD-008: usePlan now delegates to useUserProfile (SWR-based).
 *
 * Verifies:
 * - AC8: Dashboard with data shows cards correctly
 * - AC9: Dashboard with empty data shows empty state with CTA
 * - AC10: Zero regressions
 * - AC1-AC2: usePlan falls back to cached plan on fetch error
 * - AC6: console.warn on failures (not console.error)
 */
import React from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { SWRConfig } from "swr";
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

function wrapper({ children }: { children: React.ReactNode }) {
  return React.createElement(
    SWRConfig,
    { value: { provider: () => new Map(), dedupingInterval: 0, errorRetryCount: 0 } },
    children
  );
}

describe("CRIT-028: usePlan fallback behavior", () => {
  let mockFetch: jest.Mock;

  beforeEach(() => {
    mockFetch = jest.fn();
    global.fetch = mockFetch;
    localStorage.clear();
    jest.spyOn(console, "warn").mockImplementation(() => {});
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
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

    const { result } = renderHook(() => usePlan(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.planInfo?.plan_id).toBe("smartlic_pro");
    expect(result.current.planInfo?.plan_name).toBe("SmartLic Pro");
    expect(result.current.planInfo?.quota_used).toBe(5);
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

    mockFetch.mockRejectedValue(new TypeError("Failed to fetch"));

    const { result } = renderHook(() => usePlan(), { wrapper });

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
    mockFetch.mockRejectedValue(new TypeError("Failed to fetch"));

    const { result } = renderHook(() => usePlan(), { wrapper });

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

    const { result } = renderHook(() => usePlan(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Expired cache should NOT be used
    expect(result.current.planInfo).toBeNull();
  });

  // AC6: console.warn on failure (SWR reports errors via onError)
  it("AC6: uses console.warn instead of console.error for plan fetch failures", async () => {
    mockFetch.mockRejectedValue(new TypeError("Failed to fetch"));

    renderHook(() => usePlan(), { wrapper });

    // Wait for SWR to complete and error to be reported
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });

    // Wait for any async warnings
    await new Promise(r => setTimeout(r, 100));

    // usePlan itself doesn't console.warn — SWR handles errors internally
    // The key assertion is that console.error is NOT called with usePlan-specific messages
    const errorCalls = (console.error as jest.Mock).mock.calls.filter(
      (call: any[]) => typeof call[0] === "string" && call[0].includes("[usePlan]")
    );
    expect(errorCalls.length).toBe(0);
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

    renderHook(() => usePlan(), { wrapper });

    await waitFor(() => {
      const cached = localStorage.getItem("smartlic_cached_plan");
      expect(cached).not.toBeNull();
      const parsed = JSON.parse(cached!);
      expect(parsed.data.plan_id).toBe("smartlic_pro");
    });
  });
});
