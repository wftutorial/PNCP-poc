/**
 * STORY-360 AC2: Plans pricing proxy.
 * Public endpoint (no auth required) — plan pricing is public info.
 */
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { GET } = createProxyRoute({
  backendPath: "/v1/plans",
  requireAuth: false,
  fetchCache: { revalidate: 300 },
  errorMessage: "Erro ao buscar planos.",
});
