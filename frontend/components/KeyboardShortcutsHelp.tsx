"use client";

import { useState, useEffect } from "react";
import { Dialog } from "../app/components/Dialog";
import { useKeyboardShortcuts, getShortcutDisplay, type KeyboardShortcut } from "../hooks/useKeyboardShortcuts";

/**
 * A shortcut entry for display in the help overlay.
 */
export interface ShortcutEntry {
  /** Human-readable label for the shortcut action */
  label: string;
  /** The shortcut definition (from useKeyboardShortcuts) */
  shortcut: Pick<KeyboardShortcut, "key" | "ctrlKey" | "metaKey" | "shiftKey" | "altKey">;
}

/**
 * A group of related shortcuts.
 */
export interface ShortcutGroup {
  /** Category title, e.g. "Busca", "Navegação", "Ações" */
  title: string;
  shortcuts: ShortcutEntry[];
}

/**
 * Default shortcut groups covering the app-wide shortcuts available in /buscar.
 * Consumer pages can pass their own `groups` prop to customise.
 */
export const DEFAULT_SHORTCUT_GROUPS: ShortcutGroup[] = [
  {
    title: "Busca",
    shortcuts: [
      { label: "Executar análise", shortcut: { key: "k", ctrlKey: true } },
      { label: "Executar análise (alternativo)", shortcut: { key: "Enter", ctrlKey: true } },
      { label: "Selecionar todos os estados", shortcut: { key: "a", ctrlKey: true } },
    ],
  },
  {
    title: "Navegação",
    shortcuts: [
      { label: "Limpar seleção", shortcut: { key: "Escape" } },
      { label: "Mostrar atalhos", shortcut: { key: "/" } },
    ],
  },
];

interface KeyboardShortcutsHelpProps {
  /** Pass custom shortcut groups; defaults to DEFAULT_SHORTCUT_GROUPS */
  groups?: ShortcutGroup[];
  /** Controlled open state — use with onOpenChange for external trigger */
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

/**
 * KeyboardShortcutsHelp
 *
 * Displays a modal listing all keyboard shortcuts grouped by category.
 *
 * Usage (self-contained — triggered by "?" key):
 *   <KeyboardShortcutsHelp />
 *
 * Usage (controlled — triggered externally):
 *   <KeyboardShortcutsHelp open={show} onOpenChange={setShow} />
 */
export function KeyboardShortcutsHelp({
  groups = DEFAULT_SHORTCUT_GROUPS,
  open,
  onOpenChange,
}: KeyboardShortcutsHelpProps) {
  const [internalOpen, setInternalOpen] = useState(false);

  // Support both controlled and uncontrolled modes
  const isOpen = open !== undefined ? open : internalOpen;
  const setOpen = (value: boolean) => {
    if (onOpenChange) {
      onOpenChange(value);
    } else {
      setInternalOpen(value);
    }
  };

  // Register "?" shortcut to open when in uncontrolled mode
  useKeyboardShortcuts({
    enabled: open === undefined, // only self-manage when uncontrolled
    shortcuts: [
      {
        key: "?",
        action: () => setOpen(true),
        description: "Mostrar atalhos de teclado",
      },
    ],
  });

  return (
    <Dialog
      isOpen={isOpen}
      onClose={() => setOpen(false)}
      title="Atalhos de Teclado"
      className="max-w-lg"
      id="keyboard-shortcuts-help"
    >
      <div className="space-y-6">
        {groups.map((group) => (
          <section key={group.title}>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--ink-muted)] mb-2">
              {group.title}
            </h3>
            <ul className="space-y-0">
              {group.shortcuts.map((entry, idx) => (
                <li
                  key={entry.label}
                  className={`flex items-center justify-between py-2.5 ${
                    idx < group.shortcuts.length - 1
                      ? "border-b border-[var(--border)]"
                      : ""
                  }`}
                >
                  <span className="text-sm text-[var(--ink)]">{entry.label}</span>
                  <kbd className="ml-4 px-2.5 py-1 bg-[var(--surface-2)] rounded text-sm font-[var(--font-data,monospace)] border border-[var(--border)] text-[var(--ink)] whitespace-nowrap">
                    {getShortcutDisplay({
                      key: entry.shortcut.key,
                      ctrlKey: entry.shortcut.ctrlKey,
                      metaKey: entry.shortcut.metaKey,
                      shiftKey: entry.shortcut.shiftKey,
                      altKey: entry.shortcut.altKey,
                      action: () => {},
                      description: entry.label,
                    })}
                  </kbd>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <button
        type="button"
        onClick={() => setOpen(false)}
        className="mt-6 w-full px-4 py-2.5 rounded-button bg-[var(--brand-blue)] text-white text-sm font-semibold hover:bg-[var(--brand-blue-hover)] transition-colors"
      >
        Entendi
      </button>
    </Dialog>
  );
}
