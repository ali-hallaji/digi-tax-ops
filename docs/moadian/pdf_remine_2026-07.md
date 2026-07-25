# Moadian PDF re-mine — 2026-07

_Batch 2 Part 5. Findings from re-reading the official tax/SDK PDFs under
`digi-tax-ops/docs/moadian/` with fresh eyes: services/fields we haven't wired, rules we
implement more strictly/loosely than written, and merchant data we ignore._

> **Every row below is now in a FINAL state**, each resolved by the EMPIRICAL-TEST LAW:
> where the sandbox could answer, it answered, and the org's real response — not the
> doc — decided the product. Probe script: `digi-tax-ops/scripts/remine_wire_probe.py`
> (read-only; it submits nothing, so the ZERO-TOTAL rule is not in play).

> Honesty rule (Batch 2): **اینتاکد (activity classification code) and ضریب فعالیت
> (activity coefficient) are ABSENT from every documented Moadian org service.** Confirmed
> three times now — the Batch 1 Part 4 exhaustive grep of all five PDFs, the initial pass
> here, and now the wire itself (`GET_FISCAL_INFORMATION` returns four keys, none of them
> a classification code). Activity coefficients stay INTERNAL admin data
> (`tax_activity_coefficients`); the tenant's `tax_activity_code` is merchant-selected,
> never org-derived. This is final.

## Findings table — all FINAL

| # | Finding | Doc / section | Empirical verdict (evidence) | Final state |
|---|---|---|---|---|
| 1 | **Corrective (ins=2) may ADD a line** | RC_IITP §5-2 (read as forbidding it) | Sandbox **ACCEPTS** an added line (taxid …916817). | ✅ **WIRED** — add-line unlocked (Batch 2 Part 2); the empirical verdict overrode the doc reading. |
| 2 | **Corrective may NOT change an existing line's sstid** | (not explicit) | Sandbox **REJECTS** an sstid change (taxid …916829, org errors `0303301` + `0304401`) — re-seen verbatim in this batch's fresh inquiry. | ✅ **CLOSED — kept locked**, with the org's own behaviour as the stated reason. |
| 3 | **`حد مجاز فروش` (sales ceiling)** on GET_FISCAL_INFORMATION | RC_TICS.IS §9-1 (prose) + SDK `FiscalFullInformationModel` | Live sandbox `GET_FISCAL_INFORMATION` returns **exactly four keys** — `nameTrade`, `fiscalStatus`, `economicCode`, `nationalId`. **No sales-limit field on the wire.** | ✅ **CLOSED — nothing to wire.** The field lives in prose + an SDK model the REST service does not populate. Surfacing a ceiling we never receive would be an invented number. Re-open only if a future org response actually carries one. |
| 4 | **`taxpayerStatus` states** (NOT_ALLOCATED / TEMPORARY_UNAUTHORIZE = عبور از حد مجاز ماده ۶ / …) | RC_TICS.IS §9-2 (GET Taxpayer) | Our `TAXPAYER_STATUS_FA` map already covers all six documented values — **unmapped statuses = NONE**. The probe surfaced a REAL gap the doc never mentions: for an economic code the org has **no record of**, it answers **HTTP 200 with an EMPTY body** (`{}`), not a status. We rendered that as the ambiguous «نامشخص». | ✅ **WIRED** — the response gains `found`; an empty org answer now reads «در سامانهٔ مودیان یافت نشد» in the buyer-inquiry card, the customers form, and both toasts. Tests pinned to the verbatim sandbox bodies. |
| 5 | **اینتاکد / ضریب فعالیت** | (searched: all 5 PDFs) | Not present in any org response — now confirmed on the wire too. | ✅ **CLOSED** — nothing to wire (see the honesty rule above). |
| 6 | **article6Status on invoice-status inquiry** | SDK `getInvoiceStatusInquiry` | **61 recorded inquiry responses** (every `moadian_submissions.inquiry_payload_json` we have ever stored) plus a **fresh live inquiry**: the only keys the org ever returns are `uid`, `referenceNumber`, `status`, `fiscalId`, `packetType`, and `data.{success, error[], warning[]}`. **No `article6Status`, ever.** | ✅ **CLOSED — nothing to wire.** The field is in the SDK model only; the REST inquiry does not carry it. A «عبور از حد مجاز ماده ۶» timeline note would have to be invented, so it is not shipped. |

## Wire evidence (verbatim, نیک‌تجارت sandbox, 2026-07-25)

```
GET_FISCAL_INFORMATION
  {"nameTrade":"A2HP31","fiscalStatus":"ACTIVE",
   "economicCode":"10320296185","nationalId":"10320296185"}
  → keys: economicCode, fiscalStatus, nameTrade, nationalId
  → limit/ceiling-shaped keys: NONE                                  (finding #3)

GET_ECONOMIC_CODE_INFORMATION
  14008430838 → {"nameTrade":"تراز پیشه دیبا","taxpayerStatus":"ACTIVE",
                 "nationalId":"14008430838"}
  10100000000 → {}          ← well-formed, unknown to the org
  11111111111 → {}          ← well-formed, unknown to the org
  → statuses observed: [ACTIVE]; unmapped statuses: NONE             (finding #4)

INQUIRY_BY_REFERENCE_NUMBER (fresh) + 61 recorded responses
  distinct keys ever seen: uid, referenceNumber, status, fiscalId, packetType,
    data.success, data.error[].{code,message}, data.warning[].{code,message}
  → article-shaped keys: NONE                                        (finding #6)
```

## What this batch wired

Only finding #4, and only the part the org actually proved: the empty-body
"unknown economic code" case. Findings #3 and #6 are CLOSED **unwired on purpose** —
per the EMPIRICAL-TEST LAW a doc citation is not a verdict when the wire can speak,
and here the wire said the field is not there. Shipping a «حد مجاز فروش» or a «ماده ۶»
badge from data the org never sends would be exactly the invented number the
no-fake-status rule forbids.

## Follow-up (queued in LAUNCH_ROADMAP)

A full, fresh, end-to-end re-read of every PDF (not just the profile/corrective/inquiry
slices) — scoped for a dedicated pass. Any new candidate finding goes through the same
gate: sandbox first, doc second.

_Last updated: 2026-07-25 (Batch 2 Part 5 — every finding resolved to a final state)._
