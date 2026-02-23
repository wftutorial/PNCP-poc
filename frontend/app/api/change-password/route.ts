import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

export async function POST(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json(
      { message: "Servidor nao configurado" },
      { status: 503 }
    );
  }

  // Forward auth header to backend
  const authHeader = request.headers.get("authorization");
  if (!authHeader) {
    return NextResponse.json(
      { message: "Autenticacao necessaria" },
      { status: 401 }
    );
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");

  try {
    const body = await request.json();

    const response = await fetch(`${backendUrl}/v1/change-password`, {
      method: "POST",
      headers: {
        "Authorization": authHeader,
        "Content-Type": "application/json",
        ...(correlationId && { "X-Correlation-ID": correlationId }),
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const responseBody = await response.text();
      const sanitized = sanitizeProxyError(response.status, responseBody, response.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(responseBody);
        return NextResponse.json(
          { detail: data.detail || "Erro ao alterar senha" },
          { status: response.status }
        );
      } catch {
        return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: response.status });
      }
    }

    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error changing password:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
