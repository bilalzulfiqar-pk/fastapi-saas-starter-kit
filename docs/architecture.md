# Architecture

## Overview

This starter is split into two apps:

- `apps/api` for the FastAPI backend, auth, tenancy rules, invites, billing-ready models, and persistence
- `apps/web` for the Next.js dashboard shell, auth UI, settings pages, and client-side session/workspace coordination

The repository is Docker-first for local setup, while still allowing direct `pnpm` and `uvicorn` workflows when needed.

## Design goals

- Keep the starter reusable and free of product-specific business modules
- Ship a real multi-tenant SaaS foundation, not a marketing-only scaffold
- Prefer simple extension points over premature abstractions
- Keep the default local workflow easy to boot and verify

## Repository layout

```txt
apps/
  api/   FastAPI app, Alembic migrations, backend tests
  web/   Next.js app, frontend tests
docs/    Public project documentation and starter-kit guidance
scripts/ Optional runtime verification helpers
```

## Backend shape

- `app/core`
  Config, security, logging, CSRF/origin validation, rate limiting, and the email abstraction
- `app/db`
  SQLModel session dependency and metadata wiring
- `app/modules`
  Feature modules grouped by domain: `auth`, `users`, `workspaces`, `invites`, and `billing`
- `tests/`
  Backend pytest suite under `apps/api/tests/`
- `alembic/`
  Schema migrations that import `SQLModel.metadata` and the app models

The backend exposes:

- cookie-first auth endpoints
- current-user and profile endpoints
- workspace and membership APIs
- invite creation, preview, acceptance, and revocation
- billing-ready plan and subscription reads
- `GET /health` and `GET /readiness`

## Frontend shape

- App Router route groups separate marketing, auth, and authenticated app pages
- TanStack Query is wrapped in reusable hooks instead of being scattered across pages
- Lightweight UI state stays in React context providers for theme and active workspace
- `proxy.ts` protects auth-sensitive routes at the network boundary
- `AuthGuard` validates the current user inside authenticated layouts
- `WorkspaceGuard` keeps onboarding, workspace selection, and invite-accept flows consistent

## Auth and session model

- Access tokens live in an HttpOnly cookie with a short lifetime
- Refresh tokens are opaque random secrets stored hashed in the database
- Refresh cookies are path-scoped to `/api/v1/auth`
- A lightweight session marker cookie is scoped to `/` so the frontend proxy can distinguish a recoverable session from a fully signed-out visitor
- The frontend API client performs a single refresh-and-retry cycle when an access token expires
- Unsafe browser requests require a trusted `Origin` header because auth is cookie-first

## Tenancy and permissions

- Shared database, shared schema
- Tenant-owned records use `workspace_id`
- Workspace membership is enforced server-side on protected workspace routes
- Roles are `owner`, `admin`, and `member`
- Only owners can grant, revoke, or remove owner roles
- Members can leave a workspace themselves when that does not violate the last-owner rule
- Each new workspace gets a default free subscription row

## Extension boundaries

When turning this into a real product:

- add product-specific backend features under `apps/api/app/modules/<your-domain>/`
- add product-specific frontend features under `apps/web/features/<your-domain>/`
- keep shared auth, workspace, invite, and billing-foundation code generic for as long as possible

## Testing and verification

- Backend tests live in `apps/api/tests/`
- Frontend tests stay intentionally light and focus on stable behavior rather than exact UI structure
- Docker Compose runs the full local stack: `web`, `api`, `db`, and `redis`
- `scripts/verify_redis_rate_limit.py` is an optional runtime check for the Redis-backed limiter path
