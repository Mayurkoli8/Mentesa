# Design Document — Creative UI Overhaul

## Overview

This design elevates the visual craft of the Mentesa React app (`frontend-react/`)
without changing business logic, routing, or the data layer. It is a
presentation/interaction layer effort built on top of the existing CSS-variable
theme system and "boxy" design language.

The strategy has three layers:

1. **Design-system layer** — extend `index.css` with a small set of new tokens
   (focus ring, elevation, section spacing, motion duration) and a typography
   scale, plus a global `prefers-reduced-motion` guard. No token removal.
2. **Shared component layer** — add a handful of small, reusable React components
   (`PageHeader`, `EmptyState`, `ErrorState`, `Skeleton`) and standardize how
   pages compose `card` / `stat-tile` / buttons / inputs.
3. **Per-page polish** — apply the shared patterns to each page, fix
   theme-breaking hardcoded colors, and add restrained micro-interactions.

Hard constraints (from requirements): boxy radius (≤5px), dark+light parity via
tokens, accessibility, and zero feature regression.

## Architecture

```
index.css
  ├─ :root tokens         (existing + NEW: focus ring, elevation, motion, type scale)
  ├─ [data-theme=dark]    (existing + new token values)
  ├─ [data-theme=light]   (existing + new token values)
  ├─ base/typography      (refined scale, focus-visible, reduced-motion guard)
  ├─ helper classes       (card, stat-tile, btn, input, skeleton, toast, empty-state…)
  └─ boxy radius overrides (existing, unchanged)

src/components/
  ├─ PageHeader.jsx   (NEW)  title + subtitle + optional action, consistent rhythm
  ├─ EmptyState.jsx   (NEW)  icon + message + optional CTA
  ├─ ErrorState.jsx   (NEW)  message + retry button
  ├─ Skeleton.jsx     (NEW)  shape-approximating skeleton primitives
  ├─ Sidebar / Navbar / ThemeToggle / Logo  (refined, not rewritten)

src/pages/  (Landing, Login, Dashboard, CreateBot, Manage, ManageBot, Chat, Billing, MeetUs)
  └─ adopt PageHeader/EmptyState/ErrorState/Skeleton; token-only colors
```

No new dependencies. Icons continue to come from `lucide-react`. Theme stays in
`ThemeContext`; toasts stay in `ToastContext`.

## Design System Layer

### New CSS tokens (add to `:root` and both theme blocks)

| Token | Dark value | Light value | Purpose |
|-------|-----------|-------------|---------|
| `--focus-ring` | `rgba(0, 217, 217, 0.55)` | `rgba(0, 155, 155, 0.5)` | keyboard focus outline color (Req 9.1) |
| `--elev-1` | `0 1px 2px rgba(0,0,0,0.30)` | `0 1px 2px rgba(15,27,45,0.06)` | optional subtle lift (used sparingly; borders remain primary, Req 1.4) |
| `--surface-hover` | `#22324a` | `#f0f4f9` | hover fill for list rows / cards |
| `--accent-soft` | `rgba(0,217,217,0.12)` | `rgba(0,155,155,0.10)` | icon-chip backgrounds |
| `--section-gap` | `4rem` | `4rem` | vertical rhythm between landing sections |
| `--dur-fast` | `140ms` | — | hover/press transitions |
| `--dur-base` | `220ms` | — | standard transitions |
| `--dur-enter` | `360ms` | — | entrance animations (≤400ms, Req 3.3) |

Rationale: borders remain the primary separation method (Req 1.4); `--elev-1` is
available but used only where a floating element genuinely needs it (toasts,
sticky header). Durations are tokenized so motion is consistent and easy to
disable.

### Typography scale (Req 7.1)

Define utility classes in `index.css` so headings/body are consistent app-wide:

| Class | Size / weight / color |
|-------|----------------------|
| `.t-page-title` | 1.875rem (30px), 800, `--text-primary` |
| `.t-section` | 1.25rem (20px), 700, `--text-primary` |
| `.t-card-title` | 1rem (16px), 600, `--text-primary` |
| `.t-body` | 0.95rem, 400, `--text-secondary` |
| `.t-muted` | 0.8rem, 400, `--text-muted` |

Existing `h1/h2/h3` rules are kept; the classes give explicit control where
Tailwind text sizes are currently mixed inconsistently.

### Focus indicator (Req 9.1, 9.4)

Global rule:
```css
:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
/* remove only the default, never the focus-visible ring */
button:focus:not(:focus-visible) { outline: none; }
```

