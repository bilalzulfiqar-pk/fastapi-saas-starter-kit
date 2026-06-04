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

