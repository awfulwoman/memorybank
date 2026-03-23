# PRD: Expense Receipt Management

## Introduction

Currently each expense has a single `receipt_image` field with no way to view or delete it from the UI. This PRD adds support for multiple receipt images per expense (up to 5), displays them as thumbnails in the edit modal with a full-size overlay viewer, and allows the expense creator to delete individual receipts.

## Goals

- Support multiple receipt images per expense (max 5)
- Display receipt thumbnails in the edit expense modal
- Allow clicking a thumbnail to view the full-size image in an overlay
- Allow the expense creator to delete individual receipt images
- Maintain backwards compatibility with the existing single `receipt_image` field during migration

## User Stories

### US-001: Create ReceiptImage model
**Description:** As a developer, I need a separate model to store multiple receipt images per expense.

**Acceptance Criteria:**
- [ ] Create `ReceiptImage` model with fields: `id`, `expense` (FK to Expense), `image` (ImageField, upload_to='receipts/'), `created_at` (auto)
- [ ] Generate and run migration successfully
- [ ] Add data migration to move existing `receipt_image` values from Expense to new ReceiptImage records
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-002: Add receipt image API endpoints
**Description:** As a developer, I need API endpoints to upload and delete receipt images for an expense.

**Acceptance Criteria:**
- [ ] POST `/api/expenses/{id}/receipts/` uploads a new receipt image (multipart form data with `image` field)
- [ ] Validates file is an image and max 5MB
- [ ] Returns 400 if expense already has 5 receipt images
- [ ] Only the expense creator can upload receipts (403 for others)
- [ ] DELETE `/api/expenses/{id}/receipts/{receipt_id}/` deletes a receipt image
- [ ] Only the expense creator can delete receipts (403 for others)
- [ ] ExpenseSerializer includes `receipts` field listing all receipt images (`[{id, image_url}]`)
- [ ] Tests pass: `cd backend && python manage.py test core`

### US-003: Display receipt thumbnails in edit expense modal
**Description:** As a user, I want to see all attached receipts when editing an expense so I can review them.

**Acceptance Criteria:**
- [ ] Edit expense modal shows a "Receipts" section below the form fields
- [ ] Each receipt displays as a thumbnail (max 80px height, aspect ratio preserved)
- [ ] Thumbnails are rendered from the `receipts` array in the expense data
- [ ] If no receipts, show "No receipts attached"
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-004: Full-size receipt viewer overlay
**Description:** As a user, I want to click a receipt thumbnail to see the full-size image so I can read the details.

**Acceptance Criteria:**
- [ ] Clicking a thumbnail opens a full-screen overlay with the full-size image (reuse existing receipt overlay pattern from GroupDetailView)
- [ ] Clicking the overlay background or X button closes it
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-005: Delete receipt from edit modal
**Description:** As the expense creator, I want to delete individual receipts from the edit modal.

**Acceptance Criteria:**
- [ ] Each receipt thumbnail has a delete button (X icon or similar) in the corner
- [ ] Clicking delete shows a brief confirmation (e.g., "Remove this receipt?")
- [ ] Confirming calls DELETE `/api/expenses/{id}/receipts/{receipt_id}/`
- [ ] Thumbnail is removed from the list after successful deletion
- [ ] Delete button only shown if current user is the expense creator
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-006: Upload additional receipts from edit modal
**Description:** As the expense creator, I want to add more receipts to an existing expense.

**Acceptance Criteria:**
- [ ] Edit modal shows an "Add receipt" file input below existing thumbnails
- [ ] Selecting a file uploads it via POST `/api/expenses/{id}/receipts/`
- [ ] New thumbnail appears in the list after successful upload
- [ ] File input is hidden when 5 receipts are already attached
- [ ] Only shown if current user is the expense creator
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-007: Upload receipt during expense creation
**Description:** As a user, I want to attach receipt images when creating a new expense.

**Acceptance Criteria:**
- [ ] Add expense form keeps the existing file input for receipt
- [ ] After expense is created, any selected file is uploaded via POST `/api/expenses/{id}/receipts/`
- [ ] Remove the old `receipt_image` field usage from create flow — use the new receipts endpoint instead
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-008: Update expense list to show receipt indicator
**Description:** As a user, I want to see which expenses have receipts attached in the expense list.

**Acceptance Criteria:**
- [ ] Expense rows in group detail show a receipt icon/count if the expense has 1+ receipts (e.g., "📎 2")
- [ ] No indicator shown for expenses with 0 receipts
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

## Functional Requirements

- FR-1: `ReceiptImage` model stores multiple images per expense via FK
- FR-2: Maximum 5 receipt images per expense, enforced at the API level
- FR-3: POST `/api/expenses/{id}/receipts/` creates a new receipt image (multipart, creator-only)
- FR-4: DELETE `/api/expenses/{id}/receipts/{receipt_id}/` removes a receipt image (creator-only)
- FR-5: ExpenseSerializer includes `receipts` array with `[{id, image}]` for each receipt
- FR-6: Edit modal displays receipt thumbnails (80px height) with click-to-enlarge
- FR-7: Edit modal allows deleting individual receipts with confirmation
- FR-8: Edit modal allows uploading additional receipts (up to 5 total)
- FR-9: Expense creation uploads receipt via the new endpoint after the expense is created
- FR-10: Data migration moves existing `receipt_image` data to `ReceiptImage` records

## Non-Goals

- No drag-and-drop upload
- No image cropping or editing
- No OCR or receipt parsing
- No receipt images on settlements (only expenses)
- No bulk upload (one file at a time)

## Technical Considerations

- Existing `receipt_image` field on Expense should be deprecated after data migration but can remain on the model to avoid breaking changes until cleanup
- The new receipts endpoint should use `MultiPartParser` explicitly
- Receipt thumbnails can use the raw image URL with CSS sizing — no server-side thumbnail generation needed
- Reuse the existing receipt overlay pattern (`.receipt-overlay` in GroupDetailView) or extract to a shared component
- The `receipts` field in ExpenseSerializer should be a nested serializer (read-only)

## Success Metrics

- Users can attach up to 5 receipt images to any expense
- Users can view receipt images at full size from the edit modal
- Users can delete individual receipts without affecting the expense
- Existing single receipt_image data is preserved in migration

## Open Questions

- Should the old `receipt_image` field be removed from the Expense model in this PRD or in a follow-up cleanup?
- Should receipt thumbnails also be visible in the expense list row (not just edit modal)?
