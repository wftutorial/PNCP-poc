import LandingNavbar from "@/app/components/landing/LandingNavbar";
import AjudaFaqClient from "./components/AjudaFaqClient";

/**
 * STORY-226 AC25-AC28: FAQ / Central de Ajuda
 *
 * Server Component shell: renders the static outer wrapper and navbar.
 * All interactive FAQ content (hero with search, accordion, category filter)
 * is handled by AjudaFaqClient ("use client").
 */
export default function AjudaPage() {
  return (
    <div className="min-h-screen bg-[var(--canvas)]">
      <LandingNavbar />
      <AjudaFaqClient />
    </div>
  );
}
