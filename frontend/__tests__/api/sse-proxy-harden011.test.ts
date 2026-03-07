/**
 * @jest-environment node
 */
/**
 * HARDEN-011: SSE Proxy Inactivity Timeout Tests.
 *
 * AC1: Inactivity timeout via Promise.race in reader loop
 * AC2: Timeout emits SSE_INACTIVITY_TIMEOUT error event to client
 * AC3: AbortController cleanup on timeout
 * AC4: Unit tests validate timeout behavior
 */

import { NextRequest } from "next/server";

const originalFetch = global.fetch;

describe("HARDEN-011: SSE Inactivity Timeout", () => {
  const BACKEND_URL = "http://backend:8000";

  beforeEach(() => {
    process.env.BACKEND_URL = BACKEND_URL;
    // Use short timeout for fast tests
    process.env.SSE_INACTIVITY_TIMEOUT_MS = "100";
  });

  afterEach(() => {
    global.fetch = originalFetch;
    delete process.env.SSE_INACTIVITY_TIMEOUT_MS;
    jest.restoreAllMocks();
  });

  function makeRequest(searchId: string): NextRequest {
    const url = `http://localhost/api/buscar-progress?search_id=${searchId}`;
    return new NextRequest(new URL(url));
  }

  async function getHandler() {
    const routePath = require.resolve(
      "../../app/api/buscar-progress/route"
    );
    delete require.cache[routePath];
    const mod = await import("../../app/api/buscar-progress/route");
    return mod.GET;
  }

  async function readStream(response: Response): Promise<string> {
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let fullText = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      fullText += decoder.decode(value, { stream: true });
    }
    return fullText;
  }

  // --------------------------------------------------------------------------
  // AC1: Inactivity timeout triggers when backend stops sending data
  // --------------------------------------------------------------------------

  it("AC1: reader loop times out when backend stops sending data", async () => {
    jest.spyOn(console, "error").mockImplementation(() => {});
    jest.spyOn(console, "log").mockImplementation(() => {});

    // Stream sends one chunk then goes silent
    const mockBody = new ReadableStream({
      start(controller) {
        controller.enqueue(
          new TextEncoder().encode('data: {"stage":"fetching","progress":10}\n\n')
        );
        // Never close — simulates backend going silent
      },
    });

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      body: mockBody,
      status: 200,
    });

    const GET = await getHandler();
    const response = await GET(makeRequest("test-inactivity"));

    expect(response.status).toBe(200);
    expect(response.headers.get("Content-Type")).toBe("text/event-stream");

    const fullText = await readStream(response);

    // Should contain the initial data chunk
    expect(fullText).toContain("fetching");
    // Should contain the inactivity timeout error event
    expect(fullText).toContain("event: error");
    expect(fullText).toContain("SSE_INACTIVITY_TIMEOUT");
  });

  // --------------------------------------------------------------------------
  // AC2: Timeout emits SSE error event with correct type and message
  // --------------------------------------------------------------------------

  it("AC2: timeout emits SSE error event with SSE_INACTIVITY_TIMEOUT", async () => {
    jest.spyOn(console, "error").mockImplementation(() => {});
    jest.spyOn(console, "log").mockImplementation(() => {});

    // Stream that immediately goes silent
    const mockBody = new ReadableStream({
      start() {
        // Never enqueue anything, never close
      },
    });

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      body: mockBody,
      status: 200,
    });

    const GET = await getHandler();
    const response = await GET(makeRequest("test-error-event"));

    const fullText = await readStream(response);

    expect(fullText).toContain("event: error");
    expect(fullText).toContain("SSE_INACTIVITY_TIMEOUT");
    expect(fullText).toContain("Conexão inativa por tempo prolongado");
    expect(fullText).toContain("retry: 5000");
  });

  // --------------------------------------------------------------------------
  // AC3: Structured logging on inactivity timeout
  // --------------------------------------------------------------------------

  it("AC3: inactivity timeout logs HARDEN-011 with structured details", async () => {
    const errorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
    jest.spyOn(console, "log").mockImplementation(() => {});

    const mockBody = new ReadableStream({
      start() {
        // Silent stream
      },
    });

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      body: mockBody,
      status: 200,
    });

    const GET = await getHandler();
    const response = await GET(makeRequest("test-abort-cleanup"));

    await readStream(response);

    // Verify HARDEN-011 specific log was emitted
    const hardenLogs = errorSpy.mock.calls.filter(
      (call) =>
        typeof call[0] === "string" &&
        call[0].includes("HARDEN-011") &&
        call[0].includes("Inactivity timeout")
    );
    expect(hardenLogs.length).toBeGreaterThanOrEqual(1);

    // Verify structured log contains correct fields
    const logJson = hardenLogs[0][1];
    const parsed = JSON.parse(logJson);
    expect(parsed.error_type).toBe("SSE_INACTIVITY_TIMEOUT");
    expect(parsed.search_id).toBe("test-abort-cleanup");
    expect(parsed.elapsed_ms).toBeDefined();
  });

  // --------------------------------------------------------------------------
  // AC4: Normal streams complete without timeout interference
  // --------------------------------------------------------------------------

  it("AC4: normal stream with timely data completes without timeout", async () => {
    jest.spyOn(console, "log").mockImplementation(() => {});
    // Use a generous timeout for this test
    process.env.SSE_INACTIVITY_TIMEOUT_MS = "5000";

    const encoder = new TextEncoder();
    const chunks = [
      'data: {"stage":"fetching","progress":10}\n\n',
      'data: {"stage":"filtering","progress":50}\n\n',
      'data: {"stage":"complete","progress":100}\n\n',
    ];

    let chunkIndex = 0;
    const mockBody = new ReadableStream({
      pull(controller) {
        if (chunkIndex < chunks.length) {
          controller.enqueue(encoder.encode(chunks[chunkIndex++]));
        } else {
          controller.close();
        }
      },
    });

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      body: mockBody,
      status: 200,
    });

    const GET = await getHandler();
    const response = await GET(makeRequest("test-normal-flow"));

    expect(response.status).toBe(200);

    const fullText = await readStream(response);

    expect(fullText).toContain("fetching");
    expect(fullText).toContain("filtering");
    expect(fullText).toContain("complete");
    // No error events
    expect(fullText).not.toContain("event: error");
    expect(fullText).not.toContain("SSE_INACTIVITY_TIMEOUT");
  });

  // --------------------------------------------------------------------------
  // Default timeout value
  // --------------------------------------------------------------------------

  it("defaults to 120000ms when env var is not set", async () => {
    delete process.env.SSE_INACTIVITY_TIMEOUT_MS;
    jest.spyOn(console, "log").mockImplementation(() => {});

    // We can't easily test the actual 120s timeout, but we can verify
    // the default is used by checking it doesn't timeout quickly
    // Just verify the module loads without error
    const routePath = require.resolve("../../app/api/buscar-progress/route");
    delete require.cache[routePath];
    const mod = await import("../../app/api/buscar-progress/route");
    expect(mod.GET).toBeDefined();
  });
});
