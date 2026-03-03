/**
 * API Proxy Route — POST /api/regenerate-excel/{searchId}
 *
 * STORY-364 AC7: Proxies to backend POST /v1/search/{search_id}/regenerate-excel
 * to regenerate Excel from stored results without re-running the search.
 */

import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

export const runtime = "nodejs";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ searchId: string }> },
) {
  const { searchId } = await params;

  if (!searchId) {
    return NextResponse.json(
      { error: "searchId is required" },
      { status: 400 },
    );
  }

  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json(
      { error: "Server not configured" },
      { status: 503 },
    );
  }

  const authHeader = request.headers.get("Authorization");
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
    const backendResponse = await fetch(
      `${backendUrl}/v1/search/${encodeURIComponent(searchId)}/regenerate-excel`,
      { method: "POST", headers },
    );

    const body = await backendResponse.text();
    const sanitized = sanitizeProxyError(backendResponse.status, body, backendResponse.headers.get("content-type"));
    if (sanitized) return sanitized;

    try {
      const data = JSON.parse(body);
      return NextResponse.json(data, { status: backendResponse.status });
    } catch {
      return NextResponse.json(
        { message: "Erro temporário de comunicação" },
        { status: backendResponse.status },
      );
    }
  } catch (error) {
    console.error("[regenerate-excel proxy] Error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
