# Invoice Flow Integrity Matrix — the permanent QA contract

_Created: 2026-07-24 (INVOICE FLOW INTEGRITY batch). This document is the canonical
scenario matrix for the ENTIRE issuance journey. **HARD LAW: a scenario counts as
PROVEN only when walked through the REAL UI journey (create → … → org response).
Engine-level calls (curl, pytest, container scripts) are supporting evidence, never
the proof.** Any change to issuance behavior must update this matrix in the same
commit; any red row blocks the batch that produced it._

## Canonical rules the matrix encodes (founder-locked)

1. **Internal invoices (پیش‌فاکتور `proforma` / فاکتور داخلی `internal_private`) never
   require a customer** and carry **zero Moadian friction** — no نوع, no validate/submit
   UI, no buyer-identity demands, anywhere.
2. **Tax-reportable + نوع اول (type 1)** is the ONLY scenario where a customer with
   full identity is required: name + (کد ملی for حقیقی | شناسه اقتصادی for حقوقی).
   Postal/address are recommendations (warnings), never blockers.
3. **Tax-reportable + نوع دوم (type 2)**: buyer is OPTIONAL and never blocking.
   «بدون مشخصات خریدار» is ONE tap with ZERO required fields and proceeds straight to
   finalize. An attached customer with missing/partial ids never blocks. A legacy
   12-digit economic code is ACCEPTED with an amber (never red) nudge; the packet
   builder substitutes the 11-digit شناسه ملی for `tinb` automatically.
4. **Type switch 1↔2 on an existing draft re-evaluates requirements LIVE** — stale
   rules must never trap the user.
5. **The finalize/submit button always explains what's missing** — never silently dead.
6. **Single source of (effective buyer, نوع):** backend
   `converter.resolve_effective_buyer_and_type` — `moadian_type_override` wins (1|2);
   otherwise buyer presence derives the نوع (buyer→1, walk-in→2). The draft readiness
   gate, the Moadian validator, the preview, and the UI must all obey the SAME resolver.
7. **ZERO-TOTAL law**: real (non-sandbox) test submissions are zero-total only
   (100% discount, نوع دوم walk-in). Non-zero proofs go to the نیک‌تجارت sandbox.

Persona map for proofs: **نیک‌تجارت** `09120001002` (sandbox, non-zero allowed) ·
**دیباتک** `09120000000` (live, zero-total smoke only) · demo «کاربر نمونه»
`09120009000` (sandbox, drafts).

## A — Issuance core: kind × نوع × buyer × amount

Legend: kind `INT` = internal (proforma/internal_private), `TAX` = tax_reportable.
Proof = real-UI Playwright journey on dev unless noted. Viewport: rows marked 📱 are
proven at 390px; the rest desktop.

