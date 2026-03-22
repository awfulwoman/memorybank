# PRD: Security Vulnerability Fixes

## Introduction

A security review identified four high-severity vulnerabilities in MemoryBank: broken authorization on group-scoped API endpoints (IDOR), unvalidated settlement payee and expense split recipients, a hardcoded SECRET_KEY fallback, and DEBUG mode enabled by default. This PRD addresses all four with code fixes and tests.

## Goals

- Prevent authenticated users from accessing groups they don't belong to
- Validate that settlement payees and expense split recipients are group members
- Remove hardcoded SECRET_KEY fallback so deployments must provide their own
- Default DEBUG to false so production deployments are safe out of the box
- Add tests proving unauthorized access is blocked

## User Stories

### US-001: Add group membership permission class
**Description:** As a developer, I need a reusable DRF permission class that checks group membership so all group-scoped views can use it consistently.

**Acceptance Criteria:**
- [ ] Create `IsGroupMemberOrAdmin` permission class in `backend/core/permissions.py` (or add to existing file)
- [ ] Permission checks that `request.user` is in `group.members.all()` OR `request.user.is_staff`
- [ ] Permission extracts group `pk` from the URL kwargs
- [ ] Returns 403 Forbidden for non-members/non-staff
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-002: Apply group membership checks to GroupExpenseView
**Description:** As a user, I want my group's expenses to be private so that only group members and admins can view or create them.

**Acceptance Criteria:**
- [ ] `GroupExpenseView` uses `IsGroupMemberOrAdmin` permission (or inline check)
- [ ] GET `/api/groups/{id}/expenses/` returns 403 for non-member, non-staff users
- [ ] POST `/api/groups/{id}/expenses/` returns 403 for non-member, non-staff users
- [ ] Staff users can still access any group's expenses
- [ ] Group members can still access their group's expenses normally
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-003: Apply group membership checks to GroupSettlementView
**Description:** As a user, I want my group's settlements to be private so that only group members and admins can view or create them.

**Acceptance Criteria:**
- [ ] `GroupSettlementView` uses `IsGroupMemberOrAdmin` permission (or inline check)
- [ ] GET `/api/groups/{id}/settlements/` returns 403 for non-member, non-staff users
- [ ] POST `/api/groups/{id}/settlements/` returns 403 for non-member, non-staff users
- [ ] Staff users can still access any group's settlements
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-004: Apply group membership checks to GroupBalanceView and GroupExportView
**Description:** As a user, I want my group's balances and exports to be private so that only group members and admins can access them.

**Acceptance Criteria:**
- [ ] `GroupBalanceView` uses `IsGroupMemberOrAdmin` permission (or inline check)
- [ ] `GroupExportView` uses `IsGroupMemberOrAdmin` permission (or inline check)
- [ ] GET `/api/groups/{id}/balances/` returns 403 for non-member, non-staff users
- [ ] GET `/api/groups/{id}/export/` returns 403 for non-member, non-staff users
- [ ] Staff users can still access any group's data
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-005: Validate settlement payee is a group member
**Description:** As a developer, I need to ensure settlement payees are members of the target group so users cannot create false debt records for arbitrary users.

**Acceptance Criteria:**
- [ ] `SettlementSerializer` or `GroupSettlementView.post()` validates that `payee` is in `group.members.all()`
- [ ] POST `/api/groups/{id}/settlements/` with a payee who is not a group member returns 400
- [ ] POST with a valid group member payee still succeeds
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-006: Validate expense split user_ids are group members
**Description:** As a developer, I need to ensure custom expense splits only reference group members so users cannot assign debts to arbitrary users.

**Acceptance Criteria:**
- [ ] `ExpenseSerializer._create_splits()` validates each `user_id` in `split_data` is in `group.members.all()`
- [ ] POST `/api/groups/{id}/expenses/` with `split_data` containing a non-member user_id returns 400
- [ ] POST with valid group member user_ids still succeeds
- [ ] Equal splits (no `split_data`) still work correctly for group members only
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-007: Remove hardcoded SECRET_KEY fallback
**Description:** As a deployer, I want the app to refuse to start without a proper SECRET_KEY so I don't accidentally run with an insecure default.

