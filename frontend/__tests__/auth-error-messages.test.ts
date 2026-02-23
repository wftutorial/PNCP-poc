/**
 * GTM-PROXY-001: Tests for centralized auth error translation.
 *
 * T2: Login with wrong password shows "Email ou senha incorretos"
 * T3: Signup with existing email shows "Este email já está cadastrado"
 *
 * AC4: "Invalid login credentials" → "Email ou senha incorretos"
 * AC5: "User already registered" → "Este email já está cadastrado"
 * AC6: "Email not confirmed" → "Confirme seu email antes de fazer login"
 * AC7: "Password should be at least 6 characters" → "A senha deve ter pelo menos 6 caracteres"
 * AC8: Centralized map in lib/error-messages.ts
 */

import { translateAuthError, AUTH_ERROR_MAP } from "../lib/error-messages";

describe("GTM-PROXY-001: Auth error translation (AC4-AC8)", () => {
  // AC4
  it("T2: translates 'Invalid login credentials' to PT", () => {
    const result = translateAuthError("Invalid login credentials");
    expect(result).toBe("Email ou senha incorretos");
  });

  // AC5
  it("T3: translates 'User already registered' to PT", () => {
    const result = translateAuthError("User already registered");
    expect(result).toBe("Este email já está cadastrado");
  });

  // AC6
  it("translates 'Email not confirmed' to PT", () => {
    const result = translateAuthError("Email not confirmed");
    expect(result).toBe("Confirme seu email antes de fazer login");
  });

  // AC7
  it("translates password policy error to PT", () => {
    const result = translateAuthError("Password should be at least 6 characters");
    expect(result).toBe("A senha deve ter pelo menos 6 caracteres");
  });

  // Additional translations
  it("translates 'Error sending magic link email' to PT", () => {
    const result = translateAuthError("Error sending magic link email");
    expect(result).toContain("cadastrado");
  });

  it("translates 'Email rate limit exceeded' to PT", () => {
    const result = translateAuthError("Email rate limit exceeded");
    expect(result).toContain("tentativas");
  });

  it("translates network errors to PT", () => {
    expect(translateAuthError("fetch failed")).toContain("conexão");
    expect(translateAuthError("Failed to fetch")).toContain("conexão");
    expect(translateAuthError("NetworkError")).toContain("conexão");
  });

  // Partial match
  it("partial match works for security rate limit", () => {
    const result = translateAuthError(
      "For security purposes, you can only request this after 30 seconds"
    );
    expect(result).toContain("segurança");
  });

  // Unknown error passthrough
  it("returns original message for unknown errors", () => {
    const result = translateAuthError("Some unknown error");
    expect(result).toBe("Some unknown error");
  });

  // AC8: Centralized map exists
  it("AUTH_ERROR_MAP is exported and has all required translations", () => {
    expect(AUTH_ERROR_MAP).toBeDefined();
    expect(AUTH_ERROR_MAP["Invalid login credentials"]).toBeTruthy();
    expect(AUTH_ERROR_MAP["User already registered"]).toBeTruthy();
    expect(AUTH_ERROR_MAP["Email not confirmed"]).toBeTruthy();
    expect(AUTH_ERROR_MAP["Password should be at least 6 characters"]).toBeTruthy();
  });

  // No English text in translated output
  it("translated messages never contain English auth jargon", () => {
    const englishErrors = [
      "Invalid login credentials",
      "User already registered",
      "Email not confirmed",
      "Password should be at least 6 characters",
      "Email rate limit exceeded",
    ];

    for (const err of englishErrors) {
      const translated = translateAuthError(err);
      expect(translated).not.toBe(err); // Must be translated, not passthrough
      expect(translated).not.toMatch(/invalid|credentials|registered|confirmed/i);
    }
  });
});