| # | Kind | نوع | Buyer | Amount | Expected behavior | Proof | Status |
|---|------|-----|-------|--------|-------------------|-------|--------|
| A1 📱 | TAX | 2 (one-tap walk-in) | none | real | Step 2 «بدون مشخصات خریدار» = one tap, zero fields → finalize enabled → validate OK → sandbox submit → org ACCEPTED | UI journey, نیک‌تجارت sandbox | ✅ org ثبت شد (clean) — A1-01..04*.png |
| A2 📱 | TAX | 2 | customer, no ids | real | Customer attaches fine; identity NEVER blocks finalize/validate/submit; org ACCEPTED | UI journey, sandbox | ✅ org ثبت شد — A2-*.png |
| A3 | TAX | 2 | customer, partial (name only) | real | Same as A2 — warnings only (postal/address «توصیه می‌شود»), never a blocker | UI journey, sandbox | ✅ org ثبت شد — A3-*.png |
| A4 | TAX | 2 | customer, full ids | real | Accepted; packet carries buyer snapshot with inty=2 | UI journey, sandbox | ✅ org ثبت شد |
| A5 📱 | TAX | 1 | customer, full ids | real | The strict path: finalize OK, validate OK, submit → org ACCEPTED | UI journey, sandbox | ✅ org ثبت شد — A5-*.png |
| A6 | TAX | 1 | customer, missing id | real | BLOCKED with the named missing field (e.g. «کد/شناسه ملی برای اشخاص حقیقی لازم است») shown inline AND on the finalize button explainer; one-tap escape to نوع دوم offered | UI journey, sandbox | ✅ blocked+named field — A6-*.png |
| A7 | TAX | 1 | none | real | BLOCKED with «برای صورتحساب نوع اول، اطلاعات خریدار لازم است» + visible path (select customer OR switch to نوع دوم); button explains, never silently dead | UI journey | ✅ blocked+escape paths — A7-*.png |
| A8 | TAX | 1 | customer, legacy 12-digit eco code | real | ACCEPTED with amber nudge «کد اقتصادی جدید همان شناسه ملی (۱۱ رقمی) است»; packet `tinb` = the 11-digit شناسه ملی | UI journey, sandbox | ✅ amber + wire tinb=11digit + org ثبت شد — A8-01*.png |
| A9 | TAX | 1↔2 switch on existing draft | any | real | Switching type re-evaluates requirements LIVE both directions; no stale blockers; readiness + validate + button text all follow | UI journey | ✅ live both directions — A9-*.png |
| A10 📱 | INT | — | none | real | No customer demanded at ANY step; no Moadian UI anywhere; finalize + print/PDF work | UI journey | ✅ — A10-D1-*.png |
| A11 | INT | — | customer | real | Customer optional-attach works; still zero Moadian friction | UI journey | ✅ (optional select verified on internal wizard) |
| A12 | TAX | 2 | none | **zero-total** (100% discount) | THE live smoke on دیباتک: finalize → validate → LIVE submit → org ACCEPTED «ثبت شده»; ZERO-TOTAL law honored | UI journey, دیباتک LIVE | ✅ LIVE ثبت شد، بدون تذکر — A12-*.png |

## B — Draft lifecycle

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| B1 📱 | Create draft → add lines (product + free-title) | Lines add/edit/remove; totals recompute; Shamsi date; money formatting per §7.3 | UI journey | ✅ (A1 journey) |
| B2 | Edit draft header + lines | Only `draft` status editable; edits persist (reload-proof) | UI journey | ✅ (edits persist; finalized 409s) |
| B3 | Delete line / archive draft | Friendly Persian confirm; totals recompute; archived leaves list | UI journey | ✅ (confirm dialogs; archived left list) |
| B4 | Finalize | Document number assigned per business numbering config; editing locks; receivable recomputes when customer attached | UI journey | ✅ (INV-2026-000012) |
| B5 | Finalize with zero lines | BLOCKED «برای نهایی‌سازی، حداقل یک ردیف لازم است» — explained, not dead | UI journey | ✅ (disabled+hint; step gate bounces) |
| B6 | Convert internal → tax_reportable | Allowed only when tax requirements satisfied (override-aware); gated on approved taxpayer profile | UI journey | ✅ (blocked→sstid fixed→converted) |
| B7 | Settle — cash receipt | Payment records; `payment_status` transitions unpaid→partial→paid | UI journey | ✅ تسویه جزئی — B7-B8-*.png |
| B8 | Settle — cheque | Cheque received against invoice; lifecycle (در جریان/وصول) reflects on invoice paid state | UI journey | ✅ در انتظار وصول چک — B7-B8-*.png |
| B9 | Print view + PDF | Both kinds render Persian RTL, Vazirmatn, correct totals; walk-in shows «مصرف‌کنندهٔ نهایی», never an empty buyer error | UI journey | ✅ print 200 + PDF 85KB (follow-up: Gregorian date in print header) |
| B10 | Fiscal-year lock | Out-of-window issue date blocked with the FY message; in-window passes | UI journey | ✅ friendly FY 422 via real save |

