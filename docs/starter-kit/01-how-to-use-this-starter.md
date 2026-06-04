# How To Use This Starter

Keep the shared SaaS foundation:

- Auth
- Users
- Workspaces
- Members and roles
- Invites
- Billing-ready models
- Dashboard shell
- Settings pages

Then add your product-specific logic in separate modules.

Recommended customization pattern:

- Add backend features under new `apps/api/app/modules/<your-domain>/` modules
- Add frontend features under `apps/web/features/<your-domain>/` and related dashboard pages
- Keep the starter's shared auth, workspace, and invite logic reusable instead of mixing product logic into them too early
- Update branding, marketing copy, and navigation links once the real product direction is clear