### Reduced-motion guard (Req 3.4, 5.3, 9.5)

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }
  .skeleton { animation: none; }
}
```

### Theming audit (Req 2.5, 2.6)

Replace theme-breaking fixed Tailwind palette utilities with tokens:
- `text-gray-400` / `text-gray-500` → `style={{ color: 'var(--text-muted)' }}` or `.t-muted`
- `hover:text-white` → token-based hover
- `border-white/5`, `bg-white/5` → `--border-soft`, `--hover-soft`
- `text-green-400` for success ticks → keep (semantic, acceptable) but prefer `--status-active`

Known offenders to fix: `ManageBot.jsx` (`text-gray-400`, `text-gray-500`,
`rounded-lg` sections, hardcoded `bg-secondary`), `Billing.jsx` (`text-gray-400`,
`rounded-full`/`rounded-lg`, `rgba(255,255,255,0.1)` borders), `MeetUs.jsx`
(`from-purple-400 to-pink-600` heading gradient is fine, but `text-gray-400`),
`Chat.jsx` minor, `Dashboard.jsx` (`rounded-lg`).

## Components and Interfaces

### `PageHeader.jsx` (Req 7.1, 7.4, 8)
```
props: { title, subtitle?, icon?, actions? }
renders: <header class="page-header">
  [icon chip] title (.t-page-title) / subtitle (.t-muted)   [actions right-aligned]
```
Used by Dashboard, Manage, CreateBot, Billing, ManageBot for consistent top rhythm
and a shared content container (`.page` wrapper: max-width + horizontal padding).

### `EmptyState.jsx` (Req 4)
```
props: { icon, title, description, action? (label+to/onClick) }
renders: centered card with accent icon chip, title, muted description, optional CTA button
```
Adopted by Dashboard (no bots), Manage (no bots / no search match), Chat (no bot,
no messages).

### `ErrorState.jsx` (Req 6.1, 6.4)
```
props: { message, onRetry }
renders: card with alert icon, message, "Try again" button -> calls onRetry
```
Adopted by any page whose initial data fetch can fail (Dashboard, Manage,
ManageBot, Billing, Chat bot list).

### `Skeleton.jsx` (Req 5.1, 5.2)
```
exports: <Skeleton h w radius/>, <SkeletonText lines/>, <SkeletonCard/>
all use the shared .skeleton class so shimmer + reduced-motion behavior is uniform
```
Replaces ad-hoc `<div className="skeleton" style={{height}}/>` blocks.

### Refined existing helpers (`index.css`)
- `.card-hover:hover` → border-color shift to `--accent-cyan` **and** background to
  `--surface-hover` (restrained, no transform > 3%, Req 3.5).
- `.btn-primary:active` / `.btn-secondary:active` → `transform: translateY(1px)`
  pressed state (Req 3.2).
- `.input-field:focus` → keep accent border, add focus-ring on `:focus-visible`.
- `.empty-state`, `.icon-chip`, `.page`, `.page-header` utility classes added.
- `.list-row` for Dashboard bot rows (consistent hover via `--surface-hover`).

## Per-Page Treatment

### Landing (Req 11.1)
- Already strong. Refinements: standardize section vertical rhythm with
  `--section-gap`; ensure the hero badge pill uses ≤4px radius via existing
  override; add `.t-section` to section headings; confirm blobs respect
  reduced-motion (they're static, fine). Footer + header logo already use `Logo`.
- Add `aria-label`s to icon-only/anchor nav where needed.

### Login (Req 11.2)
- Wrap card in consistent max-width; replace any `text-gray-*` with tokens;
  ensure inputs show focus ring; keep the centered, balanced layout.

### Dashboard (Req 4.2, 5, 6, 8.2)
- Use `PageHeader` (title + "New Bot" action).
- Stat tiles already use `.stat-tile`; add accent `.icon-chip` and entrance stagger.
- Loading → `SkeletonCard` rows; empty → `EmptyState`; fetch failure → `ErrorState`.
- Bot rows → `.list-row` with `--surface-hover` hover; squared icon chip.

### CreateBot
- Keep the 3-card stepper. Replace `rounded-lg`/`rounded-full` preset chips to
  honor boxy overrides; replace `bg-red-500/10` error block with a tokenized
  `.alert-error` helper. Add focus rings to inputs and dropzone. Bot icon chip
  uses `.icon-chip`.

### Manage (Req 4.2)
- `PageHeader`; `Skeleton` grid while loading; `EmptyState` (no bots) and a
  distinct empty for "no search match"; `ErrorState` on failure. Cards already
  boxy; standardize icon chip.

### ManageBot (Req 2.6, 8)
- Replace `text-gray-400/500`, inline `rounded-lg` sections, and ad-hoc
  `bg-secondary` with `.card` + tokens. Section headers use `.t-section`.
- Loading → skeleton; not-found → `ErrorState`-style. Copy/rotate keep toasts.

### Chat (Req 4.3, 4.4)
- Bot selector header stays. Empty (no bot) and empty (no messages) → `EmptyState`.
- Message bubbles already tokenized; add subtle entrance on new messages (respect
  reduced-motion). Keep typing indicator. Ensure select has focus ring + aria-label.

### Billing (Req 2.6, 6, 8.2)
- Replace `rgba(255,255,255,0.1)` borders and `text-gray-400` with tokens; plan
  cards use `.card`; current-plan panel uses `.card`; usage bar keeps pill.
- Loading → skeleton; load failure → `ErrorState`. Keep sync-on-return logic.

### MeetUs (Req 11.3)
- Convert to shared `.card` styling and tokens; keep team gradient avatars
  (boxy). Replace `text-gray-400` with `--text-muted`.

## Micro-Interactions & Motion (Req 3)

| Interaction | Spec |
|-------------|------|
| Card hover | border → accent, bg → `--surface-hover`, `--dur-fast`, no transform |
| Button hover | bg lighten, `--dur-fast` |
| Button press | `translateY(1px)`, instant |
| Nav link hover | bg `--hover-soft`, `--dur-fast` |
| Page/list entrance | `fadeIn` ≤ `--dur-enter`, optional 60ms stagger for grids |
| Icon action hover | opacity 0.7→1, `--dur-fast` |
| Reduced motion | all of the above collapse to ~0ms via the global guard |

No effect may shift layout or scale > 3% (Req 3.5).

## Accessibility (Req 9)

- Global `:focus-visible` ring (above).
- Every icon-only control gets `aria-label` (ThemeToggle already has one; add to
  Dashboard row actions, Chat send, Navbar hamburger/logout, copy/rotate buttons).
- Contrast: token values chosen so body text meets ≥4.5:1 and large text ≥3:1 in
  both themes (`--text-secondary`/`--text-muted` on `--bg-*` verified).
- All controls reachable/operable by keyboard; selects and buttons are native
  elements (already keyboard-friendly).
- No info conveyed by motion alone.

## Theming Approach (Req 2)

- All new styles reference tokens; no raw hex in JSX except inside gradient
  decorations that are theme-agnostic by design (e.g., team avatar gradients,
  blobs at low opacity).
- Add tokens (not hardcode) when a needed color is missing (Req 2.5).
- A grep pass for `text-gray-`, `bg-white/`, `border-white/`, `#fff`, `#1a2332`
  in `src/` guides the cleanup; replace with tokens.

