import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

const getBackendUrl = () => process.env.BACKEND_URL;

export async function GET(request: NextRequest) {
  const backendUrl = getBackendUrl();
  if (!backendUrl) {
    return NextResponse.json({ message: "Servidor nao configurado" }, { status: 503 });
  }

  const authHeader = request.headers.get("authorization");
  if (!authHeader) {
    return NextResponse.json({ message: "Autenticacao necessaria" }, { status: 401 });
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");

  try {
    const response = await fetch(`${backendUrl}/v1/profile/context`, {
      headers: { Authorization: authHeader, "Content-Type": "application/json", ...(correlationId && { "X-Correlation-ID": correlationId }) },
    });

    if (!response.ok) {
      const body = await response.text();
      const sanitized = sanitizeProxyError(response.status, body, response.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(body);
        return NextResponse.json(
          { message: data.detail || "Erro ao obter contexto" },
          { status: response.status },
        );
      } catch {
        return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: response.status });
      }
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching profile context:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}

export async function PUT(request: NextRequest) {
  const backendUrl = getBackendUrl();
  if (!backendUrl) {
    return NextResponse.json({ message: "Servidor nao configurado" }, { status: 503 });
  }

  const authHeader = request.headers.get("authorization");
  if (!authHeader) {
    return NextResponse.json({ message: "Autenticacao necessaria" }, { status: 401 });
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationIdPut = request.headers.get("X-Correlation-ID");

  try {
    const body = await request.json();
    const response = await fetch(`${backendUrl}/v1/profile/context`, {
      method: "PUT",
      headers: { Authorization: authHeader, "Content-Type": "application/json", ...(correlationIdPut && { "X-Correlation-ID": correlationIdPut }) },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const responseBody = await response.text();
      const sanitized = sanitizeProxyError(response.status, responseBody, response.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(responseBody);
        return NextResponse.json(
          { message: data.detail || "Erro ao salvar contexto" },
          { status: response.status },
        );
      } catch {
        return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: response.status });
      }
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error saving profile context:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
