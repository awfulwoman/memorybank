# PRD: MemoryBank — Shared Expense Splitting App

## Introduction

MemoryBank is a self-hosted web application that allows two or more people to share financial expenses and split them fairly. Users organize expenses into groups (e.g. Household, Vacation, Friends), record who paid what, and the app calculates who owes whom. Settlements can be recorded within the app to zero out balances. Built with Django + Vue, deployed via Docker.

## Goals

- Provide a self-hosted Splitwise alternative for small groups (under 10 users)
- Allow flexible expense splitting (equal or custom) within groups
- Track balances per-group and across all groups per user
- Support recording settlements to resolve debts
- Expose a REST API for programmatic access
- Ship as a Docker Compose stack for easy self-hosting

## User Stories

### US-001: Admin creates user accounts
**Description:** As an admin, I want to create and manage user accounts so that only authorized people can use the app.

**Acceptance Criteria:**
- [ ] Admin can create a user with username, display name, and password
- [ ] Admin can edit/deactivate user accounts
- [ ] Users can log in with username/password
- [ ] Users can update their own display name and avatar
- [ ] Typecheck/lint passes

### US-002: User uploads avatar
**Description:** As a user, I want to set a custom avatar so others can identify me visually.

**Acceptance Criteria:**
- [ ] User can upload an image as avatar from profile page
- [ ] Avatar stored on backend filesystem, served via API
- [ ] Default avatar shown if none uploaded
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-003: Admin manages categories
**Description:** As an admin, I want to define expense categories centrally so users can tag their expenses consistently.

**Acceptance Criteria:**
- [ ] Admin console lists all categories
- [ ] Admin can create, edit, and delete categories
- [ ] Categories available in expense creation dropdown
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-004: Admin manages group types
**Description:** As an admin, I want to define group types (Vacation, Household, Friends, etc.) so groups can be categorized.

**Acceptance Criteria:**
- [ ] Admin console lists all group types
- [ ] Admin can create, edit, and delete group types
- [ ] Group types selectable when creating/editing a group
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-005: Admin manages currencies
**Description:** As an admin, I want to define available currencies so groups can be assigned the correct currency.

**Acceptance Criteria:**
- [ ] Admin console lists all currencies (name, symbol, code)
- [ ] Admin can create, edit, and delete currencies
- [ ] Typecheck/lint passes

### US-006: Admin creates and manages groups
**Description:** As an admin, I want to create expense groups so users can track expenses separately for different contexts.

**Acceptance Criteria:**
- [ ] Admin can create a group with name, group type, and currency
- [ ] Admin can add/remove members to a group
- [ ] Admin can set a default split method for the group (equal or custom percentages)
- [ ] A default group exists for new installations
- [ ] Non-admin users cannot create or delete groups
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-007: Add an expense to a group
**Description:** As a user, I want to add an expense so the group can track who paid for what.

**Acceptance Criteria:**
- [ ] Expense form captures: amount, description, date, category, optional receipt image
- [ ] Expense records which user added it
- [ ] User can choose equal split or custom split among group members
- [ ] Custom split allows specifying exact amounts or percentages per member
- [ ] Default split method from group settings pre-selected
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-008: Edit an expense
**Description:** As a user, I want to edit an expense I entered so I can correct mistakes.

**Acceptance Criteria:**
- [ ] User can edit any field of an expense they created
- [ ] Editing recalculates balances for all affected members
- [ ] Edit history or last-modified timestamp visible
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-009: View group balances
**Description:** As a user, I want to see how much each person owes or is owed within a group so we know who needs to pay whom.

**Acceptance Criteria:**
- [ ] Group page shows net balance for each member (positive = owed, negative = owes)
- [ ] Shows simplified debt list: "Alice owes Bob $25"
- [ ] Balances update immediately after expense changes
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-010: Record a settlement
**Description:** As a user, I want to record a payment/settlement so that balances reflect money that has changed hands.

**Acceptance Criteria:**
- [ ] User can record "I paid X amount to Y person" within a group
- [ ] Settlement adjusts balances accordingly
- [ ] Settlements visible in group expense list (visually distinct from expenses)
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-011: View user profile with cross-group balances
**Description:** As a user, I want to see my total balances across all groups so I know my overall debts/credits with each person.

**Acceptance Criteria:**
- [ ] Profile page shows per-person net balance aggregated across all groups
- [ ] Shows breakdown by group if expanded
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-012: Upload receipt image
**Description:** As a user, I want to attach a photo of a receipt to an expense for record-keeping.

