/**
 * STORY-311 AC19: CSP violation report endpoint tests.
 *
 * Tests the /api/csp-report endpoint that collects Content-Security-Policy
 * violation reports from browsers.
 *
 * @jest-environment node
 */

import { POST } from "../app/api/csp-report/route";
import { NextRequest } from "next/server";

function createRequest(body: object, ip?: string): NextRequest {
  return new NextRequest("http://localhost:3000/api/csp-report", {
    method: "POST",
    body: JSON.stringify(body),
    headers: {
      "Content-Type": "application/json",
      ...(ip ? { "x-forwarded-for": ip } : {}),
    },
  });
}

describe("STORY-311 AC19: CSP Report Endpoint", () => {
  it("should accept valid legacy report-uri format", async () => {
    const req = createRequest(
      {
        "csp-report": {
          "document-uri": "https://smartlic.tech/buscar",
          "violated-directive": "script-src 'self'",
          "blocked-uri": "https://evil.com/script.js",
        },
      },
      "legacy-format-ip"
    );
    const resp = await POST(req);
    expect(resp.status).toBe(204);
  });

  it("should accept Reporting API v1 format", async () => {
    const req = createRequest(
      {
        documentURL: "https://smartlic.tech/buscar",
        violatedDirective: "script-src",
        blockedURL: "https://evil.com/script.js",
        disposition: "enforce",
      },
      "reporting-api-ip"
    );
    const resp = await POST(req);
    expect(resp.status).toBe(204);
  });

  it("should return 400 on invalid JSON", async () => {
    const req = new NextRequest("http://localhost:3000/api/csp-report", {
      method: "POST",
      body: "not valid json{",
      headers: { "Content-Type": "application/json" },
    });
    const resp = await POST(req);
    expect(resp.status).toBe(400);
  });

  it("should rate limit after 100 requests from same IP", async () => {
    const testIp = "test-rate-limit-ip";

    // Send 100 requests (all should succeed with 204)
    for (let i = 0; i < 100; i++) {
      const req = createRequest(
        { "csp-report": { "violated-directive": "test" } },
        testIp
      );
      const resp = await POST(req);
      expect(resp.status).toBe(204);
    }

    // 101st should be rate limited
    const req = createRequest(
      { "csp-report": { "violated-directive": "test" } },
      testIp
    );
    const resp = await POST(req);
    expect(resp.status).toBe(429);
  });

  it("should not rate limit different IPs independently", async () => {
    const ip1 = "test-ip-one";
    const ip2 = "test-ip-two";

    // IP1 sends 50 requests
    for (let i = 0; i < 50; i++) {
      const req = createRequest(
        { "csp-report": { "violated-directive": "test" } },
        ip1
      );
      await POST(req);
    }

    // IP2 should not be affected
    const req = createRequest(
      { "csp-report": { "violated-directive": "test" } },
      ip2
    );
    const resp = await POST(req);
    expect(resp.status).toBe(204);
  });

  it("should log structured violation data", async () => {
    const consoleSpy = jest.spyOn(console, "log").mockImplementation();

    const req = createRequest(
      {
        "csp-report": {
          "document-uri": "https://smartlic.tech/dashboard",
          "violated-directive": "connect-src 'self'",
          "blocked-uri": "https://malicious.com/api",
        },
      },
      "log-test-ip"
    );
    await POST(req);

    const logCall = consoleSpy.mock.calls.find((call) => {
      try {
        const parsed = JSON.parse(call[0]);
        return parsed.type === "csp-violation";
      } catch {
        return false;
      }
    });

    expect(logCall).toBeDefined();
    const logData = JSON.parse(logCall![0]);
    expect(logData.violated_directive).toContain("connect-src");
    expect(logData.blocked_uri).toBe("https://malicious.com/api");
    expect(logData.document_uri).toBe("https://smartlic.tech/dashboard");

    consoleSpy.mockRestore();
  });
});
