#!/usr/bin/env python3
"""Digi Invoice workspace script manager.

A thin dispatcher: prints what it will run, then runs existing scripts.
Never reimplements what a script already does.

Usage:
    python3 digi-tax-ops/scripts/digi-invoice-manager.py [command]
    python3 digi-tax-ops/scripts/digi-invoice-manager.py --help

Run from anywhere in the workspace; paths are resolved from this script's location.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
OPS_DIR    = SCRIPT_DIR.parent
WORKSPACE  = OPS_DIR.parent
BACKEND    = WORKSPACE / "digi-tax-backend"
FRONTEND   = WORKSPACE / "digi-tax-frontend"

# ── Helpers ───────────────────────────────────────────────────────────────────

def _run(cmd: list | str, *, cwd: Path | None = None) -> None:
    """Print what will run, then exec it; propagate exit code."""
    label = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f"\n▶  {label}\n", flush=True)
    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str))
    if result.returncode != 0:
        sys.exit(result.returncode)

def _die(msg: str) -> None:
    print(f"\n✗  {msg}", file=sys.stderr)
    sys.exit(1)

def _check_ops_services() -> None:
    """Fail loudly if docker-compose stack is not up."""
    r = subprocess.run(
        ["docker-compose", "ps", "--services", "--filter", "status=running"],
        cwd=OPS_DIR, capture_output=True, text=True,
    )
    running = r.stdout.strip().splitlines()
    for svc in ("postgres", "api"):
        if svc not in running:
            _die(
                f"Service '{svc}' is not running. "
                "Start the stack first: python3 scripts/digi-invoice-manager.py setup:up"
            )

# ── SETUP ─────────────────────────────────────────────────────────────────────

def setup_preflight() -> None:
    """Check Docker, env, DB name, and all service readiness."""
    _run(["bash", "scripts/preflight.sh"], cwd=OPS_DIR)

def setup_bootstrap() -> None:
    """First-time: create DB, user, run all Alembic migrations (idempotent)."""
    _run(["bash", "scripts/bootstrap.sh"], cwd=OPS_DIR)

def setup_up() -> None:
    """Bring up the full local stack (postgres + redis + api) via docker-compose."""
    _run(["docker-compose", "up", "-d"], cwd=OPS_DIR)

# ── SEED ──────────────────────────────────────────────────────────────────────

def seed_dev() -> None:
    """Load fixed test accounts (09120000000 / 09120000099 / 09120000001) into running stack."""
    _check_ops_services()
    _run(
        ["docker-compose", "exec", "-T", "api", "python", "-m", "app.cli.seed_dev_data"],
        cwd=OPS_DIR,
    )

def seed_qa() -> None:
    """Load QA invoice scenario data into running stack."""
    _check_ops_services()
    _run(
        ["docker-compose", "exec", "-T", "api", "python", "-m", "app.cli.seed_qa_invoice"],
        cwd=OPS_DIR,
    )

def seed_demo() -> None:
    """Seed realistic demo business data via the public API (safe, re-runnable)."""
    _check_ops_services()
    _run(["python3", "scripts/seed_demo_business.py"], cwd=OPS_DIR)

# ── DATABASE ──────────────────────────────────────────────────────────────────

def db_upgrade() -> None:
    """Run all pending Alembic migrations inside the api container."""
    _check_ops_services()
    _run(
        ["docker-compose", "exec", "-T", "api", "alembic", "upgrade", "head"],
        cwd=OPS_DIR,
    )

def db_status() -> None:
    """Show Alembic head revision AND list all DB tables (psql verification)."""
    _check_ops_services()
    print("\n── Alembic current ──")
    _run(
        ["docker-compose", "exec", "-T", "api", "alembic", "current"],
        cwd=OPS_DIR,
    )
    print("\n── DB tables (psql) ──")
    _run(
        [
            "docker-compose", "exec", "-T", "postgres",
            "psql", "-U", "digitax", "-d", "digitax",
            "-c", r"\dt",
        ],
        cwd=OPS_DIR,
    )

def db_tables() -> None:
    """List all tables in the digitax database via psql."""
    _check_ops_services()
    _run(
        [
            "docker-compose", "exec", "-T", "postgres",
            "psql", "-U", "digitax", "-d", "digitax",
            "-c",
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;",
        ],
        cwd=OPS_DIR,
    )

# ── FRONTEND ──────────────────────────────────────────────────────────────────

def front_dev() -> None:
    """Start the Vite dev server (localhost:8080). Requires pnpm in PATH."""
    _run(["pnpm", "run", "dev"], cwd=FRONTEND)

def front_build() -> None:
    """Production build — must succeed before any commit or deploy."""
    _run(["pnpm", "run", "build"], cwd=FRONTEND)

def front_typecheck() -> None:
    """TypeScript check — must be zero errors before any commit."""
    _run(["pnpm", "run", "typecheck"], cwd=FRONTEND)

# ── TEST ──────────────────────────────────────────────────────────────────────

def test_backend() -> None:
    """Run pytest inside Docker. 513+ pass / 7 pre-existing fail = green baseline."""
    _check_ops_services()
    _run(
        [
            "docker-compose", "exec", "-T", "api",
            "python", "-m", "pytest", "-v", "--tb=short",
        ],
        cwd=OPS_DIR,
    )

def test_e2e() -> None:
    """Run Playwright E2E suite (phase-end only). Requires frontend dev server + stack up.

    IMPORTANT: E2E needs captcha/rate-limit disabled in the backend env:
      AUTH_CAPTCHA_ENABLED=false
      AUTH_RATE_LIMIT_ENABLED=false
    Set these in digi-tax-ops/.env before running, then restore to true.
    Trust the real exit code — not the report text file.
    """
    print(__doc__)
    _run(["pnpm", "e2e"], cwd=FRONTEND)

# ── MAINTENANCE ───────────────────────────────────────────────────────────────

def maintenance_smoke() -> None:
    """Smoke test running stack: health, CORS, OTP, bearer, frontend."""
    _run(["bash", "scripts/smoke_test.sh"], cwd=OPS_DIR)

def maintenance_rebuild_api() -> None:
    """Rebuild api Docker image after any backend code change (no-cache to avoid stale layer)."""
    _run(
        ["docker-compose", "build", "--no-cache", "api"],
        cwd=OPS_DIR,
    )
    _run(["docker-compose", "up", "-d"], cwd=OPS_DIR)

def maintenance_rebuild_frontend() -> None:
    """Rebuild frontend Docker image after frontend code or VITE_* env change."""
    _run(
        ["docker-compose", "build", "--no-cache", "frontend"],
        cwd=OPS_DIR,
    )
    _run(
        ["docker-compose", "up", "-d", "--force-recreate", "frontend"],
        cwd=OPS_DIR,
    )

# ── ENV ───────────────────────────────────────────────────────────────────────

# Vars that come from docker-compose / infra — expected in .env but not in config.py
_INFRA_VARS = {
    "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
    "POSTGRES_HOST", "POSTGRES_PORT",
    "REDIS_HOST", "REDIS_PORT",
    "FRONTEND_BUILD_HTTP_PROXY", "FRONTEND_BUILD_HTTPS_PROXY",
    "FRONTEND_BUILD_ALL_PROXY",
    "FRONTEND_PORT",
    "LOVABLE_API_KEY",
    # docker-compose passes HOST/PORT via uvicorn cmd; API_HOST/API_PORT are legacy aliases
    "API_HOST", "API_PORT",
    "VITE_API_TIMEOUT_MS",  # in env/example but unused in frontend source (legacy)
}


def _parse_backend_vars() -> list[str]:
    """Extract env var names from the pydantic Settings class in config.py."""
    config_file = BACKEND / "app" / "core" / "config.py"
    if not config_file.exists():
        return []
    text = config_file.read_text()
    # Grab everything between class Settings(BaseSettings): and the nested Config class
    m = re.search(r"class Settings\(BaseSettings\):(.*?)(?=\n    class |\Z)", text, re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    # Field definitions: 4-space indent, lowercase identifier, colon type annotation
    fields = re.findall(r"^\s{4}([a-z][a-z0-9_]*)\s*:", body, re.MULTILINE)
    return [f.upper() for f in fields]


def _parse_frontend_vars() -> list[str]:
    """Grep VITE_* env var names referenced in frontend source."""
    src = FRONTEND / "src"
    if not src.exists():
        return []
    r = subprocess.run(
        ["grep", "-rEh", "--include=*.ts", "--include=*.tsx",
         r"VITE_[A-Z0-9_]+", str(src)],
        capture_output=True, text=True,
    )
    return sorted(set(re.findall(r"VITE_[A-Z0-9_]+", r.stdout)))


def _load_env(path: Path) -> dict[str, str]:
    """Parse a .env file into {KEY: value} — ignores comments and blank lines."""
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def env_check() -> None:
    """Diff the authoritative env-var list against digi-tax-ops/.env; refresh .env.example."""
    backend_vars  = _parse_backend_vars()
    frontend_vars = _parse_frontend_vars()
    env_path      = OPS_DIR / ".env"
    current_env   = _load_env(env_path)

    all_expected  = set(backend_vars) | set(frontend_vars)
    current_keys  = set(current_env.keys())

    missing = all_expected - current_keys - _INFRA_VARS
    extra   = current_keys - all_expected - _INFRA_VARS

    print("\n══ ENV CHECK ═══════════════════════════════════════════════════════════\n")
    print(f"Backend vars (config.py): {len(backend_vars)}")
    print(f"Frontend vars (VITE_*):   {len(frontend_vars)}")
    print(f"Current .env keys:        {len(current_keys)}\n")

    if missing:
        print("MISSING from digi-tax-ops/.env (defined in code but not in .env):")
        for v in sorted(missing):
            flag = "  ⚠ SECRET — set a real value before deploy" if v in ("SECRET_KEY",) else ""
            print(f"  - {v}{flag}")
    else:
        print("✓  No missing vars (all code-defined vars are present in .env)")

    if extra:
        print(f"\nEXTRA in .env (not in config.py or VITE_* — may be intentional):")
        for v in sorted(extra):
            print(f"  - {v}")
    else:
        print("✓  No extra vars")

    print("\n── Refreshing digi-tax-ops/.env.example ──────────────────────────────\n")
    _write_env_example(backend_vars, frontend_vars)

    print("\n── Refreshing digi-tax-frontend/.env.example ────────────────────────\n")
    _write_frontend_env_example(frontend_vars)

    print("\nDone. Review .env.example and update digi-tax-ops/.env for any missing vars.")
    print("Run  python3 scripts/digi-invoice-manager.py env:prod  for production guidance.\n")


def _write_env_example(backend_vars: list[str], frontend_vars: list[str]) -> None:
    content = """\
