import { Metadata } from "next";
import { FaqStructuredData } from "./FaqStructuredData";

// GTM-COPY-006 AC5: Per-page metadata for /ajuda
export const metadata: Metadata = {
  title: "Perguntas Frequentes sobre Análise de Licitações",
  description:
    "Tire dúvidas sobre como avaliar licitações, filtros por setor, fontes de dados oficiais, pagamentos e conta no SmartLic.",
  alternates: {
    canonical: "https://smartlic.tech/ajuda",
  },
};

// GTM-COPY-006 AC6: FAQPage JSON-LD structured data
export default function AjudaLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <FaqStructuredData />
      {children}
    </>
  );
}
