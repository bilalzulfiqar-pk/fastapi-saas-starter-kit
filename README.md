# FastAPI SaaS Starter Kit

A reusable SaaS starter kit built with Next.js, FastAPI, PostgreSQL, SQLModel, Redis, Docker Compose, and starter documentation.

## What ships in the MVP

- Cookie-first auth with secure defaults
- Workspace-based multi-tenancy
- Team members, roles, and invites
- Billing-ready plans and subscriptions
- Dashboard shell and settings pages
- Centralized API errors and basic logging
- Redis-backed rate limiting with in-memory fallback
- Docker Compose, tests, and starter docs

## What is intentionally out of scope

- Product-specific modules such as CRM, inventory, LMS, booking, support, or AI/RAG
- API keys
- Audit logs
- Password reset and email verification
- Real email delivery providers
- Stripe checkout, customer portal, and webhooks

## Project layout

```txt
apps/api     FastAPI backend
apps/web     Next.js frontend
docs/        Architecture, API, security, deployment, and starter conversion notes
scripts/     Optional verification and helper scripts
```

## Requirements

- Docker Desktop or another Docker engine with Compose support
- Optional for local non-Docker checks:
  - Python 3.11+
  - Node.js 22+
  - `pnpm`

## Quick start with Docker

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open `http://localhost:3000`.
4. Use `http://localhost:8000/health` and `http://localhost:8000/readiness` if you want to confirm API health.

## Useful commands

Most teams can stay Docker-first. The commands below cover both the Docker workflow and optional local development workflows.

- `pnpm dev`
  Starts the Docker Compose stack from the repo root.
- `pnpm dev:web`
  Starts the Next.js app locally outside Docker.
- `pnpm dev:api`
  Starts the FastAPI app locally outside Docker.
- `pnpm lint`
  Runs the web ESLint checks.
- `pnpm typecheck`
  Runs the web TypeScript checks.
- `pnpm test:api`
  Runs the backend pytest suite.
- `pnpm test:web`
  Runs the frontend Vitest suite.

## Verification

Run the core checks before publishing or customizing the starter:

- `python -m pytest apps/api/tests`
- `corepack pnpm --dir apps/web lint`
- `corepack pnpm --dir apps/web typecheck`
- `corepack pnpm --dir apps/web test`
- `corepack pnpm --dir apps/web build`
- `docker compose up --build`
- `python scripts/verify_redis_rate_limit.py` (optional Redis-path runtime check)

Recommended smoke flow:

1. Register a new account.
2. Create the first workspace in onboarding.
3. Open the dashboard and each settings page.
4. Send an invite from the members/settings flow.
5. Register or log in as the invited user and accept the invite.
6. Confirm the invited user appears in workspace members.

## Key implementation notes

- The frontend uses `Next.js 16` and `proxy.ts`.
- The frontend uses TanStack Query for server state and React context for small UI state.
- The backend uses `SQLModel` with explicit model imports in `alembic/env.py`.
- Auth uses a short-lived access cookie, a path-scoped refresh cookie, and a lightweight session marker cookie for protected-route recovery.
- `COOKIE_DOMAIN=""` is the development default so cookies remain host-only on localhost.
- Real email sending is out of scope for v1; `ConsoleEmailProvider` logs email content instead.

## Docs

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Security](docs/security.md)
- [Deployment](docs/deployment.md)
- [Scripts](scripts/README.md)
- [Starter kit guide](docs/starter-kit/00-start-here.md)
