# Requirements Document

## Introduction

The Creative UI Overhaul elevates the visual craft, polish, and consistency of the Mentesa web application (`frontend-react/`) without altering its existing functionality, theme system, or "boxy" design language. The goal is to make the product feel professionally designed and intentional (not "AI-generated") across every page (Landing, Login, Dashboard, CreateBot, Manage, ManageBot, Chat, Billing, Meet Us) and shared component (Sidebar, Navbar, ThemeToggle, Logo, cards, stat tiles, toasts, skeletons).

This effort is purely presentational and interaction-level. It introduces refined micro-interactions, designed empty/loading/error states, consistent spacing and typography rhythm, and a richer shared component vocabulary, all while honoring four hard constraints: (1) the boxy aesthetic (small border-radius, flat borders, squared corners, restrained hovers); (2) full dark and light theme parity driven by CSS variables with no theme-breaking hardcoded colors; (3) accessibility (keyboard, focus, contrast, motion, semantics); and (4) zero regression of existing features (auth, bot CRUD, chat, billing, embed).

## Glossary

- **App**: The Mentesa React single-page application located in `frontend-react/`.
- **Boxy_Design_Language**: The established visual style using small border-radius tokens (`--radius-sm` 2px through `--radius-lg`/xl 4–5px enforced in `index.css`), flat 1px borders, squared corners, and restrained hover treatments.
- **Theme_System**: The CSS-variable-based theming applied via the `data-theme` attribute on the document root, supporting `dark` (default) and `light` values, defined in `frontend-react/src/index.css`.
- **Theme_Token**: A CSS custom property such as `--text-primary`, `--bg-secondary`, `--accent-cyan`, `--border-soft`, used to keep styling theme-adaptive.
- **Accent_Color**: The cyan brand color exposed via `--accent-cyan` (and theme-specific variants), `#00d9d9` in dark, `#009b9b` in light.
- **Shared_Component**: A reusable UI element or helper class used across pages: Sidebar, Navbar, ThemeToggle, Logo, and the `card`, `card-hover`, `stat-tile`, `brand-gradient`, `logo-mark`, `glass`, `skeleton`, `toast` classes.
- **Page**: A top-level route view in `frontend-react/src/pages/`: Landing, Login, Home, Dashboard, CreateBot, Manage, ManageBot, Chat, Billing, Meet Us.
- **Empty_State**: The view a Page or component renders when there is no data to display (e.g., no bots, no messages, no usage).
- **Loading_State**: The view rendered while asynchronous data is being fetched, typically using skeleton placeholders.
- **Error_State**: The view rendered when an asynchronous operation fails.
- **Micro_Interaction**: A small, purposeful animation or feedback effect on user action (hover, focus, press, transition, appearance).
- **Reduced_Motion_Preference**: The user's operating-system setting exposed via the `prefers-reduced-motion` CSS media query.
- **Focus_Indicator**: A visible visual treatment shown on an interactive element when it receives keyboard focus.
- **Design_Reviewer**: The role (developer or designer) who verifies the overhaul against the constraints and acceptance criteria.
- **Developer**: The person implementing or maintaining the App.
- **End_User**: A person using the deployed App in a browser.
- **Contrast_Ratio**: The WCAG luminance contrast ratio between foreground and background colors.

## Requirements

### Requirement 1: Preserve the Boxy Design Language

**User Story:** As an End_User, I want the refreshed interface to keep its distinctive squared, flat look, so that the product retains its recognizable identity while feeling more polished.

#### Acceptance Criteria

1. THE App SHALL apply border-radius values to all visual elements using only the established radius Theme_Tokens (`--radius-sm`, `--radius-md`, `--radius-lg`) or the boxy override values defined in `index.css` (maximum 5px for standard surfaces).
2. WHERE an element is a pill, badge, or progress bar, THE App SHALL constrain its border-radius to a maximum of 4px.
3. WHERE an element is the theme toggle control or its knob, THE App SHALL retain a fully circular (999px) border-radius.
4. THE App SHALL render container surfaces (cards, tiles, inputs, buttons, panels) with flat 1px borders using the `--border-soft` Theme_Token rather than heavy drop shadows as the primary separation method.
5. IF a new visual element is introduced during the overhaul, THEN THE App SHALL style that element with squared corners consistent with the Boxy_Design_Language.

### Requirement 2: Maintain Dark and Light Theme Parity

**User Story:** As an End_User, I want every refreshed screen to look correct in both dark and light mode, so that I can use my preferred theme without visual defects.

