# API Contracts

Store exported OpenAPI snapshots here. Frontend must consume backend contracts, not invent routes.

## Exporting a snapshot

Run these commands from `digi-tax-ops` after the api container is up:

```bash
# Export OpenAPI JSON snapshot
curl -s http://localhost:8000/openapi.json | python3 -m json.tool > api-contracts/openapi.json

# Or export YAML via the backend's export command if available
docker-compose exec api python -c "
import json, asyncio
from app.main import app
print(json.dumps(app.openapi()))
" > api-contracts/openapi.json
```

Commit the snapshot after any backend API change:

```bash
git add api-contracts/openapi.json
git commit -m "chore: update OpenAPI snapshot"
```

## Rules

- All API routes are under `/api/v1` except `/health`.
- Frontend reads these contracts; it does not invent routes.
- Keep the snapshot in sync with the running backend — stale snapshots hide drift.
- See `docs/api_contract_rules.md` for full endpoint list and contract rules.
