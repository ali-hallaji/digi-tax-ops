# Moadian org services — full map (MOADIAN D PART 3)

_2026-07-22. Source of truth: the SELF-TSP SDK guide (راهنمای اتصال به زیرسامانه
جمع‌آوری بدون گواهی، فروردین ۱۴۰۴) + RC_IITP_IS v7.8; packet types as encoded in
`app/modules/moadian/application/transport_selftsp.py` (PT_* constants). This is the
COMPLETE service surface the org offers on this transport — nothing else exists to wire._

## Services table

| # | Packet / service | Returns (org fields) | Wired? | Surfaced where |
|---|------------------|----------------------|--------|----------------|
| 1 | `GET_SERVER_INFORMATION` | `serverTime`, `publicKeys[{key,id}]` | ✅ | Connection test («آزمایش اتصال») + every submit (encryption key) |
| 2 | `GET_TOKEN` | `token` (auth proof against the registered key) | ✅ | Every authenticated call (transport-internal) |
| 3 | `GET_FISCAL_INFORMATION` | `fiscalStatus` (ACTIVE/INACTIVE/…); `nameTrade` echoes the memory id on self-tsp (verified live — never shown as a trade name) | ✅ **NEW (D)** | Cockpit «وضعیت حافظهٔ مالیاتی» card (read-only refresh, `GET /moadian/profile/fiscal-status`) + connection-test enrichment |
| 4 | `GET_ECONOMIC_CODE_INFORMATION` | `nameTrade`, `taxpayerStatus`, `nationalId` — **nothing else** (no address/postal/phone) | ✅ | «استعلام از سامانه مودیان» on customer form + invoice buyer card; fill-EMPTY rule writes only نام + کد/شناسه ملی |
| 5 | `INQUIRY_BY_UID` | per-packet `{status, data{error[],warning[]}, referenceNumber}` | ✅ | Per-row «استعلام» + **NEW (D)** bulk «به‌روزرسانی همهٔ در انتظارها» (`POST /admin/moadian/submissions/refresh-pending`, newest 50 pending) |
| 6 | `INQUIRY_BY_REFERENCE_NUMBER` | same shape as #5 | ✅ | `refresh_submission` (preferred when a referenceNumber exists) |
| 7 | `INQUIRY_BY_TIME` | submissions of one day | ❌ (transport method not built) | Nothing — subsumed by #8; build only if a "resync a day" admin tool is ever needed |
| 8 | `INQUIRY_BY_TIME_RANGE` | submissions in a range | ⚠️ transport method exists (`inquiry_by_time_range`), no caller | Candidate: admin-side "org-side reconciliation" report (backlog; per-uid refresh covers merchant needs today) |
| 9 | `INVOICE.V01` | `{uid, referenceNumber}` per packet | ✅ | Submit / bulk submit / lifecycle (اصلاحی/ابطالی) / برگشت از فروش — all four subjects org-proven on sandbox (PART 0) |

**Bottom line:** every org service that helps a merchant is wired and surfaced; the two
unwired items (#7, #8-caller) are org-side *reconciliation* reads with no merchant-visible
value today — logged in backlog, not silently dropped.

## Honest boundary — «نیازمند سرویس بیرونی» (NOT Moadian services)

Services people commonly expect here that Moadian does NOT provide on this transport —
we wire NOTHING for these; anything claiming otherwise would be inventing data:

| Expected capability | Reality | What it would need |
|--------------------|---------|--------------------|
| موبایل ↔ کد ملی matching (شاهکار) | Not a Moadian service | The شاهکار service (وزارت ارتباطات) via a commercial aggregator; contract + per-call fee |
| Company address / postal code / phone from an استعلام | `GET Taxpayer` returns ONLY `nameTrade`, `taxpayerStatus`, `nationalId` | Official company-registry access (`ilenc.ssaa.ir` / روزنامه رسمی aggregator) |
| کد پستی validation | Not provided | Post company (شرکت ملی پست) API via aggregator |
| شبا/bank-account owner matching | Not provided | Bank/PSP services (e.g. finnotech-type aggregator) |
| Real-time VAT-rate lookup per stuffid beyond the catalog | The stuffid catalog file IS the org's delivery mechanism (imported, 3.98M codes) | Nothing — already at parity |

## Follow-ups logged
- `INQUIRY_BY_TIME_RANGE` reconciliation report (admin) — backlog, low priority.
- True uid-list batching inside the bulk refresh (transport supports it; per-row
  `refresh_submission` owns persistence today; fine at ≤50 rows).
