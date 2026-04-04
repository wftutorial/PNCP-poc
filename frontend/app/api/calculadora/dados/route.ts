import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const setor = searchParams.get("setor");
  const uf = searchParams.get("uf");

  if (!setor || !uf) {
    return NextResponse.json(
      { message: "Parâmetros 'setor' e 'uf' são obrigatórios" },
      { status: 400 }
    );
  }

  try {
    const resp = await fetch(
      `${BACKEND_URL}/v1/calculadora/dados?setor=${encodeURIComponent(setor)}&uf=${encodeURIComponent(uf)}`,
      {
        headers: { "Content-Type": "application/json" },
        next: { revalidate: 3600 },
      }
    );

    if (!resp.ok) {
      const detail = await resp.text();
      return NextResponse.json(
        { message: detail || "Erro ao buscar dados" },
        { status: resp.status }
      );
    }

    const data = await resp.json();
    return NextResponse.json(data, {
      headers: { "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=7200" },
    });
  } catch (error) {
    return NextResponse.json(
      { message: "Erro de conexão com o servidor" },
      { status: 502 }
    );
  }
}
