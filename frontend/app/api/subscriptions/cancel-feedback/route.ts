/**
 * Subscription cancel feedback proxy — requires auth with token refresh, POST only.
 */
import { createProxyRoute } from "../../../../lib/create-proxy-route";

export const { POST } = createProxyRoute({
  backendPath: "/v1/api/subscriptions/cancel-feedback",
  methods: ["POST"],
  requireAuth: true,
  allowRefresh: true,
  errorMessage: "Erro temporário de comunicação",
});
