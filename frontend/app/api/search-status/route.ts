/**
 * CRIT-003 AC11: Proxy for search status polling endpoint.
 *
 * GET /api/search-status?search_id=xxx → backend GET /v1/search/{search_id}/status
 */

import type { NextRequest } from "next/server";
import { createProxyRoute } from "../../../lib/create-proxy-route";

export const { GET } = createProxyRoute({
  backendPath: (request: NextRequest) => {
    const searchId = new URL(request.url).searchParams.get("search_id") || "";
    return `/v1/search/${encodeURIComponent(searchId)}/status`;
  },
  methods: ["GET"],
  requireAuth: false,
  forwardQuery: false,
  errorMessage: "Erro temporário de comunicação",
});
