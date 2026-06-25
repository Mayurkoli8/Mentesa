# Implementation Plan — Creative UI Overhaul

## Overview

This plan implements the creative UI overhaul as a presentation-only effort:
first establish the design-system layer and shared components (tasks 1–3), then
apply them page by page (tasks 4–9), then audit theming/responsiveness and verify
(tasks 10–11). Every task references requirements and ends with a build check.

## Tasks

- [x] 1. Extend the design-system layer in `index.css`
  - Add new tokens (`--focus-ring`, `--elev-1`, `--surface-hover`, `--accent-soft`, `--section-gap`, `--dur-fast`, `--dur-base`, `--dur-enter`) to `:root` and both `[data-theme=dark]` and `[data-theme=light]` blocks with the values from the design
  - Add typography utility classes (`.t-page-title`, `.t-section`, `.t-card-title`, `.t-body`, `.t-muted`)
  - Add global `:focus-visible` ring rule and `button:focus:not(:focus-visible)` reset
  - Add the `@media (prefers-reduced-motion: reduce)` guard (disable animations/transitions/shimmer)
  - Add helper classes: `.page`, `.page-header`, `.icon-chip`, `.list-row`, `.empty-state`, `.alert-error`
  - Add `:active` pressed states to `.btn-primary` / `.btn-secondary` and refine `.card-hover` (border + `--surface-hover`, no transform)
  - Verify `npm run build` succeeds
  - _Requirements: 1.4, 2.1, 2.5, 3.1, 3.2, 3.4, 3.5, 7.1, 7.2, 9.1, 9.5_

- [x] 2. Create shared presentation components
- [x] 2.1 Create `src/components/Skeleton.jsx`
  - Export `Skeleton` ({h,w,radius}), `SkeletonText` ({lines}), `SkeletonCard`
  - All use the shared `.skeleton` class
  - _Requirements: 5.1, 5.2, 5.3_
- [x] 2.2 Create `src/components/PageHeader.jsx`
  - Props: `{ title, subtitle?, icon?, actions? }`; uses `.page-header`, `.t-page-title`, `.t-muted`, `.icon-chip`
  - _Requirements: 7.1, 7.4, 8.5_
- [x] 2.3 Create `src/components/EmptyState.jsx`
  - Props: `{ icon, title, description?, action? }`; renders centered `.card` with accent icon chip and optional CTA (Link or button)
  - _Requirements: 4.1, 4.5_
- [x] 2.4 Create `src/components/ErrorState.jsx`
  - Props: `{ message, onRetry }`; renders `.card` with alert icon, message, and a "Try again" button calling `onRetry`
  - _Requirements: 6.1, 6.3, 6.4_

- [x] 3. Refine the authenticated shell (Sidebar + Navbar)
  - Sidebar: confirm active-link uses token styling; add `aria-label`s where needed; token-only colors
  - Navbar: add `aria-label`s to hamburger and logout; ensure avatar/identity/toggle spacing uses tokens; focus rings visible
  - Verify `npm run build`
  - _Requirements: 8.3, 8.4, 9.1, 9.2, 9.4_

- [x] 4. Overhaul Dashboard
  - Replace inline header with `PageHeader` (title + "New Bot" action)
  - Use `SkeletonCard`/`Skeleton` for loading; `EmptyState` for no bots; `ErrorState` for fetch failure (track `error`, add `retry`)
  - Convert bot rows to `.list-row` with squared `.icon-chip`; replace `rounded-lg` with boxy tokens
  - Add `aria-label`s to row action icon buttons; entrance stagger on the list
  - Verify build + manual dark/light check
  - _Requirements: 3.3, 4.1, 4.2, 5.1, 6.1, 7.1, 8.1, 8.2, 9.2_

- [x] 5. Overhaul Manage
  - Use `PageHeader`; `Skeleton` grid while loading; `EmptyState` for no bots and a distinct empty for no-search-match; `ErrorState` on failure
  - Standardize card icon chips and tokens
  - _Requirements: 4.1, 4.2, 5.1, 6.1, 8.1_

