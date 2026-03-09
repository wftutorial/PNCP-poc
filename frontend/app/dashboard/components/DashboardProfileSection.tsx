"use client";

import type { Session } from "@supabase/supabase-js";
import ProfileCompletionPrompt from "../../../components/ProfileCompletionPrompt";
import ProfileProgressBar from "../../../components/ProfileProgressBar";
import ProfileCongratulations from "../../../components/ProfileCongratulations";

export function DashboardProfileHeaderControls({
  profilePct,
}: {
  profilePct: number | null;
}) {
  if (profilePct === null || profilePct >= 100) return null;

  return (
    <ProfileProgressBar
      percentage={profilePct}
      size={40}
      onClickNext={() => {
        const el = document.querySelector("[data-testid='profile-completion-prompt']");
        if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
      }}
    />
  );
}

export function DashboardProfileSection({
  session,
  profilePct,
  onProfileUpdated,
}: {
  session: Session | null;
  profilePct: number | null;
  onProfileUpdated: (pct: number) => void;
}) {
  if (!session) return null;

  if (profilePct === 100) {
    return (
      <div className="mb-6">
        <ProfileCongratulations />
      </div>
    );
  }

  if (profilePct !== null && profilePct !== 100) {
    return (
      <div className="mb-6">
        {/* AC13: "Completar perfil" link above the prompt */}
        <div className="flex items-center justify-end mb-2">
          <a href="/conta#perfil" className="text-sm text-[var(--brand-blue)] hover:underline">
            Completar perfil →
          </a>
        </div>
        <ProfileCompletionPrompt
          accessToken={session.access_token}
          onProfileUpdated={onProfileUpdated}
        />
      </div>
    );
  }

  return null;
}
