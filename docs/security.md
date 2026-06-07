# Security

## Auth defaults

- Access tokens are stored in an HttpOnly cookie with a short lifetime
- Refresh tokens are random opaque secrets stored hashed in the database
- Refresh cookies are path-scoped to `/api/v1/auth`
- A lightweight session marker cookie is scoped to `/` so protected routes can distinguish recoverable sessions from signed-out visitors
- Refresh tokens are rotated on successful refresh and revoked on logout
- Passwords are hashed with Argon2id

Cookie names are configurable through environment variables:

- `ACCESS_COOKIE_NAME`
- `REFRESH_COOKIE_NAME`
- `SESSION_COOKIE_NAME`

## CSRF and origin validation

This starter uses cookie-first auth, so unsafe browser requests must be origin-checked.

- Unsafe methods are `POST`, `PATCH`, `PUT`, and `DELETE`
- `GET /health` and `GET /readiness` are exempt
- Login and registration are public, but they still require a trusted `Origin`
- The backend validates `Origin` against `FRONTEND_ORIGINS`
- No separate CSRF token is added in v1

## Cookie domain

In development the default is:

```txt
COOKIE_DOMAIN=""
```

That keeps cookies host-only on localhost and avoids brittle local domain handling.

## Logging rules

- Never log passwords, raw refresh tokens, API secrets, or cookies
- The console email provider logs email content for development only
- Replace `ConsoleEmailProvider` before adding production password-reset or verification flows

## Rate limiting

- Automated tests verify rate-limit behavior and use the in-memory fallback path by default
- In production, rate limiting should use Redis so limits are shared across app instances
- If Redis is unavailable, the app falls back to in-memory rate limiting, which still works but becomes process-local
- Verify Redis connectivity and health before deploying environments that rely on shared rate limits

### Optional Redis verification

If you want to confirm that the Redis-backed limiter path is being used in a live environment:

1. Start the stack with `docker compose up`.
2. Run `python scripts/verify_redis_rate_limit.py`.
3. Confirm the script receives `429`.
4. Confirm the script does not report a `Falling back to in-memory rate limiter` warning.

This does not replace the automated tests. It is a lightweight runtime check that Redis is reachable and the shared limiter path is active.
