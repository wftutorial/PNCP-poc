"use client";

type ViewMode = "personal" | "team";

export function DashboardViewToggle({
  viewMode,
  setViewMode,
  userOrg,
  teamLoading,
}: {
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  userOrg: { id: string; name: string; user_role: string } | null;
  teamLoading: boolean;
}) {
  if (!userOrg) return null;

  return (
    <>
      <div className="flex items-center gap-2 mb-4" data-testid="team-toggle">
        <button
          onClick={() => setViewMode("personal")}
          className={`px-3 py-1.5 text-sm rounded-button transition-colors ${
            viewMode === "personal"
              ? "bg-[var(--brand-blue)] text-white"
              : "bg-[var(--surface-1)] text-[var(--ink-secondary)]"
          }`}
          data-testid="toggle-personal"
        >
          Meus dados
        </button>
        <button
          onClick={() => setViewMode("team")}
          className={`px-3 py-1.5 text-sm rounded-button transition-colors ${
            viewMode === "team"
              ? "bg-[var(--brand-blue)] text-white"
              : "bg-[var(--surface-1)] text-[var(--ink-secondary)]"
          }`}
          data-testid="toggle-team"
        >
          Dados da equipe
        </button>
        {viewMode === "team" && (
          <span className="text-xs text-[var(--ink-muted)] ml-1">{userOrg.name}</span>
        )}
      </div>

      {viewMode === "team" && teamLoading && (
        <div
          className="flex items-center gap-2 mb-4 text-sm text-[var(--ink-secondary)]"
          data-testid="team-loading"
        >
          <div className="w-4 h-4 border-2 border-[var(--brand-blue)] border-t-transparent rounded-full animate-spin" />
          Carregando dados da equipe...
        </div>
      )}
    </>
  );
}
