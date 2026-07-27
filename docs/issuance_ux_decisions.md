# Issuance UX — decisions doc (PRIORITY BATCH, Part 1)

The long-owed deep overhaul of **create → finalize → submit**. Written BEFORE any code
changed, from a real walk of the live dev app as three users. Every claim below was
observed in the browser, not inferred from source.

_Walked 2026-07-27 on dev (`791bf93` / `0a70cda`) as بازرگانی نیک‌تجارت (09120001002),
approved taxpayer + Moadian-connected._

---

## 0. Constraints this overhaul must respect (non-negotiable)

```
✓ invoice_flow_matrix stays green — affected rows re-walked, not assumed.
✓ NO new required fields. (Removing/relaxing an existing one is allowed and wanted.)
✓ Backend contracts untouched unless truly needed. This batch: UNTOUCHED.
✓ Never rewrite working code — every change is in place.
✓ 390px parity: the shopkeeper is on a phone behind a counter, not at a desk.
✓ Persian RTL, «شما», no raw codes, no dead ends (§7 workspace CLAUDE.md).
```

---

## 1. The three users, and what each actually needs

| # | User | Real situation | Wants | Today's blocker |
|---|------|----------------|-------|-----------------|
| a | **Rushed shopkeeper** | Customer at the counter, phone in one hand | Walk-in نوع دوم, 1–2 lines, done in seconds | 6 screens; a required free-text title; mouse needed for every line |
| b | **Distributor** | Office, known buyer, credit terms | نوع اول + buyer inquiry + cheque settlement | Buyer step is fine; line entry is the same slow path × 10 lines |
| c | **Accountant** | End of day, batch of drafts to finalize | Sweep drafts → finalize | Must re-enter each draft one at a time through all 5 steps |

---

## 2. Pain points found in the real walk (the honest list)

### P1 — A walk-in sale costs **six screens**
`/app/invoices/new` (type + Moadian type + title) → editor step **۱ سند** → **۲ مشتری**
→ **۳ اقلام** → **۴ آمادگی** → **۵ نهایی**. For a cash sale with one item, four of those
six screens ask nothing the shopkeeper needs.

### P2 — «عنوان سند» is REQUIRED and meaningless for retail
The create screen refuses to proceed without a free-text title. A walk-in cafe sale has
no "title". This is the single largest time cost before any real work begins, and it is
exactly the "default-visible field a merchant doesn't need" the batch calls out.

### P3 — Line entry is mouse-bound
`SmartLineInput` wires submit **only** to the «افزودن ردیف» button's `onClick`. There is
no Enter-to-add. Per line the merchant must leave the keyboard, aim, click, come back.
At 10 lines (user b) that is 10 round trips.

### P4 — Typeahead exists but is not reachable by keyboard
The resolver (`resolveSmartLine`, 400ms debounce) returns candidates, but they render as a
**block below the field** requiring a mouse click on «انتخاب» — even for `exact_match`.
There is no ↑/↓ navigation and no Enter-to-accept. A typeahead you cannot drive from the
keyboard is a list, not a typeahead.

### P5 — Four numeric fields always visible; two are rarely touched
`مقدار / قیمت واحد / تخفیف / نرخ مالیات` all render at once. تخفیف is usually empty and
نرخ مالیات is usually the default 10. They cost width at 390px and attention everywhere.

### P6 — No repeat-last-item
`resetLine()` clears to `EMPTY_FIELDS` after every add. A shop selling the same item twice
retypes it in full.

### P7 — The Moadian type is asked twice
Chosen on `/invoices/new`, then shown again on editor step ۲. The page's own tour promises
«دیگر دوبار پرسیده نمی‌شود» — the UI contradicts its own copy.

### P8 — Blocked CTAs go quiet
The step CTA greys out with the reason living elsewhere on the page (or, on the Moadian
card, only inside a hover tooltip — already fixed in the previous batch for touch). A
disabled button that does not say why is a dead end.

### P9 — The شناسه مالیاتی blocker is discovered FOUR steps too late ⚠️ worst dead end
A free-text line entered at step ۳ passes silently. Only at step ۵ نهایی does the app
say «شناسه کالا/خدمت (شناسه مالیاتی) برای ردیف لازم است» — after the merchant has walked
مشتری → اقلام → آمادگی → نهایی believing the sale was captured. The information needed to
prevent it (this is a tax-reportable invoice, so every line needs a stuff-id) is known the
moment the line is typed.

This is the single worst dead end in the journey and it is a *sequencing* bug, not a
missing feature: the readiness truth exists, it is just surfaced last instead of first.

> Note: the finalize button is deliberately left ENABLED with the blocker list rendered
> above it (see the comment at `_app.app.invoices.$invoiceId.tsx:1402`) — that is an
> existing, documented decision and is NOT changed here.

