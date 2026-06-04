# Security

## Auth defaults

- Access tokens are stored in an HttpOnly cookie with a short lifetime
- Refresh tokens are random opaque secrets stored hashed in the database
- Refresh cookies are path-scoped to `/api/v1/auth`
- Passwords are hashed with Argon2id

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

