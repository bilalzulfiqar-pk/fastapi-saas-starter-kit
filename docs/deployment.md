# Deployment

## MVP targets

- Frontend: Vercel or Docker
- Backend: Render, Railway, Fly.io, or Docker on a VPS
- Database: managed PostgreSQL
- Redis: managed Redis or local container in small environments

## Production checklist

- Set a strong `SECRET_KEY`
- Set `COOKIE_SECURE=true`
- Configure a real `FRONTEND_ORIGINS` allowlist
- Run `alembic upgrade head`
- Use HTTPS for both frontend and backend
- Replace `ConsoleEmailProvider` with a real provider before enabling password reset or verification flows

## Local release check

Before pushing a public starter update, run the local verification set:

- `python -m pytest apps/api/tests`
- `corepack pnpm --dir apps/web lint`
- `corepack pnpm --dir apps/web typecheck`
- `corepack pnpm --dir apps/web test`
- `corepack pnpm --dir apps/web build`
- `docker compose up --build`

Smoke-check the starter by registering a user, creating a first workspace, opening the settings pages, inviting a teammate, and accepting that invite from a second account.

If you also want to verify the Redis-backed rate limiter path, run `python scripts/verify_redis_rate_limit.py` against the live Docker stack.
