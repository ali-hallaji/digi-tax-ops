#!/usr/bin/env bash

set -u

pass() {
  printf 'PASS: %s\n' "$1"
}

info() {
  printf 'INFO: %s\n' "$1"
}

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

load_env() {
  if [ -f ".env" ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
    info "Loaded environment from .env"
  else
    info ".env not found, using current shell environment and script defaults"
  fi
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

json_value() {
  local json="$1"
  local key="$2"

  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$json" | jq -r "$key"
    return
  fi

  case "$key" in
    .dev_otp)
      printf '%s' "$json" | sed -n 's/.*"dev_otp"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p'
      ;;
    .access_token)
      printf '%s' "$json" | sed -n 's/.*"access_token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p'
      ;;
    *)
      fail "jq is not installed and key '$key' is not supported by the fallback parser"
      ;;
  esac
}

assert_http_ok() {
  local url="$1"
  local name="$2"
  local response

  response="$(curl -sS -o /tmp/digitax_smoke_body.$$ -w '%{http_code}' "$url")" || fail "$name request failed"
  if [ "$response" = "200" ]; then
    pass "$name returned HTTP 200"
  else
    fail "$name returned HTTP $response"
  fi
}

load_env
require_command curl
require_command docker-compose

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
API_V1_URL="${API_V1_URL:-${API_BASE_URL}/api/v1}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:9000}"
TEST_MOBILE="${TEST_MOBILE:-09120000099}"

assert_http_ok "${API_BASE_URL}/health/check" "GET /health/check"
assert_http_ok "${API_BASE_URL}/health/db" "GET /health/db"

cors_headers="$(
  curl -sS -D - -o /dev/null -X OPTIONS "${API_V1_URL}/auth/otp/request" \
    -H "Origin: http://127.0.0.1:8080" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type"
)" || fail "CORS preflight request failed"

printf '%s\n' "$cors_headers" | grep -i '^HTTP/.* 200\|^HTTP/.* 204' >/dev/null 2>&1 \
  || fail "CORS preflight did not return HTTP 200 or 204"
printf '%s\n' "$cors_headers" | grep -i '^access-control-allow-origin:' >/dev/null 2>&1 \
  || fail "CORS preflight response is missing access-control-allow-origin"
pass "OPTIONS CORS preflight returned success status and access-control-allow-origin"

otp_request_body="$(curl -sS -X POST "${API_V1_URL}/auth/otp/request" \
  -H 'Content-Type: application/json' \
  -d "{\"mobile\":\"${TEST_MOBILE}\"}")" || fail "POST /auth/otp/request failed"
printf '%s' "$otp_request_body" | grep -q '"status"[[:space:]]*:[[:space:]]*"otp_sent"' \
  || fail "POST /auth/otp/request did not return otp_sent"
pass "POST /auth/otp/request returned otp_sent"

dev_otp="$(json_value "$otp_request_body" '.dev_otp')"
[ -n "$dev_otp" ] && [ "$dev_otp" != "null" ] \
  || fail "POST /auth/otp/request did not return dev_otp; enable DEBUG/dev OTP response for this smoke test"
pass "POST /auth/otp/request returned dev_otp for smoke verification"

otp_verify_body="$(curl -sS -X POST "${API_V1_URL}/auth/otp/verify" \
  -H 'Content-Type: application/json' \
  -d "{\"mobile\":\"${TEST_MOBILE}\",\"otp\":\"${dev_otp}\"}")" || fail "POST /auth/otp/verify failed"
access_token="$(json_value "$otp_verify_body" '.access_token')"
[ -n "$access_token" ] && [ "$access_token" != "null" ] \
  || fail "POST /auth/otp/verify did not return access_token"
pass "POST /auth/otp/verify returned access_token"

auth_header="Authorization: Bearer ${access_token}"

for endpoint in me businesses dashboard/summary dashboard/tax-status; do
  response_code="$(
    curl -sS -o /tmp/digitax_smoke_body.$$ -w '%{http_code}' \
      "${API_V1_URL}/${endpoint}" -H "$auth_header"
  )" || fail "GET /${endpoint} request failed"

  if [ "$response_code" = "200" ]; then
    pass "GET /${endpoint} returned HTTP 200"
  else
    fail "GET /${endpoint} returned HTTP $response_code"
  fi
done

if docker-compose config --services | grep -Fx frontend >/dev/null 2>&1; then
  frontend_status="$(curl -sS -o /tmp/digitax_frontend_body.$$ -w '%{http_code}' "$FRONTEND_URL")" \
    || fail "Frontend URL check failed"
  if [ "$frontend_status" = "200" ]; then
    pass "Frontend URL returned HTTP 200"
  else
    fail "Frontend URL returned HTTP $frontend_status"
  fi
else
  info "Frontend service is not defined; skipping frontend URL check"
fi