**Acceptance Criteria:**
- [ ] `settings.py` reads `DJANGO_SECRET_KEY` from environment with NO insecure fallback
- [ ] App raises an error on startup if `DJANGO_SECRET_KEY` is not set (except when running tests)
- [ ] `docker-compose.yml` sets `DJANGO_SECRET_KEY` to a placeholder with a comment to change it
- [ ] `docker-compose.ghcr.yml` (if exists) also sets `DJANGO_SECRET_KEY`
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-008: Default DEBUG to false
**Description:** As a deployer, I want DEBUG mode off by default so production deployments don't leak error details.

**Acceptance Criteria:**
- [ ] `settings.py` defaults `DJANGO_DEBUG` to `'false'` when env var is not set
- [ ] `docker-compose.yml` sets `DJANGO_DEBUG=false` (or removes it to use safe default)
- [ ] `docker-compose.ghcr.yml` (if exists) also sets `DJANGO_DEBUG=false`
- [ ] App still works with `DJANGO_DEBUG=true` for local development
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-009: Security authorization tests
**Description:** As a developer, I want tests that prove unauthorized group access is blocked so regressions are caught immediately.

**Acceptance Criteria:**
- [ ] Test: non-member GET `/api/groups/{id}/expenses/` returns 403
- [ ] Test: non-member POST `/api/groups/{id}/expenses/` returns 403
- [ ] Test: non-member GET `/api/groups/{id}/settlements/` returns 403
- [ ] Test: non-member POST `/api/groups/{id}/settlements/` returns 403
- [ ] Test: non-member GET `/api/groups/{id}/balances/` returns 403
- [ ] Test: non-member GET `/api/groups/{id}/export/` returns 403
- [ ] Test: staff (non-member) GET `/api/groups/{id}/expenses/` returns 200
- [ ] Test: settlement with non-member payee returns 400
- [ ] Test: expense with non-member in split_data returns 400
- [ ] All tests pass: `cd backend && python manage.py test core`

## Functional Requirements

- FR-1: All group-scoped endpoints must verify `request.user` is in `group.members` or `request.user.is_staff` before processing
- FR-2: Settlement payee must be validated as a member of the target group
- FR-3: All user_ids in expense `split_data` must be validated as members of the target group
- FR-4: `SECRET_KEY` must not have a hardcoded fallback; app must fail to start without it
- FR-5: `DEBUG` must default to `false` when `DJANGO_DEBUG` env var is not set
- FR-6: Unauthorized group access must return HTTP 403 Forbidden
- FR-7: Invalid payee/split user_ids must return HTTP 400 Bad Request with descriptive error
- FR-8: All existing tests must continue to pass after changes

## Non-Goals

- No changes to the frontend (these are all backend fixes)
- No new authentication mechanisms
- No changes to the admin user CRUD endpoints (already use `AdminWritePermission`)
- No rate limiting or brute-force protection (separate concern)
- No audit logging of unauthorized access attempts

## Technical Considerations

- `GroupViewSet.get_queryset()` already filters by membership for list/detail — use the same pattern
- `ExpenseDetailView` already checks `created_by == request.user` — similar pattern for group views
- The `IsGroupMemberOrAdmin` permission needs to extract the group `pk` from URL kwargs — all group-scoped URLs use `<int:pk>` for the group ID
- `docker-compose.yml` environment variables need updating — ensure the dev workflow still works by documenting `DJANGO_DEBUG=true` for local dev
- For SECRET_KEY, use `os.environ['DJANGO_SECRET_KEY']` (raises KeyError) or a conditional check with a clear error message
- Test fixtures already have 2 users (admin=staff, alice=regular) and 1 group with both as members — create a third user for "non-member" tests

## Success Metrics

- All 4 identified vulnerabilities are resolved
- Zero existing tests broken
- New tests cover all authorization boundary cases
- App starts correctly with proper env vars and fails clearly without them

## Open Questions

- Should the GroupMemberView (add/remove members) also require group membership, or keep it staff-only as it currently is?
