/**
 * STORY-260: Profile completeness proxy — requires auth.
 */
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { GET } = createProxyRoute({
  backendPath: "/v1/profile/completeness",
  requireAuth: true,
  errorMessage: "Erro ao obter completude do perfil",
});
