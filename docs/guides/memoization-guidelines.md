# Memoization Guidelines — SmartLic Frontend

## When to Use `React.memo`

Wrap a component in `React.memo` when:
- It receives **stable primitive props** (strings, numbers, booleans) that rarely change
- It's rendered in a **list** (e.g., `AlertCard`, `StatCard`)
- Its parent re-renders frequently but its own props stay the same

Do NOT use `React.memo` when:
- The component receives **new objects/arrays** every render (memo comparison always fails)
- The component is lightweight (the memoization check costs more than re-rendering)
- The component has **internal state** that changes frequently

## When to Use `useMemo`

Use `useMemo` for:
- **Derived data** from props/state used in rendering (e.g., `new Set(selected)`, chart data transformations)
- **Expensive computations** (sorting, filtering, mapping large arrays)
- **Objects/arrays passed to child components** (prevents unnecessary child re-renders)

Do NOT use `useMemo` for:
- Simple string concatenations or number arithmetic
- Values used only in event handlers (not in rendering)
- Constants defined outside the component

## When to Use `useCallback`

Use `useCallback` for:
- **Event handlers** passed to memoized child components
- **Functions** used as dependencies in other hooks (e.g., fetch functions in `useEffect`)
- **Callbacks** passed to third-party libraries (e.g., chart tooltip renderers)

## Current Patterns in Codebase

| Page | Memoization | Details |
|------|------------|---------|
| `dashboard/page.tsx` | `useMemo` (2), `useCallback` (3), `React.memo` (StatCard) | Chart data + CSV export + ChartTooltip |
| `alertas/page.tsx` | `useCallback` (1), `useMemo` (1), `React.memo` (AlertCard) | fetchAlerts + selectedSet |
| `buscar/page.tsx` | `useMemo` (7), `useCallback` (7) | Most memoized page |
| `DashboardCharts.tsx` | `React.memo` (ChartTooltip) | Memoized tooltip prevents re-creation on hover |

## Rules of Thumb

1. **Measure first** — Use React DevTools Profiler before adding memoization
2. **Memoize at boundaries** — Focus on parent-child prop boundaries, not internal computations
3. **Avoid premature optimization** — 3 similar lines of code > 1 premature useMemo
4. **Keep dependency arrays minimal** — More deps = more comparisons = less benefit
