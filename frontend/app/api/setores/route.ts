/**
 * Setores proxy — public endpoint.
 */
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { GET } = createProxyRoute({
  backendPath: "/v1/setores",
  requireAuth: false,
  errorMessage: "Erro ao buscar setores",
});