# digi-tax-ops/.env.example — canonical env template
# cp .env.example .env  and fill in real values.
# DATABASE_URL db name MUST match POSTGRES_DB (canonical name: digitax, no underscore).
# SECRET_KEY MUST be replaced with a strong random value in every environment.
# Rebuild the frontend image after changing VITE_* values.
# Rebuild the api image after adding argon2-cffi or other new dependencies.

# ── PostgreSQL (infra) ─────────────────────────────────────────────────────────
POSTGRES_USER=digitax
POSTGRES_PASSWORD=digitax
POSTGRES_DB=digitax
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# ── Redis (infra) ──────────────────────────────────────────────────────────────
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# ── Backend application ────────────────────────────────────────────────────────
APP_NAME=DigiTax Backend
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://digitax:CHANGE_ME@postgres:5432/digitax
API_HOST=0.0.0.0
API_PORT=8000

# ── Security (SECRETS — rotate before every deploy) ───────────────────────────
SECRET_KEY=CHANGE_ME_use_a_long_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ── CORS ───────────────────────────────────────────────────────────────────────
# Lock down to your domain in production. Never leave as * in prod.
BACKEND_CORS_ORIGINS=*

# ── Auth hardening (rate-limit + Altcha PoW CAPTCHA) ─────────────────────────
# Keep both ON in staging and production.
# Set to false ONLY in E2E test environments (AUTH_CAPTCHA_ENABLED=false).
AUTH_RATE_LIMIT_ENABLED=true
AUTH_RATE_LIMIT_MAX_ATTEMPTS=5
AUTH_RATE_LIMIT_WINDOW_SECONDS=60
AUTH_RATE_LIMIT_BLOCK_SECONDS=300
AUTH_CAPTCHA_ENABLED=true
AUTH_CAPTCHA_MAX_NUMBER=100000
AUTH_CAPTCHA_TTL_SECONDS=300

