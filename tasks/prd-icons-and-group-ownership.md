# PRD: Icons & Group Ownership

## Introduction

Add MDI icon support for categories and groups, allow any authenticated user to create groups (removing the admin-only restriction), and introduce group ownership so the creator can edit group details, manage members, and delete the group.

## Goals

- Allow any authenticated user to create a group (they become the owner)
- Group owner can edit name, icon, add/remove members, and delete the group
- Add an icon field to Group and Category models (stores MDI icon name)
- Provide a searchable icon picker UI with MDI icon previews
- Display icons alongside group and category names throughout the app
- Install `@mdi/font` in the frontend for icon rendering

## User Stories

### US-001: Add icon field to Category and Group models
**Description:** As a developer, I need to store an icon name for categories and groups so they can be displayed in the UI.

**Acceptance Criteria:**
- [ ] Add `icon` CharField to Category model (max_length=50, default='mdi-shape-outline', blank=True)
- [ ] Add `icon` CharField to Group model (max_length=50, default='mdi-account-group', blank=True)
- [ ] Generate and run migration successfully
- [ ] CategorySerializer includes `icon` field (read and write)
- [ ] GroupSerializer includes `icon` field (read and write)
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-002: Remove admin-only restriction on group creation
**Description:** As a user, I want to create my own groups so I don't need to ask an admin.

**Acceptance Criteria:**
- [ ] GroupViewSet allows POST (create) for any authenticated user, not just staff
- [ ] GroupViewSet keeps admin-only for PUT/PATCH/DELETE (will be updated in US-003)
- [ ] GET still returns only groups the user is a member of (non-staff) or all groups (staff)
- [ ] `perform_create()` still sets `created_by=request.user` and auto-adds creator to `members`
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-003: Add group ownership permissions
**Description:** As a group owner, I want to edit my group's details, manage members, and delete it so I have control over groups I created.

**Acceptance Criteria:**
- [ ] Create `IsGroupOwnerOrAdmin` permission class in `backend/core/permissions.py`
- [ ] Permission returns True if `request.user == group.created_by` OR `request.user.is_staff`
- [ ] GroupViewSet uses `IsGroupOwnerOrAdmin` for update/partial_update/destroy actions
- [ ] Non-owner, non-staff PATCH `/api/groups/{id}/` returns 403
- [ ] Owner PATCH `/api/groups/{id}/` succeeds (200)
- [ ] Staff PATCH `/api/groups/{id}/` succeeds (200)
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-004: Allow group owner to manage members
**Description:** As a group owner, I want to add and remove members so I can control who's in my group.

**Acceptance Criteria:**
- [ ] GroupMemberView permission changed from `IsAdminUser` to allow group owner OR staff
- [ ] Owner can POST `/api/groups/{id}/members/` to add a member
- [ ] Owner can DELETE `/api/groups/{id}/members/{user_id}/` to remove a member
- [ ] Non-owner, non-staff POST/DELETE returns 403
- [ ] Staff can still add/remove members in any group
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-005: Install @mdi/font and create icon picker component
**Description:** As a developer, I need an MDI icon library and a reusable icon picker component for the frontend.

**Acceptance Criteria:**
- [ ] Install `@mdi/font` via npm in `frontend/`
- [ ] Import `@mdi/font/css/materialdesignicons.min.css` in `main.ts` or `main.css`
- [ ] Create `frontend/src/components/IconPicker.vue` component
- [ ] IconPicker shows a search input that filters icons by name
- [ ] IconPicker displays matching icons in a grid with the icon rendered and name shown on hover
- [ ] IconPicker emits `select` event with the chosen icon name (e.g., `mdi-home`)
- [ ] Include a curated list of ~50-80 common icons (home, food, travel, shopping, car, medical, etc.) as the default searchable set
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-006: Add icon display to group cards on dashboard
**Description:** As a user, I want to see group icons on the dashboard so I can quickly identify my groups.

**Acceptance Criteria:**
- [ ] Dashboard group cards show the group's icon (rendered as MDI icon) next to the group name
- [ ] If no icon is set, show default icon `mdi-account-group`
- [ ] Icon is sized appropriately (1.25rem–1.5rem) and uses `var(--color-primary)` color
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-007: Add group creation UI for regular users
**Description:** As a user, I want a "Create Group" button on the dashboard that opens a form so I can create my own groups.

