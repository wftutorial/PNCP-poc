import { NextRequest, NextResponse } from "next/server";
import { getRefreshedToken } from "../../../lib/serverAuth";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

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

  try {
    const response = await fetch(`${backendUrl}/v1/me`, { headers });

    if (!response.ok) {
      // CRIT-017: Sanitize infrastructure errors
      const body = await response.text();
      const sanitized = sanitizeProxyError(response.status, body, response.headers.get("content-type"));
      if (sanitized) return sanitized;

      try {
        const error = JSON.parse(body);
        return NextResponse.json(
          { message: error.detail || "Erro ao obter perfil" },
          { status: response.status }
        );
      } catch {
        return NextResponse.json(
          { message: "Erro ao obter perfil" },
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
    console.error("Error fetching profile:", error);
    return sanitizeNetworkError(error);
  }
}

export async function DELETE(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json(
      { message: "Servidor nao configurado" },
      { status: 503 }
    );
  }

  const authHeader = request.headers.get("authorization");
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
  };
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  try {
    const response = await fetch(`${backendUrl}/v1/me`, {
      method: "DELETE",
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
          { message: error.detail || "Erro ao excluir conta" },
          { status: response.status }
        );
      } catch {
        return NextResponse.json(
          { message: "Erro ao excluir conta" },
          { status: response.status }
        );
      }
    }

    const data = await response.json().catch(() => ({ success: true }));
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error deleting account:", error);
    return sanitizeNetworkError(error);
  }
}
