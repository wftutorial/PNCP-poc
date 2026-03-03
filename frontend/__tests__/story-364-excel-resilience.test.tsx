/**
 * STORY-364: Excel Resilience Tests
 *
 * Tests:
 *  T1 (AC9/AC4): Excel polling starts when excel_status is 'processing' and SSE disconnected
 *  T2 (AC5): Polling updates result when excel_url is returned
 *  T3 (AC6): Polling stops after 12 attempts
 *  T4 (AC10/AC7): "Gerar novamente" button calls onRegenerateExcel
 *  T5 (AC11): excelTimedOut timer does NOT fire if download_url is present
 *  T6: handleRegenerateExcel updates state correctly on success
 *  T7: handleRegenerateExcel handles 404 (expired results)
 */

import React from "react";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";

// ---- Module mocks (hoisted by Jest) ----

jest.mock("sonner", () => ({
  toast: { success: jest.fn(), error: jest.fn(), info: jest.fn() },
}));

jest.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(),
  useRouter: () => ({ push: jest.fn(), replace: jest.fn() }),
}));

jest.mock("../app/components/AuthProvider", () => ({
  useAuth: () => ({
    session: { access_token: "test-token-364", expires_at: Math.floor(Date.now() / 1000) + 3600 },
    user: null,
    loading: false,
  }),
}));

jest.mock("../hooks/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent: jest.fn() }),
}));

jest.mock("../hooks/useQuota", () => ({
  useQuota: () => ({ refresh: jest.fn() }),
}));

const mockUseSearchSSE = jest.fn();
jest.mock("../hooks/useSearchSSE", () => ({
  useSearchSSE: (...args: any[]) => mockUseSearchSSE(...args),
}));

jest.mock("../hooks/useSearchPolling", () => ({
  useSearchPolling: () => ({ asProgressEvent: null }),
}));

jest.mock("../hooks/useSavedSearches", () => ({
  useSavedSearches: () => ({ saveNewSearch: jest.fn(), isMaxCapacity: false }),
}));

jest.mock("../lib/error-messages", () => ({
  getUserFriendlyError: jest.fn((e: any) => (typeof e === "string" ? e : e?.message || "Error")),
  getMessageFromErrorCode: jest.fn(() => null),
  isTransientError: jest.fn(() => false),
  getRetryMessage: jest.fn(() => null),
  getHumanizedError: jest.fn(() => null),
  TRANSIENT_HTTP_CODES: new Set([502, 503, 504]),
  ERROR_CODE_MESSAGES: {},
  getErrorMessage: jest.fn(() => "Error"),
  DEFAULT_ERROR_MESSAGE: "Erro inesperado.",
}));

jest.mock("../lib/searchStatePersistence", () => ({
  saveSearchState: jest.fn(),
  restoreSearchState: jest.fn(() => null),
}));

jest.mock("../lib/lastSearchCache", () => ({
  saveLastSearch: jest.fn(),
}));

jest.mock("../lib/searchPartialCache", () => ({
  savePartialSearch: jest.fn(),
  recoverPartialSearch: jest.fn(() => null),
  clearPartialSearch: jest.fn(),
  cleanupExpiredPartials: jest.fn(),
}));

jest.mock("../lib/utils/correlationId", () => ({
  getCorrelationId: () => "test-correlation-364",
  logCorrelatedRequest: jest.fn(),
}));

jest.mock("../lib/utils/dateDiffInDays", () => ({
  dateDiffInDays: () => 10,
}));

// ---- Constants & helpers ----

const defaultSSEReturn = {
  currentEvent: null,
  sseAvailable: false,
  sseDisconnected: true,
  isReconnecting: false,
  isDegraded: false,
  degradedDetail: null,
  partialProgress: null,
  refreshAvailable: null,
  ufStatuses: new Map(),
  ufTotalFound: 0,
  ufAllComplete: false,
  batchProgress: null,
  sourceStatuses: new Map(),
  filterSummary: null,
  pendingReviewUpdate: null,
};

