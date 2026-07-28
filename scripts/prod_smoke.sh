#!/usr/bin/env bash
# The «prod smoke suite» — what CAN be verified automatically on a freshly
# migrated, production-shaped stack (PRE-PRODUCTION rehearsal deliverable).
#
#   bash scripts/prod_smoke.sh                        # defaults to the dev stack
#   API=http://127.0.0.1:8100 WEB=http://127.0.0.1:3100 bash scripts/prod_smoke.sh
#
# WHY THIS IS SHORT — and why that is not laziness:
# the experience harness logs in by reading the dev OTP out of the API response.
# A production-shaped stack has DEBUG=false and a real SMS provider, so the OTP
# is never returned to any client. Therefore NO automated spec can authenticate
# on production, and 14 of the 15 harness specs (all persona-dependent) are
# meaningless on a database that has no personas. Exactly one harness spec —
# 11-landing — is production-safe. Select it BY PATH, never `--grep landing`:
# that ALSO matches 05-p5-admin («/admin landing»), which needs personas and
# fails on a virgin database (proven during the rehearsal).
#
# So the honest production gate is:
#   1. this script (unauthenticated surface + the security postures)   ← automated
#   2. pnpm harness tests/e2e-harness/specs/11-landing.spec.ts         ← automated
#   3. ONE manual founder login with a real OTP                        ← human, required
# Step 3 is NOT optional and NOT automatable. Do not declare a bring-up verified
# without it.
set -uo pipefail

API="${API:-http://127.0.0.1:8000}"
WEB="${WEB:-http://127.0.0.1:3000}"

pass=0
fail=0
ok()   { echo "  ✓ $1"; pass=$((pass + 1)); }
bad()  { echo "  ✗ $1"; fail=$((fail + 1)); }

echo "▶ prod smoke — API=$API  WEB=$WEB"
echo

echo "1. Liveness"
code=$(curl -s -o /dev/null -w '%{http_code}' "$API/health/check")
[ "$code" = "200" ] && ok "GET /health/check → 200" || bad "GET /health/check → $code"

ver=$(curl -s "$API/health/version")
head=$(printf '%s' "$ver" | grep -o '"alembic_head":"[^"]*"' | cut -d'"' -f4)
[ -n "$head" ] && ok "alembic head reported: $head" || bad "no alembic_head in /health/version"

sha=$(printf '%s' "$ver" | grep -o '"git_sha":"[^"]*"' | cut -d'"' -f4)
if [ "$sha" = "unknown" ] || [ -z "$sha" ]; then
  bad "api git_sha is «$sha» — BACKEND_SHA was not exported before the build"
else
  ok "api git_sha: $sha"
fi

code=$(curl -s -o /dev/null -w '%{http_code}' "$WEB/")
[ "$code" = "200" ] && ok "GET $WEB/ → 200" || bad "GET $WEB/ → $code"

wsha=$(curl -s "$WEB/version.json" | grep -o '"sha":"[^"]*"' | cut -d'"' -f4)
if [ -z "$wsha" ] || [ "$wsha" = "unknown" ]; then
  bad "frontend version.json sha is «$wsha» — FRONTEND_SHA was not exported"
else
  ok "frontend sha: $wsha"
fi

echo
echo "2. Production security posture (these MUST hold before anyone is let in)"

# Captcha on: a raw OTP request carrying no PoW must be refused.
#
# Probe a mobile that is NOBODY. 09120000000 is the founder's protected persona
# and it is exactly the account `dev_login_otp_hint` is allowed to hint for, so
# probing it tested the one number whose behaviour is deliberately special —
# a green here said nothing about what a real visitor meets.
PROBE_MOBILE=${PROBE_MOBILE:-09129999999}
body=$(curl -s -X POST "$API/api/v1/auth/otp/request" \
  -H 'Content-Type: application/json' -d "{\"mobile\":\"$PROBE_MOBILE\"}")
if printf '%s' "$body" | grep -qi 'altcha\|captcha\|تأیید امنیتی'; then
  ok "captcha refuses a raw OTP request"
else
  bad "raw OTP request was NOT refused by captcha — body: $(printf '%s' "$body" | head -c 120)"
fi

# DEBUG=false: no OTP may ever appear in an API response.
#
# The pattern used to be '"otp"' — which does NOT match `"otp_hint"`, the field
# the API actually returns (schemas.py OtpRequestResponse.otp_hint). The one
# leak this check exists to catch was the one shape it could not see. Match any
# key that STARTS with otp, plus a bare numeric code.
if printf '%s' "$body" | grep -qiE '"(dev_)?otp[a-z_]*"[[:space:]]*:[[:space:]]*"?[0-9]|"code"[[:space:]]*:[[:space:]]*"?[0-9]'; then
  bad "an OTP-looking field appeared in the response — DEBUG/OTP-hint is not off: $(printf '%s' "$body" | head -c 160)"
else
  ok "no OTP echoed in the API response (DEBUG off, no otp_hint)"
fi

# Swagger auto-auth / docs exposure.
code=$(curl -s -o /dev/null -w '%{http_code}' "$API/docs")
if [ "$code" = "200" ]; then
  echo "  · note: /docs is reachable (200) — acceptable only if deliberate"
else
  ok "/docs not publicly served ($code)"
fi

# An unauthenticated tenant-scoped call must be refused, never served.
code=$(curl -s -o /dev/null -w '%{http_code}' "$API/api/v1/customers")
[ "$code" = "401" ] || [ "$code" = "403" ] \
  && ok "unauthenticated /customers → $code" \
  || bad "unauthenticated /customers → $code (expected 401/403)"

echo
echo "3. Reference data"
units=$(curl -s -o /dev/null -w '%{http_code}' "$API/health/check")
echo "  · tax_units / module prices are DB facts — verify with psql:"
echo "      docker compose exec -T postgres psql -U digitax -d digitax \\"
echo "        -c 'SELECT count(*) FROM tax_units;'   # expect 102 (RC_UMGS v1.18)"

echo
echo "────────────────────────────────────────────"
echo "  passed: $pass    failed: $fail"
if [ "$fail" -gt 0 ]; then
  echo "  ✗ PROD SMOKE RED — do not open the door."
  exit 1
fi
cat <<'REMAINING'
  ✓ automated prod smoke GREEN.

  STILL REQUIRED before go-live (not automatable — see header):
    · pnpm harness --base-url <prod> tests/e2e-harness/specs/11-landing.spec.ts
    · ONE manual founder login with a REAL OTP to a real handset
REMAINING
