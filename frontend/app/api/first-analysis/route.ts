/**
 * First analysis proxy — requires auth, POST only.
 */
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { POST } = createProxyRoute({
  backendPath: "/v1/first-analysis",
  methods: ["POST"],
  requireAuth: true,
  errorMessage: "Erro ao iniciar analise",
});
