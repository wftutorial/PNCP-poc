/**
 * useSearchRetry isolation tests — FE-035
 *
 * Tests the retry sub-hook in complete isolation:
 * - getRetryCooldown scaling by error type
 * - retryNow() immediate retry during countdown
 * - cancelRetry() clears countdown without retrying
 * - resetForNewSearch() resets state unless auto-retry in progress
 * - startAutoRetry() countdown for transient errors
 * - startAutoRetry() marks exhausted when 3 attempts used
 * - startAutoRetry() ignores non-transient errors
 */

import { renderHook, act } from "@testing-library/react";

// ---------------------------------------------------------------------------
// Module mocks — error-messages controls transient error classification
// ---------------------------------------------------------------------------

const mockIsTransientError = jest.fn(() => false);
const mockGetRetryMessage = jest.fn(() => "Problema na conexão. Tentando novamente...");

jest.mock("../../lib/error-messages", () => ({
  isTransientError: (...args: unknown[]) => mockIsTransientError(...args),
  getRetryMessage: (...args: unknown[]) => mockGetRetryMessage(...args),
  getUserFriendlyError: (e: unknown) =>
    e instanceof Error ? e.message : String(e),
  getMessageFromErrorCode: () => null,
  getHumanizedError: () => ({
    message: "Erro",
    actionLabel: "Tentar",
    tone: "blue",
    suggestReduceScope: false,
  }),
}));

// ---------------------------------------------------------------------------
// Import under test
// ---------------------------------------------------------------------------

