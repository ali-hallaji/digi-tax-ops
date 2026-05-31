# Architecture Decisions - Ops

These decisions are immutable unless the user explicitly approves an architecture change.

- Keep the three canonical repositories: `digi-tax-backend`, `digi-tax-frontend`, and `digi-tax-ops`.
- `digi-tax-ops` owns Docker Compose, Nginx, scripts, API contract snapshots, integration docs, environment examples, and local/staging orchestration.
- Backend application logic belongs in `digi-tax-backend`.
- Frontend application logic belongs in `digi-tax-frontend`.
- The canonical frontend stack is React/TanStack/Vite.
- Initial deployment target is Docker Compose + Nginx.
- Backend and ops validation must be Docker/Compose-first.
- Do not use Python, Poetry, or Python package installation on the host for backend/ops validation.
- Do not rebuild Docker images for every small change; rebuild only for dependency, Dockerfile, base image, or environment/build config changes.
- Proxy values must come from the developer shell, ignored local env files, or explicit one-off user-provided build args.
- Do not commit or embed proxy URLs, proxy ports, credentials, tokens, or network workarounds.
- Do not add Kubernetes by default.
- Do not add Prometheus, Grafana, MinIO, or other optional stacks by default.
- Do not commit secrets or production credentials.
