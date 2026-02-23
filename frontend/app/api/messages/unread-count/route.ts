import { NextRequest, NextResponse } from "next/server";
import { getRefreshedToken } from "../../../../lib/serverAuth";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

const backendUrl = process.env.BACKEND_URL;

export async function GET(request: NextRequest) {
  if (!backendUrl)
    return NextResponse.json({ message: "Servidor nao configurado" }, { status: 503 });

  // STORY-253 AC7: Prefer server-side refreshed token, fall back to header
  const refreshedToken = await getRefreshedToken();
  const authHeader = refreshedToken
    ? `Bearer ${refreshedToken}`
    : request.headers.get("authorization");

  if (!authHeader)
    return NextResponse.json({ message: "Autenticacao necessaria" }, { status: 401 });

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");

  try {
    const res = await fetch(`${backendUrl}/v1/api/messages/unread-count`, {
      headers: { Authorization: authHeader, "Content-Type": "application/json", ...(correlationId && { "X-Correlation-ID": correlationId }) },
    });

    // If 401 even after refresh, signal session expired
    if (res.status === 401) {
      return NextResponse.json(
        { message: "Sessao expirada", session_expired: true },
        { status: 401 }
      );
    }

    if (!res.ok) {
      const body = await res.text();
      const sanitized = sanitizeProxyError(res.status, body, res.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(body);
        return NextResponse.json(data, { status: res.status });
      } catch {
        return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: res.status });
      }
    }

    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error("[messages/unread-count] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