function makeFilters(overrides: Partial<any> = {}) {
  return {
    ufsSelecionadas: new Set(["SP"]),
    dataInicial: "2026-02-01",
    dataFinal: "2026-02-28",
    searchMode: "setor" as const,
    modoBusca: "abertas" as const,
    setorId: "vestuario",
    termosArray: [] as string[],
    status: "abertas" as any,
    modalidades: [] as number[],
    valorMin: null,
    valorMax: null,
    esferas: [] as any[],
    municipios: [] as any[],
    ordenacao: "relevancia" as const,
    sectorName: "Vestuario",
    canSearch: true,
    setOrdenacao: jest.fn(),
    setUfsSelecionadas: jest.fn(),
    setDataInicial: jest.fn(),
    setDataFinal: jest.fn(),
    setSearchMode: jest.fn(),
    setSetorId: jest.fn(),
    setTermosArray: jest.fn(),
    setStatus: jest.fn(),
    setModalidades: jest.fn(),
    setValorMin: jest.fn(),
    setValorMax: jest.fn(),
    setEsferas: jest.fn(),
    setMunicipios: jest.fn(),
    ...overrides,
  };
}

/**
 * Build a BuscaResult response for the /api/buscar mock.
 */
function makeBuscarResponse(overrides: Partial<any> = {}) {
  return {
    resumo: {
      resumo_executivo: "Test resumo.",
      total_oportunidades: 3,
      valor_total: 50000,
      destaques: ["Destaque 1"],
      alerta_urgencia: null,
      alertas_urgencia: null,
      recomendacoes: null,
      insight_setorial: null,
    },
    licitacoes: [
      {
        pncp_id: "bid-001",
        objeto: "Aquisicao de uniformes",
        orgao: "Prefeitura Municipal",
        uf: "SP",
        municipio: "Sao Paulo",
        valor: 50000,
        modalidade: "pregao",
        data_abertura: "2026-03-01",
        data_publicacao: "2026-02-15",
        situacao: "aberta",
        link: "https://pncp.gov.br/bid-001",
        match_details: null,
      },
    ],
    download_id: null,
    download_url: null,
    total_raw: 10,
    total_filtrado: 3,
    filter_stats: null,
    termos_utilizados: ["uniforme"],
    stopwords_removidas: null,
    excel_available: true,
    upgrade_message: null,
    sources_used: ["PNCP"],
    source_stats: null,
    hidden_by_min_match: null,
    filter_relaxed: null,
    metadata: null,
    is_partial: false,
    cached: false,
    is_truncated: false,
    excel_status: "processing",
    llm_status: "ready",
    ...overrides,
  };
}

/**
 * Creates a fetch mock that responds to /api/buscar with a result,
 * and to /api/search-status with a configurable response.
 */
function createFetchMock(options: {
  buscarResponse?: any;
  searchStatusResponses?: (() => any)[];
  regenerateResponse?: () => { ok: boolean; status: number; json: () => Promise<any> };
}) {
  const { buscarResponse, searchStatusResponses = [], regenerateResponse } = options;
  let searchStatusCallIndex = 0;

  return jest.fn().mockImplementation((url: string, init?: any) => {
    // /api/buscar — POST search
    if (typeof url === "string" && url.includes("/api/buscar")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        headers: { get: () => null },
        json: () => Promise.resolve(buscarResponse || makeBuscarResponse()),
      });
    }

    // /api/search-status — polling for Excel status
    if (typeof url === "string" && url.includes("/api/search-status")) {
      const idx = Math.min(searchStatusCallIndex, searchStatusResponses.length - 1);
      searchStatusCallIndex++;
      if (searchStatusResponses.length > 0 && idx >= 0) {
        const resp = searchStatusResponses[idx]();
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(resp),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ excel_status: "processing" }),
      });
    }

    // /api/regenerate-excel — regenerate Excel
    if (typeof url === "string" && url.includes("/api/regenerate-excel")) {
      if (regenerateResponse) {
        const resp = regenerateResponse();
        return Promise.resolve(resp);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ excel_status: "ready", download_url: "https://regen.example.com/test.xlsx" }),
      });
    }

    // /api/v1/search/*/cancel — cancel search
    if (typeof url === "string" && url.includes("/cancel")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }

    // Default
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
}

// ===========================================================================
// T1 (AC9/AC4): Excel polling starts when excel_status is 'processing'
//               and SSE disconnected
// ===========================================================================