**Acceptance Criteria:**
- [ ] File upload field on expense form (accepts common image formats)
- [ ] Maximum file size enforced at 5MB
- [ ] Image stored on backend filesystem
- [ ] Receipt viewable from expense detail
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-013: Export expense data
**Description:** As a user, I want to export expense data as CSV or JSON so I can use it in spreadsheets or other tools.

**Acceptance Criteria:**
- [ ] Export button on group page exports that group's expenses
- [ ] Export button on user profile exports all user's expenses across groups
- [ ] Supports CSV and JSON formats
- [ ] Includes all expense fields (date, amount, description, category, payer, split details)
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-014: REST API with API key auth
**Description:** As a developer, I want to access all features via REST API so I can build integrations or automate expense tracking.

**Acceptance Criteria:**
- [ ] Each user can generate/revoke a personal API key from profile
- [ ] API key passed via header authenticates requests
- [ ] API covers: groups CRUD, expenses CRUD, settlements, balances, export
- [ ] API returns JSON responses
- [ ] Typecheck/lint passes

### US-015: Docker Compose setup
**Description:** As a self-hoster, I want a Docker Compose file so I can deploy the entire stack easily.

**Acceptance Criteria:**
- [ ] `docker-compose.yml` defines backend, frontend, and database services
- [ ] Backend uses Django with SQLite by default
- [ ] Frontend serves built Vue app
- [ ] File storage volume mounted for avatars and receipts
- [ ] App functional after `docker compose up`
- [ ] README documents basic setup steps

## Functional Requirements

- FR-1: Admin can create, edit, and deactivate user accounts (username, display name, password)
- FR-2: Users authenticate via username/password; sessions managed by Django
- FR-3: Users can update their display name and upload a custom avatar image
- FR-4: Admin can CRUD expense categories (centrally defined)
- FR-5: Admin can CRUD group types (e.g. Vacation, Household, Friends)
- FR-6: Admin can CRUD currencies (name, symbol, code)
- FR-7: Only admins can create groups with a name, type, currency, and default split method
- FR-8: Only admins can add/remove members from groups
- FR-9: A default group must exist on fresh installation
- FR-10: Users can add expenses with: amount, description, date, category, optional receipt image
- FR-11: Each expense records the user who created it
- FR-12: Expenses can be split equally or with custom amounts/percentages among group members
- FR-13: Users can edit expenses they created; edits recalculate all affected balances
- FR-13a: Deleted expenses are soft-deleted (hidden but retained in database)
- FR-14: Group page displays per-member net balances and simplified debt list
- FR-15: Users can record settlements (payer, payee, amount) that adjust balances
- FR-16: User profile shows per-person net balances aggregated across all groups
- FR-17: Users and groups can export expense data as CSV or JSON
- FR-18: REST API with per-user API key authentication covers all app functionality
- FR-19: Receipt and avatar images stored on filesystem, served via backend; max 5MB per image
- FR-20: App ships as Docker Compose stack (Django backend, Vue frontend, SQLite DB)

## Non-Goals

- No OAuth/social login — admin creates all accounts
- No multi-currency within a single group (one currency per group)
- No live currency conversion rates
- No payment provider integrations (Venmo, PayPal, etc.)
- No push notifications or email alerts
- No mobile native app (web only)
- No recurring/scheduled expenses
- No audit log beyond basic edit tracking
- No support for more than ~10 concurrent users (not designed for scale)
- No debt simplification algorithm — balances shown as direct pairwise debts only

## Design Considerations

- Clean, simple UI — this is a utility app, not a social platform
- Mobile-responsive layout (Vue + CSS, no native app)
- Group dashboard should be the primary view after login
- Use clear color coding for owed (green) vs owes (red) balances
- Admin console can be a separate Vue route or Django admin

## Technical Considerations

- **Backend:** Django + Django REST Framework for API
- **Frontend:** Vue 3 (Composition API) as separate SPA
- **Database:** SQLite by default (single file, easy for small self-hosted setups)
- **File storage:** Local filesystem volume for avatars and receipts
- **Auth:** Django session auth for frontend, API key header auth for REST API
- **Docker:** Multi-stage builds for both services; compose file mounts DB and file volumes
- **Balance calculation:** Computed from expense/settlement records, not stored as mutable state — recalculate on read to avoid drift
- **TLS/reverse-proxy:** Not handled by the app — expected from deployment infrastructure

## Success Metrics

- Full expense lifecycle works: create group → add expense → view balances → settle → export
- API parity with frontend (all actions available via REST)
- `docker compose up` gets a working instance with zero additional config
- Balance calculations are accurate after any combination of adds, edits, and settlements

## Open Questions

None — all questions resolved.
