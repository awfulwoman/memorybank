# MemoryBank

Self-hosted shared expense splitting app. Built with Django + Vue 3.

## Quick Start

```bash
docker compose up
```

The app will be available at http://localhost (frontend) and the Django backend at http://localhost:8000.

On first run, Django migrations are applied automatically.

## Default Admin Credentials

Create the first admin user via the Django management command:

```bash
docker compose exec backend python manage.py createsuperuser
```

Or set the initial password interactively. The Django admin panel is available at http://localhost:8000/admin/.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | insecure default | Set to a secure random string in production |
| `DJANGO_DEBUG` | `true` | Set to `false` in production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated list of allowed hosts |
| `SQLITE_PATH` | `/data/db/db.sqlite3` | Path to SQLite database file |
| `MEDIA_ROOT` | `/data/media` | Path to media file storage |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost` | Comma-separated trusted origins for CSRF |

## Data Persistence

Two volumes are mounted:
- `./data/db/` — SQLite database
- `./data/media/` — uploaded files (avatars, receipts)

## API Usage

### Authentication

**Session (browser):**
```bash
POST /api/auth/login/
{"username": "admin", "password": "password"}
```

**API Key:**
Generate a key via the Profile page, then pass it as a header:
```bash
curl -H "X-API-Key: <your-key>" http://localhost:8000/api/users/me/
```

### Key Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login/` | POST | Login |
| `/api/auth/logout/` | POST | Logout |
| `/api/users/me/` | GET/PATCH | Current user profile |
| `/api/users/me/balances/` | GET | Cross-group balances |
| `/api/users/me/export/` | GET | Export expenses (CSV/JSON) |
| `/api/groups/` | GET/POST | List/create groups |
| `/api/groups/{id}/expenses/` | GET/POST | Group expenses |
| `/api/groups/{id}/settlements/` | GET/POST | Group settlements |
| `/api/groups/{id}/balances/` | GET | Group balance summary |
| `/api/groups/{id}/export/` | GET | Export group expenses |
| `/api/categories/` | CRUD | Expense categories (write: admin only) |
| `/api/currencies/` | CRUD | Currencies (write: admin only) |
| `/api/group-types/` | CRUD | Group types (write: admin only) |

## Deploy

Run MemoryBank from pre-built images published to GitHub Container Registry — no need to clone the repository.

### Images

- Backend: [ghcr.io/awfulwoman/memorybank-backend](https://github.com/awfulwoman/memorybank/pkgs/container/memorybank-backend)
- Frontend: [ghcr.io/awfulwoman/memorybank-frontend](https://github.com/awfulwoman/memorybank/pkgs/container/memorybank-frontend)

### Steps

1. Download the Compose file:
   ```bash
   curl -O https://raw.githubusercontent.com/awfulwoman/memorybank/main/docker-compose.ghcr.yml
   ```

2. Create the data directories:
   ```bash
   mkdir -p data/db data/media
   ```

3. Start the stack:
   ```bash
   docker compose -f docker-compose.ghcr.yml up -d
   ```

The app will be available at http://localhost (frontend) and http://localhost:8000 (API).

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SQLITE_PATH` | `/data/db/db.sqlite3` | Path to SQLite database file inside the container |
| `MEDIA_ROOT` | `/data/media` | Path to media file storage inside the container |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost` | Comma-separated trusted origins for CSRF (set to your domain in production) |

Pass them inline or via a `.env` file:
```bash
CSRF_TRUSTED_ORIGINS=https://expenses.example.com docker compose -f docker-compose.ghcr.yml up -d
```

## LLM Disclaimer

I'm testing out a Ralph loop to create this. Don't even think of using it yourself.