describe("T1 (AC9/AC4): Excel polling activation conditions", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockUseSearchSSE.mockReturnValue(defaultSSEReturn);
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  it("starts polling /api/search-status when excel_status='processing', no download_url, SSE disconnected, not loading", async () => {
    const fetchMock = createFetchMock({
      buscarResponse: makeBuscarResponse({ excel_status: "processing", download_url: null }),
    });
    global.fetch = fetchMock;

    const { useSearch } = require("../app/buscar/hooks/useSearch");

    function TestHarness() {
      const filters = makeFilters();
      const search = useSearch(filters);

      return (
        <div>
          <span data-testid="loading">{String(search.loading)}</span>
          <span data-testid="search-id">{search.searchId ?? "null"}</span>
          <span data-testid="excel-status">{search.result?.excel_status ?? "null"}</span>
          <button data-testid="search-btn" onClick={() => search.buscar()}>Search</button>
        </div>
      );
    }

    await act(async () => {
      render(<TestHarness />);
    });

    // Trigger the search
    await act(async () => {
      fireEvent.click(screen.getByTestId("search-btn"));
    });

    // Flush the buscar() async call (fetch, JSON parsing, state updates)
    await act(async () => {
      jest.advanceTimersByTime(200);
    });

    // Wait for buscar to complete (loading goes false, result is set)
    // The finally block keeps searchId alive because excel_status='processing'
    await act(async () => {
      jest.advanceTimersByTime(6000); // past SSE deferred cleanup (5s)
    });

    // Now the polling effect should have started since:
    // - result.excel_status === 'processing'
    // - result.download_url is null
    // - sseDisconnected is true (from mock)
    // - loading is false
    const searchStatusCalls = fetchMock.mock.calls.filter(
      (call: any[]) => typeof call[0] === "string" && call[0].includes("/api/search-status")
    );

    // Immediate poll + at least one interval poll should have fired
    expect(searchStatusCalls.length).toBeGreaterThanOrEqual(1);

    // Advance 5s to trigger the interval poll
    await act(async () => {
      jest.advanceTimersByTime(5000);
    });

    const searchStatusCallsAfter = fetchMock.mock.calls.filter(
      (call: any[]) => typeof call[0] === "string" && call[0].includes("/api/search-status")
    );

    expect(searchStatusCallsAfter.length).toBeGreaterThanOrEqual(2);
  });
});

// ===========================================================================
// T2 (AC5): Polling updates result when excel_url is returned
// ===========================================================================

describe("T2 (AC5): Excel polling updates result on excel_url", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockUseSearchSSE.mockReturnValue(defaultSSEReturn);
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  it("updates result with download_url and excel_status='ready' when API returns excel_url", async () => {
    const fetchMock = createFetchMock({
      buscarResponse: makeBuscarResponse({ excel_status: "processing", download_url: null }),
      searchStatusResponses: [
        // First poll: still processing
        () => ({ excel_status: "processing" }),
        // Second poll: ready with URL
        () => ({ excel_url: "https://storage.example.com/results/test-search.xlsx", excel_status: "ready" }),
      ],
    });
    global.fetch = fetchMock;

    const { useSearch } = require("../app/buscar/hooks/useSearch");

    function TestHarness() {
      const filters = makeFilters();
      const search = useSearch(filters);

      return (
        <div>
          <span data-testid="excel-status">{search.result?.excel_status ?? "null"}</span>
          <span data-testid="download-url">{search.result?.download_url ?? "null"}</span>
          <button data-testid="search-btn" onClick={() => search.buscar()}>Search</button>
        </div>
      );
    }

    await act(async () => {
      render(<TestHarness />);
    });

    // Trigger search
    await act(async () => {
      fireEvent.click(screen.getByTestId("search-btn"));
    });

    // Flush the buscar async + SSE deferred cleanup
    await act(async () => {
      jest.advanceTimersByTime(6200);
    });

    // First poll fires immediately on effect mount (returns processing)
    // Second poll fires at 5s interval (returns excel_url)
    await act(async () => {
      jest.advanceTimersByTime(5000);
    });

    await waitFor(() => {
      expect(screen.getByTestId("excel-status").textContent).toBe("ready");
      expect(screen.getByTestId("download-url").textContent).toBe(
        "https://storage.example.com/results/test-search.xlsx"
      );
    });
  });
});

// ===========================================================================
// T3 (AC6): Polling stops after 12 attempts
// ===========================================================================