**Acceptance Criteria:**
- [ ] "Create Group" button visible on dashboard for all authenticated users
- [ ] Clicking opens a modal with fields: name (required), icon (icon picker), currency (dropdown), default split method (dropdown)
- [ ] Submitting calls POST `/api/groups/` and adds the new group to the dashboard
- [ ] Creator is automatically a member of the new group
- [ ] Modal closes and dashboard refreshes after successful creation
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-008: Add group settings page for owner
**Description:** As a group owner, I want to edit my group's name, icon, and manage members from the group detail page.

**Acceptance Criteria:**
- [ ] Group detail view shows a "Settings" or gear icon button (visible only to owner and staff)
- [ ] Clicking opens a settings section/modal with: edit name, edit icon (icon picker), member list with remove buttons, add member input, delete group button
- [ ] Edit name/icon saves via PATCH `/api/groups/{id}/`
- [ ] Add member via POST `/api/groups/{id}/members/`
- [ ] Remove member via DELETE `/api/groups/{id}/members/{user_id}/`
- [ ] Delete group shows confirmation dialog, then calls DELETE `/api/groups/{id}/`
- [ ] After delete, redirect to dashboard
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-009: Add icon picker to admin category management
**Description:** As an admin, I want to assign icons to categories so they display throughout the app.

**Acceptance Criteria:**
- [ ] Admin view category creation form includes an icon picker
- [ ] Admin view category edit shows current icon and allows changing it
- [ ] Category icon saved via API when creating/editing
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-010: Display category icons in expense forms and lists
**Description:** As a user, I want to see category icons in expense forms and lists for visual clarity.

**Acceptance Criteria:**
- [ ] Category dropdown in AddExpenseForm and EditExpenseForm shows icon next to category name
- [ ] Expense list items on group detail page show the category icon next to the category name
- [ ] If category has no icon, show default `mdi-shape-outline`
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

## Functional Requirements

- FR-1: Add `icon` CharField (max_length=50) to Category and Group models with sensible defaults
- FR-2: GroupViewSet allows POST for any authenticated user (not just staff)
- FR-3: GroupViewSet restricts PUT/PATCH/DELETE to group owner (`created_by`) or staff
- FR-4: GroupMemberView allows group owner or staff to add/remove members
- FR-5: `perform_create()` on GroupViewSet auto-adds creator as group member
- FR-6: Frontend uses `@mdi/font` for icon rendering via CSS classes
- FR-7: IconPicker component provides searchable grid of MDI icons
- FR-8: Group cards on dashboard display the group icon
- FR-9: Category dropdowns and expense lists display category icons
- FR-10: Group detail page shows settings UI for owner/staff to edit group and manage members
- FR-11: Delete group requires confirmation dialog and redirects to dashboard

## Non-Goals

- No custom icon uploads (only MDI icon names)
- No icon for individual expenses (only categories and groups)
- No role system beyond owner/member/staff (no "co-owner" or "moderator")
- No group transfer (changing owner)
- No group invitations or invite links (members added by user ID)

## Design Considerations

- Use `<span class="mdi mdi-{icon-name}"></span>` pattern for rendering MDI icons
- IconPicker should be a modal or popover, not a full page
- Icon picker grid: 6-8 icons per row, scrollable, with search filtering
- Keep the existing admin view functional — admin can still manage all groups/categories
- Group settings on group detail page should be a collapsible section or modal to avoid cluttering the main view

## Technical Considerations

- `@mdi/font` is ~250KB CSS + font files — acceptable for this app
- Icon names stored as strings (e.g., `mdi-home`) — no FK needed
- `created_by` already exists on Group model — use it for ownership checks
- The `perform_create()` already sets `created_by`, just needs to also add user to `members`
- Frontend `api.ts` already has `createGroup()`, `updateGroup()`, `deleteGroup()` — verify they exist or add as needed
- `IsGroupOwnerOrAdmin` is separate from `IsGroupMemberOrAdmin` — owner permission is stricter (only creator), member permission is broader (any member)

## Success Metrics

- Any user can create a group and start adding expenses without admin intervention
- Groups and categories display icons throughout the UI
- Group owners can manage their groups end-to-end (create, edit, manage members, delete)
- No regression in existing admin functionality

## Open Questions

- Should there be a limit on how many groups a user can create?
- When owner is removed from group members, should ownership transfer or be blocked?
