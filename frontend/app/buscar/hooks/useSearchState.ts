"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
import { checkHasLastSearch } from "../../../lib/lastSearchCache";
import { safeSetItem, safeGetItem } from "../../../lib/storage";

export interface UseSearchStateReturn {
  // Upgrade modal
  showUpgradeModal: boolean;
  setShowUpgradeModal: (v: boolean) => void;
  upgradeSource: string | undefined;
  handleShowUpgradeModal: (_plan?: string, source?: string) => void;

  // Keyboard help
  showKeyboardHelp: boolean;
  setShowKeyboardHelp: (v: boolean) => void;

  // Filter panel visibility
  customizeOpen: boolean;
  setCustomizeOpen: (v: boolean) => void;

  // First-use tip
  showFirstUseTip: boolean;
  setShowFirstUseTip: (v: boolean) => void;
  dismissFirstUseTip: () => void;

  // Results drawer
  drawerOpen: boolean;
  setDrawerOpen: (v: boolean) => void;

  // Profile / history flags (memo, read-once on mount)
  hasSearchedBefore: boolean;
  isProfileComplete: boolean;

  // Last search availability
  lastSearchAvailable: boolean;
  setLastSearchAvailable: (v: boolean) => void;

  // PDF modal
  pdfLoading: boolean;
  setPdfLoading: (v: boolean) => void;
  pdfModalOpen: boolean;
  setPdfModalOpen: (v: boolean) => void;
}

/**
 * DEBT-FE-001: Extracted from useSearchOrchestration.
 * Owns all UI-layer state — modals, panel visibility, tips, PDF modal.
 */
export function useSearchState(): UseSearchStateReturn {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeSource, setUpgradeSource] = useState<string | undefined>();
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);

  // ── Profile / history ────────────────────────────────────────────────
  const hasSearchedBefore = useMemo(() => {
    return safeGetItem('smartlic-has-searched') === 'true';
  }, []);

  const isProfileComplete = useMemo(() => {
    try {
      const cached = safeGetItem('profileContext');
      if (!cached) return false;
      const ctx = JSON.parse(cached);
      return !!(ctx.porte_empresa && ctx.ufs_atuacao?.length > 0);
    } catch { return false; }
  }, []);

  // ── Filter panel ─────────────────────────────────────────────────────
  // UX-417 AC4: Filters visible by default (open on first access and always)
  const [customizeOpen, setCustomizeOpen] = useState(() => {
    const current = safeGetItem('smartlic:buscar:filters-expanded');
    if (current !== null) return current === 'true';
    return true;
  });

  useEffect(() => {
    safeSetItem('smartlic:buscar:filters-expanded', String(customizeOpen));
  }, [customizeOpen]);

  // ── First-use tip ────────────────────────────────────────────────────
  const [showFirstUseTip, setShowFirstUseTip] = useState(() => {
    return safeGetItem('smartlic-has-searched') !== 'true'
      && safeGetItem('smartlic-first-tip-dismissed') !== 'true';
  });

  const dismissFirstUseTip = useCallback(() => {
    setShowFirstUseTip(false);
    safeSetItem('smartlic-first-tip-dismissed', 'true');
  }, []);

  // ── Misc UI ──────────────────────────────────────────────────────────
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [lastSearchAvailable, setLastSearchAvailable] = useState(() => checkHasLastSearch());
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfModalOpen, setPdfModalOpen] = useState(false);

  const handleShowUpgradeModal = useCallback((_plan?: string, source?: string) => {
    setUpgradeSource(source);
    setShowUpgradeModal(true);
  }, []);

  return {
    showUpgradeModal,
    setShowUpgradeModal,
    upgradeSource,
    handleShowUpgradeModal,
    showKeyboardHelp,
    setShowKeyboardHelp,
    customizeOpen,
    setCustomizeOpen,
    showFirstUseTip,
    setShowFirstUseTip,
    dismissFirstUseTip,
    drawerOpen,
    setDrawerOpen,
    hasSearchedBefore,
    isProfileComplete,
    lastSearchAvailable,
    setLastSearchAvailable,
    pdfLoading,
    setPdfLoading,
    pdfModalOpen,
    setPdfModalOpen,
  };
}
