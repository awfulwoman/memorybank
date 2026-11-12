# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MemoryBank** is a self-hosted shared expense splitting application (Splitwise alternative). It is a monorepo with a Django REST API backend and a Vue 3 TypeScript frontend, deployed via Docker Compose.
## Commands

### Docker (primary workflow)
```bash
docker compose up          # Start all services (backend :8000, frontend :80)
docker compose up --build  # Rebuild images before starting
docker compose down        # Stop services
```

### Backend (Django)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000

# Run tests
python manage.py test core
python manage.py test core.tests.TestClassName.test_method_name  # single test
```

### Frontend (Vue 3 + Vite)
```bash
cd frontend
npm install
npm run dev          # Dev server with HMR (proxies /api/ to localhost:8000)
npm run type-check   # vue-tsc type checking
npm run build        # Type-check + production build
```

## Architecture

### Backend (`backend/`)

**Django project layout:**
- `memorybank/` — project package (settings, root URLs, wsgi/asgi)
- `core/` — single Django app containing all models, views, serializers, and authentication

**Key models (`core/models.py`):**
- `User` — extends `AbstractUser` with `display_name` and `avatar` (ImageField)
- `Group` — expense group with M2M `members`, FK `currency`, and `default_split_method`
- `Expense` — soft-deleted via `is_deleted`; uses custom `ExpenseManager` (excludes deleted) and `all_objects` manager (includes all)
- `ExpenseSplit` — per-member split amounts; validates splits sum to expense total
- `Settlement` — payment records between members to zero balances
- `ApiKey` — one-to-one with User for programmatic API access

**Authentication:**
- Session-based (browser/frontend)
- `X-API-Key` header via custom `ApiKeyAuthentication` class
- `AdminWritePermission`: reads allowed for all authenticated users; writes restricted to staff

**Balance calculation** (`core/views.py` `_compute_balances()`): computed on-the-fly from `ExpenseSplit` and `Settlement` — no stored mutable state. Returns per-member net balance and simplified pairwise debts.

**API structure** — all routes prefixed `/api/`:
- Auth: `POST /api/auth/login/`, `POST /api/auth/logout/`
- Current user: `/api/users/me/` (GET/PATCH), `/api/users/me/avatar/`, `/api/users/me/api-key/`, `/api/users/me/balances/`, `/api/users/me/export/`
- Groups: `/api/groups/` (CRUD), `/api/groups/{id}/members/`, `/api/groups/{id}/expenses/`, `/api/groups/{id}/settlements/`, `/api/groups/{id}/balances/`, `/api/groups/{id}/export/`
- Expenses: `/api/expenses/{id}/` (PATCH/DELETE — soft delete)
- Admin CRUD: `/api/categories/`, `/api/group-types/`, `/api/currencies/`, `/api/users/`

**Configuration:**
- `AUTH_USER_MODEL = 'core.User'` — must be set before any migrations
- `SQLITE_PATH` env var — database location (default: `db.sqlite3` in project root)
- `MEDIA_ROOT` env var — uploaded file storage (default: `media/` in project root)
- `CSRF_TRUSTED_ORIGINS` env var — comma-separated origins (default: `http://localhost`)

### Frontend (`frontend/`)

**Stack:** Vue 3 + TypeScript, Pinia (state), Vue Router, Vite

**State management (`src/stores/`):**
- `auth` store — login state, current user, `isStaff` flag; actions: `fetchMe()`, `login()`, `logout()`

**Routing (`src/router/`):** Global guard redirects unauthenticated users to `/login`. Routes: `/login`, `/` (dashboard), `/group/:id`, `/profile`, `/admin` (staff only).

**API client (`src/api.ts`):** Fetch-based client with base URL `/api/`. In dev, Vite proxies `/api/` and `/media/` to `http://localhost:8000`.

**Production:** Multi-stage Docker build → Nginx serves static assets and proxies `/api/` and `/media/` to backend; all other routes fall back to `index.html` (SPA).

### Data Volumes (`data/`)
- `data/db/` — SQLite database file
- `data/media/` — uploaded avatars and receipt images (5 MB max per file)

## Development Notes

- `ExpenseSerializer` handles split logic: accepts `split_data` (`[{user_id, amount}]`) for custom splits, or auto-calculates equal splits when omitted.
- Expense deletion is soft: sets `is_deleted=True`. Use `Expense.all_objects` to query including deleted records.
- The `prd.json` file tracks 30 user stories (`US-001`–`US-030`) with `passes: true/false` — used by the Ralph autonomous agent (`ralph.sh`).
