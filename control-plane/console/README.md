# Management Console

Static HTML/JS control plane UI — no business logic in the browser beyond API calls.

## Features

- Skill catalog browse/search
- Usage & estimated cost (chargeback)
- Audit log viewer
- Approval queue
- Tenant listing (admin)

## Serve locally

The API mounts this directory at `/console/` when `CONTEXT_SKILLS_CONSOLE=enabled`.

Auth: paste a Bearer JWT from your mock IdP or SSO provider.

## Skill publish lifecycle

Publishing invokes the four validation gates server-side via `POST /skills/{name}/publish` (requires approved workflow).
