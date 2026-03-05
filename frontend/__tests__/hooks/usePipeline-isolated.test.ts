/**
 * TD-006 AC3: Isolated test suite for usePipeline hook.
 *
 * Covers:
 * - fetchItems success and error
 * - fetchItems with stage filter
 * - addItem success, 409 conflict, 403 pipeline limit
 * - updateItem success, 409 version conflict
 * - removeItem success and error
 * - fetchAlerts success and silent fail
 * - Auth headers sent correctly
 * - Loading states
 */

import { renderHook, act, waitFor } from "@testing-library/react";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockSession = { access_token: "pipeline-test-token" };

jest.mock("../../app/components/AuthProvider", () => ({
  useAuth: () => ({ session: mockSession }),
}));

jest.mock("../../lib/error-messages", () => ({
  getUserFriendlyError: (e: unknown) =>
    e instanceof Error ? e.message : String(e),
  getMessageFromErrorCode: jest.fn(() => null),
  isTransientError: jest.fn(() => false),
  getRetryMessage: jest.fn(() => "Tentando novamente..."),
  getHumanizedError: jest.fn(() => ({
    message: "Erro",
    actionLabel: "Tentar novamente",
    tone: "blue" as const,
    suggestReduceScope: false,
  })),
  getErrorMessage: jest.fn((e: any) => (typeof e === "string" ? e : "Erro")),
  DEFAULT_ERROR_MESSAGE: "Ocorreu um erro inesperado.",
  TRANSIENT_HTTP_CODES: new Set([502, 503, 504]),
  translateAuthError: jest.fn((e: string) => e),
}));

const mockFetch = jest.fn();
global.fetch = mockFetch;

// ---------------------------------------------------------------------------
// Import under test
// ---------------------------------------------------------------------------

import { usePipeline } from "../../hooks/usePipeline";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makePipelineItem(overrides: Record<string, unknown> = {}) {
  return {
    id: "item-1",
    user_id: "user-1",
    pncp_id: "pncp-123",
    objeto: "Teste de licitacao",
    orgao: "Orgao X",
    uf: "SP",
    valor_estimado: 50000,
    data_encerramento: "2026-04-01",
    link_pncp: "https://pncp.gov.br/123",
    stage: "descoberta",
    notes: null,
    created_at: "2026-03-01T00:00:00Z",
    updated_at: "2026-03-01T00:00:00Z",
    version: 1,
    ...overrides,
  };
}

