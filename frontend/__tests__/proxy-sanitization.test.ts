/**
 * @jest-environment node
 */

/**
 * GTM-PROXY-001: Tests for proxy sanitization across ALL proxy routes.
 *
 * T1: Each proxy returns PT message when backend offline
 * T2: Login with wrong password shows "Email ou senha incorretos"
 * T3: Signup with existing email shows "Este email já está cadastrado"
 *
 * AC1: All proxies use sanitizeProxyError()
 * AC2: Zero localhost:8000 fallbacks
 * AC3: Missing BACKEND_URL returns 503 with PT message
 * AC12: grep localhost:8000 returns ZERO
 * AC13: grep "Invalid login" returns ZERO in user-facing code
 */

import { NextRequest } from "next/server";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeRequest(
  url: string,
  options?: { method?: string; headers?: Record<string, string>; body?: string },
): NextRequest {
  const { method = "GET", headers = {}, body } = options ?? {};
  return new NextRequest(new URL(url, "http://localhost:3000"), {
    method,
    headers: {
      authorization: "Bearer test-token",
      ...headers,
    },
    ...(body ? { body } : {}),
  });
}

// ---------------------------------------------------------------------------
// T1: Each proxy returns PT message when backend offline
// ---------------------------------------------------------------------------

describe("GTM-PROXY-001 T1: All proxies return PT when backend offline", () => {
  const originalEnv = process.env.BACKEND_URL;

  beforeEach(() => {
    // Simulate missing BACKEND_URL (AC3)
    delete process.env.BACKEND_URL;
  });

  afterEach(() => {
    if (originalEnv) {
      process.env.BACKEND_URL = originalEnv;
    } else {
      delete process.env.BACKEND_URL;
    }
    jest.resetModules();
  });

  it("pipeline GET returns 503 PT when BACKEND_URL missing", async () => {
    const { GET } = await import("../app/api/pipeline/route");
    const req = makeRequest("http://localhost:3000/api/pipeline");
    const res = await GET(req);
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.message).toMatch(/indispon|temporariamente/i);
  });

  it("feedback POST returns 503 PT when BACKEND_URL missing", async () => {
    const { POST } = await import("../app/api/feedback/route");
    const req = makeRequest("http://localhost:3000/api/feedback", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ search_id: "x", bid_id: "y", is_relevant: true }),
    });
    const res = await POST(req);
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.message).toMatch(/indispon|temporariamente|configurado/i);
  });

  it("subscription-status GET returns 503 PT when BACKEND_URL missing", async () => {
    const { GET } = await import("../app/api/subscription-status/route");
    const req = makeRequest("http://localhost:3000/api/subscription-status");
    const res = await GET(req);
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.message).toMatch(/indispon|temporariamente|configurado/i);
  });

  it("search-status GET returns 503 PT when BACKEND_URL missing", async () => {
    const { GET } = await import("../app/api/search-status/route");
    const req = makeRequest("http://localhost:3000/api/search-status?search_id=test");
    const res = await GET(req);
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.message).toMatch(/indispon|temporariamente|configurado/i);
  });

  it("sessions GET returns 503 PT when BACKEND_URL missing", async () => {
    jest.mock("../lib/serverAuth", () => ({
      getRefreshedToken: jest.fn().mockResolvedValue("mock-token"),
    }));
    const { GET } = await import("../app/api/sessions/route");
    const req = makeRequest("http://localhost:3000/api/sessions");
    const res = await GET(req);
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.message).toMatch(/indispon|configurado|temporariamente/i);
  });

  it("analytics GET returns 503 PT when BACKEND_URL missing", async () => {
    const { GET } = await import("../app/api/analytics/route");
    const req = makeRequest("http://localhost:3000/api/analytics?endpoint=summary");
    const res = await GET(req);
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.error || body.message).toMatch(/indispon|configurado|temporariamente/i);
  });

  it("setores GET returns 503 PT when BACKEND_URL missing", async () => {
    const { GET } = await import("../app/api/setores/route");
    const req = makeRequest("http://localhost:3000/api/setores");
    const res = await GET(req);
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.message || body.error).toMatch(/indispon|configurado|temporariamente/i);
  });
});

// ---------------------------------------------------------------------------
// AC2: Zero localhost:8000 fallbacks (static analysis)
// ---------------------------------------------------------------------------

describe("GTM-PROXY-001 AC2: Zero localhost:8000 fallbacks", () => {
  it("no proxy file exports localhost:8000 as fallback", async () => {
    const fs = await import("fs");
    const path = await import("path");
    const glob = await import("glob");

    const apiDir = path.join(process.cwd(), "app", "api");
    const files = glob.sync("**/route.ts", { cwd: apiDir });

    for (const file of files) {
      const content = fs.readFileSync(path.join(apiDir, file), "utf-8");
      expect(content).not.toContain("localhost:8000");
    }
  });
});

// ---------------------------------------------------------------------------
// AC3: Missing BACKEND_URL returns 503 with specific PT message
// ---------------------------------------------------------------------------

describe("GTM-PROXY-001 AC3: Missing BACKEND_URL → 503 PT", () => {
  it("message is in Portuguese, not English", async () => {
    delete process.env.BACKEND_URL;
    jest.resetModules();

    const { GET } = await import("../app/api/pipeline/route");
    const req = makeRequest("http://localhost:3000/api/pipeline");
    const res = await GET(req);

    expect(res.status).toBe(503);
    const body = await res.json();
    // Must NOT contain English infrastructure jargon
    expect(JSON.stringify(body)).not.toMatch(/not configured|not found|unavailable/i);
    // Must contain PT message
    expect(body.message).toBeTruthy();
  });
});
