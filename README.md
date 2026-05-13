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

### 1. Clone sibling repository

```bash
# Go to parent directory of digi-tax-ops
cd ..
git clone <digi-tax-backend-repo>
```

### 2. Set up environment

```bash
cd digi-tax-ops
cp .env.example .env
# Edit .env with your actual values if needed
```

### 3. Run services

```bash
# Start postgres and redis
docker compose up -d postgres redis

# Start api service
docker compose up -d api

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

### Rebuild api service

```bash
docker compose build api
```

## Environment Variables

Required env vars (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `APP_NAME` - Application name
- `DEBUG` - Enable debug mode

## Next Steps

- **Phase 0** ✅ - Local Docker Compose setup (current)
- **Phase 1** - CI/CD integration
- **Phase 2** - Kubernetes orchestration
- **Phase 3** - Production-ready configs

## License

Internal use only.
```

---