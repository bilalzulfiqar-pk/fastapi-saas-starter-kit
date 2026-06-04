# Architecture

## Overview

The starter is split into two apps:

- `apps/api` for the FastAPI backend, auth, multi-tenant rules, and data models
- `apps/web` for the Next.js dashboard shell and settings experience

The repo is intentionally Docker-first for local setup, while still allowing local `pnpm` and `uvicorn` workflows when you want them.

## Repo layout

```txt
apps/
  api/   FastAPI app, Alembic migrations, backend tests
  web/   Next.js app, frontend tests
docs/    Public project documentation and starter-kit guidance
scripts/ Optional runtime verification helpers
```

## Backend shape

- `app/core` contains config, security, logging, CSRF/origin validation, and the email abstraction
- `app/modules` keeps feature logic grouped by domain: `auth`, `users`, `workspaces`, `invites`, and `billing`
- `app/db` owns the SQLModel metadata wiring and session dependency
- `tests/` contains the backend pytest suite
- `alembic/` manages schema migrations and imports SQLModel metadata from the app modules

The backend exposes:

- cookie-first auth endpoints
- workspace and membership APIs
- invite creation, preview, acceptance, and revocation
- billing-ready plan and subscription reads
- `GET /health` and `GET /readiness` for runtime checks

## Frontend shape

- App Router route groups separate marketing, auth, and authenticated app pages
- TanStack Query is wrapped in reusable hooks instead of being scattered across pages
- Lightweight UI state stays in React context providers for sidebar, theme, and active workspace
- `proxy.ts` protects auth-sensitive routes at the network edge
- `AuthGuard` validates the current user inside authenticated layouts
- `WorkspaceGuard` keeps onboarding, workspace selection, and invite-accept flows consistent

## Auth and session model

- Access tokens live in an HttpOnly cookie with a short lifetime
- Refresh tokens are opaque random secrets stored hashed in the database
- Refresh cookies are path-scoped to `/api/v1/auth`
- A lightweight session marker cookie is scoped to `/` so the Next.js proxy can distinguish a recoverable session from a fully signed-out visitor
- The frontend API client performs a single refresh-and-retry cycle when an access token expires
- Unsafe browser requests require a trusted `Origin` header because auth is cookie-first

## Tenancy

- Shared database, shared schema
- Every tenant-owned entity is tied to `workspace_id`
- Workspace membership is checked server-side on every protected workspace route
- Roles are `owner`, `admin`, and `member`
- Only owners can grant, revoke, or remove owner roles
- Each new workspace gets a default free subscription row

## Testing and verification

- Backend tests live in `apps/api/tests/`
- Frontend tests live next to web hooks and components where lightweight behavior coverage adds value
- Docker Compose runs the full local stack: `web`, `api`, `db`, and `redis`
- `scripts/verify_redis_rate_limit.py` is an optional runtime check for the Redis-backed limiter path
