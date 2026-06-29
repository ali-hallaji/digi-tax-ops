# Auth Hardening — Rate Limiting + Self-Hosted CAPTCHA (design note)

_Added 2026-06-29 with user management + per-business RBAC + password login._

Goal: brute-force protection and bot mitigation on the auth surface that works
**inside Iran** — no Google reCAPTCHA, hCaptcha, Cloudflare Turnstile, or any
remote CDN. Everything is self-hosted and backed by the Postgres/Redis we already run.

## Threat model
- Credential stuffing / password brute force on `POST /auth/login`.
- OTP request flooding / SMS-abuse on `POST /auth/otp/request`.
- Automated scripted abuse of both endpoints.

## Controls

### 1. Redis sliding-window rate limiting — `app/core/rate_limit.py`
- Keys: **per client IP** (`ip:<ip>`) **and** per identifier (`login:<username>` /
  `otp:<mobile>`). Either tripping blocks the attempt.
- Window: a Redis **sorted set** per key; each attempt is a timestamped member.
  Members older than the window are trimmed on every hit, so the count reflects
  only the trailing `auth_rate_limit_window_seconds`.
- Lockout: once the count exceeds `auth_rate_limit_max_attempts`, a block key is
  set for `auth_rate_limit_block_seconds`; while present the caller is rejected
  up-front with the remaining TTL as `Retry-After`.
- Response: **429** with friendly Persian «تعداد تلاش بیش از حد مجاز؛ کمی بعد دوباره امتحان کنید»
  (never a raw 500).
- Failure mode: **fail-open** — if Redis is unreachable we allow the request
  (availability over strictness; the CAPTCHA below is the fail-closed control).

Defaults (env-tunable): 5 attempts / 60 s window / 300 s lockout.

### 2. Self-hosted proof-of-work CAPTCHA (Altcha) — `app/core/captcha.py`
- `GET /auth/captcha/challenge` returns a signed Altcha PoW challenge
  `{algorithm, challenge, salt, signature, maxnumber}`.
  - `challenge = SHA256(salt + secret_number)`, `signature = HMAC_SHA256(secret_key, challenge)`.
  - `salt` embeds `?expires=<unix_ts>` for a short validity window.
- The client (bundled **`altcha` web component**, no CDN) brute-forces the integer
  whose `SHA256(salt + n)` matches `challenge`, then returns
  `base64(JSON{algorithm, challenge, number, salt, signature})`.
- Verification recomputes the challenge and the HMAC signature, enforces the salt
  expiry, and records the challenge in Redis (`captcha:used:<challenge>`) so each
  challenge is **single-use** (replay protection).
- Enforced server-side on `POST /auth/login` and `POST /auth/otp/request`. A
  missing/invalid solution → **400** «تأیید امنیتی ناموفق بود؛ لطفاً دوباره تلاش کنید».
- Failure mode: **fail-closed** on the cryptographic checks; the replay guard is
  best-effort (if Redis is down the PoW + signature + expiry checks still stand).

## Why Altcha PoW (not reCAPTCHA/hCaptcha)
- Fully self-hosted; the only network call the widget makes is to **our** challenge
  endpoint. Works when Google/Cloudflare are blocked — the Iran-safe requirement.
- No third-party JS, no tracking, no API keys.

## Config flags (`app/core/config.py`) — default ON
| Flag | Default | Purpose |
|---|---|---|
| `auth_rate_limit_enabled` | `true` | master switch for rate limiting |
| `auth_rate_limit_max_attempts` | `5` | attempts per window per key |
| `auth_rate_limit_window_seconds` | `60` | sliding window |
| `auth_rate_limit_block_seconds` | `300` | lockout once exceeded |
| `auth_captcha_enabled` | `true` | master switch for the PoW CAPTCHA |
| `auth_captcha_max_number` | `100000` | PoW search space |
| `auth_captcha_ttl_seconds` | `300` | challenge validity / replay-key TTL |

## Testing
- `tests/conftest.py` disables both controls for the broad suite (which predates them).
- `tests/modules/identity/test_auth_hardening.py` re-enables and exercises: the
  sliding-window blocking, the route-level 429, captcha-required (400), captcha-solved
  (200), and the challenge endpoint. fakeredis backs the limiter/captcha in tests.

## Deploy / env notes
- **Rebuild the `api` image** — `argon2-cffi` was added for password hashing.
- Keep both flags **ON** in staging/prod.
- **E2E:** set `AUTH_CAPTCHA_ENABLED=false` and `AUTH_RATE_LIMIT_ENABLED=false` in the
  E2E backend env (otherwise `/auth/otp/request` returns 400 without a solved challenge).
- Redis is already required (OTP store); these controls add keys under `authrl:*` and
  `captcha:used:*`.
