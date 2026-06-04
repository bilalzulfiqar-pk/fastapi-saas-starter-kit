# FastAPI SaaS Starter Kit

A reusable SaaS starter kit built with Next.js, FastAPI, PostgreSQL, SQLModel, Redis, Docker Compose, and starter documentation.

## What this starter includes

- Cookie-first auth with secure defaults
- Workspace-based multi-tenancy
- Team members, roles, and invites
- Billing-ready plans and subscriptions
- Dashboard shell and settings pages
- Centralized API errors and basic logging
- Redis-backed rate limiting with in-memory fallback
- Docker Compose and starter docs

## Project layout

```txt
apps/api   FastAPI backend
apps/web   Next.js frontend
docs/      Architecture, API, security, deployment, and starter conversion notes
```

## Quick start

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open `http://localhost:3000`.

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
- The backend uses `SQLModel` with explicit model imports in `alembic/env.py`.
- `COOKIE_DOMAIN=""` is the development default so cookies remain host-only on localhost.
- Real email sending is out of scope for v1; `ConsoleEmailProvider` logs email content instead.

## Docs

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Security](docs/security.md)
- [Deployment](docs/deployment.md)
- [Starter kit guide](docs/starter-kit/00-start-here.md)
