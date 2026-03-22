# PRD: Backend Test Suite

## Introduction

MemoryBank has zero backend tests. This PRD covers creating a comprehensive test suite for the Django backend — both unit tests (models, serializers, balance logic) and API integration tests (endpoint request/response). Tests use Django fixtures for test data and Django's built-in `TestCase`/`APITestCase`.

## Goals

- Achieve test coverage for all models, serializers, and views in `core/`
- Catch regressions in financial logic (balance computation, expense splitting)
- Verify authentication, permissions, and soft-delete behavior
- Establish a fixture-based test data strategy for consistency
- All tests runnable via `python manage.py test core`

## User Stories

### US-001: Test fixtures
**Description:** As a developer, I need shared test fixtures so all tests use consistent, realistic data.

**Acceptance Criteria:**
- [ ] Create `backend/core/fixtures/test_data.json` with: 2+ users (1 staff, 1 regular), 1 currency, 1 category, 1 group type, 1 group with both users as members
- [ ] Fixture loads successfully via `python manage.py loaddata test_data`
- [ ] Tests can reference fixture data by known PKs or usernames

### US-002: Model unit tests
**Description:** As a developer, I want unit tests for all models so that field constraints, managers, and methods are verified.

**Acceptance Criteria:**
- [ ] Test `User` creation with `display_name` and `avatar` fields
- [ ] Test `Category`, `GroupType`, `Currency` `__str__` methods
- [ ] Test `Group` creation with members M2M, `created_by`, and `default_split_method`
- [ ] Test `ExpenseManager` excludes soft-deleted expenses from default queryset
- [ ] Test `Expense.all_objects` includes soft-deleted expenses
- [ ] Test `ExpenseSplit.clean()` raises `ValidationError` when splits don't sum to expense amount
- [ ] Test `Settlement` creation and `__str__`
- [ ] Test `ApiKey.generate_key()` returns 64-char hex string
- [ ] All tests pass: `python manage.py test core`

### US-003: Serializer unit tests
**Description:** As a developer, I want unit tests for serializers so that data transformation and validation logic is verified.

**Acceptance Criteria:**
- [ ] Test `ExpenseSerializer` creates equal splits when `split_data` is omitted
- [ ] Test `ExpenseSerializer` creates custom splits when `split_data` is provided
- [ ] Test `ExpenseSerializer` rejects `split_data` where amounts don't sum to expense total
- [ ] Test `AdminUserSerializer` hashes password on create (not stored as plaintext)
- [ ] Test `AdminUserSerializer` hashes password on update
- [ ] Test `GroupSerializer` returns correct `member_count` and `member_ids`
- [ ] All tests pass: `python manage.py test core`

### US-004: Balance computation unit tests
**Description:** As a developer, I want thorough tests for `_compute_balances()` since it's the core financial logic.

**Acceptance Criteria:**
- [ ] Test simple case: 1 expense, 2 members, equal split — verify net balances and pairwise debts
- [ ] Test multiple expenses by different payers — verify correct net balances
- [ ] Test settlement partially zeroing a debt
- [ ] Test settlement fully zeroing a debt (net balance = 0)
- [ ] Test expense with `created_by=None` is skipped
- [ ] Test no expenses/settlements returns empty balances
- [ ] Test 3+ members with cross-debts simplify correctly
- [ ] All tests pass: `python manage.py test core`

### US-005: Auth API tests
**Description:** As a developer, I want API tests for login, logout, and session-based auth flows.

**Acceptance Criteria:**
- [ ] `POST /api/auth/login/` with valid credentials returns 200 and username
- [ ] `POST /api/auth/login/` with invalid credentials returns 401
- [ ] `POST /api/auth/logout/` clears session and returns 200
- [ ] Unauthenticated requests to protected endpoints return 401/403
- [ ] All tests pass: `python manage.py test core`

### US-006: API key auth tests
**Description:** As a developer, I want tests for API key creation, deletion, and authentication.

**Acceptance Criteria:**
- [ ] `POST /api/users/me/api-key/` creates a new key and returns it
- [ ] `POST /api/users/me/api-key/` regenerates (replaces) existing key
- [ ] `DELETE /api/users/me/api-key/` removes key, returns 204
- [ ] `DELETE /api/users/me/api-key/` with no key returns 404
- [ ] Request with valid `X-API-Key` header is authenticated
- [ ] All tests pass: `python manage.py test core`

### US-007: Admin permission API tests
**Description:** As a developer, I want tests verifying `AdminWritePermission` — reads for all auth users, writes for staff only.

**Acceptance Criteria:**
- [ ] Authenticated non-staff user can `GET /api/categories/` (200)
- [ ] Authenticated non-staff user gets 403 on `POST /api/categories/`
- [ ] Staff user can `POST /api/categories/` (201)
- [ ] Staff user can `PUT/PATCH/DELETE` on admin-only endpoints
- [ ] Non-staff user gets 403 on `POST/PUT/PATCH/DELETE` for `/api/groups/`
- [ ] All tests pass: `python manage.py test core`