---

## 3. What changes (and what deliberately does NOT)

### Changing

| # | Change | Fixes | Why this shape |
|---|--------|-------|----------------|
| C1 | **Enter adds the line.** Enter anywhere in the line form submits it and returns focus to the title field. | P3 | Type → Enter → type → Enter. The keyboard never leaves the merchant's hands. Button stays for touch (it is the 390px path). |
| C2 | **Real typeahead**: candidates in a listbox under the field, ↑/↓ to move, Enter to accept, Esc to dismiss. Exact match is pre-highlighted. | P4 | `keyboard-nav` is a HIGH-severity rule. Mouse users lose nothing — clicking still works. |
| C3 | **تخفیف + نرخ مالیات move behind «جزئیات بیشتر»**, collapsed by default, with a summary chip when either is non-default so nothing hides silently. | P5 | `progressive-disclosure` (§8). The chip is the honesty guard: collapsed ≠ invisible. |
| C4 | **«تکرار آخرین ردیف»** chip appears after the first add; one click refills title/price/VAT of the previous line. | P6 | Cheapest possible win for repeat-heavy retail. |
| C5 | **«عنوان سند» becomes optional** with an auto-derived default («فروش — ۵ مرداد ۱۴۰۵»), editable behind the same details expander. | P2 | Removes a required field without removing the capability. NOT a new required field — the opposite. |
| C6 | **Every blocked CTA narrates** — the reason renders as plain inline text next to the button, never tooltip-only. | P8 | Same fix already proven on the Moadian lifecycle card; generalised. |
| C7 | **The stuff-id blocker moves to the point of entry.** When the invoice is tax-reportable, the line form says so as the line is typed and the اقلام step CTA carries the count of lines still missing a شناسه — so the merchant learns at step ۳, not step ۵. | P9 | Pure sequencing: same readiness truth, surfaced where it can still be acted on cheaply. No new required field — an unresolved line is still savable, it just stops being a silent surprise. |

### Deliberately NOT changing

- **The 5-step wizard stays.** It is the right teaching structure for a first-time
  merchant and the accountant's mental model. The fix for P1 is making the *fast path*
  through it cheap (C1–C5), not deleting steps a novice needs.
- **The Moadian type selector stays on both screens** — but step ۲'s copy will say it is
  the same choice, not a fresh question (P7 is a copy bug, not a structure bug).
- **Backend contracts, validation rules, money handling, Jalali dates** — untouched.
- **No redesign of colours/spacing** — that is Part 2, and mixing them would make this
  diff unreviewable.

---

## 4. Measurement — before/after (measured, not estimated)

Committed, re-runnable benchmark: `digi-tax-frontend/tests/issuance-bench/`, run with
`pnpm bench [--base-url …]`. It drives the **real UI** and always takes the fastest path
the build offers (empty title if allowed, Enter-to-add if supported, button if not), so
one script measures both builds fairly.

**Persona (a) — rushed shopkeeper, walk-in نوع دوم, one line:**

| Metric | Before | After | Δ |
|--------|--------|-------|---|
| **keystrokes** | 33 | **18** | −45% |
| **pointer clicks** | 6 | **5** | −1 |
| screens | 5 | 5 | unchanged (by design, §3) |

Measured 2026-07-27: *before* = the deployed build `0a70cda` on dev, *after* = the new
build locally. The 15 keystrokes are the dead «عنوان سند» requirement; the click is the
«افزودن ردیف» pointer trip that Enter replaces.

> **Wall-clock is deliberately NOT quoted as a win here.** The two runs hit different
> targets (remote dev vs localhost), so the seconds differ by network latency alone.
> Keystrokes and clicks are properties of the BUILD and are comparable; seconds are not,
> unless both builds run against the same target. The bench header says so too, so nobody
> later mistakes a latency delta for a UX result.

**Scaling note (honest):** the per-line savings compound for persona (b), who enters ~10
lines — each line drops one pointer trip, and picking an existing product becomes
`↓ Enter` instead of typing the full name plus a click. That is arithmetic from the
measured per-line delta, **not** a separately measured 10-line run; persona (b) and (c)
journeys are not yet in the bench.

---

## 5. Open questions parked (not silently dropped)

- **Currency unit on the line form reads «ریال» while the app elsewhere uses تومان.**
  This is likely deliberate (Moadian is ریال-native and `useMoney()` drives a display
  unit) but it deserves a founder confirmation before anyone calls it a bug.
- **A true one-screen «فروش سریع» mode** (single sheet: item + price + done, wizard
  bypassed) is the logical end state for user (a). It is a bigger structural change than
  this batch should carry alongside Parts 2–4; logged here as the next issuance step.
