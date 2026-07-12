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

assert_frontend_route() {
  local url="$1"
  local name="$2"
  local body_file="$3"
  local response

  response="$(curl -sS -L -o "$body_file" -w '%{http_code}' "$url")" || fail "$name request failed"
  case "$response" in
    200|301|302|307|308|401|403)
      pass "$name returned acceptable HTTP $response"
      ;;
    404|5??)
      fail "$name returned HTTP $response"
      ;;
    *)
      fail "$name returned unexpected HTTP $response"
      ;;
  esac
}

assert_no_hardcoded_backend_ip() {
  local body_file="$1"
  local name="$2"

  if grep -E 'https?://([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]+)?/api' "$body_file" >/dev/null 2>&1; then
    fail "$name contains an apparent hardcoded backend IP URL"
  fi

  pass "$name does not contain an obvious hardcoded backend IP URL"
}

scan_frontend_script_urls() {
  local body_file="$1"
  local base_url="$2"
  local script_paths script_path script_url script_body

  script_paths="$(
    grep -Eo 'src="[^"]+\.js[^"]*"' "$body_file" 2>/dev/null \
      | sed 's/^src="//; s/"$//' \
      | head -n 5
  )"

  [ -n "$script_paths" ] || return 0

  while IFS= read -r script_path; do
    case "$script_path" in
      http://*|https://*)
        script_url="$script_path"
        ;;
      /*)
        script_url="${base_url%/}${script_path}"
        ;;
      *)
        script_url="${base_url%/}/${script_path}"
        ;;
    esac

    script_body="/tmp/digitax_frontend_script.$$"
    if curl -sS -L -o "$script_body" "$script_url" >/dev/null 2>&1; then
      assert_no_hardcoded_backend_ip "$script_body" "Frontend JS asset $script_path"
    else
      info "Skipping frontend JS asset scan for $script_path; asset fetch failed"
    fi
  done <<EOF
$script_paths
EOF
}

load_env
require_command curl
require_command docker

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
API_V1_URL="${API_V1_URL:-${API_BASE_URL}/api/v1}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:${FRONTEND_PORT}}"
FRONTEND_BASE_URL="${FRONTEND_BASE_URL:-$FRONTEND_URL}"
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

# ── OTP persistence across api restart (verifies Redis-backed OTP) ────────────
SMOKE_TEST_RESTART_OTP="${SMOKE_TEST_RESTART_OTP:-}"
if [ "${SMOKE_TEST_RESTART_OTP:-0}" = "1" ]; then
  RESTART_MOBILE="${RESTART_MOBILE:-09120000098}"
  otp_restart_body="$(curl -sS -X POST "${API_V1_URL}/auth/otp/request" \
    -H 'Content-Type: application/json' \
    -d "{\"mobile\":\"${RESTART_MOBILE}\"}")" || fail "OTP restart: POST /auth/otp/request failed"
  restart_otp="$(json_value "$otp_restart_body" '.dev_otp')"
  [ -n "$restart_otp" ] && [ "$restart_otp" != "null" ] \
    || fail "OTP restart: did not get dev_otp before restart"
  pass "OTP restart: dev_otp obtained before api restart"

  docker compose restart api >/dev/null 2>&1 || fail "OTP restart: docker compose restart api failed"
  info "OTP restart: api restarted, waiting for health..."
  for i in $(seq 1 15); do
    if curl -sS -o /dev/null -w '%{http_code}' "${API_BASE_URL}/health/check" 2>/dev/null | grep -q '^200$'; then
      break
    fi
    sleep 2
  done
  curl -sS -o /dev/null -w '%{http_code}' "${API_BASE_URL}/health/check" | grep -q '^200$' \
    || fail "OTP restart: api did not recover after restart"
  pass "OTP restart: api healthy after restart"

  otp_verify_after_restart="$(curl -sS -X POST "${API_V1_URL}/auth/otp/verify" \
    -H 'Content-Type: application/json' \
    -d "{\"mobile\":\"${RESTART_MOBILE}\",\"otp\":\"${restart_otp}\"}")" \
    || fail "OTP restart: POST /auth/otp/verify failed after restart"
  restart_token="$(json_value "$otp_verify_after_restart" '.access_token')"
  [ -n "$restart_token" ] && [ "$restart_token" != "null" ] \
    || fail "OTP restart: OTP was lost after api restart — Redis may not be in use"
  pass "OTP restart: OTP survived api restart (Redis-backed confirmed)"
else
  info "OTP restart test skipped (set SMOKE_TEST_RESTART_OTP=1 to enable)"
fi

if docker compose config --services | grep -Fx frontend >/dev/null 2>&1; then
  frontend_root_body="/tmp/digitax_frontend_root.$$"
  frontend_login_body="/tmp/digitax_frontend_login.$$"
  frontend_app_body="/tmp/digitax_frontend_app.$$"

  assert_frontend_route "${FRONTEND_BASE_URL%/}/" "Frontend root" "$frontend_root_body"
  assert_frontend_route "${FRONTEND_BASE_URL%/}/login" "Frontend /login" "$frontend_login_body"
  assert_frontend_route "${FRONTEND_BASE_URL%/}/app" "Frontend /app deep route" "$frontend_app_body"

  assert_no_hardcoded_backend_ip "$frontend_root_body" "Frontend root HTML"
  assert_no_hardcoded_backend_ip "$frontend_login_body" "Frontend /login HTML"
  assert_no_hardcoded_backend_ip "$frontend_app_body" "Frontend /app HTML"
  scan_frontend_script_urls "$frontend_login_body" "$FRONTEND_BASE_URL"
else
  info "Frontend service is not defined; skipping frontend URL check"
fi
