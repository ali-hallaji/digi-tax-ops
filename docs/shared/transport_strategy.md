# Tax Transport Strategy v1.3

## Critical decision
Both transport modes are first-class. Neither is globally superior. The selected mode is a customer/fiscal-memory configuration decision.

## Default mode
Use `LEGACY_SELF_TSP` as the default for v1 onboarding because:
- it was smoke-tested successfully;
- it is simpler for early customers;
- it may avoid extra certificate cost for customers;
- it reduces onboarding friction.

Use `REQUESTS_MANAGER_V2` as an optional advanced mode because:
- it uses the newer certificate-based API style;
- it may support richer REST-style inquiry/status capabilities;
- it may be required by some customer/legal setups;
- it can be enabled when customer has the required certificate.

The UI text must be neutral and business-friendly. Do not call v2 "better" and do not call legacy "old/bad" in customer-facing labels.

## Customer-facing labels

```txt
LEGACY_SELF_TSP:
  عنوان: اتصال ساده Self-TSP
  توضیح: مناسب شروع سریع و کم‌هزینه‌تر برای بسیاری از مودیان. این روش توسط سیستم پشتیبانی و مانیتور می‌شود.

REQUESTS_MANAGER_V2:
  عنوان: اتصال گواهی‌محور RequestsManager v2
  توضیح: مناسب مودیانی که گواهی امضا دارند یا نیاز به روش گواهی‌محور و امکانات پیشرفته‌تر دارند.
```

## Internal enum

```python
class TransportMode(str, Enum):
    LEGACY_SELF_TSP = "LEGACY_SELF_TSP"
    REQUESTS_MANAGER_V2 = "REQUESTS_MANAGER_V2"
```

## Database fields

```txt
fiscal_memories.transport_mode text default 'LEGACY_SELF_TSP'
fiscal_memory_certificates optional; required only when selected mode requires certificate
```

## Capability object

```python
class TransportCapabilities(BaseModel):
    mode: TransportMode
    supports_batch: bool
    max_batch_size: int
    requires_private_key: bool
    requires_certificate: bool
    requires_token: bool
    requires_nonce_jwt: bool
    supports_reference_inquiry: bool
    supports_uid_inquiry: bool
    supports_taxid_status_inquiry: bool
    supports_invoice_payment: bool
```

## Adapter interface

```python
class TaxTransportProvider(Protocol):
    mode: TransportMode
    capabilities: TransportCapabilities

    async def test_connection(self, fiscal_memory: FiscalMemorySecrets) -> TestConnectionResult: ...
    async def submit_invoices(self, request: SubmitInvoicesRequest) -> SubmitInvoicesResult: ...
    async def inquiry_by_reference(self, request: InquiryByReferenceRequest) -> InquiryResult: ...
    async def inquiry_by_uid(self, request: InquiryByUidRequest) -> InquiryResult: ...
    async def inquiry_invoice_status(self, request: InquiryInvoiceStatusRequest) -> InvoiceStatusResult: ...
```

## Submission service rule
The submission service chooses the provider through a factory:

```python
provider = transport_factory.for_mode(fiscal_memory.transport_mode)
```

Do not import concrete transport classes inside invoice code.

## UI restriction rule
Frontend must read backend capabilities from:

```txt
GET /api/v1/fiscal-memories/{id}/transport-capabilities
```

Then disable unsupported actions.

## Tests
Test both transports separately:
- fake successful submit;
- fake rejected submit;
- inquiry pending;
- inquiry accepted;
- inquiry rejected;
- missing private key;
- missing certificate for v2;
- token expired for legacy;
- nonce expired for v2;
- redaction in transport logs.