describe("T3 (AC6): Excel polling stops after max 12 attempts", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockUseSearchSSE.mockReturnValue(defaultSSEReturn);
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  it("does not poll more than 12 times", async () => {
    let searchStatusPollCount = 0;
    const fetchMock = jest.fn().mockImplementation((url: string) => {
      if (typeof url === "string" && url.includes("/api/buscar")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: { get: () => null },
          json: () => Promise.resolve(makeBuscarResponse({ excel_status: "processing", download_url: null })),
        });
      }
      if (typeof url === "string" && url.includes("/api/search-status")) {
        searchStatusPollCount++;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ excel_status: "processing" }), // never returns excel_url
        });
      }
      if (typeof url === "string" && url.includes("/cancel")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    global.fetch = fetchMock;

    const { useSearch } = require("../app/buscar/hooks/useSearch");

    function TestHarness() {
      const filters = makeFilters();
      const search = useSearch(filters);

      return (
        <div>
          <span data-testid="excel-status">{search.result?.excel_status ?? "null"}</span>
          <button data-testid="search-btn" onClick={() => search.buscar()}>Search</button>
        </div>
      );
    }

    await act(async () => {
      render(<TestHarness />);
    });

    // Trigger search
    await act(async () => {
      fireEvent.click(screen.getByTestId("search-btn"));
    });

    // Flush buscar + SSE deferred cleanup
    await act(async () => {
      jest.advanceTimersByTime(6200);
    });

    // Reset counter after buscar has completed to only track polling calls
    const pollCountAfterBuscar = searchStatusPollCount;

    // Advance through 14 intervals (70s) to exceed the 12-poll limit
    for (let i = 0; i < 14; i++) {
      await act(async () => {
        jest.advanceTimersByTime(5000);
      });
    }

    const pollingCallsDuringPhase = searchStatusPollCount - pollCountAfterBuscar;

    // Should not exceed 12 polls (AC6)
    expect(pollingCallsDuringPhase).toBeLessThanOrEqual(12);

    // Record count at this point
    const countAtExhaustion = searchStatusPollCount;

    // Advance another 30s — no more polls should fire
    for (let i = 0; i < 6; i++) {
      await act(async () => {
        jest.advanceTimersByTime(5000);
      });
    }

    // No additional polls
    expect(searchStatusPollCount).toBe(countAtExhaustion);
  });
});

// ===========================================================================
// T4 (AC10/AC7): "Gerar novamente" button calls onRegenerateExcel
// ===========================================================================

describe("T4 (AC10/AC7): Gerar novamente button calls onRegenerateExcel", () => {
  it("renders retry button when excel_status is 'failed' and calls onRegenerateExcel on click", () => {
    const SearchResults = require("../app/buscar/components/SearchResults").default;

    const mockRegenerateExcel = jest.fn();
    const mockSearch = jest.fn();

    const resultWithFailedExcel = makeBuscarResponse({
      excel_status: "failed",
      download_url: null,
      download_id: null,
    });

    const baseProps = {
      loading: false,
      loadingStep: 0,
      estimatedTime: 0,
      stateCount: 0,
      statesProcessed: 0,
      onCancel: jest.fn(),
      sseEvent: null,
      useRealProgress: false,
      sseAvailable: false,
      onStageChange: jest.fn(),
      error: null,
      quotaError: null,
      result: resultWithFailedExcel,
      rawCount: 10,
      ufsSelecionadas: new Set(["SP"]),
      sectorName: "Vestuario",
      searchMode: "setor" as const,
      termosArray: [] as string[],
      ordenacao: "relevancia" as const,
      onOrdenacaoChange: jest.fn(),
      downloadLoading: false,
      downloadError: null,
      onDownload: jest.fn(),
      onSearch: mockSearch,
      onRegenerateExcel: mockRegenerateExcel,
      planInfo: {
        plan_id: "smartlic_pro",
        plan_name: "SmartLic Pro",
        quota_used: 5,
        quota_reset_date: "2026-03-01",
        capabilities: { max_history_days: 1825, max_requests_per_month: 1000, allow_excel: true },
      },
      session: { access_token: "test-token" },
      onShowUpgradeModal: jest.fn(),
      onTrackEvent: jest.fn(),
    };

    render(<SearchResults {...baseProps} />);

    const retryBtn = screen.getByTestId("excel-retry-button");
    expect(retryBtn).toBeInTheDocument();
    expect(retryBtn).toHaveTextContent("Gerar novamente");

    fireEvent.click(retryBtn);

    // Should call onRegenerateExcel, NOT onSearch
    expect(mockRegenerateExcel).toHaveBeenCalledTimes(1);
    expect(mockSearch).not.toHaveBeenCalled();
  });

  it("falls back to onSearch when onRegenerateExcel is not provided", () => {
    const SearchResults = require("../app/buscar/components/SearchResults").default;

    const mockSearch = jest.fn();

    const resultWithFailedExcel = makeBuscarResponse({
      excel_status: "failed",
      download_url: null,
      download_id: null,
    });

    const baseProps = {
      loading: false,
      loadingStep: 0,
      estimatedTime: 0,
      stateCount: 0,
      statesProcessed: 0,
      onCancel: jest.fn(),
      sseEvent: null,
      useRealProgress: false,
      sseAvailable: false,
      onStageChange: jest.fn(),
      error: null,
      quotaError: null,
      result: resultWithFailedExcel,
      rawCount: 10,
      ufsSelecionadas: new Set(["SP"]),
      sectorName: "Vestuario",
      searchMode: "setor" as const,
      termosArray: [] as string[],
      ordenacao: "relevancia" as const,
      onOrdenacaoChange: jest.fn(),
      downloadLoading: false,
      downloadError: null,
      onDownload: jest.fn(),
      onSearch: mockSearch,
      // onRegenerateExcel NOT provided
      planInfo: {
        plan_id: "smartlic_pro",
        plan_name: "SmartLic Pro",
        quota_used: 5,
        quota_reset_date: "2026-03-01",
        capabilities: { max_history_days: 1825, max_requests_per_month: 1000, allow_excel: true },
      },
      session: { access_token: "test-token" },
      onShowUpgradeModal: jest.fn(),
      onTrackEvent: jest.fn(),
    };

    render(<SearchResults {...baseProps} />);

    const retryBtn = screen.getByTestId("excel-retry-button");
    fireEvent.click(retryBtn);

    // Without onRegenerateExcel, fallback to onSearch
    expect(mockSearch).toHaveBeenCalledTimes(1);
  });
});

