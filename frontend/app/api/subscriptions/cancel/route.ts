/**
 * UX-308: Subscription cancel proxy — requires auth with token refresh, POST only.
 */
import { createProxyRoute } from "../../../../lib/create-proxy-route";

export const { POST } = createProxyRoute({
  backendPath: "/v1/api/subscriptions/cancel",
  methods: ["POST"],
  requireAuth: true,
  allowRefresh: true,
  errorMessage: "Erro temporário de comunicação",
});
