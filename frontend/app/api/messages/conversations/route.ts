import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

const backendUrl = process.env.BACKEND_URL;

function errorResponse(msg: string, status: number) {
  return NextResponse.json({ message: msg }, { status });
}

export async function GET(request: NextRequest) {
  if (!backendUrl) return errorResponse("Servidor nao configurado", 503);

  const authHeader = request.headers.get("authorization");
  if (!authHeader) return errorResponse("Autenticacao necessaria", 401);

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");

  const { searchParams } = new URL(request.url);
  const qs = searchParams.toString();
  const url = `${backendUrl}/v1/api/messages/conversations${qs ? `?${qs}` : ""}`;

  try {
    const res = await fetch(url, {
      headers: { Authorization: authHeader, "Content-Type": "application/json", ...(correlationId && { "X-Correlation-ID": correlationId }) },
    });
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
    console.error("[messages/conversations] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}

export async function POST(request: NextRequest) {
  if (!backendUrl) return errorResponse("Servidor nao configurado", 503);

  const authHeader = request.headers.get("authorization");
  if (!authHeader) return errorResponse("Autenticacao necessaria", 401);

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");

  try {
    const body = await request.json();
    const res = await fetch(`${backendUrl}/v1/api/messages/conversations`, {
      method: "POST",
      headers: { Authorization: authHeader, "Content-Type": "application/json", ...(correlationId && { "X-Correlation-ID": correlationId }) },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const resBody = await res.text();
      const sanitized = sanitizeProxyError(res.status, resBody, res.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(resBody);
        return NextResponse.json(data, { status: res.status });
      } catch {
        return NextResponse.json({ message: "Erro temporário de comunicação" }, { status: res.status });
      }
    }
    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error("[messages/conversations] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
