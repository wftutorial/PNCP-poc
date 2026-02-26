import { NextRequest, NextResponse } from "next/server";
import { getRefreshedToken } from "../../../../lib/serverAuth";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

/**
 * STORY-274 AC5: Proxy route for backend /health/cache endpoint.
 *
 * Admin-only access: checks Supabase session, then verifies admin status
 * via backend /v1/me before proxying to /v1/health/cache.
 */
export async function GET(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json(
      { message: "Servidor nao configurado" },
      { status: 503 }
    );
  }

  // STORY-253 AC7: Prefer server-side refreshed token, fall back to header
  const refreshedToken = await getRefreshedToken();
  const authHeader = refreshedToken
    ? `Bearer ${refreshedToken}`
    : request.headers.get("authorization");

  if (!authHeader) {
    return NextResponse.json(
      { message: "Autenticacao necessaria" },
      { status: 401 }
    );
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
  const correlationId = request.headers.get("X-Correlation-ID");
  const headers: Record<string, string> = {
    "Authorization": authHeader,
    "Content-Type": "application/json",
  };
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  // --- Admin check: verify user is admin via backend /v1/me ---
  try {
    const meResponse = await fetch(`${backendUrl}/v1/me`, { headers });

    if (!meResponse.ok) {
      return NextResponse.json(
        { message: "Falha ao verificar permissoes" },
        { status: 403 }
      );
    }

    const meData = await meResponse.json();
    if (meData.is_admin !== true && meData.is_master !== true) {
      return NextResponse.json(
        { message: "Acesso restrito a administradores" },
        { status: 403 }
      );
    }
  } catch (error) {
    console.error("[health/cache] Error checking admin status:", error);
    return NextResponse.json(
      { message: "Falha ao verificar permissoes" },
      { status: 500 }
    );
  }

  // --- Proxy to backend /v1/health/cache ---
  try {
    const response = await fetch(`${backendUrl}/v1/health/cache`, {
      headers,
    });

    if (!response.ok) {
      // CRIT-017: Sanitize infrastructure errors
      const body = await response.text();
      const sanitized = sanitizeProxyError(response.status, body, response.headers.get("content-type"));
      if (sanitized) return sanitized;

      try {
        const error = JSON.parse(body);
        return NextResponse.json(
          { message: error.detail || "Erro ao obter status do cache" },
          { status: response.status }
        );
      } catch {
        return NextResponse.json(
          { message: "Erro ao obter status do cache" },
          { status: response.status }
        );
      }
    }

    const data = await response.json().catch(() => null);
    if (!data) {
      return NextResponse.json(
        { message: "Resposta inesperada do servidor" },
        { status: 502 }
      );
    }
    return NextResponse.json(data);
  } catch (error) {
    console.error("[health/cache] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
