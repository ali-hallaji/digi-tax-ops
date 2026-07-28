# PRIORITY BATCH — saved state (2026-07-27)

Resume point. Updated after the second working session.

---

## Deployed SHAs on dev (all verified live via /health/version + /version.json)

```
backend   0e57164
frontend  cf897a6
ops       4d822dd
```

---

## DONE and SHIPPED

| Item | State |
|------|-------|
| **STEP 0** — pending ship | ✅ pushed + deployed + harness green |
| **STEP 0.5** — real Kavenegar SMS proof | ✅ **PROVEN** |
| **PART 1** — issuance UX deep overhaul | ✅ doc + code + bench + specs |
| **PART 2** — UI consistency remainder | ✅ (scoped honestly — see below) |
| **PART 4.1** — legacy soft-state sweep + «سلامت داده» | ✅ |
| **PART 4.2** — crn پیمانکاری empirical test | ✅ **answered, and it changed the product** |

### Step 0.5 — the proof
`provider=kavenegar · status=sent · provider_ref=45334056 · template=digiotp`.
`otp_delivery_bypass` **OFF** for `09120000000` and MUST STAY OFF; all 16 personas
bypassed. Last OTP blocker: emptying `SMS_ALLOWLIST` (founder's env-only call).

### Part 1 — measured
`pnpm bench`: walk-in journey **33→18 keystrokes, 6→5 clicks**. Doc:
`issuance_ux_decisions.md`. Wall-clock deliberately not claimed (different targets).

### Part 2 — what was and was NOT done
- ✅ `DataTable` responsive primitive; `/app/returns` no longer hides مبلغ+actions
  behind a sideways swipe at 390px (was 560px table in a 358px wrapper).
- ✅ payments + purchases stopped forking `EmptyState`'s markup; it gained `actionIcon`.
- ✅ dashboard padding: 4 values → 20px×6 + one documented strip + two chart cards.
  Scale written down in `ui_padding_scale.md`.
- ✅ admin SMS log: raw English «bypass» → Persian; date-only time → date+time.
- ⏸️ **~200 other card-padding sites deliberately NOT swept.** An unreviewable
  visual change across 104 files that no screenshot pass could honestly verify.
  The scale is now the written rule; surfaces move onto it as they are touched.

### Part 4.2 — the crn verdict (headline)
Real sandbox pattern-4 submission, taxid `A2HP31050B5006AF916898`. Org rejected:

> «در مقدار وارد شده در فیلد «شناسه یکتا ثبت قرارداد فروشنده» الگو(`^\d{12}$`)
> رعایت نشده است» — code `0102004`

**The org enforces FORMAT before registration.** crn must be exactly 12 digits.
Our UI was teaching the failure (hint «حداکثر ۱۲ رقم», placeholder «مثال: 1001»);
now exactly-12 validation + live counter + corrected copy. Recorded as matrix **G1**.

---

## NOT DONE — resume here

### PART 3 — pricing leftovers (NOT STARTED)
Untouched. Nothing half-built. Needs:
1. «بستهٔ افزایش سند» purchasable — consumable quota units on top of the monthly
   allowance, admin-priced SKU, checkout via the existing gateway flow, usage card
   reflecting purchased headroom.
2. Admin price history — effective-from date + audited change history per SKU;
   plans page reflects current.
3. Plans page final polish (tier presentation, included volumes, overage pack).
4. Document the `DOCUMENT_CAP_ENFORCED` flip procedure (flag stays OFF).

### PART 4.3 — sandbox rotation re-verification (DONE 2026-07-28)
Re-walked the whole lifecycle chain on a brand-new اصلی — see
`docs/invoice_flow_matrix.md` § I and `scripts/rotation_rewalk.py` (re-runnable).

It was NOT just a walk: it surfaced two real rules and one product bug.
  • a registered اصلاحیه SUPERSEDES the original — a later ابطال/برگشت must
    reference the NEWEST version, and ours referenced the original, which the
    org refuses with 0300601. Fixed in `_reference_submission`.
  • an ابطال must be header-only; sending body/totals draws «خارج از الگو» on
    every field.

### PART 4.2 follow-up — still open for the founder
Whether a **well-formed but unregistered** 12-digit crn is accepted is UNANSWERED —
the format rule fired first. Needs a real contract registered in the نیک‌تجارت
کارپوشه (one founder click), then re-run matrix row G1.

---

## Open findings logged, NOT fixed

1. **`prod_smoke.sh` false-green**: its "no OTP echoed" check greps `"otp"`/`"dev_otp"`
   but not `otp_hint`, and probes the one mobile that is hint-protected by design —
   it cannot trip even with `DEV_LOGIN_OTP_HINT` wrongly left on. One-line fix.
2. **`smoke_test.sh` stale vs captcha**: its OTP leg expects `otp_sent` and gets the
   400 captcha refusal; also needs `SMOKE_CORS_ORIGIN` exported on the server.
3. **1.7 GB of DB dumps untracked in `backups/`** inside the ops git worktree on the
   server — one `git add -A` from committing a database dump.
4. **Moadian unknown code `0102004`** returned «توضیح این کد هنوز ثبت نشده است» —
   the unknown-code catalog should learn it.
5. **Currency unit question (founder)**: invoice line form and totals read «ریال»
   while much of the app uses تومان. Likely deliberate (`useMoney()` display unit,
   Moadian is ریال-native) — wants one line of confirmation before anyone "fixes" it.
6. **Bench covers persona (a) only**; (b) distributor and (c) accountant journeys are
   not yet in `tests/issuance-bench/`.

---

## Gotcha worth keeping

**Never run the harness against dev immediately after recreating the frontend
container.** A cold SSR context loses the first spec's hydration and reds spec 01 with
a filled-but-unsubmitted OTP form. Warm it first (a few curls to `/` and `/login`) —
done in this session, and the dev run went green with zero retries.