#### Acceptance Criteria

1. THE App SHALL express all foreground, background, border, and accent colors for overhauled elements using Theme_Tokens defined in the Theme_System.
2. WHEN the active theme is `dark`, THE App SHALL render every overhauled Page and Shared_Component with legible text and visible boundaries using the dark Theme_Token values.
3. WHEN the active theme is `light`, THE App SHALL render every overhauled Page and Shared_Component with legible text and visible boundaries using the light Theme_Token values.
4. WHEN the End_User toggles the theme, THE App SHALL update all overhauled elements to the selected theme without requiring a page reload.
5. IF a color value is required that is not covered by an existing Theme_Token, THEN THE Developer SHALL add a new Theme_Token with both dark and light values rather than hardcoding a theme-specific color.
6. THE App SHALL NOT apply fixed Tailwind palette color utilities (for example `text-gray-400`) where those colors fail to adapt across both themes.

### Requirement 3: Refined Micro-Interactions

**User Story:** As an End_User, I want subtle, responsive feedback when I interact with controls, so that the interface feels crafted and responsive rather than static.

#### Acceptance Criteria

1. WHEN the End_User hovers over an interactive element (button, card, navigation link, icon action), THE App SHALL provide a restrained visual response consistent with the Boxy_Design_Language within 200ms.
2. WHEN the End_User presses an interactive button, THE App SHALL provide a visible pressed-state response.
3. WHEN a Page or list of items first renders, THE App SHALL animate the appearance of primary content using an entrance transition no longer than 400ms.
4. WHILE the Reduced_Motion_Preference is enabled, THE App SHALL disable or substantially reduce non-essential motion and transitions.
5. THE App SHALL keep hover and transition effects restrained, avoiding scale jumps larger than 3% and avoiding effects that obscure content or shift surrounding layout.

### Requirement 4: Designed Empty States

**User Story:** As an End_User, I want helpful and visually considered screens when there is no data, so that I understand what to do next instead of seeing a blank area.

#### Acceptance Criteria

1. WHERE a Page or component can render with no data, THE App SHALL display an Empty_State containing an icon or illustration, an explanatory message, and, where an action applies, a primary call-to-action control.
2. WHEN the Dashboard or Manage Page has zero bots, THE App SHALL display an Empty_State that links to the bot creation flow.
3. WHEN the Chat Page has no messages for the selected bot, THE App SHALL display an Empty_State that prompts the End_User to start a conversation.
4. WHEN the Chat Page has no selected bot available, THE App SHALL display an Empty_State that guides the End_User to select or create a bot.
5. THE App SHALL style all Empty_States using Theme_Tokens and the Boxy_Design_Language so that they render correctly in both themes.

### Requirement 5: Consistent Loading States

**User Story:** As an End_User, I want consistent loading placeholders while data loads, so that the interface feels stable and intentional during waits.

#### Acceptance Criteria

1. WHILE asynchronous data for a Page is being fetched, THE App SHALL display skeleton placeholders that approximate the shape and layout of the content being loaded.
2. THE App SHALL render all skeleton placeholders using the shared `skeleton` helper styling so that loading treatment is visually consistent across Pages.
3. WHILE the Reduced_Motion_Preference is enabled, THE App SHALL render skeleton placeholders without the shimmer animation.
4. WHEN asynchronous data finishes loading, THE App SHALL replace skeleton placeholders with the loaded content using a transition no longer than 400ms.

### Requirement 6: Visible Error States

**User Story:** As an End_User, I want clear feedback when something fails to load or save, so that I know an error occurred and how to recover.

#### Acceptance Criteria

1. IF an asynchronous data fetch for a Page fails, THEN THE App SHALL display an Error_State that communicates that loading failed and offers a retry control.
2. IF a user-initiated action fails, THEN THE App SHALL surface a toast notification using the existing toast styling rather than a native browser alert.
3. THE App SHALL style all Error_States and error toasts using Theme_Tokens so that they render correctly in both themes.
4. WHEN an Error_State retry control is activated, THE App SHALL re-attempt the failed operation.

### Requirement 7: Typography and Spacing Consistency

**User Story:** As an End_User, I want consistent text sizing and spacing across the app, so that the interface looks cohesive and deliberately designed.

#### Acceptance Criteria