- [x] 6. Overhaul Chat
  - Replace no-bot and no-messages blank areas with `EmptyState`
  - Add `aria-label` to the bot `select` and send button; ensure select shows focus ring
  - Add restrained entrance on new messages (reduced-motion safe); token-only colors
  - _Requirements: 3.3, 4.3, 4.4, 9.2, 9.4_

- [x] 7. Overhaul ManageBot
  - Replace `text-gray-400/500` and ad-hoc `bg-secondary`/`rounded-lg` sections with `.card` + tokens; section titles use `.t-section`
  - Loading skeleton; not-found/forbidden → error card with link back to Dashboard
  - Add `aria-label`s to copy/rotate icon buttons (keep toasts on success)
  - _Requirements: 2.6, 6.1, 6.2, 7.1, 8.1, 9.2, 10.5_

- [x] 8. Overhaul Billing
  - Replace `rgba(255,255,255,0.1)` borders and `text-gray-400` with tokens; plan + current-plan panels use `.card`
  - Loading skeleton; load failure → `ErrorState`; keep checkout/sync/portal logic intact
  - _Requirements: 2.6, 5.1, 6.1, 8.1, 8.2, 10.4_

- [x] 9. Polish public pages (Landing, Login, MeetUs)
  - Landing: apply `--section-gap` rhythm, `.t-section` headings, `aria-label`s on nav; confirm boxy pills
  - Login: token-only colors, input focus rings, balanced centered layout
  - MeetUs: convert to shared `.card` + tokens; replace `text-gray-400`
  - _Requirements: 8.1, 9.1, 9.2, 11.1, 11.2, 11.3, 11.5_

- [x] 10. Theme + responsiveness audit and cleanup
  - Grep `src/` for `text-gray-`, `bg-white/`, `border-white/`, `#fff`, `#1a2332`, `#7a8a9e`; replace theme-breaking instances with tokens
  - Verify each route at ≤768px: no horizontal overflow, sidebar collapses to hamburger overlay, grids reflow, touch targets ≥44px
  - _Requirements: 2.6, 12.1, 12.2, 12.3, 12.4_

- [x] 11. Final verification pass
  - Run `npm run build` (must pass)
  - Toggle dark/light on every route; confirm parity (Property 1)
  - Keyboard pass: visible focus ring on all controls; operate via keyboard (Property 5)
  - Enable reduced-motion; confirm animations/shimmer stop (Property 4)
  - Regression check: login, bot CRUD, chat send/history, billing display, ManageBot key/embed/upload (Property 3)
  - _Requirements: 2.2, 2.3, 2.4, 3.4, 9.1, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5, 10.7_

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": ["1"] },
    { "wave": 2, "tasks": ["2.1", "2.2", "2.3", "2.4"] },
    { "wave": 3, "tasks": ["3", "4", "5", "6", "7", "8", "9"] },
    { "wave": 4, "tasks": ["10"] },
    { "wave": 5, "tasks": ["11"] }
  ]
}
```

```
1 (design-system layer)
└─> 2 (shared components: 2.1 Skeleton, 2.2 PageHeader, 2.3 EmptyState, 2.4 ErrorState)
     ├─> 3 (shell: Sidebar + Navbar)
     ├─> 4 (Dashboard)
     ├─> 5 (Manage)
     ├─> 6 (Chat)
     ├─> 7 (ManageBot)
     ├─> 8 (Billing)
     └─> 9 (public pages)

10 (theme + responsive audit)  depends on -> 3,4,5,6,7,8,9
11 (final verification)        depends on -> 10
```

- Task 1 must complete first (tokens/classes everything else uses).
- Task 2 sub-tasks can be done in any order but before pages that consume them.
- Tasks 3–9 are independent of each other and may be done in any order / parallel.
- Tasks 10 and 11 are the closing audit/verification gates.

## Notes

- Presentation-only: do not change routing, auth, billing, RAG, or embed logic.
- After each page task, run `npm run build` and spot-check dark/light.
- Prefer editing shared classes in `index.css` over per-page inline styles.
- Keep all colors token-driven; add a token (dark+light) rather than hardcoding.