## C — Moadian journey (tax_reportable only)

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| C1 📱 | Validate (پیش‌بررسی) | Interpreted issues; نوع-aware (same resolver); zero raw JSON | UI journey | ✅ (all journeys) |
| C2 📱 | Submit → org result | Sandbox: real submit → interpreted org response; taxid + reference rendered copyable | UI journey, sandbox | ✅ (A-rows) |
| C3 | Inquiry / refresh status | «به‌روزرسانی وضعیت» updates from org; «آخرین استعلام» timestamp | UI journey | ✅ (A1/C8b) |
| C4 📱 | Status lock after registration | Panel permanently shows persisted state (no re-validate CTA); lifecycle actions offered | UI journey | ✅ persisted lock — C4-*.png |
| C5 | اصلاحیه (amendment) | New packet ins=2 carrying accepted original's taxid; org ACCEPTED | UI journey, sandbox | ✅ org ثبت شد — C5-*.png |
| C6 | ابطال (cancellation) | ins=3 carrying original taxid; org ACCEPTED; amend-after-cancel blocked friendly | UI journey, sandbox | ✅ org ثبت شد — C6-*.png |
| C7 | برگشت از فروش — full | Return document → packet sold-minus-returned; org ACCEPTED | UI journey, sandbox | ✅ spec-correct: full return refused → «باید ابطال شود» (guidance now inline) |
| C8 | برگشت از فروش — partial | Partial quantities; org ACCEPTED | UI journey, sandbox | ✅ partial 1/3 org ثبت شد (14xxx خارج‌ازالگو notices, non-blocking) |
| C9 | Bulk submit | Multi-select → submit-bulk (≤1000); per-invoice interpreted results | UI journey, sandbox | ✅ 2/2 per-row progress + org accepted — C9-*.png |
| C10 | Excel import — نوع اول rows | Sample downloads; import creates drafts; per-type columns honored | UI journey | ✅ friendly per-row errors; crn col parses — C10-*.png |
| C11 | Excel import — نوع دوم rows | Walk-in rows import with NO buyer columns required | UI journey | ✅ ۲ پیش‌نویس ساخته شد — C11-*.png |
| C12 | Entitlement-gated business | No `moadian_submission` → honest «FEATURE_NOT_ENABLED» Persian module-state message, NEVER a generic access-denied; internal invoicing untouched | UI journey | ✅ honest plan-state message — C12-*.png |
| C13 | Duplicate اصلی re-submit | Friendly rejection steering to اصلاحیه/ابطال (E PART 2 guard) | UI journey | ✅ «قبلاً ثبت شده … اصلاحیه/ابطال» |
| C14 | 1300501 تذکر rendering | Serial-continuity notice renders as calm non-blocking تذکر, never red/error | UI journey | ✅ calm تذکر + دلیل سامانه — C14-*.png |
| C15 | پیمانکاری (الگوی ۴) | Pattern selector فروش/پیمانکاری (نوع اول only); crn required (numeric ≤12) when پیمانکاری; Excel crn column | UI journey; org proof founder-blocked on کارپوشه crn | ✅ UI complete + finalize crn gate — C15-*.png; org proof FOUNDER-BLOCKED on کارپوشه crn |

## D — Internal-invoice purity sweep

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| D1 | Internal create/edit/finalize/print | Zero Moadian UI (no نوع line, no validate/submit, no buyer-identity text) at every step | UI sweep | ✅ zero Moadian UI (honest clarifier note only) |
| D2 | Internal invoice list + detail | No Moadian status column/filter leakage for internal docs | UI sweep | ✅ fixed this batch (chip was leaking) — D2-*.png |

## E — Editable اصلاحیه (MOADIAN F, RC_IITP §5-2)

