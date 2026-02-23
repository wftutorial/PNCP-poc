import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

const BACKEND_URL = process.env.BACKEND_URL;

function getAuthHeader(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) return null;
  return authHeader;
}

// CRIT-017: Shared helper to safely parse response with infrastructure error sanitization
async function safeProxyResponse(
  response: Response,
  fallbackMessage: string,
): Promise<NextResponse> {
  const body = await response.text();
  const sanitized = sanitizeProxyError(
    response.status,
    body,
    response.headers.get("content-type"),
  );
  if (sanitized) return sanitized;

  // Parse JSON — safe because sanitizeProxyError verified it's valid structured JSON
  try {
    const data = JSON.parse(body);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { message: fallbackMessage },
      { status: response.status },
    );
  }
}

export async function GET(request: NextRequest) {
  if (!BACKEND_URL) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json({ message: "Serviço temporariamente indisponível" }, { status: 503 });
  }

  const auth = getAuthHeader(request);
  if (!auth) {
    return NextResponse.json({ message: "Autenticação necessária." }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const path = searchParams.get("_path") || "/pipeline";
  const cleanParams = new URLSearchParams(searchParams);
  cleanParams.delete("_path");
  const qs = cleanParams.toString();

  const url = `${BACKEND_URL}/v1${path}${qs ? `?${qs}` : ""}`;

  // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
  const correlationId = request.headers.get("X-Correlation-ID");
  const headers: Record<string, string> = {
    Authorization: auth,
  };
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  try {
    const response = await fetch(url, { headers });
    return safeProxyResponse(response, "Erro ao conectar com servidor.");
  } catch (error) {
    console.error("[pipeline] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}

export async function POST(request: NextRequest) {
  if (!BACKEND_URL) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json({ message: "Serviço temporariamente indisponível" }, { status: 503 });
  }

  const auth = getAuthHeader(request);
  if (!auth) {
    return NextResponse.json({ message: "Autenticação necessária." }, { status: 401 });
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
  const correlationId = request.headers.get("X-Correlation-ID");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: auth,
  };
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  try {
    const body = await request.json();
    const response = await fetch(`${BACKEND_URL}/v1/pipeline`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    return safeProxyResponse(response, "Erro ao conectar com servidor.");
  } catch (error) {
    console.error("[pipeline] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}

export async function PATCH(request: NextRequest) {
  if (!BACKEND_URL) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json({ message: "Serviço temporariamente indisponível" }, { status: 503 });
  }

  const auth = getAuthHeader(request);
  if (!auth) {
    return NextResponse.json({ message: "Autenticação necessária." }, { status: 401 });
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
  const correlationId = request.headers.get("X-Correlation-ID");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: auth,
  };
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  try {
    const body = await request.json();
    const { item_id, ...updateData } = body;
    const response = await fetch(`${BACKEND_URL}/v1/pipeline/${item_id}`, {
      method: "PATCH",
      headers,
      body: JSON.stringify(updateData),
    });
    return safeProxyResponse(response, "Erro ao conectar com servidor.");
  } catch (error) {
    console.error("[pipeline] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}

export async function DELETE(request: NextRequest) {
  if (!BACKEND_URL) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json({ message: "Serviço temporariamente indisponível" }, { status: 503 });
  }

  const auth = getAuthHeader(request);
  if (!auth) {
    return NextResponse.json({ message: "Autenticação necessária." }, { status: 401 });
  }

  // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
  const correlationId = request.headers.get("X-Correlation-ID");
  const headers: Record<string, string> = {
    Authorization: auth,
  };
  if (correlationId) {
    headers["X-Correlation-ID"] = correlationId;
  }

  try {
    const { searchParams } = new URL(request.url);
    const itemId = searchParams.get("id");
    if (!itemId) {
      return NextResponse.json({ message: "ID do item é obrigatório." }, { status: 400 });
    }
    const response = await fetch(`${BACKEND_URL}/v1/pipeline/${itemId}`, {
      method: "DELETE",
      headers,
    });
    return safeProxyResponse(response, "Erro ao conectar com servidor.");
  } catch (error) {
    console.error("[pipeline] Network error:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