// ===========================================================================
// T5 (AC11): excelTimedOut timer does NOT fire if download_url is present
// ===========================================================================

describe("T5 (AC11): excelTimedOut timer does not fire when download_url present", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("does NOT set excelTimedOut when excel_status is 'processing' but download_url exists", async () => {
    const SearchResults = require("../app/buscar/components/SearchResults").default;

    // Result has excel_status='processing' but ALSO has download_url
    const resultWithUrl = makeBuscarResponse({
      excel_status: "processing",
      download_url: "https://storage.example.com/results/test.xlsx",
      download_id: null,
    });

    const baseProps = {
      loading: false,
      loadingStep: 0,
      estimatedTime: 0,
      stateCount: 0,
      statesProcessed: 0,
      onCancel: jest.fn(),
      sseEvent: null,
      useRealProgress: false,
      sseAvailable: false,
      onStageChange: jest.fn(),
      error: null,
      quotaError: null,
      result: resultWithUrl,
      rawCount: 10,
      ufsSelecionadas: new Set(["SP"]),
      sectorName: "Vestuario",
      searchMode: "setor" as const,
      termosArray: [] as string[],
      ordenacao: "relevancia" as const,
      onOrdenacaoChange: jest.fn(),
      downloadLoading: false,
      downloadError: null,
      onDownload: jest.fn(),
      onSearch: jest.fn(),
      planInfo: {
        plan_id: "smartlic_pro",
        plan_name: "SmartLic Pro",
        quota_used: 5,
        quota_reset_date: "2026-03-01",
        capabilities: { max_history_days: 1825, max_requests_per_month: 1000, allow_excel: true },
      },
      session: { access_token: "test-token" },
      onShowUpgradeModal: jest.fn(),
      onTrackEvent: jest.fn(),
    };

    render(<SearchResults {...baseProps} />);

    // Advance 61 seconds (past the 60s excelTimedOut threshold)
    await act(async () => {
      jest.advanceTimersByTime(61_000);
    });

    // The download button should be available (not the retry button),
    // because download_url is present so excelTimedOut condition does not trigger isFailed
    expect(screen.getByTestId("excel-download-button")).toBeInTheDocument();
    expect(screen.queryByTestId("excel-retry-button")).not.toBeInTheDocument();
  });

  it("DOES set excelTimedOut when excel_status is 'processing' and no download_url", async () => {
    const SearchResults = require("../app/buscar/components/SearchResults").default;

    const resultWithoutUrl = makeBuscarResponse({
      excel_status: "processing",
      download_url: null,
      download_id: null,
    });

    const baseProps = {
      loading: false,
      loadingStep: 0,
      estimatedTime: 0,
      stateCount: 0,
      statesProcessed: 0,
      onCancel: jest.fn(),
      sseEvent: null,
      useRealProgress: false,
      sseAvailable: false,
      onStageChange: jest.fn(),
      error: null,
      quotaError: null,
      result: resultWithoutUrl,
      rawCount: 10,
      ufsSelecionadas: new Set(["SP"]),
      sectorName: "Vestuario",
      searchMode: "setor" as const,
      termosArray: [] as string[],
      ordenacao: "relevancia" as const,
      onOrdenacaoChange: jest.fn(),
      downloadLoading: false,
      downloadError: null,
      onDownload: jest.fn(),
      onSearch: jest.fn(),
      planInfo: {
        plan_id: "smartlic_pro",
        plan_name: "SmartLic Pro",
        quota_used: 5,
        quota_reset_date: "2026-03-01",
        capabilities: { max_history_days: 1825, max_requests_per_month: 1000, allow_excel: true },
      },
      session: { access_token: "test-token" },
      onShowUpgradeModal: jest.fn(),
      onTrackEvent: jest.fn(),
    };

    render(<SearchResults {...baseProps} />);

    // Initially shows processing button
    expect(screen.getByTestId("excel-processing-button")).toBeInTheDocument();

    // Advance 61 seconds past the 60s timeout
    await act(async () => {
      jest.advanceTimersByTime(61_000);
    });

    // After timeout, excelTimedOut=true makes isFailed=true, showing retry button
    await waitFor(() => {
      expect(screen.getByTestId("excel-retry-button")).toBeInTheDocument();
    });
    expect(screen.queryByTestId("excel-processing-button")).not.toBeInTheDocument();
  });
});

