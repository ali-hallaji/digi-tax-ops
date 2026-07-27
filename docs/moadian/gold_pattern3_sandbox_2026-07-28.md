# الگوی سوم (طلا) — sandbox verdict, 2026-07-28

**Outcome: the org REJECTED our sourced formula reading. That leg is STOPPED, per
the batch instruction — no formula guessing beyond the source.**

Environment: نیک‌تجارت **sandbox**, fiscalId `A2HP31`. Two submissions, both on
fresh references (rotation law).

---

## Attempt 1 — taxid `A2HP31050B5006AF916 8A8`

Line used a **made-up** stuffid (`2710000000000`) with `vra = 0`.

Org verdict (inquiry), verbatim:

> «مقدار فیلد «نرخ مالیات بر ارزش‌افزوده(J)» در قلم کالای «1» صورتحساب با اطلاعات
> سامانه منطبق نیست.»
> راه حل: «نرخ ارزش افزوده باید با نرخ ثبت‌شده برای همان شناسهٔ کالا/خدمت یکی باشد.»
> codes: `0303301`, `0204501`

**Learned:** `vra` must equal the rate the org has registered **for that exact
stuffid**. You cannot declare a line exempt by writing `vra = 0`; the stuffid
decides. This independently confirms the research's claim that the gold exemption
comes from a zero-rate شناسهٔ کالا, not from the pattern.

## Attempt 2 — taxid `A2HP31050B5006AF9168B2` (the real test)

Fixed attempt 1 by using a **genuine exempt gold stuffid** from the org catalog:
`2001584175153` — «شمش طلا، خلوص 99.5 %، وزن 1000 g», `vat_rate = 0`,
`tax_status = exempt`.

Exact body we sent:

```json
{"sstid":"2001584175153","sstt":"شمش طلا ۱۰۰۰ گرمی",
 "am":1,"fee":23598000,"prdis":23598000,"dis":0,
 "adis":29037339,"vra":0,"vam":543934,"tsstam":29581273,
 "consfee":3539700,"bros":0,"spro":1899639,"tcpbs":5439339}
```

Those are the research's own worked-example numbers
(اجرت ۳٬۵۳۹٬۷۰۰ + سود ۱٬۸۹۹٬۶۳۹ = tcpbs ۵٬۴۳۹٬۳۳۹) with the current ۱۰٪ rate,
i.e. `vam = 5,439,339 × 10% = 543,934`.

Org verdict (inquiry `FAILED`), verbatim:

> `0204501` — «مقدار فیلد «مبلغ مالیات بر ارزش افزوده(KS)» در قلم کالای «1»
> صورتحساب از لحاظ قواعد محاسباتی و منطقی معتبر نیست.»

---

## What this settles, and what it does not

**Settled:**
- `tcpbs = TA + TA2 + TA3` was accepted without complaint (never flagged in either
  attempt) — the sum field itself is right.
- `vra` must match the stuffid's registered rate. Attempt 1 proves it.
- The packet shape, taxid, signing and transport for الگوی ۳ all work; the
  rejection is about ONE numeric field.

**NOT settled — and deliberately not guessed:**
The org rejects our **Ks/vam** on a line whose own `vra` is 0. Our reading, taken
straight from `docs/tax_research_1404.md` «سؤال ۱», is:

```
Ks = ((TAs × goldRate)/100) + ((Es × J)/100)
```

which on an exempt line collapses to `TAs × 10%` = 543,934. The org calls that
«از لحاظ قواعد محاسباتی و منطقی معتبر نیست».

The obvious hypothesis — that a line carrying an EXEMPT stuffid must report
`vam = 0`, with the taxable اجرت/حق‌العمل/سود belonging on a SEPARATE line under a
taxable stuffid — is **a hypothesis, not a source**, and the batch instruction is
explicit: no formula guessing beyond the sourced one. So it is written here as a
question, not shipped as behaviour.

**Our code is unchanged and still implements the sourced formula.** The 1-ریال
rounding question (half-up 489,541 vs the ترازسامانه example's 489,540) is
therefore ALSO still open: the org never got far enough to judge rounding, because
it rejected the value's magnitude, not its last digit.

---

## What the founder needs to ask

One question, for the org or an accountant who has filed a real gold invoice:

> در الگوی سوم، وقتی شناسهٔ کالای ردیف «معاف» است، مبلغ مالیات ارزش افزودهٔ آن
> ردیف (KS) باید صفر باشد و اجرت/حق‌العمل/سود در ردیف جداگانه با شناسهٔ مشمول ثبت
> شود؟ یا KS همان ردیف باید ۱۰٪ مجموع اجرت/حق‌العمل/سود باشد؟

The moment that is answered, the mapper is a few lines from correct — the engine,
fields, UI and transport are all in place and proven by these two submissions.

## Product state right now

- الگوی ۳ is selectable, the gold fields appear only for gold, tcpbs is
  auto-computed and read-only, `crn` is correctly hidden. All verified in the
  real UI on dev.
- A gold invoice can be built and submitted end-to-end; the org rejects it at
  inquiry on KS.
- **Do not present gold as usable to a goldsmith until the KS question is
  answered.** Everything else about the pattern works.
