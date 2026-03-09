/**
 * useSearchExport isolation tests — FE-035
 *
 * Tests the export sub-hook in isolation:
 * - handleDownload: success with download_url, success with download_id,
 *   missing download info error, 401 redirect, 404 expired, network error
 * - handleRegenerateExcel: queued 202, ready inline, 404 expired, 500 failure,
 *   network error, blocked after 2 failures
 * - handleExcelFailure: toast dedup, Mixpanel events, result status update
 * - Excel polling: starts when SSE disconnected + processing, stops on resolve
 */

import { renderHook, act, waitFor } from "@testing-library/react";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockTrackEvent = jest.fn();
jest.mock("../../hooks/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent: mockTrackEvent }),
}));

jest.mock("sonner", () => ({
  toast: { success: jest.fn(), error: jest.fn(), info: jest.fn() },
}));

jest.mock("../../lib/error-messages", () => ({
  getUserFriendlyError: (e: unknown) =>
    e instanceof Error ? e.message : String(e),
  getMessageFromErrorCode: () => null,
  isTransientError: () => false,
  getRetryMessage: () => "Tentando novamente...",
  getHumanizedError: () => ({
    message: "Erro",
    actionLabel: "Tentar",
    tone: "blue",
    suggestReduceScope: false,
  }),
}));

jest.mock("../../lib/utils/correlationId", () => ({
  getCorrelationId: () => "test-correlation-id",
  logCorrelatedRequest: jest.fn(),
}));

jest.mock("../../lib/config", () => ({
  APP_NAME: "SmartLic",
}));

// ---------------------------------------------------------------------------
// DOM environment helpers
// ---------------------------------------------------------------------------

// URL.createObjectURL / revokeObjectURL are not available in jsdom
beforeAll(() => {
  global.URL.createObjectURL = jest.fn(() => "blob:mock-url");
  global.URL.revokeObjectURL = jest.fn();
});

// ---------------------------------------------------------------------------
// Import under test
// ---------------------------------------------------------------------------

import { useSearchExport } from "../../app/buscar/hooks/useSearchExport";
import type { BuscaResult } from "../../app/types";

const { toast: mockToast } = require("sonner");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

type BuscaResultPartial = Partial<BuscaResult>;

function makeBuscaResult(overrides: BuscaResultPartial = {}): BuscaResult {
  return {
    resumo: {
      resumo_executivo: "Teste",
      total_oportunidades: 2,
      valor_total: 50000,
      destaques: [],
      recomendacoes: [],
      alertas_urgencia: [],
      insight_setorial: "",
    } as BuscaResult["resumo"],
    licitacoes: [{ pncp_id: "lic-1" } as BuscaResult["licitacoes"][0]],
    total_raw: 5,
    total_filtrado: 2,
    excel_available: false,
    quota_used: 1,
    quota_remaining: 9,
    response_state: "live" as const,
    ...overrides,
  } as BuscaResult;
}

function makeParams(overrides: Record<string, unknown> = {}) {
  const excelFailCountRef = { current: 0 };
  const excelToastFiredRef = { current: false };
  const asyncSearchIdRef = { current: null as string | null };
  const setResult = jest.fn();

  return {
    result: makeBuscaResult({ download_id: "dl-test-123" }),
    setResult,
    searchId: "search-id-123",
    asyncSearchIdRef,
    sseDisconnected: false,
    sseAvailable: true,
    loading: false,
    session: { access_token: "test-token" },
    sectorName: "Vestuário",
    dataInicial: "2026-01-01",
    dataFinal: "2026-01-15",
    excelFailCountRef,
    excelToastFiredRef,
    _excelFailCountRef: excelFailCountRef,
    _excelToastFiredRef: excelToastFiredRef,
    _asyncSearchIdRef: asyncSearchIdRef,
    ...overrides,
  };
}

