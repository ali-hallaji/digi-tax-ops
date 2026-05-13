# API Contract Rules v1.3

## Ownership
Backend owns OpenAPI and API behavior. Frontend consumes generated or documented contracts. Ops stores snapshots if needed.

## Rules
- All API routes are under `/api/v1` except `/health`.
- Submit endpoint returns 202 and `submission_id`.
- Frontend never assumes transport capabilities; it asks backend.
- Financial values are strings or integers as agreed by backend; never JS floating point calculations for authoritative amounts.
- API errors must be structured and user-message-ready.

## Key endpoints

```txt
GET /health
GET /api/v1/health

GET /api/v1/fiscal-memories/{id}/transport-capabilities
PATCH /api/v1/fiscal-memories/{id}/transport-mode
POST /api/v1/fiscal-memories/{id}/upload-certificate
POST /api/v1/fiscal-memories/{id}/test-connection

POST /api/v1/invoices/{id}/validate
POST /api/v1/invoices/{id}/submit
GET /api/v1/invoices/{id}/standard-payload

POST /api/v1/imports/invoices
GET /api/v1/imports/invoices/{id}
POST /api/v1/imports/invoices/{id}/submit-valid-rows

GET /api/v1/submissions/{id}
POST /api/v1/submissions/{id}/retry
POST /api/v1/submissions/{id}/inquiry
```
