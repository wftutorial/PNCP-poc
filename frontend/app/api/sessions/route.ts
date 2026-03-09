/**
 * Sessions proxy — requires auth with token refresh.
 */
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { GET } = createProxyRoute({
  backendPath: "/v1/sessions",
  requireAuth: true,
  allowRefresh: true,
  errorMessage: "Erro ao carregar historico",
});
