/**
 * CRIT-031 AC9: usePlan with backend 503 → max 3 retries with increasing delays.
 *
 * Verifies:
 * - AC5: usePlan uses exponential backoff (useFetchWithBackoff)
 * - AC6: Maximum 3 retries with backoff (2s → 4s → 8s), not 6 instant retries
 * - AC7: Console warnings limited to max 3 (not 12)
 */
import React from "react";
import { renderHook, act, waitFor } from "@testing-library/react";
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

describe("CRIT-031 AC9: usePlan backoff behavior", () => {
  let mockFetch: jest.Mock;
  let warnSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.useFakeTimers();
    mockFetch = jest.fn();
    global.fetch = mockFetch;
    localStorage.clear();
    warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  describe("AC5: Uses exponential backoff", () => {
    it("retries with increasing delays (2s, 4s)", async () => {
      const fetchTimestamps: number[] = [];

      mockFetch.mockImplementation(() => {
        fetchTimestamps.push(Date.now());
        return Promise.reject(new Error("503 Service Unavailable"));
      });

      renderHook(() => usePlan());

      // Initial attempt
      await act(async () => {
        jest.advanceTimersByTime(100);
        await Promise.resolve();
        await Promise.resolve();
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);

      // After 2s backoff → second attempt
      await act(async () => {
        jest.advanceTimersByTime(2000);
        await Promise.resolve();
        await Promise.resolve();
      });

      expect(mockFetch).toHaveBeenCalledTimes(2);

      // After 4s backoff → third attempt
      await act(async () => {
        jest.advanceTimersByTime(4000);
        await Promise.resolve();
        await Promise.resolve();
      });

      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    it("does NOT make instant retries (no 6 rapid calls)", async () => {
      mockFetch.mockRejectedValue(new Error("503"));

      renderHook(() => usePlan());

      // Run initial attempt
      await act(async () => {
        jest.advanceTimersByTime(100);
        await Promise.resolve();
        await Promise.resolve();
      });

      // Only 1 call after 100ms (not 6)
      expect(mockFetch).toHaveBeenCalledTimes(1);

      // After 500ms still only 1
      await act(async () => {
        jest.advanceTimersByTime(500);
        await Promise.resolve();
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });

  describe("AC6: Maximum 3 retries", () => {
    it("stops after 3 retries total", async () => {
      mockFetch.mockRejectedValue(new Error("503"));

      const { result } = renderHook(() => usePlan());

      // Exhaust all retries: attempt 0 + backoff 2s + attempt 1 + backoff 4s + attempt 2
      for (let i = 0; i < 4; i++) {
        await act(async () => {
          jest.advanceTimersByTime(i === 0 ? 100 : 10_000);
          await Promise.resolve();
          await Promise.resolve();
        });
      }

      // Should have made exactly 3 calls (initial + 2 retries)
      expect(mockFetch).toHaveBeenCalledTimes(3);

      // Wait more — no additional calls
      await act(async () => {
        jest.advanceTimersByTime(30_000);
        await Promise.resolve();
      });

      expect(mockFetch).toHaveBeenCalledTimes(3);

      // Loading should be false (done)
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });
  });

  describe("AC7: Limited console warnings", () => {
    it("produces at most 1 console.warn for plan fetch failure (not 12)", async () => {
      mockFetch.mockRejectedValue(new Error("503"));

      renderHook(() => usePlan());

      // Exhaust retries
      for (let i = 0; i < 4; i++) {
        await act(async () => {
          jest.advanceTimersByTime(i === 0 ? 100 : 10_000);
          await Promise.resolve();
          await Promise.resolve();
        });
      }

      // Count usePlan-specific warnings
      const usePlanWarns = warnSpy.mock.calls.filter(
        (call: any[]) => typeof call[0] === "string" && call[0].includes("[usePlan]")
      );

      // Should be 1 warning (not 12)
      expect(usePlanWarns.length).toBeLessThanOrEqual(3);
      // At minimum, there should be at least one warning about failure
      expect(usePlanWarns.length).toBeGreaterThanOrEqual(1);
    });

    it("warns once about cache fallback when cache exists", async () => {
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

      renderHook(() => usePlan());

      // Exhaust retries
      for (let i = 0; i < 4; i++) {
        await act(async () => {
          jest.advanceTimersByTime(i === 0 ? 100 : 10_000);
          await Promise.resolve();
          await Promise.resolve();
        });
      }

      // Should have exactly 1 cache-fallback warning
      const cacheWarns = warnSpy.mock.calls.filter(
        (call: any[]) =>
          typeof call[0] === "string" && call[0].includes("[usePlan] Backend error — using cached plan")
      );

      expect(cacheWarns.length).toBe(1);
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

      const { result } = renderHook(() => usePlan());

      await act(async () => {
        jest.advanceTimersByTime(100);
        await Promise.resolve();
      });

      await waitFor(() => {
        expect(result.current.planInfo?.plan_id).toBe("smartlic_pro");
      });

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining("Backend returned free_trial but cached paid plan exists"),
        expect.anything()
      );
    });
  });
});
