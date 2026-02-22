import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

export async function GET(request: NextRequest) {
  const authHeader = request.headers.get("authorization");
  if (!authHeader) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json(
      { error: "Servidor nao configurado" },
      { status: 503 }
    );
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
  const correlationId = request.headers.get("X-Correlation-ID");
  const headers: Record<string, string> = {
    Authorization: authHeader,
  };
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  try {
    const res = await fetch(`${backendUrl}/v1/trial-status`, { headers });

    if (!res.ok) {
      // CRIT-017: Sanitize non-JSON / infrastructure errors
      const body = await res.text();
      const sanitized = sanitizeProxyError(res.status, body, res.headers.get("content-type"));
      if (sanitized) return sanitized;

      // Structured backend error — parse and forward
      try {
        const parsed = JSON.parse(body);
        return NextResponse.json(
          { error: parsed.detail || parsed.message || "Erro do servidor" },
          { status: res.status }
        );
      } catch {
        return NextResponse.json(
          { error: "Erro do servidor" },
          { status: res.status }
        );
      }
    }

    const data = await res.json().catch(() => null);
    if (!data) {
      return NextResponse.json(
        { error: "Resposta inesperada do servidor" },
        { status: 502 }
      );
    }
    return NextResponse.json(data);
  } catch (error) {
    // CRIT-017: Sanitize network errors
    console.error("[trial-status] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
