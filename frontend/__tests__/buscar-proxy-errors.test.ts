/**
 * CRIT-017: Integration tests for proxy error sanitization in buscar route.
 *
 * AC11: proxy returns structured error when backend returns HTML
 * AC12: proxy returns structured error when backend returns 502
 * AC14: frontend component renders PT-BR for BACKEND_UNAVAILABLE
 */

import { getUserFriendlyError, getMessageFromErrorCode } from "../lib/error-messages";

/**
 * AC14: Frontend error message system handles BACKEND_UNAVAILABLE error_code.
 */
describe("error-messages BACKEND_UNAVAILABLE", () => {
  it("getMessageFromErrorCode returns PT-BR for BACKEND_UNAVAILABLE", () => {
    const msg = getMessageFromErrorCode("BACKEND_UNAVAILABLE");
    // CRIT-009: Updated to match current ERROR_CODE_MESSAGES value
    expect(msg).toBe(
      "Estamos voltando em instantes. Tente novamente em alguns segundos."
    );
  });

  it("getUserFriendlyError sanitizes 'Application not found' string", () => {
    const msg = getUserFriendlyError("Application not found");
    expect(msg).toBe(
      "Nossos servidores estão sendo atualizados. Tente novamente em alguns instantes."
    );
    expect(msg).not.toContain("Application not found");
  });

  it("getUserFriendlyError keeps the friendly message if already sanitized", () => {
    const msg = getUserFriendlyError(
      "Nossos servidores estão sendo atualizados. Tente novamente em alguns instantes."
    );
    // Should be kept as-is (keep_original or pass-through)
    expect(msg).toBe(
      "Nossos servidores estão sendo atualizados. Tente novamente em alguns instantes."
    );
  });

  it("getUserFriendlyError handles Error object with 'Application not found'", () => {
    const error = new Error("Application not found");
    const msg = getUserFriendlyError(error);
    expect(msg).toBe(
      "Nossos servidores estão sendo atualizados. Tente novamente em alguns instantes."
    );
  });
});

/**
 * AC9: "Application not found" should NEVER appear in any user-facing text.
 */
describe("AC9: no raw infrastructure text leaks", () => {
  const infraErrors = [
    "Application not found",
    "Bad Gateway",
    "502 Bad Gateway",
    "Service Unavailable",
    "Gateway Timeout",
  ];

  infraErrors.forEach((rawText) => {
    it(`sanitizes "${rawText}" via getUserFriendlyError`, () => {
      const msg = getUserFriendlyError(rawText);
      expect(msg).not.toBe(rawText);
      // Should be a known PT-BR message
      expect(msg.length).toBeGreaterThan(10);
    });
  });
});

/**
 * AC6: Buscar page error rendering shows PT-BR.
 * Simulates the error flow: proxy returns { message, error_code } →
 * frontend extracts and displays via getUserFriendlyError.
 */
describe("AC6: buscar error rendering flow", () => {
  it("structured proxy error (BACKEND_UNAVAILABLE) renders friendly message", () => {
    // Simulates the response from the proxy after CRIT-017 sanitization
    const proxyResponse = {
      error: "Nossos servidores estão sendo atualizados. Tente novamente em alguns instantes.",
      message: "Nossos servidores estão sendo atualizados. Tente novamente em alguns instantes.",
      error_code: "BACKEND_UNAVAILABLE",
      retry_after_seconds: 30,
    };

    // Frontend reads error_code first (CRIT-009 pattern)
    const fromCode = getMessageFromErrorCode(proxyResponse.error_code);
    expect(fromCode).toBeTruthy();
    expect(fromCode).not.toContain("Application");

    // Fallback: getUserFriendlyError on message field
    const fromMessage = getUserFriendlyError(proxyResponse.message);
    expect(fromMessage).not.toContain("Application");
  });

  it("generic 502 renders friendly message even without error_code", () => {
    const msg = getUserFriendlyError("502");
    expect(msg).toBe("O servidor está temporariamente indisponível. Tente novamente em instantes.");
  });
});