// ===========================================================================
// T6: handleRegenerateExcel updates state correctly on success
// ===========================================================================

describe("T6: handleRegenerateExcel updates state on success", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockUseSearchSSE.mockReturnValue(defaultSSEReturn);
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  it("sets excel_status to 'ready' and download_url when regenerate returns inline result", async () => {
    // buscar returns excel_status='processing' so searchId stays alive (hasJobsRunning=true)
    const fetchMock = createFetchMock({
      buscarResponse: makeBuscarResponse({ excel_status: "processing", download_url: null }),
      regenerateResponse: () => ({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            excel_status: "ready",
            download_url: "https://storage.example.com/regenerated.xlsx",
          }),
      }),
    });
    global.fetch = fetchMock;

    const { useSearch } = require("../app/buscar/hooks/useSearch");

    function TestHarness() {
      const filters = makeFilters();
      const search = useSearch(filters);

      return (
        <div>
          <span data-testid="excel-status">{search.result?.excel_status ?? "null"}</span>
          <span data-testid="download-url">{search.result?.download_url ?? "null"}</span>
          <span data-testid="download-error">{search.downloadError ?? "null"}</span>
          <span data-testid="search-id">{search.searchId ?? "null"}</span>
          <button data-testid="search-btn" onClick={() => search.buscar()}>Search</button>
          <button data-testid="regenerate-btn" onClick={search.handleRegenerateExcel}>
            Regenerate
          </button>
        </div>
      );
    }

    await act(async () => {
      render(<TestHarness />);
    });

    // Run a search to set searchId (excel_status='processing' keeps it alive)
    await act(async () => {
      fireEvent.click(screen.getByTestId("search-btn"));
    });

    // Flush buscar async — short delay only, searchId stays because hasJobsRunning
    await act(async () => {
      jest.advanceTimersByTime(500);
    });

    // Verify searchId is set
    await waitFor(() => {
      expect(screen.getByTestId("search-id").textContent).not.toBe("null");
    });

    // Click regenerate
    await act(async () => {
      fireEvent.click(screen.getByTestId("regenerate-btn"));
    });

    // Flush the async regenerate call
    await act(async () => {
      jest.advanceTimersByTime(200);
    });

    await waitFor(() => {
      expect(screen.getByTestId("excel-status").textContent).toBe("ready");
      expect(screen.getByTestId("download-url").textContent).toBe(
        "https://storage.example.com/regenerated.xlsx"
      );
      expect(screen.getByTestId("download-error").textContent).toBe("null");
    });
  });
});

// ===========================================================================
// T7: handleRegenerateExcel handles 404 (expired results)
// ===========================================================================

