/**
 * STORY-300: Security Headers Tests
 *
 * Tests CSP and security headers configuration.
 * Since Next.js middleware requires edge runtime APIs unavailable in jsdom,
 * we test the CSP policy content and next.config.js headers directly.
 *
 * AC1: CSP header configured in middleware.ts
 * AC2: CSP report-only mode
 * AC3: X-Content-Type-Options: nosniff
 * AC4: X-Frame-Options: DENY
 */

import fs from "fs";
import path from "path";

const middlewarePath = path.join(__dirname, "..", "middleware.ts");
const nextConfigPath = path.join(__dirname, "..", "next.config.js");

describe("STORY-300: Security Headers Configuration", () => {
  let middlewareSource: string;
  let nextConfigSource: string;

  beforeAll(() => {
    middlewareSource = fs.readFileSync(middlewarePath, "utf-8");
    nextConfigSource = fs.readFileSync(nextConfigPath, "utf-8");
  });

  describe("AC1: CSP header in middleware.ts", () => {
    it("should define addSecurityHeaders function", () => {
      expect(middlewareSource).toContain("function addSecurityHeaders");
    });

    it("should include default-src 'self' directive", () => {
      expect(middlewareSource).toContain("default-src 'self'");
    });

    it("should include Stripe in script-src", () => {
      expect(middlewareSource).toContain("https://js.stripe.com");
    });

    it("should include Sentry CDN in script-src", () => {
      expect(middlewareSource).toContain("https://cdn.sentry.io");
    });

    it("should include Supabase in connect-src", () => {
      expect(middlewareSource).toContain("https://*.supabase.co");
    });

    it("should include Supabase WebSocket in connect-src", () => {
      expect(middlewareSource).toContain("wss://*.supabase.co");
    });

    it("should include Stripe API in connect-src", () => {
      expect(middlewareSource).toContain("https://api.stripe.com");
    });

    it("should include Sentry ingest in connect-src", () => {
      expect(middlewareSource).toContain("https://*.sentry.io");
    });

    it("should include Mixpanel in connect-src", () => {
      expect(middlewareSource).toContain("https://api-js.mixpanel.com");
      expect(middlewareSource).toContain("https://api.mixpanel.com");
    });

    it("should include Stripe in frame-src", () => {
      expect(middlewareSource).toContain("frame-src");
      expect(middlewareSource).toContain("https://js.stripe.com");
    });

    it("should block object-src", () => {
      expect(middlewareSource).toContain("object-src 'none'");
    });

    it("should restrict base-uri", () => {
      expect(middlewareSource).toContain("base-uri 'self'");
    });

    it("should apply headers to API routes", () => {
      expect(middlewareSource).toContain(
        'addSecurityHeaders(NextResponse.next())'
      );
    });

    it("should apply headers to public routes", () => {
      // Verify addSecurityHeaders wraps public route responses
      const publicRouteReturn = middlewareSource.includes(
        "return addSecurityHeaders(NextResponse.next())"
      );
      expect(publicRouteReturn).toBe(true);
    });

    it("should apply headers to authenticated route responses", () => {
      expect(middlewareSource).toContain(
        "return addSecurityHeaders(NextResponse.next({"
      );
    });
  });

  describe("AC2: CSP Report-Only mode", () => {
    it("should use Content-Security-Policy-Report-Only in middleware", () => {
      expect(middlewareSource).toContain(
        "Content-Security-Policy-Report-Only"
      );
    });

    it("should NOT use enforcing Content-Security-Policy in middleware", () => {
      // Count occurrences of CSP header name - all should be Report-Only
      const enforceMatches = middlewareSource.match(
        /["']Content-Security-Policy["']/g
      );
      const reportOnlyMatches = middlewareSource.match(
        /Content-Security-Policy-Report-Only/g
      );

      // All CSP references should be report-only
      if (enforceMatches) {
        // Every "Content-Security-Policy" should be part of "Content-Security-Policy-Report-Only"
        expect(reportOnlyMatches!.length).toBeGreaterThanOrEqual(
          enforceMatches.length
        );
      }
    });

    it("should use Content-Security-Policy-Report-Only in next.config.js", () => {
      expect(nextConfigSource).toContain(
        "Content-Security-Policy-Report-Only"
      );
    });

    it("should NOT use enforcing CSP in next.config.js", () => {
      // The old enforcing header should be gone
      const lines = nextConfigSource.split("\n");
      const cspLines = lines.filter(
        (l) =>
          l.includes("Content-Security-Policy") &&
          !l.includes("Report-Only") &&
          !l.includes("//")
      );
      expect(cspLines.length).toBe(0);
    });
  });

  describe("AC3: X-Content-Type-Options", () => {
    it("should set X-Content-Type-Options: nosniff in middleware", () => {
      expect(middlewareSource).toContain("X-Content-Type-Options");
      expect(middlewareSource).toContain("nosniff");
    });

    it("should set X-Content-Type-Options in next.config.js", () => {
      expect(nextConfigSource).toContain("X-Content-Type-Options");
      expect(nextConfigSource).toContain("nosniff");
    });
  });

  describe("AC4: X-Frame-Options", () => {
    it("should set X-Frame-Options: DENY in middleware", () => {
      expect(middlewareSource).toContain("X-Frame-Options");
      expect(middlewareSource).toContain("DENY");
    });

    it("should set X-Frame-Options in next.config.js", () => {
      expect(nextConfigSource).toContain("X-Frame-Options");
      expect(nextConfigSource).toContain("DENY");
    });
  });

  describe("Additional security headers in middleware", () => {
    it("should set HSTS header", () => {
      expect(middlewareSource).toContain("Strict-Transport-Security");
      expect(middlewareSource).toContain("max-age=31536000");
    });

    it("should set Referrer-Policy", () => {
      expect(middlewareSource).toContain("Referrer-Policy");
      expect(middlewareSource).toContain("strict-origin-when-cross-origin");
    });

    it("should set Permissions-Policy", () => {
      expect(middlewareSource).toContain("Permissions-Policy");
      expect(middlewareSource).toContain("camera=()");
      expect(middlewareSource).toContain("microphone=()");
      expect(middlewareSource).toContain("geolocation=()");
    });

    it("should set X-XSS-Protection", () => {
      expect(middlewareSource).toContain("X-XSS-Protection");
      expect(middlewareSource).toContain("1; mode=block");
    });
  });

  describe("CSP completeness check", () => {
    it("should have matching CSP directives between middleware and next.config.js", () => {
      // Both should have the same directives
      const requiredDirectives = [
        "default-src",
        "script-src",
        "style-src",
        "img-src",
        "font-src",
        "connect-src",
        "frame-src",
        "object-src",
        "base-uri",
      ];

      for (const directive of requiredDirectives) {
        expect(middlewareSource).toContain(directive);
        expect(nextConfigSource).toContain(directive);
      }
    });
  });
});
