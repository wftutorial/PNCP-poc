/**
 * Billing portal session proxy — requires auth with token refresh, POST only.
 */
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { POST } = createProxyRoute({
  backendPath: "/v1/billing-portal",
  methods: ["POST"],
  requireAuth: true,
  allowRefresh: true,
  errorMessage: "Erro ao criar sessão do portal",
});
