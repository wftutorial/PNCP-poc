import { NextRequest, NextResponse } from "next/server";
import { sanitizeProxyError, sanitizeNetworkError } from "../../../../lib/proxy-error-handler";

const getBackendUrl = () => process.env.BACKEND_URL;

interface RouteContext {
  params: Promise<{ id: string }>;
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { id } = await context.params;
  const backendUrl = getBackendUrl();
  if (!backendUrl) {
    return NextResponse.json({ message: "Servidor nao configurado" }, { status: 503 });
  }

  const authHeader = request.headers.get("authorization");
  if (!authHeader) {
    return NextResponse.json({ message: "Autenticacao necessaria" }, { status: 401 });
  }

  try {
    const response = await fetch(`${backendUrl}/v1/organizations/${id}`, {
      headers: { Authorization: authHeader, "Content-Type": "application/json" },
    });

    if (!response.ok) {
      const body = await response.text();
      const sanitized = sanitizeProxyError(response.status, body, response.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(body);
        return NextResponse.json(
          { message: data.detail || "Erro ao obter organizacao" },
          { status: response.status },
        );
      } catch {
        return NextResponse.json({ message: "Erro temporario" }, { status: response.status });
      }
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching organization details:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { id } = await context.params;
  const backendUrl = getBackendUrl();
  if (!backendUrl) {
    return NextResponse.json({ message: "Servidor nao configurado" }, { status: 503 });
  }

  const authHeader = request.headers.get("authorization");
  if (!authHeader) {
    return NextResponse.json({ message: "Autenticacao necessaria" }, { status: 401 });
  }

  // Determine action from search params
  const { searchParams } = new URL(request.url);
  const action = searchParams.get("action");

  try {
    const body = await request.json();
    const endpoint =
      action === "invite"
        ? `${backendUrl}/v1/organizations/${id}/invite`
        : `${backendUrl}/v1/organizations/${id}`;

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { Authorization: authHeader, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const responseBody = await response.text();
      const sanitized = sanitizeProxyError(response.status, responseBody, response.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(responseBody);
        return NextResponse.json(
          { message: data.detail || "Erro ao processar solicitacao" },
          { status: response.status },
        );
      } catch {
        return NextResponse.json({ message: "Erro temporario" }, { status: response.status });
      }
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error posting to organization:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  const { id } = await context.params;
  const backendUrl = getBackendUrl();
  if (!backendUrl) {
    return NextResponse.json({ message: "Servidor nao configurado" }, { status: 503 });
  }

  const authHeader = request.headers.get("authorization");
  if (!authHeader) {
    return NextResponse.json({ message: "Autenticacao necessaria" }, { status: 401 });
  }

  // Member ID to remove comes from query param
  const { searchParams } = new URL(request.url);
  const memberId = searchParams.get("member_id");

  if (!memberId) {
    return NextResponse.json({ message: "member_id e obrigatorio" }, { status: 400 });
  }

  try {
    const response = await fetch(`${backendUrl}/v1/organizations/${id}/members/${memberId}`, {
      method: "DELETE",
      headers: { Authorization: authHeader },
    });

    if (!response.ok) {
      const responseBody = await response.text();
      const sanitized = sanitizeProxyError(response.status, responseBody, response.headers.get("content-type"));
      if (sanitized) return sanitized;
      try {
        const data = JSON.parse(responseBody);
        return NextResponse.json(
          { message: data.detail || "Erro ao remover membro" },
          { status: response.status },
        );
      } catch {
        return NextResponse.json({ message: "Erro temporario" }, { status: response.status });
      }
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error removing organization member:", error instanceof Error ? error.message : error);
    return sanitizeNetworkError(error);
  }
}
