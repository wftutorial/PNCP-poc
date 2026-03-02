/**
 * @jest-environment node
 *
 * STORY-357: Auth token refresh during long searches.
 *
 * AC6: Mock expired token during search → refresh succeeds → request retried
 * AC7: Mock refresh failing → return 401 with returnTo
 */
import { NextRequest } from "next/server";

// Mock getRefreshedToken from serverAuth
const mockGetRefreshedToken = jest.fn();
jest.mock("../../lib/serverAuth", () => ({
  getRefreshedToken: (...args: unknown[]) => mockGetRefreshedToken(...args),
}));

// Mock proxy-error-handler to avoid import issues
jest.mock("../../lib/proxy-error-handler", () => ({
  sanitizeProxyError: () => null,
  sanitizeNetworkError: (error: unknown) => {
    const { NextResponse } = require("next/server");
    return NextResponse.json(
      { message: "Erro de conexão" },
      { status: 502 }
    );
  },
}));

// Mock fetch globally
global.fetch = jest.fn();

// Set BACKEND_URL for all tests
process.env.BACKEND_URL = "http://test-backend:8000";

// Import AFTER mocks
import { POST } from "../../app/api/buscar/route";

function makeRequest(authHeader?: string) {
  const headers: Record<string, string> = {};
  if (authHeader) headers["Authorization"] = authHeader;
  return new NextRequest("http://localhost:3000/api/buscar", {
    method: "POST",
    headers,
    body: JSON.stringify({
      ufs: ["SP"],
      data_inicial: "2026-01-01",
      data_final: "2026-01-10",
    }),
  });
}

function mockBackendOk() {
  return {
    ok: true,
    status: 200,
    text: async () => JSON.stringify({
      licitacoes: [],
      total_raw: 0,
      total_filtrado: 0,
      excel_available: false,
    }),
    json: async () => ({
      licitacoes: [],
      total_raw: 0,
      total_filtrado: 0,
      excel_available: false,
    }),
  };
}

function mock401Response() {
  return {
    ok: false,
    status: 401,
    text: async () => JSON.stringify({ detail: "Token expired" }),
    headers: { get: () => "application/json" },
  };
}

describe("STORY-357: Auth token refresh-and-retry in proxy", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // AC6: Token expired → refresh succeeds → retry succeeds
  it("retries request with refreshed token when backend returns 401", async () => {
    // First call: getRefreshedToken returns initial token
    mockGetRefreshedToken.mockResolvedValueOnce("initial-token");
    // After 401: getRefreshedToken returns fresh token
    mockGetRefreshedToken.mockResolvedValueOnce("refreshed-token");

    // Backend: first call 401, second call 200
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce(mock401Response())
      .mockResolvedValueOnce(mockBackendOk());

    const request = makeRequest("Bearer initial-token");
    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    // Verify fetch was called twice (original + retry)
    expect(global.fetch).toHaveBeenCalledTimes(2);
    // Second call should have the refreshed token
    const secondCallHeaders = (global.fetch as jest.Mock).mock.calls[1][1].headers;
    expect(secondCallHeaders.Authorization).toBe("Bearer refreshed-token");
  });

  // AC2: Only one refresh retry allowed (no infinite loop)
  it("does not retry more than once on 401", async () => {
    mockGetRefreshedToken.mockResolvedValueOnce("initial-token");
    // After first 401: refresh returns a token
    mockGetRefreshedToken.mockResolvedValueOnce("refreshed-token");

    // Both calls return 401
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce(mock401Response())
      .mockResolvedValueOnce(mock401Response());

    const request = makeRequest("Bearer initial-token");
    const response = await POST(request);
    const data = await response.json();

    // Should break out after second 401 (non-retryable once refresh attempted)
    expect(response.status).toBe(401);
    // getRefreshedToken called twice (initial + retry)
    expect(mockGetRefreshedToken).toHaveBeenCalledTimes(2);
  });

  // AC7: Refresh fails → return 401 with returnTo
  it("returns 401 with returnTo when token refresh fails", async () => {
    mockGetRefreshedToken.mockResolvedValueOnce("initial-token");
    // After 401: refresh returns null (failure)
    mockGetRefreshedToken.mockResolvedValueOnce(null);

    (global.fetch as jest.Mock).mockResolvedValueOnce(mock401Response());

    const request = makeRequest("Bearer initial-token");
    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.message).toBe("Sua sessão expirou. Faça login novamente.");
    expect(data.returnTo).toBe("/buscar");
  });

  // AC1: Normal flow (no 401) does not trigger refresh retry
  it("does not attempt refresh on successful response", async () => {
    mockGetRefreshedToken.mockResolvedValueOnce("valid-token");

    (global.fetch as jest.Mock).mockResolvedValueOnce(mockBackendOk());

    const request = makeRequest("Bearer valid-token");
    const response = await POST(request);

    expect(response.status).toBe(200);
    expect(global.fetch).toHaveBeenCalledTimes(1);
    // getRefreshedToken called only once (initial)
    expect(mockGetRefreshedToken).toHaveBeenCalledTimes(1);
  });
});
