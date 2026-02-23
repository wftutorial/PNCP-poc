import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../../../lib/proxy-error-handler";

const backendUrl = process.env.BACKEND_URL;

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  if (!backendUrl)
    return NextResponse.json({ message: "Servidor nao configurado" }, { status: 503 });

  const authHeader = request.headers.get("authorization");
  if (!authHeader)
    return NextResponse.json({ message: "Autenticacao necessaria" }, { status: 401 });

  const { id } = await params;

  // CRIT-004 AC4: Forward X-Correlation-ID for end-to-end tracing
  const correlationId = request.headers.get("X-Correlation-ID");

  try {
    const body = await request.json();
    const res = await fetch(
      `${backendUrl}/v1/api/messages/conversations/${id}/status`,
      {
        method: "PATCH",
        headers: { Authorization: authHeader, "Content-Type": "application/json", ...(correlationId && { "X-Correlation-ID": correlationId }) },
        body: JSON.stringify(body),
      },
    );
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
    console.error("[messages/conversations/[id]/status] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
