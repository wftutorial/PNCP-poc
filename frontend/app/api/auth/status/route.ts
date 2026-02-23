/**
 * GTM-FIX-009: Proxy for GET /v1/auth/status?email=...
 * Checks if a signup email has been confirmed.
 */
import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

export async function GET(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json(
      { message: "Serviço temporariamente indisponível" },
      { status: 503 }
    );
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");

  try {
    const email = request.nextUrl.searchParams.get("email");
    if (!email) {
      return NextResponse.json(
        { confirmed: false, error: "Email required" },
        { status: 400 }
      );
    }

    const response = await fetch(
      `${backendUrl}/v1/auth/status?email=${encodeURIComponent(email)}`,
      { headers: { ...(correlationId && { "X-Correlation-ID": correlationId }) } }
    );

    const body = await response.text();
    const sanitized = sanitizeProxyError(response.status, body, response.headers.get("content-type"));
    if (sanitized) return sanitized;

    try {
      const data = JSON.parse(body);
      return NextResponse.json(data, { status: response.status });
    } catch {
      return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: response.status });
    }
  } catch (error) {
    console.error("[auth/status] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
