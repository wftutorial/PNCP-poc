import { NextRequest, NextResponse } from "next/server";
import { getRefreshedToken } from "../../../lib/serverAuth";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

export async function POST(request: NextRequest) {
  try {
    // Get auth token (prefer server-side refreshed, fall back to header)
    const refreshedToken = await getRefreshedToken();
    const authHeader = refreshedToken
      ? `Bearer ${refreshedToken}`
      : request.headers.get("authorization");

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        { message: "Autenticacao necessaria. Faca login para continuar." },
        { status: 401 }
      );
    }

    const backendUrl = process.env.BACKEND_URL;
    if (!backendUrl) {
      console.error("BACKEND_URL environment variable is not configured");
      return NextResponse.json(
        { message: "Servidor nao configurado. Contate o suporte." },
        { status: 503 }
      );
    }

    // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
    const correlationId = request.headers.get("X-Correlation-ID");
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Authorization: authHeader,
    };
    if (correlationId) {
      headers["X-Correlation-ID"] = correlationId;
    }

    // Call backend billing portal endpoint
    const response = await fetch(`${backendUrl}/v1/billing-portal`, {
      method: "POST",
      headers,
    });

    if (!response.ok) {
      const body = await response.text();
      const sanitized = sanitizeProxyError(response.status, body, response.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(body);
        return NextResponse.json(
          { message: data.detail || "Erro ao criar sessão do portal" },
          { status: response.status }
        );
      } catch {
        return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: response.status });
      }
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error creating billing portal session:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
