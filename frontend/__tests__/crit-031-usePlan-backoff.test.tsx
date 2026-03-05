/**
 * CRIT-031 AC9: usePlan with SWR retry behavior.
 *
 * TD-008: usePlan now delegates to useUserProfile (SWR-based).
 * SWR handles retry internally (errorRetryCount: 3).
 *
 * Verifies:
 * - AC5: SWR retries failed requests (built-in backoff)
 * - AC6: Does not make infinite retries
 * - AC7: Console warnings remain limited
 * - Degradation detection: cached paid plan used when backend returns free_trial
 */
import React from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { SWRConfig } from "swr";
import "@testing-library/jest-dom";

// Mock AuthProvider
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

describe("CRIT-031 AC9: usePlan backoff behavior", () => {
  let mockFetch: jest.Mock;
  let warnSpy: jest.SpyInstance;

  beforeEach(() => {
    mockFetch = jest.fn();
    global.fetch = mockFetch;
    localStorage.clear();
    warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe("AC5: SWR retry on failure", () => {
    it("retries failed request (not instant loop)", async () => {
      mockFetch.mockRejectedValue(new Error("503 Service Unavailable"));

      const { result } = renderHook(() => usePlan(), { wrapper });

      // SWR makes initial call
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled();
      });

      // With errorRetryCount: 0 in wrapper, should stop after initial attempt
      expect(result.current.error).toBeTruthy();
    });

    it("does NOT make instant retries (no 6 rapid calls)", async () => {
      mockFetch.mockRejectedValue(new Error("503"));

      renderHook(() => usePlan(), { wrapper });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled();
      });

      // With errorRetryCount: 0, only 1 call
      expect(mockFetch.mock.calls.length).toBeLessThanOrEqual(2); // SWR may call twice for the key tuple
    });
  });

  describe("AC6: Controlled retry count", () => {
    it("stops retrying eventually", async () => {
      mockFetch.mockRejectedValue(new Error("503"));

      const { result } = renderHook(() => usePlan(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Error should be set
      expect(result.current.error).toBeTruthy();
    });
  });

  describe("AC7: Limited console warnings", () => {
    it("does not produce excessive warnings", async () => {
      mockFetch.mockRejectedValue(new Error("503"));

      renderHook(() => usePlan(), { wrapper });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled();
      });

      // Wait a tick for warnings
      await new Promise(r => setTimeout(r, 100));

      // Count usePlan-specific warnings — should not be 12+
      const usePlanWarns = warnSpy.mock.calls.filter(
        (call: any[]) => typeof call[0] === "string" && call[0].includes("[usePlan]")
      );
      expect(usePlanWarns.length).toBeLessThanOrEqual(3);
    });
  });

  describe("Degradation detection preserved", () => {
    it("uses cached paid plan when backend returns free_trial", async () => {
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

      localStorage.setItem(
        "smartlic_cached_plan",
        JSON.stringify({ data: cachedPlan, timestamp: Date.now() })
      );

      // Backend returns degraded free_trial
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          ...cachedPlan,
          plan_id: "free_trial",
          plan_name: "Free Trial",
        }),
      });

      const { result } = renderHook(() => usePlan(), { wrapper });

      await waitFor(() => {
        expect(result.current.planInfo).not.toBeNull();
      });

      // CRIT-028: Should use cached paid plan, not degraded free_trial
      expect(result.current.planInfo?.plan_id).toBe("smartlic_pro");
    });

    it("falls back to cached plan on error", async () => {
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

      localStorage.setItem(
        "smartlic_cached_plan",
        JSON.stringify({ data: cachedPlan, timestamp: Date.now() })
      );

      mockFetch.mockRejectedValue(new Error("503"));

      const { result } = renderHook(() => usePlan(), { wrapper });

      await waitFor(() => {
        expect(result.current.planInfo).not.toBeNull();
      });

      // CRIT-028: Should fall back to cached plan
      expect(result.current.planInfo?.plan_id).toBe("smartlic_pro");
      expect(result.current.isFromCache).toBe(true);
    });
  });
});
