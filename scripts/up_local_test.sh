#!/usr/bin/env bash
# Local test environment bring-up for Digi Invoice / DigiTax
# Run from: digi-tax-ops/   (where docker-compose.yml lives)
# Usage:    bash up_local_test.sh
set -euo pipefail

echo "▶ 1/5  Bringing up postgres + redis + api ..."
docker compose up -d postgres redis api

echo "▶ 2/5  Waiting a few seconds for postgres to accept connections ..."
sleep 6

echo "▶ 3/5  Applying database migrations (inside the api container) ..."
# IMPORTANT: use 'exec' (inside compose network), NOT 'docker run' (isolated, can't see postgres)
docker compose exec -T api python -m alembic upgrade head

echo "▶ 4/5  Seeding sample/dev data (inside the api container) ..."
docker compose exec -T api python -m app.cli.seed_dev_data

echo "▶ 5/5  Service status:"
docker compose ps

cat <<'EOF'

✅ Backend + DB are up and seeded.

NOW START THE FRONTEND (on your laptop, in another terminal):
    cd ../digi-tax-frontend
    pnpm install        # first time only
    pnpm run dev

Then GO CHECK in your browser:
    open the URL pnpm prints (usually http://localhost:3000)
    - log in with the dev OTP flow (the OTP is returned in the response — test mode)
    - walk the onboarding journey: is the next step always obvious?
    - is it welcoming, simple, calm, RTL-correct?
    - narrow the window / use device toolbar → check mobile responsiveness

API docs (to confirm backend is alive): http://localhost:8000/docs

To stop everything later:
    docker compose down
EOF