describe("T7: handleRegenerateExcel handles 404 (expired results)", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockUseSearchSSE.mockReturnValue(defaultSSEReturn);
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  it("sets downloadError and excel_status='failed' on 404 response", async () => {
    // buscar returns excel_status='processing' so searchId stays alive
    const fetchMock = createFetchMock({
      buscarResponse: makeBuscarResponse({ excel_status: "processing", download_url: null }),
      regenerateResponse: () => ({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: "Search not found" }),
      }),
    });
    global.fetch = fetchMock;

    const { useSearch } = require("../app/buscar/hooks/useSearch");

    function TestHarness() {
      const filters = makeFilters();
      const search = useSearch(filters);

      return (
        <div>
          <span data-testid="excel-status">{search.result?.excel_status ?? "null"}</span>
          <span data-testid="download-error">{search.downloadError ?? "null"}</span>
          <span data-testid="search-id">{search.searchId ?? "null"}</span>
          <button data-testid="search-btn" onClick={() => search.buscar()}>Search</button>
          <button data-testid="regenerate-btn" onClick={search.handleRegenerateExcel}>
            Regenerate
          </button>
        </div>
      );
    }

    await act(async () => {
      render(<TestHarness />);
    });

    // Run search to set searchId (excel_status='processing' keeps it alive)
    await act(async () => {
      fireEvent.click(screen.getByTestId("search-btn"));
    });

    await act(async () => {
      jest.advanceTimersByTime(500);
    });

    // Verify searchId is alive
    await waitFor(() => {
      expect(screen.getByTestId("search-id").textContent).not.toBe("null");
    });

    // Click regenerate
    await act(async () => {
      fireEvent.click(screen.getByTestId("regenerate-btn"));
    });

    await act(async () => {
      jest.advanceTimersByTime(200);
    });

    await waitFor(() => {
      expect(screen.getByTestId("excel-status").textContent).toBe("failed");
      // "Resultados expirados. Faca uma nova busca."
      expect(screen.getByTestId("download-error").textContent).toContain("expirados");
    });
  });

  it("sets downloadError and excel_status='failed' on network error", async () => {
    // buscar returns excel_status='processing' so searchId stays alive;
    // regenerate-excel throws a network error.
    const fetchMock = jest.fn().mockImplementation((url: string) => {
      if (typeof url === "string" && url.includes("/api/buscar")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: { get: () => null },
          json: () => Promise.resolve(makeBuscarResponse({ excel_status: "processing", download_url: null })),
        });
      }
      if (typeof url === "string" && url.includes("/api/regenerate-excel")) {
        return Promise.reject(new Error("Network failure"));
      }
      if (typeof url === "string" && url.includes("/cancel")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      }
      if (typeof url === "string" && url.includes("/api/search-status")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ excel_status: "processing" }) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    global.fetch = fetchMock;

    const { useSearch } = require("../app/buscar/hooks/useSearch");

    function TestHarness() {
      const filters = makeFilters();
      const search = useSearch(filters);

      return (
        <div>
          <span data-testid="excel-status">{search.result?.excel_status ?? "null"}</span>
          <span data-testid="download-error">{search.downloadError ?? "null"}</span>
          <span data-testid="search-id">{search.searchId ?? "null"}</span>
          <button data-testid="search-btn" onClick={() => search.buscar()}>Search</button>
          <button data-testid="regenerate-btn" onClick={search.handleRegenerateExcel}>
            Regenerate
          </button>
        </div>
      );
    }

    await act(async () => {
      render(<TestHarness />);
    });

    // Run search to set searchId (excel_status='processing' keeps it alive)
    await act(async () => {
      fireEvent.click(screen.getByTestId("search-btn"));
    });

    await act(async () => {
      jest.advanceTimersByTime(500);
    });

    // Verify searchId is alive
    await waitFor(() => {
      expect(screen.getByTestId("search-id").textContent).not.toBe("null");
    });

    // Suppress expected console.error from the catch block
    const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    // Click regenerate
    await act(async () => {
      fireEvent.click(screen.getByTestId("regenerate-btn"));
    });

    await act(async () => {
      jest.advanceTimersByTime(200);
    });

    await waitFor(() => {
      expect(screen.getByTestId("excel-status").textContent).toBe("failed");
      // "Erro de rede ao regenerar Excel."
      expect(screen.getByTestId("download-error").textContent).toContain("rede");
    });

    consoleSpy.mockRestore();
  });
});
