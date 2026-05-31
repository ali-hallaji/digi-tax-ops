# HISTORICAL

Archived on 2026-05-31. This file contains old shared architecture guidance and is not active. Use `docs/architecture_decisions.md`, `docs/current_phase.md`, and `docs/progress.md` for current ops guidance.

# DigiTax Platform Architecture v1.3 — Agent Source of Truth

This file is the shared architecture source for all Zed/Ollama agents. Keep this file in every repo, or keep it in `digi-tax-ops/docs` and reference it from backend/frontend prompts.

## Product vision
DigiTax is a low-cost cloud tax and accounting platform for small and medium Iranian businesses. Phase 1 is the professional Tax Core for issuing, validating, submitting, and inquiring electronic invoices in the Tax Organization system. Phase 2 adds simple cloud accounting, payroll, salary tax, insurance, VAT period tracking, and tax reminders. Phase 3 adds an AI assistant that answers business/tax/accounting questions by calling validated reporting APIs, not by querying raw tables directly. Phase 4 adds analytics, market intelligence, inventory/goods circulation analysis, and business insights.

## Repository decision
Use three repositories:

```txt
workspace/
  digi-tax-backend/
  digi-tax-frontend/
  digi-tax-ops/
```

Do not use one monorepo for backend and frontend. The backend and frontend must remain separate Zed workspaces to reduce context noise, token usage, accidental cross-file edits, and agent confusion. The `digi-tax-ops` repo owns Docker Compose, Nginx, shared docs, environment templates, API contract snapshots, and local orchestration.

## Core architecture
Use:

```txt
Backend: Python 3.12 + FastAPI async + SQLAlchemy 2 async
Frontend: Vue 3 + Quasar + TypeScript
Database: PostgreSQL 16+
Cache/lock/rate-limit: Redis
Initial job queue: PostgreSQL outbox/jobs with FOR UPDATE SKIP LOCKED
Initial deployment: Docker Compose + Nginx
Architecture style: modular monolith + stateless API + scalable workers
```

Do not use MongoDB for the transactional core. Use PostgreSQL relations and constraints for tax/legal/accounting data. Use JSONB only for snapshots, official payloads, transport responses, validation context, and audit metadata.

Do not split into microservices in v1. Use a modular monolith with clear module boundaries. Scale horizontally by running more API and worker replicas.

## Domain separation
Keep these concepts separate in code, database, services, and UI:

```txt
BusinessInvoice
  The user-editable business invoice/draft in the application.

StandardTaxInvoice
  The official normalized invoice JSON generated according to IITP_V7_8.

Submission
  The process of signing/encrypting/sending/inquiring/retrying and receiving status.
```

Invoice modules prepare and validate invoices. Submission modules send and inquire. Transport modules only know how to talk to the Tax Organization.

## Two transport modes — no superiority, both first-class
The platform must support both Tax Organization transport methods as first-class options. Do not hard-code one as universally better. The correct method depends on customer cost, certificate availability, legal setup, operational needs, and Tax Organization compatibility.

```txt
LEGACY_SELF_TSP
  Default for v1 onboarding because it is cheaper/easier for many taxpayers and was already smoke-tested successfully.
  Uses self-tsp packet-based flow.
  Does not require the certificate workflow used by v2 in the same way.
  Must be production-ready, tested, monitored, and supported.

REQUESTS_MANAGER_V2
  Optional advanced/professional transport.
  Uses nonce + JWT/JWS + certificate + JWS invoice + JWE encryption.
  May require obtaining/maintaining a certificate from an intermediate CA, which can add customer cost.
  Must be production-ready, tested, monitored, and supported.
```

Default transport mode in new fiscal memory records:

```txt
transport_mode = LEGACY_SELF_TSP
```

The UI must explain both options neutrally:

```txt
Legacy Self-TSP: simpler and usually cheaper onboarding.
RequestsManager v2: advanced certificate-based method for customers who need or already have certificate setup.
```

The system must use a capability matrix, not scattered if/else logic.

## Transport capabilities
Each fiscal memory stores a selected `transport_mode`. The backend derives capabilities from the selected transport.

```txt
capabilities:
  supports_batch
  max_batch_size
  supports_certificate_auth
  requires_certificate
  requires_private_key
  requires_token
  requires_nonce_jwt
  supports_reference_inquiry
  supports_uid_inquiry
  supports_taxid_status_inquiry
  supports_invoice_payment
  supports_server_information
  supports_taxpayer_lookup
```

