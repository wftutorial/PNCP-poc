/**
 * STORY-301: API proxy for email alerts CRUD.
 * GET /api/alerts → GET BACKEND_URL/v1/alerts
 * POST /api/alerts → POST BACKEND_URL/v1/alerts
 */
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { GET, POST } = createProxyRoute({
  backendPath: "/v1/alerts",
  methods: ["GET", "POST"],
  requireAuth: true,
  authRequiredMessage: "Autenticacao necessaria.",
  backendMissingMessage: "Servico temporariamente indisponivel",
  errorMessage: "Erro ao carregar alertas",
});
