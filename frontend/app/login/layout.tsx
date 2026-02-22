import { Metadata } from "next";

// GTM-COPY-006 AC5: Per-page metadata for /login
export const metadata: Metadata = {
  title: "Acesse Suas Análises",
  description:
    "Entre na sua conta SmartLic para acessar análises de viabilidade, pipeline de oportunidades e relatórios de licitações.",
  alternates: {
    canonical: "https://smartlic.tech/login",
  },
  robots: {
    index: false,
    follow: true,
  },
};

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
