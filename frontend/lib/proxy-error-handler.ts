/**
 * CRIT-017: Centralized proxy error sanitizer.
 *
 * Prevents raw infrastructure errors (Railway "Application not found",
 * nginx "Bad Gateway", etc.) from leaking to users.
 *
 * Principle: Users must NEVER see text that wasn't written by SmartLic.
 */

import { NextResponse } from "next/server";

// Infrastructure error patterns that should never reach the user
const INFRA_ERROR_PATTERNS = [
  "application not found",   // Railway: no container running
  "bad gateway",             // nginx/Railway: upstream error
  "service unavailable",     // generic infrastructure
  "gateway timeout",         // infrastructure timeout
  "upstream connect error",  // envoy/nginx
  "no healthy upstream",     // load balancer
  "<!doctype",               // HTML error page
  "<html",                   // HTML error page
];

// HTTP status codes indicating backend/infra unavailability
const UNAVAILABLE_STATUSES = new Set([502, 503, 504]);

export interface SanitizedProxyError {
  error: string;
  message: string;
  error_code: string;
  retry_after_seconds: number;
}

const BACKEND_UNAVAILABLE_MSG =
  "Nossos servidores estão sendo atualizados. Tente novamente em alguns instantes.";

const BACKEND_UNAVAILABLE: SanitizedProxyError = {
  error: BACKEND_UNAVAILABLE_MSG,
  message: BACKEND_UNAVAILABLE_MSG,
  error_code: "BACKEND_UNAVAILABLE",
  retry_after_seconds: 30,
};

/**
 * Check if a response body contains infrastructure error patterns.
 * AC3: "Application not found" (Railway)
 * AC4: "Bad Gateway" (nginx)
 */
function containsInfraError(body: string): boolean {
  const lower = body.toLowerCase();
  return INFRA_ERROR_PATTERNS.some((pattern) => lower.includes(pattern));
}

/**
 * Check if a Content-Type header indicates JSON.
 */
function isJsonContentType(contentType: string | null): boolean {
  if (!contentType) return false;
  return contentType.includes("application/json");
}

/**
 * Attempt to parse JSON safely from a response body string.
 */
function tryParseJson(body: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(body);
    return typeof parsed === "object" && parsed !== null ? parsed : null;
  } catch {
    return null;
  }
}

/**
 * Check if parsed JSON contains structured error fields from our backend.
 */
function isStructuredBackendError(parsed: Record<string, unknown>): boolean {
  return !!(parsed.detail || parsed.message || parsed.error_code);
}

/**
 * Create a sanitized BACKEND_UNAVAILABLE response.
 * AC5: Adds X-Error-Source: proxy header.
 */
export function createUnavailableResponse(status?: number): NextResponse {
  const httpStatus =
    status && UNAVAILABLE_STATUSES.has(status) ? status : 503;
  const resp = NextResponse.json(BACKEND_UNAVAILABLE, { status: httpStatus });
  resp.headers.set("X-Error-Source", "proxy");
  return resp;
}

/**
 * Sanitize a proxy error response from backend/infrastructure.
 *
 * Returns a sanitized NextResponse if the response contains infrastructure
 * errors or non-JSON content. Returns null if the response is safe to
 * pass through (i.e., it's a structured backend error).
 *
 * AC1: Detects non-JSON responses
 * AC2: Detects 502/503/504 status codes
 * AC3: Detects "Application not found" (Railway)
 * AC4: Detects "Bad Gateway" (nginx)
 * AC5: Adds X-Error-Source: proxy header
 */
export function sanitizeProxyError(
  responseStatus: number,
  responseBody: string,
  contentType: string | null,
): NextResponse | null {
  // AC3/AC4: Check for infrastructure error patterns in body FIRST
  if (containsInfraError(responseBody)) {
    return createUnavailableResponse(responseStatus);
  }

  // AC1: Non-JSON content type on error responses
  if (!isJsonContentType(contentType) && responseStatus >= 400) {
    return createUnavailableResponse(responseStatus);
  }

  // AC2: 502/503/504 — check if body is structured backend error
  if (UNAVAILABLE_STATUSES.has(responseStatus)) {
    const parsed = tryParseJson(responseBody);
    if (parsed && isStructuredBackendError(parsed)) {
      // Structured backend error — safe to pass through
      return null;
    }
    // Not structured — sanitize
    return createUnavailableResponse(responseStatus);
  }

  return null; // Response is fine, don't intercept
}

/**
 * Sanitize a network/fetch error (connection refused, timeout, etc.).
 * AC5: Adds X-Error-Source: proxy header.
 */
export function sanitizeNetworkError(_error: unknown): NextResponse {
  return createUnavailableResponse(503);
}
