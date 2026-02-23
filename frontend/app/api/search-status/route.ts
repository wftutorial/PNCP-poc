/**
 * CRIT-003 AC11: Proxy for search status polling endpoint.
 *
 * GET /api/search-status?search_id=xxx → backend GET /v1/search/{search_id}/status
 */

import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

export async function GET(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json(
      { message: "Serviço temporariamente indisponível" },
      { status: 503 }
    );
  }

  const searchId = request.nextUrl.searchParams.get("search_id");

  if (!searchId) {
    return NextResponse.json(
      { error: "search_id is required" },
      { status: 400 }
    );
  }

  const authHeader = request.headers.get("authorization");
  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (authHeader) {
    headers["Authorization"] = authHeader;
  }
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  try {
    const res = await fetch(
      `${backendUrl}/v1/search/${encodeURIComponent(searchId)}/status`,
      { headers, cache: "no-store" }
    );

    const body = await res.text();
    const sanitized = sanitizeProxyError(res.status, body, res.headers.get("content-type"));
    if (sanitized) return sanitized;

    try {
      const data = JSON.parse(body);
      return NextResponse.json(data, { status: res.status });
    } catch {
      return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: res.status });
    }
  } catch (error) {
    console.error("[search-status] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