function mockFetch(data: unknown, status = 200, isBlob = false) {
  global.fetch = jest.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    blob: () => Promise.resolve(new Blob(["xlsx-content"], { type: "application/vnd.ms-excel" })),
    headers: { get: jest.fn(() => null) },
  } as unknown as Response);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useSearchExport — isolation tests (FE-035)", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // =========================================================================
  // handleDownload — no download info
  // =========================================================================

  describe("handleDownload — validation", () => {
    test("sets downloadError when neither download_id nor download_url present", async () => {
      const params = makeParams({
        result: makeBuscaResult({ download_id: undefined, download_url: undefined }),
      });
      const { result } = renderHook(() =>
        useSearchExport(params as any)
      );

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(result.current.downloadError).toBe(
        "Excel ainda não disponível. Faça uma nova análise para gerar a planilha."
      );
    });

    test("does not call fetch when no download info", async () => {
      const params = makeParams({
        result: makeBuscaResult({ download_id: undefined }),
      });
      const fetchSpy = jest.fn();
      global.fetch = fetchSpy;

      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(fetchSpy).not.toHaveBeenCalled();
    });
  });

  // =========================================================================
  // handleDownload — success with download_id
  // =========================================================================

  describe("handleDownload — success with download_id", () => {
    test("calls /api/download?id=... and triggers blob download", async () => {
      mockFetch({}, 200, true);

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      // Mock document.createElement for anchor
      const mockAnchor = {
        href: "",
        download: "",
        style: { display: "" },
        click: jest.fn(),
      };
      jest.spyOn(document, "createElement").mockReturnValue(mockAnchor as any);
      jest.spyOn(document.body, "appendChild").mockImplementation(() => mockAnchor as any);
      jest.spyOn(document.body, "removeChild").mockImplementation(() => mockAnchor as any);

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/download?id=dl-test-123"),
        expect.any(Object)
      );
      expect(result.current.downloadLoading).toBe(false);
      expect(result.current.downloadError).toBeNull();
      expect(mockTrackEvent).toHaveBeenCalledWith("download_completed", expect.any(Object));
    });
  });

  // =========================================================================
  // handleDownload — success with download_url
  // =========================================================================

  describe("handleDownload — success with download_url", () => {
    test("uses /api/download?url=... when download_url present", async () => {
      mockFetch({}, 200, true);

      const params = makeParams({
        result: makeBuscaResult({
          download_url: "https://storage.example.com/file.xlsx",
          download_id: undefined,
        }),
      });
      const { result } = renderHook(() => useSearchExport(params as any));

      const mockAnchor = {
        href: "",
        download: "",
        style: { display: "" },
        click: jest.fn(),
      };
      jest.spyOn(document, "createElement").mockReturnValue(mockAnchor as any);
      jest.spyOn(document.body, "appendChild").mockImplementation(() => mockAnchor as any);
      jest.spyOn(document.body, "removeChild").mockImplementation(() => mockAnchor as any);

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("url="),
        expect.any(Object)
      );
    });
  });

  // =========================================================================
  // handleDownload — error responses
  // =========================================================================

  describe("handleDownload — error responses", () => {
    test("sets error on 404 (file expired)", async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({}),
      } as unknown as Response);

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(result.current.downloadError).toContain("expirado");
    });

    test("sets error on generic failure", async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({}),
      } as unknown as Response);

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(result.current.downloadError).toBeTruthy();
    });

    test("sets error on network failure", async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error("Network failure"));

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(result.current.downloadError).toBeTruthy();
    });

    test("downloadLoading resets to false after error", async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error("fail"));

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(result.current.downloadLoading).toBe(false);
    });

    test("tracks download_started before fetch", async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error("fail"));

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleDownload();
      });

      expect(mockTrackEvent).toHaveBeenCalledWith("download_started", expect.any(Object));
    });
  });

  // =========================================================================
  // handleExcelFailure
  // =========================================================================

  describe("handleExcelFailure", () => {
    test("increments excelFailCountRef on each call", () => {
      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      act(() => {
        result.current.handleExcelFailure(false);
      });
      expect((params as any).excelFailCountRef.current).toBe(1);

      act(() => {
        result.current.handleExcelFailure(false);
      });
      expect((params as any).excelFailCountRef.current).toBe(2);
    });

    test("fires toast.error on first failure (dedup ref false)", () => {
      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      act(() => {
        result.current.handleExcelFailure(false);
      });

      expect(mockToast.error).toHaveBeenCalledWith(
        "Não foi possível gerar o Excel. Você pode tentar novamente."
      );
    });

    test("does not fire initial toast when excelToastFiredRef is already true", () => {
      const params = makeParams();
      (params as any).excelToastFiredRef.current = true;
      const { result } = renderHook(() => useSearchExport(params as any));

      act(() => {
        result.current.handleExcelFailure(false);
      });

      expect(mockToast.error).not.toHaveBeenCalledWith(
        "Não foi possível gerar o Excel. Você pode tentar novamente."
      );
    });

    test("shows detailed toast on second regenerate failure", () => {
      const params = makeParams();
      (params as any).excelToastFiredRef.current = true;
      (params as any).excelFailCountRef.current = 1; // Already 1 failure

      const { result } = renderHook(() => useSearchExport(params as any));

      act(() => {
        result.current.handleExcelFailure(true);
      });

      expect(mockToast.error).toHaveBeenCalledWith(
        "Excel indisponível. Tente novamente em alguns instantes ou faça uma nova busca."
      );
    });

    test("fires excel_generation_failed Mixpanel event", () => {
      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      act(() => {
        result.current.handleExcelFailure(false);
      });

      expect(mockTrackEvent).toHaveBeenCalledWith(
        "excel_generation_failed",
        expect.objectContaining({ attempt_number: 1 })
      );
    });

    test("updates result excel_status to failed", () => {
      const setResult = jest.fn();
      const params = makeParams({ setResult });
      const { result } = renderHook(() => useSearchExport(params as any));

      act(() => {
        result.current.handleExcelFailure(false);
      });

      // setResult called with an updater function
      expect(setResult).toHaveBeenCalled();
      const updater = setResult.mock.calls[0][0];
      const prevResult = makeBuscaResult({ excel_status: "processing" as any });
      const updated = updater(prevResult);
      expect(updated.excel_status).toBe("failed");
    });
  });

  // =========================================================================
  // handleRegenerateExcel
  // =========================================================================

  describe("handleRegenerateExcel", () => {
    test("sets error when no searchId available", async () => {
      const params = makeParams({ searchId: null });
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      expect(result.current.downloadError).toBe("Sem ID de análise para regenerar Excel.");
    });

    test("is blocked when excelFailCount >= 2", async () => {
      const params = makeParams();
      (params as any).excelFailCountRef.current = 2;
      const fetchSpy = jest.fn();
      global.fetch = fetchSpy;

      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      expect(fetchSpy).not.toHaveBeenCalled();
    });

    test("handles 404 response (expired results)", async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({}),
      } as unknown as Response);

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      expect(result.current.downloadError).toContain("expirados");
    });

    test("handles generic failure response", async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({}),
      } as unknown as Response);

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      expect(result.current.downloadError).toBe("Erro ao regenerar Excel. Tente novamente.");
    });

    test("handles inline ready result (excel_status: ready)", async () => {
      const setResult = jest.fn();
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            excel_status: "ready",
            download_url: "https://storage.example.com/result.xlsx",
          }),
      } as unknown as Response);

      const params = makeParams({ setResult });
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      // setResult should have been called with a function that updates download_url
      expect(setResult).toHaveBeenCalled();
      // failCount reset
      expect((params as any).excelFailCountRef.current).toBe(0);
    });

    test("handles 202 queued response (waits for polling)", async () => {
      const setResult = jest.fn();
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 202,
        json: () => Promise.resolve({ excel_status: "processing" }),
      } as unknown as Response);

      const params = makeParams({ setResult });
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      // Result should now have excel_status = processing (set at start)
      expect(setResult).toHaveBeenCalled();
      // No error set
      expect(result.current.downloadError).toBeNull();
    });

    test("handles network error", async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error("Network error"));

      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      expect(result.current.downloadError).toBe("Erro de rede ao regenerar Excel.");
    });

    test("uses asyncSearchIdRef when available", async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 202,
        json: () => Promise.resolve({ excel_status: "processing" }),
      } as unknown as Response);

      const params = makeParams();
      (params as any).asyncSearchIdRef.current = "async-search-456";

      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await result.current.handleRegenerateExcel();
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("async-search-456"),
        expect.any(Object)
      );
    });
  });

  // =========================================================================
  // Excel polling — effect behavior
  // =========================================================================

  describe("Excel polling (SSE disconnected)", () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test("does not poll when SSE is available and not disconnected", () => {
      const fetchSpy = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
      } as unknown as Response);
      global.fetch = fetchSpy;

      const params = makeParams({
        result: makeBuscaResult({ excel_status: "processing" as any }),
        sseDisconnected: false,
        sseAvailable: true,
        loading: false,
      });

      renderHook(() => useSearchExport(params as any));

      // Immediate poll check shouldn't fire
      expect(fetchSpy).not.toHaveBeenCalled();
    });

    test("polls when SSE disconnected and excel_status is processing", async () => {
      const fetchSpy = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ excel_url: null }),
      } as unknown as Response);
      global.fetch = fetchSpy;

      const params = makeParams({
        result: makeBuscaResult({
          excel_status: "processing" as any,
          download_url: undefined,
          download_id: undefined,
        }),
        sseDisconnected: true,
        sseAvailable: false,
        loading: false,
      });

      renderHook(() => useSearchExport(params as any));

      // Wait for the immediate poll
      await act(async () => {
        await Promise.resolve();
      });

      expect(fetchSpy).toHaveBeenCalledWith(
        expect.stringContaining("/api/search-status"),
        expect.any(Object)
      );
    });

    test("stops polling when excel_url returned from poll", async () => {
      const setResult = jest.fn();
      const fetchSpy = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ excel_url: "https://storage.example.com/done.xlsx" }),
      } as unknown as Response);
      global.fetch = fetchSpy;

      const params = makeParams({
        result: makeBuscaResult({
          excel_status: "processing" as any,
          download_url: undefined,
          download_id: undefined,
        }),
        sseDisconnected: true,
        sseAvailable: false,
        loading: false,
        setResult,
      });

      const { result } = renderHook(() => useSearchExport(params as any));

      await act(async () => {
        await Promise.resolve();
      });

      expect(setResult).toHaveBeenCalled();
      // After resolution, interval should be cleared
      expect(result.current.excelPollingRef.current).toBeNull();
    });

    test("stops polling after 12 attempts (max)", async () => {
      const fetchSpy = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ excel_url: null }),
      } as unknown as Response);
      global.fetch = fetchSpy;

      const params = makeParams({
        result: makeBuscaResult({
          excel_status: "processing" as any,
          download_url: undefined,
          download_id: undefined,
        }),
        sseDisconnected: true,
        sseAvailable: false,
        loading: false,
      });

      const { result } = renderHook(() => useSearchExport(params as any));

      // Fast-forward through 12 poll intervals (5s each = 60s)
      await act(async () => {
        jest.advanceTimersByTime(65000);
        await Promise.resolve();
      });

      // pollingCountRef should be at 12
      expect(result.current.excelPollingCountRef.current).toBe(12);
    });
  });

  // =========================================================================
  // setDownloadError
  // =========================================================================

  describe("setDownloadError", () => {
    test("can set and clear download error", () => {
      const params = makeParams();
      const { result } = renderHook(() => useSearchExport(params as any));

      act(() => {
        result.current.setDownloadError("Erro de teste");
      });
      expect(result.current.downloadError).toBe("Erro de teste");

      act(() => {
        result.current.setDownloadError(null);
      });
      expect(result.current.downloadError).toBeNull();
    });
  });
});