Example:

```txt
LEGACY_SELF_TSP:
  requires_private_key: true
  requires_certificate: false
  requires_token: true
  requires_nonce_jwt: false
  supports_reference_inquiry: true
  supports_uid_inquiry: limited_or_false
  supports_taxid_status_inquiry: false_or_limited
  max_batch_size: configurable

REQUESTS_MANAGER_V2:
  requires_private_key: true
  requires_certificate: true
  requires_token: false
  requires_nonce_jwt: true
  supports_reference_inquiry: true
  supports_uid_inquiry: true
  supports_taxid_status_inquiry: true
  max_batch_size: up_to_1000_configurable
```

Do not expose unavailable UI actions. For example, if the selected transport does not support a capability, the UI must disable/hide the action and show a human explanation.

## Backend module boundaries
Use this layout inside `digi-tax-backend`:

```txt
app/
  main.py
  core/
    config/
    db/
    security/
    logging/
    exceptions/
    time/
  common/
    money.py
    pagination.py
    ids.py
    events.py
    redaction.py
  modules/
    identity/
    tenants/
    taxpayers/
    fiscal_memories/
    catalog/
    customers/
    compliance/
    invoices/
    imports/
    submissions/
    central_admin/
    billing/
    support/
    notifications/
    reporting/
    accounting/
    payroll/
    ai_assistant/
  integrations/
    tax_org/
      ports.py
      tax_org_service.py
      capabilities.py
      models.py
      exceptions.py
      transports/
        legacy_self_tsp/
        requestsmanager_v2/
        fake_tax_org/
  workers/
    submission_worker.py
    inquiry_worker.py
    import_worker.py
    default_worker.py
    scheduler.py
  tests/
alembic/
pyproject.toml
Dockerfile
```

Rules:

```txt
modules/compliance must be pure logic and must not import FastAPI, SQLAlchemy, Redis, httpx, or tax_org.
modules/invoices must not import integrations/tax_org.
modules/submissions may depend on the TaxOrgClient port, not on concrete transport internals.
integrations/tax_org must not contain business invoice rules.
All financial calculations must use Decimal in Python and numeric in PostgreSQL. Never use float.
Private keys and certificates must never be logged or stored unencrypted.
API requests must never wait for real tax submission. Always enqueue jobs and return 202.
```

## Frontend boundaries
Use one Quasar app in `digi-tax-frontend`:

```txt
src/
  app/
    router/
    stores/
    boot/
    config/
  layouts/
    AuthLayout.vue
    TaxpayerLayout.vue
    AdminLayout.vue
    PublicLayout.vue
  modules/
    auth/
    dashboard/
    invoices/
    imports/
    submissions/
    products/
    customers/
    taxpayers/
    fiscal-memories/
    reports/
    central-admin/
    support/
    billing/
    accounting/
    payroll/
    tax-calendar/
    ai-assistant/
  shared/
    components/
    composables/
    api/
    types/
    utils/
```

UI priority:
1. Taxpayer login and app shell.
2. Fiscal memory setup with transport selection.
3. Products/customers basics.
4. Invoice list and create wizard.
5. Bulk Excel import.
6. Submission/inquiry status.
7. Central admin panel.
8. Accounting/payroll/tax calendar foundation.

## Phase 2 future modules
Do not implement heavy accounting in Phase 1, but reserve clean boundaries.

```txt
accounting:
  chart of accounts
  fiscal periods
  journal entries
  ledger
  VAT reports
  profit/loss
  tax reports

payroll:
  employees
  contracts
  salary components
  payslips
  salary tax
  insurance
  payroll tax files

tax_calendar:
  VAT deadlines
  salary tax deadlines
  performance tax reminders
  insurance reminders
  custom reminders

ai_assistant:
  intent parsing
  calls validated reporting APIs
  returns charts/tables/files
  never directly queries raw DB
```

## Data input channels
The system must support multiple input channels, but implement them in priority order.

Priority:
1. Web UI manual invoice entry.
2. Excel/CSV bulk invoice import.
3. REST API invoice intake with idempotency keys.
4. Accounting-generated invoices.
5. POS / cash register integration.
6. Scanner/barcode/QR flows for goods or POS scenarios.

All channels must eventually produce the same internal BusinessInvoice and pass through the same compliance engine and submission pipeline.

## Deployment direction
Phase 1 uses Docker Compose. Keep it simple. Design stateless API and workers so later migration to Kubernetes is possible without rewriting the app.