Spec: `docs/moadian/md_f_corrective_spec.md`. Corrective = editable deep-copy of a
registered invoice; نوع/الگو/خریدار/شناسهٔ کالا/خدمت/نرخ مالیات frozen; submit auto ins=2.

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| E1 📱 | «صدور اصلاحیه» on a registered invoice | Confirm dialog explains the editable-draft flow → creates a DRAFT copy linked to the original → lands in the wizard with everything editable per spec | UI journey, نیک‌تجارت sandbox | ✅ INV-000026 (ثبت شد) → صدور اصلاحیه → confirm («مرجع: …D5») → new draft INV-000027, steps navigable — E1/E2/E3-*.png |
| E2 📱 | Corrective wizard locks | نوع/الگو/crn/customer/buyer locked with a reason; «افزودن ردیف» disabled; per-line شناسهٔ کالا/خدمت + نرخ مالیات locked; qty/price/discount editable | UI journey | ✅ no «شناسه مالیاتی» btn, no add-line form («…نمی‌توان ردیف جدید افزود RC_IITP §5-2»), نرخ مالیات read-only, qty/price/discount editable — E4a-*.png |
| E3 📱 | Edit + finalize + submit | Change qty on one line + price on another + delete a line → finalize → «ارسال» → org ACCEPTED as اصلاحی (ins=2, subject_fa=«اصلاحی») | UI journey, sandbox | ✅ qty 2→5, price 2M→2.5M, deleted line 3 → org **ثبت شد** (taxid …E1, subject=2 accepted in DB). تذکر: org flags الگو/نوع «خارج از الگو» (non-blocking; see follow-up) — E4b/E6-*.png |
| E4 | Bidirectional timeline | Original shows «اصلاح شد → [شماره]»; corrective banners «اصلاحیهٔ [مرجع]» + مرجع link | UI journey | ✅ original «این صورتحساب اصلاح شده است: INV-000027» ↔ corrective «اصلاحیهٔ INV-000026» + «مشاهدهٔ صورتحساب مرجع» — E7/E3-*.png |
| E5 | Blocked — corrective on cancelled | «صدور اصلاحیه» on a باطل‌شده invoice → friendly Persian refusal, no org call | UI/curl | ⚠️ guard proven at code+test level (`_has_cancellation` in create_corrective; button enables ONLY on «ثبت شده» — proven disabled pre-registration & on «رد شد» INV-000025). Cancelled-invoice-specific UI walk not run this batch. |
| E6 | Blocked — second open corrective | A 2nd «صدور اصلاحیه» while one draft is open → friendly «یک پیش‌نویس اصلاحیه باز است» | UI/curl | ⚠️ one-open guard live (409, unit-tested; relied on it during cleanup). Explicit 2nd-attempt UI walk not run this batch. |
| E7 | Cancel corrective draft | Cancelling the corrective DRAFT leaves the original untouched (no org footprint) | UI journey | ⚠️ re-verify draft discarded (DB delete) left original INV-000023 untouched + re-correctable; UI «لغو سند» path not walked this batch. |
| E8 | Packet buyer-omit | The اصلاحی packet omits buyer identity (جدول ۱۰ ردیف ۴) — no 14xxx «خارج از الگو» تذکر from the buyer fields | wire-check | ✅ unit-tested (test_corrective_f: buyer omitted for ins 2/3/4, original keeps buyer); org returned NO buyer-field تذکر on the نوع دوم corrective. |

## F — Pagination / findability (MOADIAN F Parts 2–3)

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| F1 📱 | /app/moadian submissions | Paginated + searchable (سند/taxid/ارجاع) + status/environment filters + calm count | UI journey | ✅ «۲۹ ارسال · صفحه ۱ از ۲» pager + status & environment selects; search «9167E1» → «۱ ارسال» (server-side) — F1-*.png |
| F2 | /app/moadian api-log | Paginated with prev/next | UI journey | ✅ «سوابق ارتباط» «صفحهٔ ۱ از ۴» prev(disabled)/next |
| F3 📱 | Pattern findability — نوع اول | الگو selector visible, پیمانکاری selectable, crn field «شمارهٔ قرارداد (ثبت‌شده در کارپوشه)» appears | UI journey | ✅ builder (نوع اول): فروش/پیمانکاری segmented selector renders; «الگوهای دیگر» dialog confirms «پیمانکاری فعال است»; crn label renamed. (Create page shows read-only line intentionally.) |
| F4 📱 | Pattern findability — نوع دوم | Read-only «الگو: فروش» + visible note «الگوی پیمانکاری فقط برای نوع اول در دسترس است» | UI journey | ✅ read-only «الگو: فروش» + note «الگوی پیمانکاری فقط برای «نوع اول» در دسترس است…» on create + builder — F4-*.png |