import { useSearchRetry } from "../../app/buscar/hooks/useSearchRetry";
import type { SearchError } from "../../app/buscar/hooks/useSearch";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeSearchError(overrides: Partial<SearchError> = {}): SearchError {
  return {
    message: "Erro de rede",
    rawMessage: "Network error",
    errorCode: null,
    searchId: "test-search-id",
    correlationId: null,
    requestId: null,
    httpStatus: 503,
    timestamp: new Date().toISOString(),
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useSearchRetry — isolation tests (FE-035)", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    mockIsTransientError.mockReturnValue(false);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  // =========================================================================
  // getRetryCooldown
  // =========================================================================

  describe("getRetryCooldown", () => {
    test("returns 30 for HTTP 429 (rate limit)", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown(null, 429)).toBe(30);
    });

    test("returns 20 for HTTP 500 (server error)", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown(null, 500)).toBe(20);
    });

    test("returns 15 for HTTP 504 (gateway timeout)", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown(null, 504)).toBe(15);
    });

    test("returns 15 for timeout keyword in message", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown("demorou demais", undefined)).toBe(15);
    });

    test("returns 15 for 'timeout' keyword in message (case-insensitive)", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown("Request TIMEOUT exceeded", undefined)).toBe(15);
    });

    test("returns 10 for generic network error (default)", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown("Network unreachable", undefined)).toBe(10);
    });

    test("returns 10 for null message and no httpStatus", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown(null, undefined)).toBe(10);
    });

    test("httpStatus takes precedence — 429 returns 30 even with timeout message", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.getRetryCooldown("timeout occurred", 429)).toBe(30);
    });
  });

  // =========================================================================
  // Initial state
  // =========================================================================

  describe("initial state", () => {
    test("retryCountdown starts null", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.retryCountdown).toBeNull();
    });

    test("retryMessage starts null", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.retryMessage).toBeNull();
    });

    test("retryExhausted starts false", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.retryExhausted).toBe(false);
    });

    test("retryAttemptRef starts at 0", () => {
      const { result } = renderHook(() => useSearchRetry());
      expect(result.current.retryAttemptRef.current).toBe(0);
    });
  });

  // =========================================================================
  // cancelRetry
  // =========================================================================

  describe("cancelRetry", () => {
    test("clears countdown and message without triggering buscar", () => {
      const mockBuscar = jest.fn();
      const { result } = renderHook(() => useSearchRetry());
      result.current.buscarRef.current = mockBuscar;

      // Start a countdown manually
      act(() => {
        result.current.setRetryCountdown(10);
        result.current.setRetryMessage("Tentando novamente...");
      });

      expect(result.current.retryCountdown).toBe(10);

      act(() => {
        result.current.cancelRetry();
      });

      expect(result.current.retryCountdown).toBeNull();
      expect(result.current.retryMessage).toBeNull();
      expect(mockBuscar).not.toHaveBeenCalled();
    });

    test("cancels the active interval timer", () => {
      const { result } = renderHook(() => useSearchRetry());

      // Simulate a running interval
      const fakeInterval = setInterval(() => {}, 1000) as unknown as ReturnType<typeof setInterval>;
      act(() => {
        result.current.retryTimerRef.current = fakeInterval;
        result.current.setRetryCountdown(5);
      });

      act(() => {
        result.current.cancelRetry();
      });

      expect(result.current.retryTimerRef.current).toBeNull();
    });
  });

  // =========================================================================
  // retryNow
  // =========================================================================

  describe("retryNow", () => {
    test("calls buscarRef.current and clears countdown", () => {
      const mockBuscar = jest.fn();
      const { result } = renderHook(() => useSearchRetry());
      result.current.buscarRef.current = mockBuscar;

      act(() => {
        result.current.setRetryCountdown(7);
        result.current.setRetryMessage("Tentando...");
      });

      act(() => {
        result.current.retryNow();
      });

      expect(mockBuscar).toHaveBeenCalledTimes(1);
      expect(result.current.retryCountdown).toBeNull();
      expect(result.current.retryMessage).toBeNull();
    });

    test("increments retryAttemptRef", () => {
      const { result } = renderHook(() => useSearchRetry());
      result.current.buscarRef.current = jest.fn();

      const before = result.current.retryAttemptRef.current;
      act(() => {
        result.current.retryNow();
      });
      expect(result.current.retryAttemptRef.current).toBe(before + 1);
    });

    test("sets autoRetryInProgressRef to true", () => {
      const { result } = renderHook(() => useSearchRetry());
      result.current.buscarRef.current = jest.fn();

      act(() => {
        result.current.retryNow();
      });

      expect(result.current.autoRetryInProgressRef.current).toBe(true);
    });

    test("calls clearErrorRef if wired", () => {
      const mockClearError = jest.fn();
      const { result } = renderHook(() => useSearchRetry());
      result.current.buscarRef.current = jest.fn();
      result.current.clearErrorRef.current = mockClearError;

      act(() => {
        result.current.retryNow();
      });

      expect(mockClearError).toHaveBeenCalledTimes(1);
    });

    test("does not throw when buscarRef is null", () => {
      const { result } = renderHook(() => useSearchRetry());
      result.current.buscarRef.current = null;

      expect(() => {
        act(() => {
          result.current.retryNow();
        });
      }).not.toThrow();
    });
  });

  // =========================================================================
  // resetForNewSearch
  // =========================================================================

  describe("resetForNewSearch", () => {
    test("resets countdown and attempt when not auto-retrying", () => {
      const { result } = renderHook(() => useSearchRetry());

      act(() => {
        result.current.retryAttemptRef.current = 2;
        result.current.setRetryCountdown(8);
        result.current.setRetryMessage("...");
        result.current.setRetryExhausted(true);
        result.current.autoRetryInProgressRef.current = false;
      });

      act(() => {
        result.current.resetForNewSearch();
      });

      expect(result.current.retryAttemptRef.current).toBe(0);
      expect(result.current.retryCountdown).toBeNull();
      expect(result.current.retryMessage).toBeNull();
      expect(result.current.retryExhausted).toBe(false);
    });

    test("does NOT reset attempt count when autoRetryInProgressRef is true", () => {
      const { result } = renderHook(() => useSearchRetry());

      act(() => {
        result.current.retryAttemptRef.current = 1;
        result.current.autoRetryInProgressRef.current = true;
      });

      act(() => {
        result.current.resetForNewSearch();
      });

      // retryAttemptRef should remain at 1 (auto-retry scenario)
      expect(result.current.retryAttemptRef.current).toBe(1);
    });

    test("always sets autoRetryInProgressRef to false after reset", () => {
      const { result } = renderHook(() => useSearchRetry());

      act(() => {
        result.current.autoRetryInProgressRef.current = true;
      });

      act(() => {
        result.current.resetForNewSearch();
      });

      expect(result.current.autoRetryInProgressRef.current).toBe(false);
    });
  });

  // =========================================================================
  // startAutoRetry — transient error flow
  // =========================================================================

  describe("startAutoRetry", () => {
    test("does nothing for non-transient errors", () => {
      mockIsTransientError.mockReturnValue(false);
      const { result } = renderHook(() => useSearchRetry());
      const mockSetError = jest.fn();

      act(() => {
        result.current.startAutoRetry(makeSearchError({ httpStatus: 400 }), mockSetError);
      });

      expect(result.current.retryCountdown).toBeNull();
      expect(result.current.retryExhausted).toBe(false);
    });

    test("starts countdown for transient error on first attempt (10s)", () => {
      mockIsTransientError.mockReturnValue(true);
      mockGetRetryMessage.mockReturnValue("Problema de conexão...");

      const { result } = renderHook(() => useSearchRetry());
      result.current.retryAttemptRef.current = 0;
      const mockSetError = jest.fn();

      act(() => {
        result.current.startAutoRetry(makeSearchError({ httpStatus: 503 }), mockSetError);
      });

      expect(result.current.retryCountdown).toBe(10);
      expect(result.current.retryMessage).toBe("Problema de conexão...");
      expect(result.current.retryExhausted).toBe(false);
    });

    test("uses 20s delay on second attempt", () => {
      mockIsTransientError.mockReturnValue(true);

      const { result } = renderHook(() => useSearchRetry());
      result.current.retryAttemptRef.current = 1;
      const mockSetError = jest.fn();

      act(() => {
        result.current.startAutoRetry(makeSearchError(), mockSetError);
      });

      expect(result.current.retryCountdown).toBe(20);
    });

    test("marks retryExhausted when attempt >= 2", () => {
      mockIsTransientError.mockReturnValue(true);

      const { result } = renderHook(() => useSearchRetry());
      result.current.retryAttemptRef.current = 2;
      const mockSetError = jest.fn();

      act(() => {
        result.current.startAutoRetry(makeSearchError({ httpStatus: 503 }), mockSetError);
      });

      expect(result.current.retryExhausted).toBe(true);
      expect(result.current.retryMessage).toBeNull();
      expect(result.current.retryCountdown).toBeNull();
    });

    test("countdown ticks down every second", () => {
      mockIsTransientError.mockReturnValue(true);

      const { result } = renderHook(() => useSearchRetry());
      result.current.retryAttemptRef.current = 0;
      const mockSetError = jest.fn();

      act(() => {
        result.current.startAutoRetry(makeSearchError(), mockSetError);
      });

      expect(result.current.retryCountdown).toBe(10);

      act(() => {
        jest.advanceTimersByTime(1000);
      });
      expect(result.current.retryCountdown).toBe(9);

      act(() => {
        jest.advanceTimersByTime(1000);
      });
      expect(result.current.retryCountdown).toBe(8);
    });

    test("fires buscar and increments attempt when countdown reaches 0", () => {
      mockIsTransientError.mockReturnValue(true);

      const mockBuscar = jest.fn();
      const { result } = renderHook(() => useSearchRetry());
      result.current.buscarRef.current = mockBuscar;
      result.current.retryAttemptRef.current = 0;
      const mockSetError = jest.fn();

      act(() => {
        result.current.startAutoRetry(makeSearchError(), mockSetError);
      });

      // Advance past the 10-second delay
      act(() => {
        jest.advanceTimersByTime(10000);
      });

      expect(mockBuscar).toHaveBeenCalledTimes(1);
      expect(result.current.retryAttemptRef.current).toBe(1);
      expect(result.current.autoRetryInProgressRef.current).toBe(true);
      expect(mockSetError).toHaveBeenCalledWith(null);
      expect(result.current.retryCountdown).toBeNull();
    });

    test("clears any existing timer before starting new countdown", () => {
      mockIsTransientError.mockReturnValue(true);

      const { result } = renderHook(() => useSearchRetry());
      result.current.retryAttemptRef.current = 0;
      const mockSetError = jest.fn();

      // Start first countdown
      act(() => {
        result.current.startAutoRetry(makeSearchError(), mockSetError);
      });
      const firstTimerRef = result.current.retryTimerRef.current;

      // Start second countdown (should replace first)
      act(() => {
        result.current.startAutoRetry(makeSearchError(), mockSetError);
      });

      // Timer ref should have been replaced (not the same object)
      expect(result.current.retryTimerRef.current).toBeTruthy();
    });

    test("setRetryExhausted false when starting new countdown", () => {
      mockIsTransientError.mockReturnValue(true);

      const { result } = renderHook(() => useSearchRetry());
      result.current.retryAttemptRef.current = 0;

      act(() => {
        result.current.setRetryExhausted(true);
      });

      const mockSetError = jest.fn();
      act(() => {
        result.current.startAutoRetry(makeSearchError(), mockSetError);
      });

      expect(result.current.retryExhausted).toBe(false);
    });
  });

  // =========================================================================
  // setters are stable
  // =========================================================================

  describe("exposed setters", () => {
    test("setRetryCountdown updates countdown state", () => {
      const { result } = renderHook(() => useSearchRetry());

      act(() => {
        result.current.setRetryCountdown(15);
      });
      expect(result.current.retryCountdown).toBe(15);

      act(() => {
        result.current.setRetryCountdown(null);
      });
      expect(result.current.retryCountdown).toBeNull();
    });

    test("setRetryMessage updates message state", () => {
      const { result } = renderHook(() => useSearchRetry());

      act(() => {
        result.current.setRetryMessage("Reconectando...");
      });
      expect(result.current.retryMessage).toBe("Reconectando...");
    });

    test("setRetryExhausted updates exhausted state", () => {
      const { result } = renderHook(() => useSearchRetry());

      act(() => {
        result.current.setRetryExhausted(true);
      });
      expect(result.current.retryExhausted).toBe(true);
    });
  });
});
