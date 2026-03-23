# MemoryBank

An expense-splitting app that can be easily self-hosted.

Built with Django + Vue 3.

## Quick Start

Create a `docker-compose.yaml` file and run `docker compose up`.

```yaml
services:
  frontend:
    image: ghcr.io/awfulwoman/memorybank-frontend:latest
    ports:
      - "8080:80"
    depends_on:
      - backend

  backend:
    image: ghcr.io/awfulwoman/memorybank-backend:latest
    environment:
      - DJANGO_SECRET_KEY="" # Set this to a secure random string
      - DJANGO_DEBUG=false
    volumes:
      - ./data/db:/data/db
      - ./data/media:/data/media
```

> **Important:** Set `DJANGO_SECRET_KEY` to a long random string before starting. You can generate one with:
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(50))"
> ```

## Default Admin Credentials

Create the first admin user via the Django management command:

```bash
docker compose exec backend python manage.py createsuperuser
```

Or set the initial password interactively. The Django admin panel is available at http://localhost:8080/admin/.

## Environment Variables

| Variable            | Default | Description                                          |
| ------------------- | ------- | ---------------------------------------------------- |
| `DJANGO_SECRET_KEY` | (none)  | **Required.** Set to a secure random string.         |
| `DJANGO_DEBUG`      | `false` | Set to `true` for development only.                  |

## Data Persistence

Two volume maps are required:

- `./data/db/` — SQLite database
- `./data/media/` — uploaded files (avatars, receipts)

These can be provided as volumes or directories.

## API Usage

The application can be accessed via a REST API.

### Authentication

**API Key:**
Generate a key via the Profile page, then pass it as a header:

```bash
curl -H "X-API-Key: <your-key>" http://localhost:8080/api/users/me/
```

### Key Endpoints

| Endpoint | Method | Description |
| -------- | ------ | ----------- |
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


## LLM Disclaimer

I'm testing out a Ralph loop to create this. Don't even think of using it in any kind of production capability.
