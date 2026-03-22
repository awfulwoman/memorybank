# PRD: GitHub Container Registry Publishing

## Introduction

Build the backend (Django) and frontend (Vue 3/Nginx) into OCI container images and publish them to the GitHub Container Registry (GHCR) via GitHub Actions. Images are built on every push to `main` and on version tags. Both frontend type-check and backend tests must pass before any image is pushed. A `docker-compose.ghcr.yml` file and README deploy instructions are included so operators can run the stack without cloning the repo.

## Goals

- Automatically publish `ghcr.io/<owner>/memorybank-backend` and `ghcr.io/<owner>/memorybank-frontend` on push to `main` and on semver tags
- Tag images as `latest`, `sha-<short-sha>`, and semver (e.g., `1.2.3`) when a tag is pushed
- Enforce quality gates (backend tests + frontend type-check) before any push
- Provide a deployment compose file and README instructions for operators who only want to run the published images

## User Stories

### US-001: Backend CI quality gate
**Description:** As a maintainer, I want the backend tests to run on every push to `main` and on tags so that broken code is never published.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow runs `python manage.py test` (or equivalent) against the `backend/` directory
- [ ] Workflow fails and does NOT proceed to image build if tests fail
- [ ] Workflow runs on `push` to `main` and on `push` of tags matching `v*.*.*`
- [ ] Python version is pinned (match the version in `backend/Dockerfile`)

### US-002: Frontend CI quality gate
**Description:** As a maintainer, I want the frontend type-check to run on every push to `main` and on tags so that type errors are caught before publishing.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow runs `npm run type-check` in the `frontend/` directory
- [ ] Workflow fails and does NOT proceed to image build if type-check fails
- [ ] Node version is pinned (match the version in `frontend/Dockerfile`)

### US-003: Build and publish backend image to GHCR
**Description:** As a maintainer, I want the backend Docker image built and pushed to GHCR after CI passes so that deployments can pull a versioned image.

**Acceptance Criteria:**
- [ ] Image is built from `backend/Dockerfile`
- [ ] Image is published to `ghcr.io/<org-or-user>/memorybank-backend`
- [ ] On push to `main`: tagged `latest` and `sha-<short-sha>`
- [ ] On semver tag (e.g., `v1.2.3`): additionally tagged `1.2.3`, `1.2`, and `1`
- [ ] Uses `docker/metadata-action` (or equivalent) to compute tags deterministically
- [ ] Uses `docker/build-push-action` with GitHub Actions cache (`cache-from: type=gha`, `cache-to: type=gha,mode=max`)
- [ ] Authenticates to GHCR using `GITHUB_TOKEN` (no extra secrets required)
- [ ] Build only runs after both quality gate jobs succeed

### US-004: Build and publish frontend image to GHCR
**Description:** As a maintainer, I want the frontend Docker image built and pushed to GHCR after CI passes.

**Acceptance Criteria:**
- [ ] Image is built from `frontend/Dockerfile`
- [ ] Image is published to `ghcr.io/<org-or-user>/memorybank-frontend`
- [ ] Same tagging rules as US-003 (`latest`, `sha-<short-sha>`, semver)
- [ ] Uses `docker/metadata-action` and `docker/build-push-action` with GHA cache
- [ ] Authenticates via `GITHUB_TOKEN`
- [ ] Build only runs after both quality gate jobs succeed

### US-005: docker-compose.ghcr.yml for operators
**Description:** As an operator, I want a ready-to-use Compose file that pulls published images so I can deploy MemoryBank without cloning the repository.

**Acceptance Criteria:**
- [ ] File `docker-compose.ghcr.yml` is created at the repo root
- [ ] References `ghcr.io/<org-or-user>/memorybank-backend:latest` and `ghcr.io/<org-or-user>/memorybank-frontend:latest`
- [ ] Accepts the same environment variables as `docker-compose.yml` (`SQLITE_PATH`, `MEDIA_ROOT`, `CSRF_TRUSTED_ORIGINS`)
- [ ] Mounts the same `data/db` and `data/media` volumes
- [ ] Does NOT build images locally (no `build:` keys)

### US-006: README deployment instructions
**Description:** As an operator, I want clear instructions in the README for deploying from published images so I don't need to read the source code.

**Acceptance Criteria:**
- [ ] README gains a "Deploy" section (separate from the existing dev/build section)
- [ ] Section shows the minimal commands to pull and run using `docker-compose.ghcr.yml`
- [ ] Documents all supported environment variables with defaults
- [ ] Links to the GHCR package pages for both images
- [ ] Does not duplicate or replace existing developer quick-start content

## Functional Requirements

- FR-1: A single workflow file (`.github/workflows/publish.yml`) handles CI gates + image builds in a sequenced job graph
- FR-2: Quality gate jobs (`test-backend`, `test-frontend`) run in parallel; the two publish jobs (`publish-backend`, `publish-frontend`) each declare `needs: [test-backend, test-frontend]`
- FR-3: The workflow uses `permissions: packages: write` and `contents: read` at the job level
- FR-4: Image names are lowercase and follow the pattern `ghcr.io/${{ github.repository_owner }}/memorybank-backend` (and `-frontend`) so they work regardless of the repo owner
- FR-5: `docker/setup-buildx-action` is called before `build-push-action` to enable BuildKit
- FR-6: The semver tag stripping (e.g., `v1.2.3` → `1.2.3`) is handled by `docker/metadata-action` flavor configuration, not manually
- FR-7: `docker-compose.ghcr.yml` must be a valid Compose file (passes `docker compose config`)

## Non-Goals

- No multi-platform builds (e.g., `linux/arm64`) — `linux/amd64` only for now
- No Helm charts or Kubernetes manifests
- No image vulnerability scanning (e.g., Trivy)
- No automatic deployment or CD after publish
- No separate staging vs. production image promotion logic
- No changes to the existing `docker-compose.yml` (dev workflow untouched)

## Technical Considerations

- The `backend/Dockerfile` uses a multi-stage build; the publish workflow should target the final stage (default)
- The `frontend/Dockerfile` also uses a multi-stage build ending in an Nginx stage; same applies
- `GITHUB_TOKEN` has package write permissions by default in Actions — no additional repository secrets are needed
- `github.repository_owner` is always lowercase on GHCR; explicitly lowercasing with `${{ github.repository_owner | lower }}` avoids failures on mixed-case usernames
- The backend test job needs a minimal Django environment (no database server required since the project uses SQLite); `pip install -r requirements.txt` then `python manage.py test` should suffice

## Success Metrics

- A push to `main` results in updated `latest` and `sha-*` tags on both GHCR packages within ~5 minutes
- A pushed tag `v1.0.0` results in images also tagged `1.0.0`, `1.0`, and `1`
- A broken backend or failing type-check prevents any image from being pushed
- An operator can run `docker compose -f docker-compose.ghcr.yml up` with no local build step

## Open Questions

- Should the workflow also run on pull requests (build only, no push) to surface test failures earlier? (Not in scope per requirements, but worth revisiting.)
- What is the desired image retention policy on GHCR? (Not a workflow concern, but worth setting in the repo package settings.)