1. THE App SHALL apply a consistent typographic hierarchy for page titles, section headings, body text, and muted secondary text across all overhauled Pages.
2. THE App SHALL apply consistent spacing between sections, cards, and controls using the established spacing Theme_Tokens (`--spacing-xs` through `--spacing-xl`).
3. THE App SHALL render secondary and muted text using the `--text-secondary` and `--text-muted` Theme_Tokens rather than theme-specific hardcoded colors.
4. THE App SHALL align page-level content using a consistent content container width and horizontal padding across overhauled authenticated Pages.

### Requirement 8: Shared Component Consistency

**User Story:** As a Developer, I want shared components and helper classes to present a consistent look, so that pages composed from them feel unified without per-page overrides.

#### Acceptance Criteria

1. THE App SHALL render cards across all Pages using the shared `card` and `card-hover` helper classes rather than ad hoc per-page card styling.
2. THE App SHALL render statistic tiles using the shared `stat-tile` helper styling across all Pages that display metrics.
3. WHEN a navigation destination is active, THE Sidebar SHALL indicate the active state using the established active-link Theme_Token styling.
4. THE Navbar SHALL present the user avatar, identity, theme toggle, and logout control with consistent spacing and Theme_Token styling in both themes.
5. WHERE a new reusable visual pattern is created during the overhaul, THE Developer SHALL implement it as a shared helper class or component rather than duplicating styles per Page.

### Requirement 9: Accessibility Compliance

**User Story:** As an End_User who relies on assistive technology or keyboard navigation, I want the refreshed interface to remain operable and perceivable, so that the visual polish does not reduce usability.

#### Acceptance Criteria

1. WHEN an interactive element receives keyboard focus, THE App SHALL display a visible Focus_Indicator that meets a minimum contrast against its background.
2. THE App SHALL provide text alternatives (accessible labels) for icon-only controls introduced or modified during the overhaul.
3. THE App SHALL maintain a text-to-background Contrast_Ratio of at least 4.5:1 for normal body text and at least 3:1 for large text in both themes.
4. THE App SHALL allow all interactive controls modified during the overhaul to be reached and operated using the keyboard.
5. WHILE the Reduced_Motion_Preference is enabled, THE App SHALL ensure that no information is conveyed solely through motion.

### Requirement 10: Feature Preservation (No Regression)

**User Story:** As an End_User, I want all existing functionality to keep working after the visual overhaul, so that the redesign improves appearance without breaking what I rely on.

#### Acceptance Criteria

1. THE App SHALL preserve the existing authentication flow (login, protected routes, logout) after the overhaul.
2. THE App SHALL preserve bot create, read, update, and delete operations after the overhaul.
3. THE App SHALL preserve chat message sending, history loading, and bot selection after the overhaul.
4. THE App SHALL preserve billing plan display, usage display, and subscription actions after the overhaul.
5. THE App SHALL preserve the bot management capabilities (API key display, embed snippet, knowledge management) after the overhaul.
6. THE App SHALL route all backend data operations through the existing `src/utils/api.js` client after the overhaul.
7. WHEN the App is built with `npm run build` in `frontend-react/`, THE build SHALL complete without errors after the overhaul.

### Requirement 11: Landing and Public Page Polish

**User Story:** As a prospective End_User, I want the public Landing, Login, and Meet Us pages to look professionally crafted, so that my first impression of the product is strong.

#### Acceptance Criteria

1. THE App SHALL present the Landing Page with a cohesive hero, feature, and call-to-action structure styled with Theme_Tokens and the Boxy_Design_Language.
2. THE App SHALL render the Login Page with a visually balanced, centered authentication layout that adapts to both themes.
3. THE App SHALL render the Meet Us Page using consistent card and layout styling shared with the rest of the App.
4. WHEN the End_User views a public Page on a viewport width of 768px or less, THE App SHALL present a responsive layout without horizontal overflow.
5. THE App SHALL display the brand logo and name consistently across public Pages and the authenticated Shell.

### Requirement 12: Responsive Layout Integrity

**User Story:** As an End_User on varied screen sizes, I want every overhauled screen to remain usable and uncluttered, so that I can use the product on mobile and desktop.

#### Acceptance Criteria

1. WHEN the End_User views an overhauled Page at a viewport width of 768px or less, THE App SHALL present its content without horizontal overflow.
2. WHILE the viewport width is 768px or less, THE App SHALL collapse the Sidebar into the existing hamburger-triggered overlay navigation.
3. WHEN the End_User views grids of cards or tiles at narrow widths, THE App SHALL reflow them into fewer columns rather than truncating content.
4. THE App SHALL preserve touch-target sizing of at least 44px by 44px for primary interactive controls on small viewports.
