# Architecture

## Overview

The starter is split into two apps:

- `apps/api` for the FastAPI backend, auth, multi-tenant rules, and data models
- `apps/web` for the Next.js dashboard shell and settings experience

## Backend shape

- `app/core` contains config, security, logging, CSRF/origin validation, and the email abstraction
- `app/modules` keeps feature logic grouped by domain: `auth`, `users`, `workspaces`, `invites`, and `billing`
- `app/db` owns the SQLModel metadata wiring and session dependency

## Frontend shape

- App Router route groups separate marketing, auth, and authenticated app pages
- TanStack Query is wrapped in reusable hooks instead of being scattered across pages
- Lightweight UI state stays in React context providers for sidebar, theme, and active workspace

## Tenancy

- Shared database, shared schema
- Every tenant-owned entity is tied to `workspace_id`
- Workspace membership is checked server-side on every protected workspace route