## Data Models

This overhaul is presentation-only and introduces no new persistent data models.
It does define small in-memory prop contracts for the new shared components:

```ts
// PageHeader
{ title: string; subtitle?: string; icon?: ReactNode; actions?: ReactNode }

// EmptyState
{ icon: ReactNode; title: string; description?: string;
  action?: { label: string; to?: string; onClick?: () => void } }

// ErrorState
{ message: string; onRetry: () => void }

// Skeleton
{ h?: number|string; w?: number|string; radius?: string }   // + SkeletonText{lines}, SkeletonCard
```

No changes to bot, subscription, usage, or session shapes. All data continues to
flow through `src/utils/api.js`.

## Error Handling

- **Page data-fetch failure** (Req 6.1, 6.4): each page tracks an `error` state;
  when set, it renders `<ErrorState message onRetry={refetch}>` instead of content.
  `onRetry` re-invokes the same fetch function.
- **Action failure** (Req 6.2): create/delete/upload/rotate/checkout failures call
  `toast.error(...)` (existing `ToastContext`) — never `window.alert`.
- **Missing/forbidden resource** (e.g., ManageBot for a bot you don't own → 403):
  render an error card with a link back to Dashboard.
- **Theme of error UI** (Req 6.3): a tokenized `.alert-error` helper
  (`color`/`border`/`background` from tokens with a red status accent) replaces
  ad-hoc `bg-red-500/10` blocks so errors are legible in both themes.

## Correctness Properties

### Property 1: Theme parity invariant
For any route R and theme T ∈ {dark, light}, every text element on R has computed
color ≠ its background color (no invisible text).

**Validates: Requirements 2.2, 2.3**

### Property 2: Radius invariant
No overhauled element exceeds 5px border-radius except the theme-toggle
control/knob (999px).

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 3: No-regression invariant
The set of reachable features (auth, bot CRUD, chat, billing, embed/manage) before
and after is identical; only presentation differs.

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**

### Property 4: Motion-safety invariant
With `prefers-reduced-motion: reduce`, no element animates for longer than ~1ms and
no information is conveyed solely by motion.

**Validates: Requirements 3.4, 5.3, 9.5**

### Property 5: Focus-visibility invariant
Every keyboard-focusable control shows a focus ring meeting contrast against its
background.

**Validates: Requirements 9.1, 9.4**

## Testing Strategy

1. **Build**: `npm run build` in `frontend-react/` completes with no errors
   (Req 10.7). Run after each batch of edits.
2. **Theme parity**: toggle dark/light on every route; confirm legible text,
   visible borders, no invisible elements (Req 2).
3. **Empty/error/loading**: simulate no-bots, failed fetch (offline), and slow
   load to confirm the three states render via shared components (Req 4–6).
4. **Keyboard pass**: Tab through each page; confirm visible focus ring on every
   interactive element; activate controls with Enter/Space (Req 9.1, 9.4).
5. **Reduced motion**: enable OS "reduce motion"; confirm animations/shimmer stop
   (Req 3.4, 5.3, 9.5).
6. **Responsive**: at ≤768px confirm no horizontal overflow, sidebar collapses to
   hamburger overlay, grids reflow, touch targets ≥44px (Req 12).
7. **Regression**: manually exercise login, bot CRUD, chat send/history, billing
   display, ManageBot key/embed/upload (Req 10).

## Out of Scope

- Backend changes, new routes, data model changes.
- New third-party UI libraries.
- Rewriting auth, billing, RAG, or embed logic.
