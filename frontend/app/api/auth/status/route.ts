/**
 * GTM-FIX-009: Proxy for GET /v1/auth/status?email=...
 * Checks if a signup email has been confirmed. No auth required.
 */
import { createProxyRoute } from "../../../../lib/create-proxy-route";

export const { GET } = createProxyRoute({
  backendPath: "/v1/auth/status",
  methods: ["GET"],
  requireAuth: false,
  errorMessage: "Erro temporário de comunicação",
});
