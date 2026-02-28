import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { getRefreshedToken } from "../../../../lib/serverAuth";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

/**
 * POST /api/reports/diagnostico
 *
 * Proxy: forwards PDF generation requests to backend /v1/reports/diagnostico.
 * Streams the resulting PDF back to the client with correct Content-Type and
 * Content-Disposition headers so the browser triggers a file download.
 *
 * Patterns followed:
 *  - Server-side token refresh via getRefreshedToken() (STORY-253 AC7)
 *  - X-Request-ID generated per request (CRIT-004 AC1)
 *  - X-Correlation-ID forwarded when present (CRIT-004 AC1)
 *  - Infrastructure error sanitization via proxy-error-handler (CRIT-017)
 *  - X-Error-Source: proxy header on sanitized error responses
 */

const BACKEND_ENDPOINT = "/v1/reports/diagnostico";

/** Default filename when Content-Disposition is absent or unparseable. */
function buildDefaultFilename(): string {
  const date = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
  return `diagnostico-${date}.pdf`;
}

/** Extract filename from a Content-Disposition header value, or fall back to default. */
function extractFilename(contentDisposition: string | null): string {
  if (!contentDisposition) return buildDefaultFilename();
  // Support both quoted and unquoted filenames:
  //   attachment; filename="foo.pdf"
  //   attachment; filename=foo.pdf
  const match = contentDisposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\s]+)["']?/i);
  return match?.[1] ?? buildDefaultFilename();
}

export async function POST(request: NextRequest) {
  // ------------------------------------------------------------------
  // 1. Resolve BACKEND_URL
  // ------------------------------------------------------------------
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    console.error("[PDF Proxy] BACKEND_URL environment variable is not configured");
    return NextResponse.json(
      { error: "Serviço temporariamente indisponível" },
      { status: 503 }
    );
  }

  // ------------------------------------------------------------------
  // 2. Authenticate — prefer server-side refreshed token (STORY-253 AC7)
  // ------------------------------------------------------------------
  let authHeader: string | null;
  try {
    const refreshedToken = await getRefreshedToken();
    authHeader = refreshedToken
      ? `Bearer ${refreshedToken}`
      : request.headers.get("authorization");
  } catch {
    // getRefreshedToken can throw when Supabase env vars are missing in test envs
    authHeader = request.headers.get("authorization");
  }

  if (!authHeader?.startsWith("Bearer ")) {
    return NextResponse.json(
      { error: "Autenticação necessária. Faça login para continuar." },
      { status: 401 }
    );
  }

  // ------------------------------------------------------------------
  // 3. Parse request body
  // ------------------------------------------------------------------
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Corpo da requisição inválido." },
      { status: 400 }
    );
  }

  // ------------------------------------------------------------------
  // 4. Build upstream request headers (CRIT-004)
  // ------------------------------------------------------------------
  const requestId = randomUUID();
  const correlationId = request.headers.get("X-Correlation-ID");

  const upstreamHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    "Authorization": authHeader,
    "X-Request-ID": requestId,
  };
  if (correlationId) {
    upstreamHeaders["X-Correlation-ID"] = correlationId;
  }

  // ------------------------------------------------------------------
  // 5. Forward to backend
  // ------------------------------------------------------------------
  let response: Response;
  try {
    response = await fetch(`${backendUrl}${BACKEND_ENDPOINT}`, {
      method: "POST",
      headers: upstreamHeaders,
      body: JSON.stringify(body),
    });
  } catch (error) {
    console.error("[PDF Proxy] Network error reaching backend:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }

  // ------------------------------------------------------------------
  // 6. Handle non-OK responses
  // ------------------------------------------------------------------
  if (!response.ok) {
    const contentType = response.headers.get("content-type");
    const errorText = await response.text();

    // Infrastructure errors (nginx "Bad Gateway", Railway HTML pages, etc.)
    const sanitized = sanitizeProxyError(response.status, errorText, contentType);
    if (sanitized) return sanitized;

    // Structured backend error — pass through detail message
    let errorDetail: string | null = null;
    try {
      const errorJson = JSON.parse(errorText);
      errorDetail = typeof errorJson.detail === "string"
        ? errorJson.detail
        : typeof errorJson.message === "string"
          ? errorJson.message
          : null;
    } catch {
      // errorText is not JSON — use generic message
    }

    console.error(
      `[PDF Proxy] Backend error ${response.status} on ${BACKEND_ENDPOINT}:`,
      errorDetail ?? errorText.slice(0, 200)
    );

    const errorResponse = NextResponse.json(
      { error: errorDetail ?? "Erro ao gerar relatório. Tente novamente." },
      { status: response.status }
    );
    errorResponse.headers.set("X-Request-ID", requestId);
    return errorResponse;
  }

  // ------------------------------------------------------------------
  // 7. Verify response is PDF
  // ------------------------------------------------------------------
  const upstreamContentType = response.headers.get("content-type") ?? "";
  if (!upstreamContentType.includes("application/pdf")) {
    // Backend returned unexpected content type — treat as internal error
    console.error(
      `[PDF Proxy] Unexpected content-type from backend: "${upstreamContentType}"`
    );
    return NextResponse.json(
      { error: "Resposta inesperada do servidor ao gerar relatório." },
      { status: 502 }
    );
  }

  // ------------------------------------------------------------------
  // 8. Stream PDF buffer back to client
  // ------------------------------------------------------------------
  let pdfBuffer: ArrayBuffer;
  try {
    pdfBuffer = await response.arrayBuffer();
  } catch (error) {
    console.error("[PDF Proxy] Failed to read PDF buffer from backend:", error);
    return NextResponse.json(
      { error: "Erro ao processar relatório gerado. Tente novamente." },
      { status: 502 }
    );
  }

  if (pdfBuffer.byteLength === 0) {
    console.error("[PDF Proxy] Backend returned empty PDF buffer");
    return NextResponse.json(
      { error: "Relatório gerado está vazio. Tente novamente." },
      { status: 502 }
    );
  }

  const filename = extractFilename(response.headers.get("content-disposition"));

  console.log(
    `[PDF Proxy] Serving PDF — file: "${filename}", ` +
    `size: ${pdfBuffer.byteLength} bytes, request_id: ${requestId}`
  );

  const pdfResponse = new NextResponse(pdfBuffer, {
    status: 200,
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
      "Content-Length": String(pdfBuffer.byteLength),
      "X-Request-ID": requestId,
      // Prevent caching of generated reports
      "Cache-Control": "no-store",
    },
  });

  return pdfResponse;
}
