/**
 * UX-349 AC7: Google Sheets export API proxy.
 *
 * POST /api/export/google-sheets → POST BACKEND_URL/api/export/google-sheets
 *
 * Previously returned 404 because no proxy route existed.
 */

import { NextRequest, NextResponse } from "next/server";
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
    const authHeader = request.headers.get("authorization");
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        { detail: "Autenticação necessária. Faça login para continuar." },
        { status: 401 },
      );
    }

    const body = await request.json();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Authorization: authHeader,
    };

    const correlationId = request.headers.get("X-Correlation-ID");
    if (correlationId) {
      headers["X-Correlation-ID"] = correlationId;
    }

    const res = await fetch(`${backendUrl}/v1/api/export/google-sheets`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    const responseBody = await res.text();
    const sanitized = sanitizeProxyError(res.status, responseBody, res.headers.get("content-type"));
    if (sanitized) return sanitized;

    try {
      const data = JSON.parse(responseBody);
      return NextResponse.json(data, { status: res.status });
    } catch {
      return NextResponse.json(
        { detail: "Erro ao exportar para Google Sheets. Tente novamente." },
        { status: res.status >= 400 ? res.status : 502 },
      );
    }
  } catch (error) {
    console.error("[google-sheets-proxy] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
