# PRD: Responsive Design Overhaul

## Introduction

MemoryBank currently has minimal responsive design — mostly desktop-centric layouts with basic flexbox/grid fallbacks. The app breaks or becomes unusable in phone landscape, tablet orientations, and various screen sizes. This PRD covers a full responsive pass across all views, adding a collapsible hamburger navigation and ensuring usability from phone portrait through desktop.

## Goals

- Make all views usable and visually correct across phone (portrait + landscape), tablet (portrait + landscape), and desktop
- Replace per-view navbar duplication with a single responsive navigation component (hamburger menu on small screens)
- Ensure data-heavy views (admin tables, expense lists) remain accessible on small screens via horizontal scroll
- Maintain existing visual design — this is a layout/responsiveness fix, not a redesign

## User Stories

### US-001: Shared Responsive Navigation Component
**Description:** As a user, I want a consistent navigation bar across all pages that collapses into a hamburger menu on small screens so I can navigate the app on any device.

**Acceptance Criteria:**
- [ ] Create a reusable `AppNavbar.vue` component used by all views
- [ ] On desktop (>=1024px): horizontal nav with branding, links, profile/logout
- [ ] On tablet/phone (<1024px): hamburger icon that toggles a slide-out or dropdown menu
- [ ] Menu closes when a link is clicked or user taps outside
- [ ] Current route is visually indicated (active state)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill at 375px, 768px, and 1280px widths

### US-002: Responsive Login View
**Description:** As a user, I want the login page to look correct on all screen sizes and orientations so I can sign in from any device.

**Acceptance Criteria:**
- [ ] Login card centers vertically and horizontally on all screen sizes
- [ ] Card does not overflow viewport in phone landscape (short height)
- [ ] Form inputs and button are touch-friendly (min 44px tap targets)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill at 667px x 375px (phone landscape) and 375px x 667px (phone portrait)

### US-003: Responsive Dashboard View
**Description:** As a user, I want the dashboard group cards to reflow properly on all screen sizes so I can browse my groups on any device.

**Acceptance Criteria:**
- [ ] Group card grid adapts: 1 column on phone, 2 on tablet, 3+ on desktop
- [ ] Cards don't overflow or get clipped in landscape orientation
- [ ] Balance summary section stacks vertically on small screens if needed
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill at 375px, 768px, and 1280px widths

### US-004: Responsive Group Detail View
**Description:** As a user, I want the group detail page (expenses, balances, settlements, debts) to be usable on small screens so I can manage expenses from my phone.

**Acceptance Criteria:**
- [ ] Tab/section navigation is horizontally scrollable or wraps on small screens
- [ ] Expense list items stack content vertically on narrow screens (no horizontal overflow)
- [ ] Balance and debt summaries reflow to single-column on phone
- [ ] Action buttons (add expense, settle) remain accessible and don't overlap content
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill at 375px, 768px, and 1280px widths

### US-005: Responsive Modal Forms (Add/Edit Expense, Settlement)
**Description:** As a user, I want modal forms to be usable on small screens and in landscape orientation so I can add expenses from my phone.

**Acceptance Criteria:**
- [ ] Modals take full width on screens <480px (with small margin)
- [ ] Modal content scrolls vertically when it exceeds viewport height (phone landscape)
- [ ] Form inputs have adequate spacing and touch-friendly sizing (min 44px)
- [ ] Submit/cancel buttons are always visible (sticky footer or scroll into view)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill at 375px x 667px and 667px x 375px

### US-006: Responsive Profile View
**Description:** As a user, I want the profile page to work on all screen sizes so I can update my settings from any device.

**Acceptance Criteria:**
- [ ] Avatar upload area and form fields stack vertically on phone
- [ ] API key section doesn't overflow on narrow screens (truncate or wrap key text)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill at 375px and 768px widths

### US-007: Responsive Admin View
**Description:** As an admin, I want admin data tables to be accessible on small screens via horizontal scrolling so I can manage data on a tablet.

**Acceptance Criteria:**
- [ ] Tables wrap in a horizontally scrollable container on small screens
- [ ] Table headers remain readable (no extreme column compression)
- [ ] Add/edit forms within admin adapt to narrow screens
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill at 375px and 768px widths

### US-008: Global Responsive Utilities and Breakpoints
**Description:** As a developer, I need consistent breakpoint variables and base responsive styles so all views use the same responsive behavior.

**Acceptance Criteria:**
- [ ] Define CSS custom properties or variables for breakpoints: phone (<768px), tablet (768px-1023px), desktop (>=1024px)
- [ ] Add base styles in `main.css` or `base.css`: box-sizing border-box globally, viewport meta tag confirmed in index.html
- [ ] Add utility class for horizontal scroll containers (`.table-scroll-container`)
- [ ] Typecheck passes

## Functional Requirements

- FR-1: Create `AppNavbar.vue` component with responsive hamburger menu below 1024px breakpoint
- FR-2: Replace all per-view navbar implementations with `AppNavbar.vue`
- FR-3: All interactive elements must have minimum 44px touch targets on mobile
- FR-4: Modals must scroll internally when content exceeds viewport height
- FR-5: Tables in admin view must be wrapped in horizontally scrollable containers
- FR-6: Define three breakpoints: phone (<768px), tablet (768px-1023px), desktop (>=1024px)
- FR-7: No layout overflow (horizontal scrollbar on body) at any standard screen size
- FR-8: Viewport meta tag must be set correctly: `<meta name="viewport" content="width=device-width, initial-scale=1">`

## Non-Goals

- No visual redesign (colors, typography, branding stay the same)
- No new features or functionality changes
- No CSS framework adoption (no Tailwind, Bootstrap, etc.)
- No responsive images or art direction for different screen sizes
- No hiding table columns on small screens (horizontal scroll is sufficient)
- No offline/PWA support

## Design Considerations

- Keep the existing color scheme (#42b883 primary green, #2c3e50 dark text)
- Hamburger menu should animate open/closed (simple CSS transition)
- Use existing flexbox/grid approach — enhance with media queries, don't rewrite
- Modal overlay should dim background consistently across sizes

## Technical Considerations

- All styles are scoped per-component — shared responsive styles should go in `base.css` or `main.css`
- No CSS preprocessor in use — stick with vanilla CSS custom properties
- `AppNavbar.vue` needs access to auth store (for user info, logout, isStaff)
- `AppNavbar.vue` needs access to router (for active route detection, navigation)
- Test on Chrome DevTools device emulation for phone/tablet/desktop breakpoints

## Success Metrics

- No horizontal body overflow at any viewport width from 320px to 1920px
- All views usable (readable, navigable, interactive) at 375px wide (phone portrait)
- All views usable at 667px x 375px (phone landscape)
- Hamburger menu opens/closes without layout shift
- Modal forms completable on phone in both orientations

## Open Questions

- Should the hamburger menu be a slide-out drawer or a dropdown overlay?
- Should the group detail view use tabs or accordion sections on mobile?