beforeEach(() => {
  mockFetch.mockReset();
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("usePipeline (isolated)", () => {
  // 1. fetchItems success
  test("fetchItems loads items and total", async () => {
    const items = [makePipelineItem(), makePipelineItem({ id: "item-2" })];
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items, total: 2 }),
    });

    const { result } = renderHook(() => usePipeline());

    await act(async () => {
      await result.current.fetchItems();
    });

    expect(result.current.items).toHaveLength(2);
    expect(result.current.total).toBe(2);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  // 2. fetchItems with stage filter
  test("fetchItems passes stage parameter", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [], total: 0 }),
    });

    const { result } = renderHook(() => usePipeline());

    await act(async () => {
      await result.current.fetchItems("analise");
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("stage=analise"),
      expect.any(Object)
    );
  });

  // 3. fetchItems error
  test("fetchItems sets error on failure", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: "Internal server error" }),
    });

    const { result } = renderHook(() => usePipeline());

    await act(async () => {
      await result.current.fetchItems();
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.items).toEqual([]);
    expect(result.current.loading).toBe(false);
  });

  // 4. addItem success
  test("addItem adds new item to state", async () => {
    const newItem = makePipelineItem({ id: "new-1" });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => newItem,
    });

    const { result } = renderHook(() => usePipeline());

    let returned: any;
    await act(async () => {
      returned = await result.current.addItem({
        pncp_id: "pncp-new",
        objeto: "Nova licitacao",
        orgao: "Orgao Y",
        uf: "RJ",
        valor_estimado: 100000,
        data_encerramento: "2026-05-01",
        link_pncp: null,
        stage: "descoberta",
        notes: null,
      });
    });

    expect(returned).toEqual(newItem);
    expect(result.current.items).toContainEqual(newItem);
    expect(mockFetch).toHaveBeenCalledWith("/api/pipeline", expect.objectContaining({
      method: "POST",
    }));
  });

  // 5. addItem 409 conflict (duplicate)
  test("addItem throws on 409 conflict", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: async () => ({ detail: "Duplicate" }),
    });

    const { result } = renderHook(() => usePipeline());

    await expect(
      act(async () => {
        await result.current.addItem({
          pncp_id: "pncp-dup",
          objeto: "Duplicata",
          orgao: null,
          uf: null,
          valor_estimado: null,
          data_encerramento: null,
          link_pncp: null,
          stage: "descoberta",
          notes: null,
        });
      })
    ).rejects.toThrow("Esta licita\u00e7\u00e3o j\u00e1 est\u00e1 no seu pipeline.");
  });

  // 6. addItem 403 pipeline limit exceeded
  test("addItem throws with pipeline limit info on 403", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: async () => ({
        detail: {
          error_code: "PIPELINE_LIMIT_EXCEEDED",
          limit: 50,
          current: 50,
          message: "Limit reached",
        },
      }),
    });

    const { result } = renderHook(() => usePipeline());

    let caughtError: any;
    try {
      await act(async () => {
        await result.current.addItem({
          pncp_id: "pncp-over",
          objeto: "Over limit",
          orgao: null,
          uf: null,
          valor_estimado: null,
          data_encerramento: null,
          link_pncp: null,
          stage: "descoberta",
          notes: null,
        });
      });
    } catch (err) {
      caughtError = err;
    }

    expect(caughtError).toBeDefined();
    expect(caughtError.isPipelineLimitExceeded).toBe(true);
    expect(caughtError.limit).toBe(50);
    expect(caughtError.current).toBe(50);
  });

  // 7. updateItem success
  test("updateItem updates item in state", async () => {
    // First load items
    const item1 = makePipelineItem({ id: "item-1", stage: "descoberta", version: 1 });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [item1], total: 1 }),
    });

    const { result } = renderHook(() => usePipeline());

    await act(async () => {
      await result.current.fetchItems();
    });

    // Now update
    const updatedItem = { ...item1, stage: "analise", version: 2 };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => updatedItem,
    });

    let returned: any;
    await act(async () => {
      returned = await result.current.updateItem("item-1", { stage: "analise" as any });
    });

    expect(returned.stage).toBe("analise");
    expect(result.current.items[0].stage).toBe("analise");
  });

  // 8. updateItem 409 version conflict
  test("updateItem throws on 409 version conflict", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: async () => ({ detail: "Version mismatch" }),
    });

    const { result } = renderHook(() => usePipeline());

    let caughtError: any;
    try {
      await act(async () => {
        await result.current.updateItem("item-1", { stage: "analise" as any });
      });
    } catch (err) {
      caughtError = err;
    }

    expect(caughtError).toBeDefined();
    expect(caughtError.isConflict).toBe(true);
  });

  // 9. removeItem success
  test("removeItem removes item from state", async () => {
    // Load initial items
    const item1 = makePipelineItem({ id: "item-1" });
    const item2 = makePipelineItem({ id: "item-2" });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [item1, item2], total: 2 }),
    });

    const { result } = renderHook(() => usePipeline());

    await act(async () => {
      await result.current.fetchItems();
    });

    expect(result.current.items).toHaveLength(2);

    // Remove item-1
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    await act(async () => {
      await result.current.removeItem("item-1");
    });

    expect(result.current.items).toHaveLength(1);
    expect(result.current.items[0].id).toBe("item-2");
  });

  // 10. removeItem error
  test("removeItem throws on failure", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: "Delete failed" }),
    });

    const { result } = renderHook(() => usePipeline());

    await expect(
      act(async () => {
        await result.current.removeItem("item-1");
      })
    ).rejects.toThrow("Delete failed");
  });

  // 11. fetchAlerts success
  test("fetchAlerts loads alerts", async () => {
    const alertItem = makePipelineItem({ id: "alert-1", stage: "analise" });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [alertItem] }),
    });

    const { result } = renderHook(() => usePipeline());

    await act(async () => {
      await result.current.fetchAlerts();
    });

    expect(result.current.alerts).toHaveLength(1);
    expect(result.current.alerts[0].id).toBe("alert-1");
  });

  // 12. fetchAlerts silent fail
  test("fetchAlerts silently fails on error", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => usePipeline());

    // Should not throw
    await act(async () => {
      await result.current.fetchAlerts();
    });

    expect(result.current.alerts).toEqual([]);
  });

  // 13. Auth headers
  test("sends Authorization header with session token", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [], total: 0 }),
    });

    const { result } = renderHook(() => usePipeline());

    await act(async () => {
      await result.current.fetchItems();
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer pipeline-test-token",
          "Content-Type": "application/json",
        }),
      })
    );
  });

  // 14. Loading state during fetch
  test("sets loading during fetchItems", async () => {
    let resolvePromise: Function;
    mockFetch.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolvePromise = () =>
            resolve({
              ok: true,
              json: async () => ({ items: [], total: 0 }),
            });
        })
    );

    const { result } = renderHook(() => usePipeline());

    act(() => {
      result.current.fetchItems();
    });

    expect(result.current.loading).toBe(true);

    await act(async () => {
      resolvePromise!();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });
});
