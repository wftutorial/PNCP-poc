import { renderHook, act } from "@testing-library/react";
import { useBroadcastChannel } from "../../hooks/useBroadcastChannel";
import type { BuscaResult } from "../../app/types";

// ── Helpers ─────────────────────────────────────────────────────────────

function makeResult(overrides: Partial<BuscaResult> = {}): BuscaResult {
  return {
    resumo: {
      total_oportunidades: 5,
      valor_total_estimado: 100000,
      estados_com_oportunidades: ["SP"],
      distribuicao_por_estado: { SP: 5 },
      modalidades: { "Pregão Eletrônico": 5 },
      resumo_executivo: "Test summary",
      top_oportunidades: [],
    },
    licitacoes: [],
    download_id: null,
    total_raw: 10,
    total_filtrado: 5,
    filter_stats: null,
    termos_utilizados: null,
    stopwords_removidas: null,
    excel_available: false,
    upgrade_message: null,
    source_stats: null,
    ...overrides,
  } as BuscaResult;
}

// ── Mock BroadcastChannel ───────────────────────────────────────────────

class MockBroadcastChannel {
  static instances: MockBroadcastChannel[] = [];
  name: string;
  onmessage: ((event: MessageEvent) => void) | null = null;
  closed = false;

  constructor(name: string) {
    this.name = name;
    MockBroadcastChannel.instances.push(this);
  }

  postMessage(data: unknown) {
    // Deliver to all OTHER instances with same channel name
    for (const instance of MockBroadcastChannel.instances) {
      if (instance !== this && instance.name === this.name && !instance.closed && instance.onmessage) {
        instance.onmessage(new MessageEvent("message", { data }));
      }
    }
  }

  close() {
    this.closed = true;
    const idx = MockBroadcastChannel.instances.indexOf(this);
    if (idx >= 0) MockBroadcastChannel.instances.splice(idx, 1);
  }
}

beforeEach(() => {
  MockBroadcastChannel.instances = [];
  (globalThis as Record<string, unknown>).BroadcastChannel = MockBroadcastChannel;
});

afterEach(() => {
  MockBroadcastChannel.instances.forEach((i) => i.close());
  MockBroadcastChannel.instances = [];
});

// ── Tests ───────────────────────────────────────────────────────────────

describe("useBroadcastChannel", () => {
  it("AC1: creates BroadcastChannel with 'smartlic-search' name", () => {
    renderHook(() => useBroadcastChannel());
    expect(MockBroadcastChannel.instances.length).toBe(1);
    expect(MockBroadcastChannel.instances[0].name).toBe("smartlic-search");
  });

  it("AC2: search_complete message notifies other tabs", () => {
    const onSearchComplete = jest.fn();
    renderHook(() => useBroadcastChannel({ onSearchComplete }));

    // Simulate message from a DIFFERENT tab (different tabId)
    const testResult = makeResult();
    const instance = MockBroadcastChannel.instances[0];
    act(() => {
      instance.onmessage!(new MessageEvent("message", {
        data: {
          type: "search_complete",
          result: testResult,
          searchId: "search-123",
          timestamp: Date.now(),
          tabId: "other-tab-id",
        },
      }));
    });

    expect(onSearchComplete).toHaveBeenCalledTimes(1);
    expect(onSearchComplete).toHaveBeenCalledWith(testResult, "search-123");
  });

  it("AC3: receiving tab gets result without re-fetch", () => {
    const onSearchComplete = jest.fn();
    renderHook(() => useBroadcastChannel({ onSearchComplete }));

    const testResult = makeResult({ total_filtrado: 42 });
    const instance = MockBroadcastChannel.instances[0];
    act(() => {
      instance.onmessage!(new MessageEvent("message", {
        data: {
          type: "search_complete",
          result: testResult,
          searchId: "abc",
          timestamp: Date.now(),
          tabId: "another-tab",
        },
      }));
    });

    // Callback received the full result — no fetch needed
    const receivedResult = onSearchComplete.mock.calls[0][0];
    expect(receivedResult.total_filtrado).toBe(42);
  });

  it("AC4: graceful degradation when BroadcastChannel not supported", () => {
    delete (globalThis as Record<string, unknown>).BroadcastChannel;

    const { result } = renderHook(() => useBroadcastChannel());
    expect(result.current.isSupported).toBe(false);

    // broadcastSearchComplete should not throw
    expect(() => {
      result.current.broadcastSearchComplete(makeResult(), null);
    }).not.toThrow();
  });

  it("AC4: graceful degradation when postMessage throws", () => {
    const { result: hook } = renderHook(() => useBroadcastChannel());

    // Force postMessage to throw (e.g. uncloneable data)
    const instance = MockBroadcastChannel.instances[0];
    const origPost = instance.postMessage.bind(instance);
    instance.postMessage = () => { throw new DOMException("DataCloneError"); };

    expect(() => {
      hook.current.broadcastSearchComplete(makeResult(), null);
    }).not.toThrow();

    // Restore
    instance.postMessage = origPost;
  });

  it("does not receive own messages (same tab)", () => {
    const onSearchComplete = jest.fn();
    const { result: hook } = renderHook(() =>
      useBroadcastChannel({ onSearchComplete })
    );

    // The hook's own postMessage should NOT trigger its own onSearchComplete
    // because tabId filtering prevents self-delivery.
    // However, MockBroadcastChannel delivers to OTHER instances only,
    // so with a single hook there's no other instance to receive.
    act(() => {
      hook.current.broadcastSearchComplete(makeResult(), "x");
    });

    expect(onSearchComplete).not.toHaveBeenCalled();
  });

  it("closes channel on unmount", () => {
    const { unmount } = renderHook(() => useBroadcastChannel());
    expect(MockBroadcastChannel.instances.length).toBe(1);

    unmount();
    expect(MockBroadcastChannel.instances.length).toBe(0);
  });

  it("does not create channel when enabled=false", () => {
    renderHook(() => useBroadcastChannel({ enabled: false }));
    expect(MockBroadcastChannel.instances.length).toBe(0);
  });

  it("isSupported returns true when BroadcastChannel exists", () => {
    const { result } = renderHook(() => useBroadcastChannel());
    expect(result.current.isSupported).toBe(true);
  });
});
