# Deployment

## MVP targets

- Frontend: Vercel or Docker
- Backend: Render, Railway, Fly.io, or Docker on a VPS
- Database: managed PostgreSQL
- Redis: managed Redis or a container for smaller self-hosted environments

## Local Docker workflow

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Confirm:
   - `http://localhost:3000`
   - `http://localhost:8000/health`
   - `http://localhost:8000/readiness`

To stop the local stack:

```bash
docker compose down
```

## Production checklist

- Set a strong `SECRET_KEY`
- Set real `APP_URL`, `API_URL`, `NEXT_PUBLIC_APP_URL`, and `NEXT_PUBLIC_API_URL`
- Set `COOKIE_SECURE=true`
- Configure a real `FRONTEND_ORIGINS` allowlist
- Set production `DATABASE_URL` and `REDIS_URL`
- Run `alembic upgrade head`
- Use HTTPS for both frontend and backend
- Replace `ConsoleEmailProvider` with a real provider before enabling password reset or verification flows

## Local release check

Before publishing or tagging a public starter update, run:

- `pnpm test:api`
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test:web`
- `pnpm --dir apps/web build`
- `docker compose up --build`

Then smoke-check the starter by:

1. registering a user
2. creating a first workspace
3. opening the dashboard and settings pages
4. inviting a teammate
5. accepting that invite from a second account
6. confirming the invited member appears in the workspace

If you also want to verify the Redis-backed rate limiter path, run:

```bash
python scripts/verify_redis_rate_limit.py
```
