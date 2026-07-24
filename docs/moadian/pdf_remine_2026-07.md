# Moadian PDF re-mine — 2026-07

_Batch 2 Part 5. Findings table from re-reading the official tax/SDK PDFs under
`digi-tax-ops/docs/moadian/` with fresh eyes: services/fields we haven't wired, rules we
implement more strictly/loosely than written, and merchant data we ignore._

> Honesty rule (Batch 2): **اینتاکد (activity classification code) and ضریب فعالیت
> (activity coefficient) are ABSENT from every documented Moadian org service.** Confirmed
> twice now — the Batch 1 Part 4 exhaustive grep of all five PDFs, and re-confirmed here.
> The only threshold-type org fields are `حد مجاز فروش` (sales ceiling) and `article6Status`
> / `حد مجاز ماده ۶`. Activity coefficients stay INTERNAL admin data (`tax_activity_coefficients`);
> the tenant's `tax_activity_code` is merchant-selected, never org-derived. This is final —
> do not re-litigate it against a doc citation; only a wire response could change it.

## Findings table

| # | Finding | Doc / section | Current state | Recommended action |
|---|---|---|---|---|
| 1 | **Corrective (ins=2) may ADD a line** | RC_IITP §5-2 (read as forbidding it) | We LOCKED add — but the **sandbox ACCEPTS** an added line (Batch 2 Part 2). | ✅ DONE — add-line unlocked; the empirical verdict overrides the doc reading. |
| 2 | **Corrective may NOT change an existing line's sstid** | (not explicit) | Locked. **Sandbox REJECTS** an sstid change (Batch 2 Part 2). | ✅ DONE — kept locked, org behaviour as the reason. |
| 3 | **`حد مجاز فروش` (sales ceiling)** on GET_FISCAL_INFORMATION | RC_TICS.IS §9-1 (prose) + SDK `FiscalFullInformationModel` | NOT fetched/shown. Present in prose + SDK only; ABSENT from the concrete REST JSON example → unverified on the wire. | QUEUE (needs accountant): empirically confirm whether the sandbox fiscal-info response actually carries a sales-limit field; if yes, surface it read-only in «پروفایل مؤدی». Zero-risk only after a wire confirmation. |
| 4 | **`taxpayerStatus` states** (NOT_ALLOCATED / TEMPORARY_UNAUTHORIZE = عبور از حد مجاز ماده ۶ / …) | RC_TICS.IS §9-2 (GET Taxpayer) | We parse `taxpayerStatus` for buyer inquiry but only map ACTIVE/DEACTIVATED loosely. | QUEUE: friendlier Persian for the full status enum in buyer inquiry + the profile card (small, low-risk). |
| 5 | **اینتاکد / ضریب فعالیت** | (searched: all 5 PDFs) | Not present in any org response. | ✅ CLOSED — stated definitively above; nothing to wire. |
| 6 | **article6Status on invoice-status inquiry** | SDK `getInvoiceStatusInquiry` | Not surfaced. Non-profile (per-invoice). | QUEUE: consider surfacing عبور از حد مجاز ماده ۶ as a calm invoice-timeline note if the wire carries it. |

## Zero-risk quick wins wired this batch
None required code beyond Parts 2–3 (the corrective empirical alignment already landed). The
remaining findings (#3, #4, #6) all need a **sandbox wire confirmation** first per the
EMPIRICAL-TEST LAW before wiring — queued above, not guessed.

## Follow-up (queued in LAUNCH_ROADMAP)
A full, fresh, end-to-end re-read of every PDF (not just the profile/corrective slices) —
scoped for a dedicated pass; this doc captures the high-value findings surfaced so far.

_Last updated: 2026-07-25 (Batch 2 Part 5 — initial pass)._
