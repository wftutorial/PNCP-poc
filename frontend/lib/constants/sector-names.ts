/**
 * Sector Display Names Mapping
 *
 * Canonical mapping of sector slugs to Portuguese display names.
 * Used across the application for human-readable sector labels.
 *
 * Single source of truth — imported by:
 * - Dashboard analytics (sector charts)
 * - Histórico page (session sector display)
 * - Any component that displays sector names
 *
 * All 15 sectors defined in backend/sectors_data.yaml.
 */

export const SECTOR_DISPLAY_NAMES: Record<string, string> = {
  vestuario: "Vestuário e Uniformes",
  alimentos: "Alimentos e Merenda",
  informatica: "Hardware e Equipamentos de TI",
  mobiliario: "Mobiliário",
  papelaria: "Papelaria e Material de Escritório",
  engenharia: "Engenharia, Projetos e Obras",
  software: "Software e Sistemas",
  facilities: "Facilities e Manutenção",
  saude: "Saúde",
  vigilancia: "Vigilância e Segurança Patrimonial",
  transporte: "Transporte e Veículos",
  manutencao_predial: "Manutenção e Conservação Predial",
  engenharia_rodoviaria: "Engenharia Rodoviária e Infraestrutura Viária",
  materiais_eletricos: "Materiais Elétricos e Instalações",
  materiais_hidraulicos: "Materiais Hidráulicos e Saneamento",
} as const;

/**
 * Maps a sector slug to its display name.
 * Returns the raw slug as fallback for unknown sectors (AC3).
 */
export function getSectorDisplayName(slug: string): string {
  return SECTOR_DISPLAY_NAMES[slug] || slug;
}
