# API

## Base URLs

- Application API: `/api/v1`
- Health checks: `/health` and `/readiness`

## Response conventions

Successful responses return:

```json
{
  "data": {},
  "message": "optional"
}
```

Errors return:

```json
{
  "error": {
    "code": "workspace_not_found",
    "message": "Workspace not found"
  }
}
```

## Runtime checks

- `GET /health`
- `GET /readiness`

## Auth routes

- `POST /api/v1/auth/register`
  Creates a user and immediately issues auth cookies.
- `POST /api/v1/auth/login`
  Authenticates a user and issues auth cookies.
- `POST /api/v1/auth/logout`
  Revokes the active refresh token and clears auth cookies.
- `POST /api/v1/auth/refresh`
  Rotates the refresh token and reissues cookies.
- `GET /api/v1/auth/me`
  Returns the current authenticated user.

## User routes

- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/me/change-password`

## Workspace and membership routes

- `POST /api/v1/workspaces`
- `GET /api/v1/workspaces`
- `GET/PATCH /api/v1/workspaces/{workspace_id}`
- `GET /api/v1/workspaces/{workspace_id}/members`
- `PATCH/DELETE /api/v1/workspaces/{workspace_id}/members/{member_id}`

## Invite routes

- `POST /api/v1/workspaces/{workspace_id}/invites`
- `GET /api/v1/workspaces/{workspace_id}/invites`
- `DELETE /api/v1/workspaces/{workspace_id}/invites/{invite_id}`
- `GET /api/v1/invites/{token}`
- `POST /api/v1/invites/{token}/accept`

## Billing routes

- `GET /api/v1/billing/plans`
- `GET /api/v1/workspaces/{workspace_id}/subscription`

## Auth and browser request notes

- This starter uses cookie-first auth for the web app
- Unsafe browser methods require a trusted `Origin` header
- Login and registration remain public, but they still require a trusted `Origin`
- Rate limiting applies to sensitive routes such as login, register, refresh, and invite acceptance