# ── Moadian (dev-only fallbacks; per-tenant keys live in DB for real submission) ─
MOADIAN_LEGACY_ENABLED=false
MOADIAN_LEGACY_BASE_URL=
MOADIAN_TIMEOUT_SECONDS=30
MOADIAN_REQUEST_TTL_SECONDS=20
MOADIAN_FISCAL_MEMORY_ID=
MOADIAN_PRIVATE_KEY_PATH=
MOADIAN_PUBLIC_KEY_PATH=
MOADIAN_PROXY_ENABLED=false
MOADIAN_PROXY_URL=
MOADIAN_PROXY_TYPE=http

# ── Frontend build (SSR image) ─────────────────────────────────────────────────
# VITE_API_BASE_URL is baked into the frontend bundle at build time.
# Use /api/v1 for same-origin reverse-proxy (nginx) deployments.
# For direct port testing, override via an external env file (never commit).
VITE_API_BASE_URL=/api/v1
VITE_API_TIMEOUT_MS=30000
FRONTEND_PORT=3000

# ── Frontend build proxy (optional — for restricted networks only) ─────────────
FRONTEND_BUILD_HTTP_PROXY=
FRONTEND_BUILD_HTTPS_PROXY=
FRONTEND_BUILD_ALL_PROXY=

# ── Runtime-only frontend secrets (never passed as build args) ────────────────
LOVABLE_API_KEY=
"""
    example_path = OPS_DIR / ".env.example"
    example_path.write_text(content)
    print(f"  ✓  Wrote {example_path.relative_to(WORKSPACE)}")


def _write_frontend_env_example(frontend_vars: list[str]) -> None:
    lines = [
        "# digi-tax-frontend/.env.example",
        "# Copy to .env.local for local development.",
        "# VITE_API_BASE_URL already includes /api/v1 — module paths are relative (e.g. /customers).",
        "",
    ]
    # Always emit the known vars in a stable order
    ordered = ["VITE_API_BASE_URL", "VITE_API_TIMEOUT_MS"]
    for v in ordered:
        if v == "VITE_API_BASE_URL":
            lines.append(f"{v}=http://localhost:8000/api/v1")
        elif v == "VITE_API_TIMEOUT_MS":
            lines.append(f"{v}=30000")
        else:
            lines.append(f"{v}=")
    # Any other VITE_ vars found in source that aren't already listed
    for v in frontend_vars:
        if v not in ordered:
            lines.append(f"{v}=")
    example_path = FRONTEND / ".env.example"
    example_path.write_text("\n".join(lines) + "\n")
    print(f"  ✓  Wrote {example_path.relative_to(WORKSPACE)}")


def env_prod() -> None:
    """Print every value that MUST change for a production deployment."""
    print("""
