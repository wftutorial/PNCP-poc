/**
 * TD-006 AC4: Isolated test suite for useFetchWithBackoff hook.
 *
 * Covers:
 * - Success on first attempt
 * - Retry with exponential backoff on failure
 * - Max retries exhaustion
 * - Abort on unmount (cleanup)
 * - Manual retry resets state
 * - Timeout handling
 * - Disabled mode (enabled=false)
 * - Custom options (delays, multiplier)
 * - Generation tracking (stale callback rejection)
 */

import { renderHook, act, waitFor } from "@testing-library/react";
import { useFetchWithBackoff, BACKOFF_DEFAULTS } from "../../hooks/useFetchWithBackoff";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useFetchWithBackoff (isolated)", () => {
  // 1. Success on first attempt
  test("returns data on successful first fetch", async () => {
    const fetchFn = jest.fn(async (_signal: AbortSignal) => ({ value: 42 }));

    const { result } = renderHook(() =>
      useFetchWithBackoff(fetchFn, {
        initialDelayMs: 100,
        maxDelayMs: 1000,
        timeoutMs: 5000,
      })
    );

    // Initially loading
    expect(result.current.loading).toBe(true);

    // Resolve the promise
    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ value: 42 });
    expect(result.current.error).toBeNull();
    expect(result.current.retryCount).toBe(0);
    expect(result.current.hasExhaustedRetries).toBe(false);
    expect(fetchFn).toHaveBeenCalledTimes(1);
  });

  // 2. Retry on failure with backoff
  test("retries on failure and succeeds on second attempt", async () => {
    let callCount = 0;
    const fetchFn = jest.fn(async (_signal: AbortSignal) => {
      callCount++;
      if (callCount === 1) throw new Error("Network error");
      return { value: "ok" };
    });

    const { result } = renderHook(() =>
      useFetchWithBackoff(fetchFn, {
        initialDelayMs: 100,
        maxDelayMs: 1000,
        timeoutMs: 5000,
        maxRetries: 3,
      })
    );

    // First attempt fails
    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    await waitFor(() => {
      expect(result.current.error).toBe("Network error");
    });
    expect(result.current.retryCount).toBe(1);

    // Advance past backoff delay (100ms * 2^0 = 100ms)
    await act(async () => {
      await jest.advanceTimersByTimeAsync(150);
    });

    await waitFor(() => {
      expect(result.current.data).toEqual({ value: "ok" });
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.retryCount).toBe(0);
    expect(fetchFn).toHaveBeenCalledTimes(2);
  });

  // 3. Max retries exhaustion
  test("stops retrying after maxRetries and sets hasExhaustedRetries", async () => {
    const fetchFn = jest.fn(async (_signal: AbortSignal) => {
      throw new Error("Always fails");
    });

    const { result } = renderHook(() =>
      useFetchWithBackoff(fetchFn, {
        initialDelayMs: 50,
        maxDelayMs: 200,
        timeoutMs: 5000,
        maxRetries: 2,
      })
    );

    // Attempt 0 fails
    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    await waitFor(() => {
      expect(result.current.retryCount).toBe(1);
    });

    // Advance past backoff (50ms)
    await act(async () => {
      await jest.advanceTimersByTimeAsync(100);
    });

    // Attempt 1 fails — retryCount becomes 2, which >= maxRetries(2)
    await waitFor(() => {
      expect(result.current.hasExhaustedRetries).toBe(true);
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe("Always fails");
    expect(result.current.retryCount).toBe(2);
    expect(fetchFn).toHaveBeenCalledTimes(2);
  });

  // 4. Abort on unmount
  test("aborts in-flight request on unmount", async () => {
    const abortedSignals: boolean[] = [];
    const fetchFn = jest.fn(async (signal: AbortSignal) => {
      return new Promise<string>((resolve, reject) => {
        signal.addEventListener("abort", () => {
          abortedSignals.push(true);
          reject(new DOMException("Aborted", "AbortError"));
        });
        // Never resolves naturally
      });
    });

    const { unmount } = renderHook(() =>
      useFetchWithBackoff(fetchFn, { timeoutMs: 60000 })
    );

    // Give fetch a chance to start
    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    expect(fetchFn).toHaveBeenCalledTimes(1);

    // Unmount should abort
    unmount();

    expect(abortedSignals.length).toBeGreaterThanOrEqual(1);
  });

  // 5. Manual retry resets state
  test("manualRetry resets retryCount and fetches again", async () => {
    let callCount = 0;
    const fetchFn = jest.fn(async (_signal: AbortSignal) => {
      callCount++;
      if (callCount <= 3) throw new Error("Failing");
      return { recovered: true };
    });

    const { result } = renderHook(() =>
      useFetchWithBackoff(fetchFn, {
        initialDelayMs: 50,
        maxDelayMs: 200,
        timeoutMs: 5000,
        maxRetries: 2,
      })
    );

    // Exhaust all retries
    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });
    await act(async () => {
      await jest.advanceTimersByTimeAsync(100);
    });

    await waitFor(() => {
      expect(result.current.hasExhaustedRetries).toBe(true);
    });

    // Manual retry — callCount is now 3, next call (4th) will succeed
    callCount = 3;
    await act(async () => {
      result.current.manualRetry();
    });

    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    await waitFor(() => {
      expect(result.current.data).toEqual({ recovered: true });
    });

    expect(result.current.hasExhaustedRetries).toBe(false);
    expect(result.current.retryCount).toBe(0);
    expect(result.current.error).toBeNull();
  });

  // 6. Timeout handling
  test("times out and retries when fetch exceeds timeoutMs", async () => {
    const fetchFn = jest.fn(async (signal: AbortSignal) => {
      // Simulate a very slow request — wait for abort then throw timeout-like error
      return new Promise<string>((_resolve, reject) => {
        signal.addEventListener("abort", () => {
          reject(new Error("timeout"));
        });
      });
    });

    const { result } = renderHook(() =>
      useFetchWithBackoff(fetchFn, {
        initialDelayMs: 100,
        maxDelayMs: 500,
        timeoutMs: 200,
        maxRetries: 3,
      })
    );

    // Advance past the timeout (200ms)
    await act(async () => {
      await jest.advanceTimersByTimeAsync(250);
    });

    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
    });

    // After timeout, retryCount should be incremented
    expect(result.current.retryCount).toBeGreaterThanOrEqual(1);
  });

  // 7. Disabled mode
  test("does not fetch when enabled=false", async () => {
    const fetchFn = jest.fn(async () => "data");

    const { result } = renderHook(() =>
      useFetchWithBackoff(fetchFn, { enabled: false })
    );

    await act(async () => {
      await jest.advanceTimersByTimeAsync(100);
    });

    expect(fetchFn).not.toHaveBeenCalled();
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
  });

  // 8. Custom backoff options
  test("respects custom initialDelayMs and backoffMultiplier", async () => {
    let callCount = 0;
    const fetchFn = jest.fn(async (_signal: AbortSignal) => {
      callCount++;
      if (callCount <= 2) throw new Error("Fail");
      return "success";
    });

    renderHook(() =>
      useFetchWithBackoff(fetchFn, {
        initialDelayMs: 200,
        backoffMultiplier: 3,
        maxDelayMs: 10000,
        timeoutMs: 5000,
        maxRetries: 5,
      })
    );

    // First attempt fails immediately
    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    expect(fetchFn).toHaveBeenCalledTimes(1);

    // Backoff for attempt 0: 200 * 3^0 = 200ms
    await act(async () => {
      await jest.advanceTimersByTimeAsync(250);
    });

    expect(fetchFn).toHaveBeenCalledTimes(2);

    // Second attempt also fails, backoff for attempt 1: 200 * 3^1 = 600ms
    await act(async () => {
      await jest.advanceTimersByTimeAsync(650);
    });

    expect(fetchFn).toHaveBeenCalledTimes(3);
  });

  // 9. maxDelayMs caps the backoff
  test("caps backoff delay at maxDelayMs", async () => {
    const fetchFn = jest.fn(async () => {
      throw new Error("Fail");
    });

    renderHook(() =>
      useFetchWithBackoff(fetchFn, {
        initialDelayMs: 1000,
        backoffMultiplier: 10,
        maxDelayMs: 500,
        timeoutMs: 5000,
        maxRetries: 3,
      })
    );

    // First attempt
    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    // Calculated: 1000 * 10^0 = 1000, but capped at 500
    // So after 500ms + buffer, next attempt should fire
    await act(async () => {
      await jest.advanceTimersByTimeAsync(550);
    });

    expect(fetchFn).toHaveBeenCalledTimes(2);
  });

  // 10. BACKOFF_DEFAULTS are correct
  test("exports correct default values", () => {
    expect(BACKOFF_DEFAULTS.maxRetries).toBe(5);
    expect(BACKOFF_DEFAULTS.initialDelayMs).toBe(2000);
    expect(BACKOFF_DEFAULTS.maxDelayMs).toBe(30000);
    expect(BACKOFF_DEFAULTS.backoffMultiplier).toBe(2);
    expect(BACKOFF_DEFAULTS.timeoutMs).toBe(10000);
  });

  // 11. Re-fetch when fetchFn changes
  test("re-fetches when fetchFn reference changes", async () => {
    const fetchFn1 = jest.fn(async () => "first");
    const fetchFn2 = jest.fn(async () => "second");

    const { result, rerender } = renderHook(
      ({ fn }) => useFetchWithBackoff(fn, { initialDelayMs: 50, timeoutMs: 5000 }),
      { initialProps: { fn: fetchFn1 } }
    );

    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    await waitFor(() => {
      expect(result.current.data).toBe("first");
    });

    // Change fetchFn
    rerender({ fn: fetchFn2 });

    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    await waitFor(() => {
      expect(result.current.data).toBe("second");
    });

    expect(fetchFn2).toHaveBeenCalled();
  });

  // 12. AbortError from cancellation is silently ignored
  test("ignores AbortError from cancellation (not timeout)", async () => {
    const fetchFn = jest.fn(async (signal: AbortSignal) => {
      return new Promise<string>((_resolve, reject) => {
        signal.addEventListener("abort", () => {
          reject(new DOMException("Aborted", "AbortError"));
        });
      });
    });

    const { result, unmount } = renderHook(() =>
      useFetchWithBackoff(fetchFn, { timeoutMs: 60000, maxRetries: 3 })
    );

    await act(async () => {
      await jest.advanceTimersByTimeAsync(0);
    });

    unmount();

    // Should not set error from our own cancellation
    // (unmount sets mountedRef=false so state updates are ignored)
    expect(result.current.error).toBeNull();
  });
});
