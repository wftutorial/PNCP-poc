import { NextRequest, NextResponse } from "next/server";
import { getRefreshedToken } from "../../../../lib/serverAuth";
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

  try {
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

    // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
    const correlationId = request.headers.get("X-Correlation-ID");

    const res = await fetch(`${backendUrl}/v1/api/subscriptions/cancel`, {
      method: "POST",
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
        ...(correlationId && { "X-Correlation-ID": correlationId }),
      },
    });

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
    console.error("[api/subscriptions/cancel] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