## Proof artifacts

Walked 2026-07-24 on dev (backend `257fc23`, frontend `a8d24e2`): screenshots in
`qa-screens/matrix-walk/` (workspace root), harness spec 10 encodes the core
walk-in journey permanently (`tests/e2e-harness/specs/10-invoice-flow.spec.ts`).
Non-zero proofs on sandbox نیک‌تجارت; the one live zero-total smoke on دیباتک
(`A41XRD050B2006A5E4C576`, بدون تذکر — hex-inno fix live-proven; an earlier
attempt with vra=0 was org-REJECTED «نرخ … منطبق نیست», proving the org
validates the line rate against the sstid registry — zero-total tests must keep
the REGISTERED rate and zero out via 100% discount).

## Walk findings fixed in-batch
1. The wizard customer trap (`handleGoToStep`) — removed; نوع switch + one-tap walk-in added.
2. Backend readiness ignored `moadian_type_override` — now mirrors the resolver.
3. Stale readiness explainer after header save — invalidation added; finalize/convert decide on FRESH readiness.
4. پیمانکاری crn discovered only at validate stranded a finalized draft — crn is now a finalize blocker.
5. D2: internal rows leaked a «مودیان: ارسال‌نشده» chip — chip is tax_reportable-only now.
6. Returns dialog swallowed the backend guidance (full-return→ابطال etc.) — rendered inline now.
7. Body `inno` decimal↔hex — org parses it AS HEX vs the taxid serial; hex adopted (kills 1300501).
8. **Corrective deep-copy dropped per-line amounts (F Part 1)** — `create_corrective_draft_for_tenant` copied qty/price/discount but not `line_subtotal`/`line_vat_amount`/`line_total`, and `_recalculate_totals` only SUMS the (then-0) stored per-line totals. A copied line recomputed only when individually edited, so an UNEDITED line in a corrective submitted with a **0 amount** (understated اصلاحیه). Fixed: copy the original's already-correct per-line amounts (commit `33e3149`). `*_pg` regression test added (FakeDBSession bypassed this path). Real-UI re-proven on dev: a fresh corrective's unedited line shows «۱۳,۲۰۰ ریال», not «۰» — E4c-FIX-*.png.

## Follow-ups (logged, not this batch)
- **Corrective «خارج از الگو» تذکر (Moadian spec).** The نوع دوم corrective REGISTERED («ثبت شد») but the org returned a non-blocking تذکر that «الگوی صورتحساب» (inp) and «نوع صورتحساب» (inty) are «خارج از الگو» (codes 14007/14004). Our packet blanks only the BUYER for referring subjects (ins 2/3/4, جدول ۱۰ ردیف ۴); the org's ideal appears to also omit inty/inp on a corrective. Non-blocking today; confirm the exact referring-subject field set with the accountant before blanking inty/inp (avoid speculative packet changes). Same class as the existing 14xxx «خارج از الگو» return notices.
- Print-view header shows the Gregorian issue date («۲۰۲۶-۰۷-۲۴») — should be Jalali.
- The admin payload PREVIEW shows the raw legacy `tinb` while the wire substitutes the 11-digit شناسه ملی — align the preview with `_buyer_tinb`.
- Excel-imported drafts with out-of-FY dates import fine but need a date fix before the wizard can save — consider an import-time hint.
