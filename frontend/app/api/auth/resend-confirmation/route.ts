/**
 * GTM-FIX-009: Proxy for POST /v1/auth/resend-confirmation.
 * Resends signup confirmation email. No auth required.
 */
import { createProxyRoute } from "../../../../lib/create-proxy-route";

export const { POST } = createProxyRoute({
  backendPath: "/v1/auth/resend-confirmation",
  methods: ["POST"],
  requireAuth: false,
  errorMessage: "Erro temporário de comunicação",
});