══ PRODUCTION CHECKLIST ════════════════════════════════════════════════════════

These values MUST be changed before any production or staging deploy.
Secrets are marked [SECRET] — generate fresh values; never reuse dev values.

  SECRET_KEY=<64-char random hex>       [SECRET] — rotate; JWT signing key
  POSTGRES_PASSWORD=<strong password>   [SECRET] — DB credential
  DATABASE_URL=postgresql+asyncpg://digitax:<POSTGRES_PASSWORD>@postgres:5432/digitax

  DEBUG=false                           dev OTP exposed in API response when true
  ENVIRONMENT=production
  LOG_LEVEL=WARNING

  BACKEND_CORS_ORIGINS=https://yourdomain.com  # lock down — never * in prod
  SWAGGER_AUTO_AUTH_ENABLED=false              # disable Swagger auto-auth in prod

  AUTH_CAPTCHA_ENABLED=true             must be ON — bot protection
  AUTH_RATE_LIMIT_ENABLED=true          must be ON — brute-force protection

  VITE_API_BASE_URL=/api/v1             relative (same-origin via nginx) for prod builds

  MOADIAN_LEGACY_ENABLED=false          until R1B real submission is ready

────────────────────────────────────────────────────────────────────────────────
Generate SECRET_KEY:
  python3 -c "import secrets; print(secrets.token_hex(32))"

