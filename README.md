# digi-tax-ops - Phase 0

Local orchestration and operational documentation for DigiTax.

## Overview

This repository contains the Phase 0 infrastructure setup for DigiTax, including:

- Docker Compose configuration for local development
- Environment variable templates
- Progress tracking for implementation phases

## Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.0+
- Git
- 4GB+ RAM available for Docker

## Quick Start

### 1. Clone sibling repositories

```bash
# Go to parent directory of digi-tax-ops
cd ..
git clone <digi-tax-backend-repo>
git clone <digi-tax-frontend-repo>
```

### 2. Set up environment

```bash
cd digi-tax-ops
cp .env.example .env
# Edit .env with your actual values if needed
# For restricted networks, add proxy values:
# FRONTEND_BUILD_HTTP_PROXY=http://127.0.0.1:2080
# FRONTEND_BUILD_HTTPS_PROXY=http://127.0.0.1:2080
# FRONTEND_BUILD_ALL_PROXY=http://127.0.0.1:2080
```

### 3. Run services

```bash
# Start all services
docker compose up -d

# Or start services individually
# docker compose up -d postgres redis
# docker compose up -d api
# docker compose up -d frontend

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

## Phase 0 Services

| Service | Description | Port |
|---------|-------------|------|
| postgres | PostgreSQL 16 database | 5432 (local dev only) |
| redis | Redis 7 cache/store | 6379 (local dev only) |
| api | Backend API server | 8000 |
| frontend | Quasar/Vue frontend | 9000 |

## Project Structure

```
digi-tax-ops/
├── docker-compose.yml      # Main compose configuration
├── .env.example           # Environment template
├── README.md              # This file
├── docs/
│   ├── progress.md        # Implementation progress
│   └── ops_deployment_guide.md
└── AGENTS.md              # Project rules
```

## Development

### Health checks

All services have built-in health checks:

```bash
docker compose ps
```

### Rebuild services

```bash
# Rebuild backend services
docker compose build api

# Rebuild frontend (requires proxy for restricted networks)
docker compose build frontend
```

## Environment Variables

Required env vars (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `APP_NAME` - Application name
- `DEBUG` - Enable debug mode
- `VITE_API_BASE_URL` - Frontend API base URL
- `VITE_API_TIMEOUT_MS` - Frontend API timeout in milliseconds

## Next Steps

- **Phase 0** ✅ - Local Docker Compose setup (current)
- **Phase 1** - Worker services integration
- **Phase 2** - Kubernetes orchestration
- **Phase 3** - Production-ready configs

## License

Internal use only.