### US-008: User profile API tests
**Description:** As a developer, I want tests for the `/api/users/me/` endpoints.

**Acceptance Criteria:**
- [ ] `GET /api/users/me/` returns current user data
- [ ] `PATCH /api/users/me/` updates `display_name`
- [ ] `POST /api/users/me/avatar/` with valid image updates avatar
- [ ] `POST /api/users/me/avatar/` with no file returns 400
- [ ] `POST /api/users/me/avatar/` with >5MB file returns 400
- [ ] All tests pass: `python manage.py test core`

### US-009: Group CRUD API tests
**Description:** As a developer, I want tests for group creation, listing, updating, and member management.

**Acceptance Criteria:**
- [ ] Staff can create a group via `POST /api/groups/`
- [ ] Non-staff sees only groups they're a member of via `GET /api/groups/`
- [ ] Staff sees all groups via `GET /api/groups/`
- [ ] `POST /api/groups/{id}/members/` adds a member (admin only)
- [ ] `DELETE /api/groups/{id}/members/{user_id}/` removes a member (admin only)
- [ ] Adding non-existent user returns 404
- [ ] All tests pass: `python manage.py test core`

### US-010: Expense API tests
**Description:** As a developer, I want tests for creating, listing, updating, and soft-deleting expenses.

**Acceptance Criteria:**
- [ ] `POST /api/groups/{id}/expenses/` creates expense with auto equal splits
- [ ] `POST /api/groups/{id}/expenses/` with `split_data` creates custom splits
- [ ] `GET /api/groups/{id}/expenses/` lists non-deleted expenses
- [ ] `PATCH /api/expenses/{id}/` updates expense (only by creator)
- [ ] `PATCH /api/expenses/{id}/` by non-creator returns 403
- [ ] `DELETE /api/expenses/{id}/` soft-deletes (sets `is_deleted=True`)
- [ ] Soft-deleted expense no longer appears in `GET /api/groups/{id}/expenses/`
- [ ] All tests pass: `python manage.py test core`

### US-011: Settlement API tests
**Description:** As a developer, I want tests for creating and listing settlements.

**Acceptance Criteria:**
- [ ] `POST /api/groups/{id}/settlements/` creates settlement with current user as payer
- [ ] `GET /api/groups/{id}/settlements/` lists settlements for the group
- [ ] Settlement appears in balance computation (reduces debt)
- [ ] All tests pass: `python manage.py test core`

### US-012: Balance API tests
**Description:** As a developer, I want tests for the balance endpoints to verify end-to-end correctness.

**Acceptance Criteria:**
- [ ] `GET /api/groups/{id}/balances/` returns correct balances after expenses and settlements
- [ ] `GET /api/users/me/balances/` returns correct aggregate across all user's groups
- [ ] Empty group returns empty balances
- [ ] All tests pass: `python manage.py test core`

### US-013: Export API tests
**Description:** As a developer, I want tests for CSV and JSON export endpoints.

**Acceptance Criteria:**
- [ ] `GET /api/groups/{id}/export/?format=csv` returns CSV with correct headers and rows
- [ ] `GET /api/groups/{id}/export/?format=json` returns JSON array
- [ ] `GET /api/groups/{id}/export/?format=xml` returns 400
- [ ] `GET /api/users/me/export/?format=csv` exports only current user's expenses
- [ ] All tests pass: `python manage.py test core`

## Functional Requirements

- FR-1: All tests live in `backend/core/tests/` as a Python package (with `__init__.py`)
- FR-2: Test data provided via Django fixtures in `backend/core/fixtures/test_data.json`
- FR-3: Tests use `rest_framework.test.APITestCase` for API tests and `django.test.TestCase` for unit tests
- FR-4: Each test file corresponds to one logical area (e.g., `test_models.py`, `test_serializers.py`, `test_auth.py`, etc.)
- FR-5: Tests must not depend on external services or a running server
- FR-6: All tests runnable via `python manage.py test core`
- FR-7: Tests must clean up after themselves (use Django's test transaction rollback)

## Non-Goals

- No frontend tests (separate effort)
- No load/performance testing
- No test coverage tooling or CI integration (can be added later)
- No mocking of the database — tests hit the test DB directly

## Technical Considerations

- Django's test runner uses an in-memory SQLite database by default — no config changes needed
- `ExpenseManager` custom queryset means tests should verify both `Expense.objects` and `Expense.all_objects`
- `_compute_balances()` is a standalone function — can be tested directly with model instances
- Fixture PKs must be chosen to avoid conflicts with auto-increment during tests

## Success Metrics

- All 13 user stories pass with `python manage.py test core`
- No test takes more than 1 second individually
- Tests catch at least one real bug or unexpected behavior during development

## Open Questions

- Should we add a `conftest.py` or helper module for shared test utilities beyond fixtures?
- Should API key authentication tests mock the middleware or go through the full request cycle?
