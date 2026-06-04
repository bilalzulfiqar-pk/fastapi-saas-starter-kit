# API

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

## Core routes

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `GET/PATCH /api/v1/users/me`
- `POST /api/v1/users/me/change-password`
- `POST /api/v1/workspaces`
- `GET /api/v1/workspaces`
- `GET/PATCH /api/v1/workspaces/{workspace_id}`
- `GET /api/v1/workspaces/{workspace_id}/members`
- `PATCH/DELETE /api/v1/workspaces/{workspace_id}/members/{member_id}`
- `POST /api/v1/workspaces/{workspace_id}/invites`
- `GET /api/v1/workspaces/{workspace_id}/invites`
- `GET /api/v1/invites/{token}`
- `POST /api/v1/invites/{token}/accept`
- `DELETE /api/v1/workspaces/{workspace_id}/invites/{invite_id}`
- `GET /api/v1/billing/plans`
- `GET /api/v1/workspaces/{workspace_id}/subscription`