After updating .env:
  docker-compose build --no-cache api      # if backend deps changed
  docker-compose build --no-cache frontend # VITE_* are build-time
  docker-compose up -d
  docker-compose exec api alembic upgrade head
  bash scripts/smoke_test.sh
════════════════════════════════════════════════════════════════════════════════
""")


# ── COMMAND REGISTRY ──────────────────────────────────────────────────────────

COMMANDS: dict[str, tuple[str, object]] = {
    # setup
    "setup:preflight":  ("Check Docker, env, DB name, and service readiness", setup_preflight),
    "setup:bootstrap":  ("First-time DB init + all migrations (idempotent)", setup_bootstrap),
    "setup:up":         ("docker-compose up -d — bring up full local stack", setup_up),
    # seed
    "seed:dev":         ("Load fixed test accounts (09120000000/099/001) into running stack", seed_dev),
    "seed:qa":          ("Load QA invoice scenario data into running stack", seed_qa),
    "seed:demo":        ("Seed realistic demo business via API (safe, re-runnable)", seed_demo),
    # db
    "db:upgrade":       ("Run all pending Alembic migrations inside api container", db_upgrade),
    "db:status":        ("Show Alembic current revision + list DB tables via psql", db_status),
    "db:tables":        ("List all tables in the digitax DB", db_tables),
    # frontend
    "front:dev":        ("Start Vite dev server (localhost:8080)", front_dev),
    "front:build":      ("Production build — must pass before commit or deploy", front_build),
    "front:typecheck":  ("TypeScript check — must be zero errors before commit", front_typecheck),
    # test
    "test:backend":     ("Run pytest inside Docker (513+ pass / 7 pre-existing = green)", test_backend),
    "test:e2e":         ("Run Playwright E2E suite (phase end only; disable captcha/rate-limit first)", test_e2e),
    # maintenance
    "maintenance:smoke":              ("Smoke test running stack: health, CORS, OTP, bearer", maintenance_smoke),
    "maintenance:rebuild-api":        ("Rebuild api image (--no-cache) after backend code change", maintenance_rebuild_api),
    "maintenance:rebuild-frontend":   ("Rebuild frontend image after source or VITE_* env change", maintenance_rebuild_frontend),
    # env
    "env:check":  ("Diff code-defined vars against .env; refresh .env.example files", env_check),
    "env:prod":   ("Print production deployment checklist with secret/config guidance", env_prod),
}

GROUPS: list[tuple[str, list[str]]] = [
    ("SETUP",       ["setup:preflight", "setup:bootstrap", "setup:up"]),
    ("SEED",        ["seed:dev", "seed:qa", "seed:demo"]),
    ("DATABASE",    ["db:upgrade", "db:status", "db:tables"]),
    ("FRONTEND",    ["front:dev", "front:build", "front:typecheck"]),
    ("TEST",        ["test:backend", "test:e2e"]),
    ("MAINTENANCE", ["maintenance:smoke", "maintenance:rebuild-api", "maintenance:rebuild-frontend"]),
    ("ENV",         ["env:check", "env:prod"]),
]


def print_help() -> None:
    print("\nDigi Invoice — workspace script manager")
    print("Usage:  python3 digi-tax-ops/scripts/digi-invoice-manager.py <command>\n")
    for group, cmds in GROUPS:
        print(f"  {group}")
        for name in cmds:
            desc, _ = COMMANDS[name]
            print(f"    {name:<36}  {desc}")
        print()
    print("Run any command with --help for full details.\n")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(0)

    cmd_name = sys.argv[1]

    if cmd_name not in COMMANDS:
        print(f"✗  Unknown command: {cmd_name!r}", file=sys.stderr)
        print("   Run without arguments to list all commands.", file=sys.stderr)
        sys.exit(1)

    _, fn = COMMANDS[cmd_name]
    fn()  # type: ignore[call-arg]
