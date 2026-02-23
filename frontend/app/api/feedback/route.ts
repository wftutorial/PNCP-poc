/**
 * GTM-RESILIENCE-D05: Feedback API proxy.
 *
 * POST /api/feedback → POST BACKEND_URL/v1/feedback
 * DELETE /api/feedback?id=xxx → DELETE BACKEND_URL/v1/feedback/{id}
 */

import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../lib/proxy-error-handler";

const BACKEND_URL = process.env.BACKEND_URL;

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

  try {
    const data = JSON.parse(body);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: fallbackMessage },
      { status: response.status },
    );
  }
}

export async function POST(request: NextRequest) {
  if (!BACKEND_URL) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json({ message: "Serviço temporariamente indisponível" }, { status: 503 });
  }

  try {
    const body = await request.json();
    const authHeader = request.headers.get("authorization") || "";

    // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
    const correlationId = request.headers.get("X-Correlation-ID");
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Authorization: authHeader,
    };
    if (correlationId) {
      headers["X-Correlation-ID"] = correlationId;
    }

    const res = await fetch(`${BACKEND_URL}/v1/feedback`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    return safeProxyResponse(res, "Erro ao enviar feedback");
  } catch (error) {
    console.error("Feedback proxy error:", error);
    return sanitizeNetworkError(error);
  }
}

export async function DELETE(request: NextRequest) {
  if (!BACKEND_URL) {
    console.error("BACKEND_URL environment variable is not configured");
    return NextResponse.json({ message: "Serviço temporariamente indisponível" }, { status: 503 });
  }

  try {
    const { searchParams } = new URL(request.url);
    const feedbackId = searchParams.get("id");

    if (!feedbackId) {
      return NextResponse.json({ error: "Missing id parameter" }, { status: 400 });
    }

    const authHeader = request.headers.get("authorization") || "";

    // CRIT-004 AC4: Forward X-Correlation-ID for distributed tracing
    const correlationId = request.headers.get("X-Correlation-ID");
    const headers: Record<string, string> = {
      Authorization: authHeader,
    };
    if (correlationId) {
      headers["X-Correlation-ID"] = correlationId;
    }

    const res = await fetch(`${BACKEND_URL}/v1/feedback/${feedbackId}`, {
      method: "DELETE",
      headers,
    });

    return safeProxyResponse(res, "Erro ao remover feedback");
  } catch (error) {
    console.error("Feedback delete proxy error:", error);
    return sanitizeNetworkError(error);
  }
}
