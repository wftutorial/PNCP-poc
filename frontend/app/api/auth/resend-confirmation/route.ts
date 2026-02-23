/**
 * GTM-FIX-009: Proxy for POST /v1/auth/resend-confirmation
 * Resends signup confirmation email with 60s rate limiting.
 */
import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

export async function POST(request: NextRequest) {
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
    const body = await request.json();

    const response = await fetch(`${backendUrl}/v1/auth/resend-confirmation`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(correlationId && { "X-Correlation-ID": correlationId }) },
      body: JSON.stringify(body),
    });

    const responseBody = await response.text();
    const sanitized = sanitizeProxyError(response.status, responseBody, response.headers.get("content-type"));
    if (sanitized) return sanitized;

    try {
      const data = JSON.parse(responseBody);
      return NextResponse.json(data, { status: response.status });
    } catch {
      return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: response.status });
    }
  } catch (error) {
    console.error("[auth/resend-confirmation] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
