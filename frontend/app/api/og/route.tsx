import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const type = searchParams.get("type");

  // SEO-PLAYBOOK P6: Analysis OG image
  if (type === "analise") {
    return renderAnaliseOG(searchParams);
  }

  // Default OG image
  return renderDefaultOG();
}

function renderAnaliseOG(searchParams: URLSearchParams) {
  const score = parseInt(searchParams.get("score") || "0", 10);
  const level = searchParams.get("level") || "media";
  const title = searchParams.get("title") || "Análise de Viabilidade";

  const levelLabel = level === "alta" ? "ALTA" : level === "media" ? "MÉDIA" : "BAIXA";
  const scoreColor = level === "alta" ? "#22C55E" : level === "media" ? "#EAB308" : "#9CA3AF";
  const scoreBg = level === "alta" ? "rgba(34,197,94,0.15)" : level === "media" ? "rgba(234,179,8,0.15)" : "rgba(156,163,175,0.15)";

  return new ImageResponse(
    (
      <div
        style={{
          width: "1200",
          height: "630",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #0A1E3F 0%, #0D2B5E 50%, #116DFF 100%)",
          fontFamily: "sans-serif",
          padding: "48px",
        }}
      >
        {/* SmartLic logo */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "24px" }}>
          <span style={{ fontSize: "36px", fontWeight: 700, color: "#FFFFFF", letterSpacing: "-1px" }}>
            SmartLic
          </span>
          <span style={{ fontSize: "14px", color: "#8BA3C7" }}>Análise de Viabilidade</span>
        </div>

        {/* Score circle */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "160px",
            height: "160px",
            borderRadius: "50%",
            border: `6px solid ${scoreColor}`,
            backgroundColor: scoreBg,
            marginBottom: "24px",
          }}
        >
          <span style={{ fontSize: "64px", fontWeight: 800, color: scoreColor }}>
            {score}
          </span>
        </div>

        {/* Level label */}
        <p style={{ fontSize: "28px", fontWeight: 700, color: scoreColor, margin: "0 0 24px 0" }}>
          {levelLabel} VIABILIDADE
        </p>

        {/* Bid title */}
        <p
          style={{
            fontSize: "24px",
            color: "#FFFFFF",
            textAlign: "center",
            maxWidth: "900px",
            margin: "0 0 32px 0",
            lineHeight: 1.3,
          }}
        >
          {title.length > 80 ? title.slice(0, 77) + "..." : title}
        </p>

        {/* Factor badges */}
        <div
          style={{
            display: "flex",
            gap: "16px",
            padding: "12px 24px",
            backgroundColor: "rgba(255,255,255,0.08)",
            borderRadius: "12px",
          }}
        >
          {["Modalidade 30%", "Prazo 25%", "Valor 25%", "Geo 20%"].map((f) => (
            <span key={f} style={{ fontSize: "16px", color: "#8BA3C7", fontWeight: 500 }}>
              {f}
            </span>
          ))}
        </div>

        {/* URL */}
        <p style={{ fontSize: "16px", color: "rgba(255,255,255,0.4)", marginTop: "24px" }}>
          smartlic.tech
        </p>
      </div>
    ),
    { width: 1200, height: 630 }
  );
}

function renderDefaultOG() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "1200",
          height: "630",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #0A1E3F 0%, #0D2B5E 50%, #116DFF 100%)",
          fontFamily: "sans-serif",
        }}
      >
        {/* Logo area */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            marginBottom: "32px",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: "4px",
              alignItems: "flex-end",
            }}
          >
            {[26, 22, 28, 24, 20].map((h, i) => (
              <div
                key={i}
                style={{
                  width: "8px",
                  height: `${h}px`,
                  backgroundColor: "#116DFF",
                  borderRadius: "2px",
                  opacity: 0.7 + i * 0.05,
                }}
              />
            ))}
          </div>
          <span
            style={{
              fontSize: "72px",
              fontWeight: 800,
              color: "#FFFFFF",
              letterSpacing: "-2px",
            }}
          >
            SmartLic
          </span>
        </div>

        {/* Tagline */}
        <p
          style={{
            fontSize: "32px",
            color: "#8BA3C7",
            margin: "0 0 48px 0",
          }}
        >
          Inteligência em Licitações Públicas
        </p>

        {/* Features bar */}
        <div
          style={{
            display: "flex",
            gap: "32px",
            padding: "16px 32px",
            backgroundColor: "rgba(255,255,255,0.08)",
            borderRadius: "12px",
          }}
        >
          {["15 Setores", "27 Estados", "Cobertura Nacional", "IA Avançada"].map(
            (feat) => (
              <span
                key={feat}
                style={{
                  fontSize: "20px",
                  color: "#FFD700",
                  fontWeight: 600,
                }}
              >
                {feat}
              </span>
            )
          )}
        </div>

        {/* URL */}
        <p
          style={{
            fontSize: "20px",
            color: "rgba(255,255,255,0.5)",
            marginTop: "32px",
          }}
        >
          smartlic.tech
        </p>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
