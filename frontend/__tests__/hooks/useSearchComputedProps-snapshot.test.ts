/**
 * DEBT-202 AC: Snapshot test for searchResultsProps.
 *
 * Validates that useSearchComputedProps produces a stable, well-shaped object.
 * The snapshot acts as a safety net: any unintended structural change (added/removed
 * prop, type drift) will fail this test, catching regressions from the
 * useSearchOrchestration decomposition.
 */

import { renderHook } from "@testing-library/react";
import { useSearchComputedProps } from "../../app/buscar/hooks/useSearchComputedProps";

// ---------------------------------------------------------------------------
// Minimal mock factories
// ---------------------------------------------------------------------------

function makeMockSearch() {
  return {
    result: null,
    rawCount: 0,
    filterSummary: null,
    pendingReviewUpdate: null,
    zeroMatchProgress: null,
    loading: false,
    loadingStep: 0,
    statesProcessed: 0,
    sseEvent: null,
    useRealProgress: false,
    sseAvailable: false,
    sseDisconnected: false,
    isReconnecting: false,
    isDegraded: false,
    degradedDetail: null,
    skeletonTimeoutReached: false,
    ufStatuses: new Map(),
    ufTotalFound: 0,
    ufAllComplete: false,
    sourceStatuses: new Map(),
    partialProgress: null,
    error: null,
    quotaError: null,
    downloadLoading: false,
    downloadError: null,
    excelFailCount: 0,
    liveFetchInProgress: false,
    refreshAvailable: null,
    retryCountdown: null,
    retryMessage: null,
    retryExhausted: false,
    searchId: "test-search-id",
    cancelSearch: jest.fn(),
    buscar: jest.fn(),
    buscarForceFresh: jest.fn(),
    handleDownload: jest.fn(),
    handleRegenerateExcel: jest.fn(),
    viewPartialResults: jest.fn(),
    handleRefreshResults: jest.fn(),
    retryNow: jest.fn(),
    cancelRetry: jest.fn(),
    estimateSearchTime: jest.fn().mockReturnValue(30),
    setResult: jest.fn(),
    setError: jest.fn(),
    // unused in computed props but part of UseSearchReturn
    loadingStepLabel: "",
    searchButtonRef: { current: null },
    showSaveDialog: false,
    setShowSaveDialog: jest.fn(),
    saveSearchName: "",
    setSaveSearchName: jest.fn(),
    saveError: null,
    isMaxCapacity: false,
    handleSaveSearch: jest.fn(),
    confirmSaveSearch: jest.fn(),
    handleLoadSearch: jest.fn(),
    handleRefresh: jest.fn(),
    getRetryCooldown: jest.fn().mockReturnValue(0),
    restoreSearchStateOnMount: jest.fn(),
    pendingReviewCount: 0,
  };
}

function makeMockFilters() {
  return {
    ufsSelecionadas: new Set(["SP", "RJ"]),
    sectorName: "Software & TI",
    searchMode: "setor" as const,
    termosArray: [],
    ordenacao: "data_publicacao_desc" as const,
    status: "todas" as const,
    dataInicial: "2026-01-01",
    dataFinal: "2026-03-30",
    setorId: "software-ti",
    setOrdenacao: jest.fn(),
    setUfsSelecionadas: jest.fn(),
    setDataInicial: jest.fn(),
    setDataFinal: jest.fn(),
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useSearchComputedProps — searchResultsProps snapshot", () => {
  it("produces a stable props object with expected shape (no-result state)", () => {
    const search = makeMockSearch() as any;
    const filters = makeMockFilters() as any;
    const mockSession = { access_token: "test-token" };

    const { result } = renderHook(() =>
      useSearchComputedProps({
        search,
        filters,
        billing: { planInfo: null, trialPhase: "trial" },
        session: mockSession,
        isTrialExpiredOrQuota: false,
        isProfileComplete: true,
        searchElapsed: 0,
        partialDismissed: false,
        lastSearchAvailable: false,
        pdfLoading: false,
        handleShowUpgradeModal: jest.fn(),
        handleLoadLastSearch: jest.fn(),
        handleRetryWithUfs: jest.fn(),
        startResultsTour: jest.fn(),
        isResultsTourCompleted: jest.fn().mockReturnValue(false),
        setPdfModalOpen: jest.fn(),
        setPartialDismissed: jest.fn(),
        trackEvent: jest.fn(),
      })
    );

    const props = result.current.searchResultsProps;

    // Structural snapshot — verifies all expected keys are present with correct types.
    // Callbacks are replaced with "[Function]" for stable snapshots.
    const serializable = Object.fromEntries(
      Object.entries(props).map(([k, v]) =>
        typeof v === "function" ? [k, "[Function]"] :
        v instanceof Map ? [k, `Map(${v.size})`] :
        v instanceof Set ? [k, `Set(${v.size})`] :
        [k, v]
      )
    );

    expect(serializable).toMatchSnapshot();
  });

  it("reflects loading=true correctly", () => {
    const search = { ...makeMockSearch(), loading: true, loadingStep: 2 } as any;
    const filters = makeMockFilters() as any;

    const { result } = renderHook(() =>
      useSearchComputedProps({
        search,
        filters,
        billing: { planInfo: null, trialPhase: "none" },
        session: null,
        isTrialExpiredOrQuota: false,
        isProfileComplete: false,
        searchElapsed: 15,
        partialDismissed: false,
        lastSearchAvailable: false,
        pdfLoading: false,
        handleShowUpgradeModal: jest.fn(),
        handleLoadLastSearch: jest.fn(),
        handleRetryWithUfs: jest.fn(),
        startResultsTour: jest.fn(),
        isResultsTourCompleted: jest.fn().mockReturnValue(false),
        setPdfModalOpen: jest.fn(),
        setPartialDismissed: jest.fn(),
        trackEvent: jest.fn(),
      })
    );

    const props = result.current.searchResultsProps;
    expect(props.loading).toBe(true);
    expect(props.loadingStep).toBe(2);
    expect(props.searchElapsedSeconds).toBe(15);
  });

  it("trial expired flag propagates to searchResultsProps", () => {
    const search = makeMockSearch() as any;
    const filters = makeMockFilters() as any;

    const { result } = renderHook(() =>
      useSearchComputedProps({
        search,
        filters,
        billing: { planInfo: null, trialPhase: "expired" },
        session: null,
        isTrialExpiredOrQuota: true,
        isProfileComplete: false,
        searchElapsed: 0,
        partialDismissed: false,
        lastSearchAvailable: false,
        pdfLoading: false,
        handleShowUpgradeModal: jest.fn(),
        handleLoadLastSearch: jest.fn(),
        handleRetryWithUfs: jest.fn(),
        startResultsTour: jest.fn(),
        isResultsTourCompleted: jest.fn().mockReturnValue(false),
        setPdfModalOpen: jest.fn(),
        setPartialDismissed: jest.fn(),
        trackEvent: jest.fn(),
      })
    );

    expect(result.current.searchResultsProps.isTrialExpired).toBe(true);
    expect(result.current.searchResultsProps.trialPhase).toBe("expired");
  });
});
