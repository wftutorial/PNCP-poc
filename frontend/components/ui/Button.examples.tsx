/**
 * DEBT-006: Button Component — All Variants & States Reference
 *
 * This file documents every variant, size, and state combination
 * available in the shared Button component.
 *
 * Usage: Import and render <ButtonExamples /> in a dev/storybook route,
 * or reference this file for copy-paste patterns.
 */

import { Button } from "./button";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-ink-secondary uppercase tracking-wide">{title}</h3>
      <div className="flex flex-wrap items-center gap-3">{children}</div>
    </div>
  );
}

export function ButtonExamples() {
  return (
    <div className="p-8 space-y-8 max-w-4xl">
      <h2 className="text-2xl font-bold text-ink">Button Component — Design System</h2>

      {/* Variants */}
      <Section title="Variants">
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="destructive">Destructive</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="link">Link</Button>
      </Section>

      {/* Sizes */}
      <Section title="Sizes">
        <Button size="sm">Small</Button>
        <Button size="default">Default</Button>
        <Button size="lg">Large</Button>
        <Button size="icon" aria-label="Settings">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </Button>
      </Section>

      {/* Loading */}
      <Section title="Loading State">
        <Button loading>Saving...</Button>
        <Button variant="secondary" loading>Loading...</Button>
        <Button variant="destructive" loading>Deleting...</Button>
      </Section>

      {/* Disabled */}
      <Section title="Disabled State">
        <Button disabled>Disabled Primary</Button>
        <Button variant="secondary" disabled>Disabled Secondary</Button>
        <Button variant="destructive" disabled>Disabled Destructive</Button>
      </Section>

      {/* Icon-Only (requires aria-label) */}
      <Section title="Icon-Only (aria-label required)">
        <Button size="icon" aria-label="Close" variant="ghost">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </Button>
        <Button size="icon" aria-label="Search" variant="primary">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </Button>
        <Button size="icon" aria-label="Delete" variant="destructive">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </Button>
      </Section>

      {/* With Icons */}
      <Section title="With Icons (text + icon)">
        <Button>
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Item
        </Button>
        <Button variant="destructive">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Delete
        </Button>
        <Button variant="outline">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download
        </Button>
      </Section>

      {/* All Variant × Size Combinations */}
      <Section title="Full Matrix (Variant × Size)">
        <div className="grid gap-3">
          {(["primary", "secondary", "destructive", "ghost", "outline", "link"] as const).map(variant => (
            <div key={variant} className="flex items-center gap-3">
              <span className="w-24 text-xs font-mono text-ink-muted">{variant}</span>
              <Button variant={variant} size="sm">Small</Button>
              <Button variant={variant} size="default">Default</Button>
              <Button variant={variant} size="lg">Large</Button>
            </div>
          ))}
        </div>
      </Section>
    </div>
  );
}
