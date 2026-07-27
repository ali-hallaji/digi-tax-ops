# PRIORITY BATCH — saved state (2026-07-27, paused by founder)

Resume point for the next session. Written when the founder asked to stop mid-batch.

---

## DONE and SHIPPED to dev

| Item | State |
|------|-------|
| **STEP 0** — pending ship | ✅ pushed + deployed + harness green (done at the top of the session) |
| **STEP 0.5** — real Kavenegar SMS proof | ✅ **PROVEN** |
| **PART 1** — issuance UX deep overhaul | ✅ shipped (doc + code + bench + specs) |

### Deployed SHAs on dev
```
backend   791bf93   (unchanged this batch)
frontend  40927ad   ← live, verified via /version.json
ops       f3183d7
```

### Step 0.5 — the proof
`notification_log`: `provider=kavenegar · status=sent · provider_ref=45334056 ·
template_key=digiotp · mobile_masked=0912***0000 · body_preview=(empty)`.
`otp_delivery_bypass` is **OFF** for `09120000000` and MUST STAY OFF. All 16 personas
remain bypassed (`t`). `SMS_ALLOWLIST=09120000000` — emptying it is the founder's
env-only call and is the last launch blocker for OTP.

### Part 1 — what shipped
Doc (written first): `digi-tax-ops/docs/issuance_ux_decisions.md` — 9 pain points,
7 changes, explicit "what does NOT change".
Code: `smart-line-input.tsx` (Enter-to-add, keyboard typeahead, disclosure + honesty
chip, repeat-last), `_app.app.invoices.new.tsx` (optional title + derived default),
`_app.app.invoices.$invoiceId.tsx` (stuff-id blocker moved to the اقلام step).
Bench: `tests/issuance-bench/` + `pnpm bench` — **33→18 keystrokes, 6→5 clicks**.
Screenshots: `digi-tax-ops/qa-screens/priority-batch/` (gitignored).

---

## NOT STARTED — resume here

- **PART 2** — UI consistency remainder: card padding rhythm (167 sites → one scale),
  table→card at 390px for main lists, ~28 hand-rolled empty states → one pattern.
- **PART 3** — pricing leftovers: «بستهٔ افزایش سند» quota SKU + checkout + usage
  headroom; admin price history (effective-from, audited); plans page polish;
  document the `DOCUMENT_CAP_ENFORCED` flip procedure (stays OFF).
- **PART 4** — data-safety hardening: legacy soft-state sweep + admin «سلامت داده»
  panel; crn پیمانکاری pattern-4 sandbox attempt; sandbox-rotation re-verification of
  matrix rows referencing old taxids.

Nothing in Parts 2–4 was half-built. No dead code was left behind.

---

## Open findings logged, NOT yet fixed

1. **`prod_smoke.sh` false-green** (from the previous batch, still open): its
   "no OTP echoed" check greps `"otp"` / `"dev_otp"` but NOT `otp_hint`, and it probes
   `09120000000`, the one mobile that is hint-protected by design. It cannot trip even
   when `DEV_LOGIN_OTP_HINT` is wrongly left on. One-line fix.
2. **`smoke_test.sh` is stale vs captcha**: its OTP leg expects `otp_sent` and gets the
   400 captcha refusal on any captcha-enabled stack. Also needs `SMOKE_CORS_ORIGIN`
   exported on the server or its CORS leg fails spuriously.
3. **`backups/` (1.7 GB of DB dumps) sits untracked inside the ops git worktree** on the
   server — one `git add -A` from committing a database dump. Needs a `.gitignore` line
   or a move to `/usr/local/digi-tax-backups`.
4. **Admin «آخرین پیامک‌ها» panel**: the «زمان» column shows only the date, so all 20
   rows read «۵ مرداد ۱۴۰۵» and an admin cannot tell order or recency. Also the status
   pill renders raw English **«bypass»** in an all-Persian table (raw-code leak, §7.6).
   Both belong to Part 2.
5. **Currency unit question (parked for the founder)**: the invoice line form and totals
   read «ریال» while much of the app uses تومان. Likely deliberate (Moadian is
   ریال-native, `useMoney()` drives a display unit) — wants a one-line confirmation
   before anyone "fixes" it.
6. **Bench covers persona (a) only.** Personas (b) distributor and (c) accountant are
   not yet journeys in `tests/issuance-bench/`; the per-line scaling claim in the
   decisions doc is arithmetic from the measured per-line delta and is labelled as such.

---

## Gotcha worth keeping

**Never run the harness against dev immediately after recreating the frontend
container.** A cold SSR context loses the first spec's hydration and reds spec 01 with a
filled-but-unsubmitted OTP form. Warm it (a few `curl` hits to `/` and `/login`) first.
Cost this session: one full red dev run that was not a real regression.
