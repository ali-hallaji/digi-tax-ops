# MOADIAN E — Patterns الگوی ۴ (پیمانکاری) & الگوی ۳ (طلا/جواهر): spec + status

Sources: `RC_IITP_IS_V7_8.pdf` (جدول ۹/۱۰/۱۱/۲۴ + line tables §7-40..7-61) and
`pattern_assessment_md_d.md`. Every rule below is quoted/cited; nothing invented.

## الگوی چهارم — قرارداد پیمانکاری (Pattern 4) — READY TO BUILD (deferred, low-risk)

Fully specified, no ambiguity:
- **One pattern-specific field: `crn`** (شماره قرارداد پیمانکاری) — numeric string, max 12,
  جدول ۱۱. Mandatory for pattern-4 invoices (جدول ۱۱ ردیف ۹) and **must equal the contract
  number already on file in the taxpayer's کارپوشه** (ردیف ۸).
- **نوع اول only** (جدول ۹ ردیف ۱ lists الگوی ۴ under نوع اول; ردیف ۲ نوع دوم = only 1/3/9/13).
  No `("2","4")`.
- **Body identical to الگوی فروش** (pattern 1) — no gold-style line math.
- **allowed_ins = {1,2,3,4}** (جدول ۱۰ ردیف ۱, no restriction). **setm** = standard free
  choice (جدول ۲۴ does not force cash for pattern 4).

Build plan (a focused vertical — NOT started this batch, per the 97% rule + the proof blocker):
1. Migration: add `invoice_drafts.moadian_contract_number` (VARCHAR(12), nullable).
2. `normalizer/patterns.py`: `map_type1_pattern4` = `map_type1_pattern1` with `inp=4` +
   `header["crn"]=crn`; mark `("1","4")` `mapped=True`; catalog auto-lights «پیمانکاری».
3. Validator: when resolved pattern=4, `crn` required (numeric, ≤12) → friendly Persian blocker.
4. FE: the read-only «الگو: فروش» line becomes a real selector فروش/پیمانکاری for نوع اول;
   a crn input appears only for پیمانکاری. Excel: optional `crn` column + sample.
5. **Sandbox proof is founder-blocked:** «crn must equal the کارپوشه contract» — the founder
   must first register a contract number in the نیک‌تجارت sandbox کارپوشه; then one
   contracting invoice with that crn → org accept.

## الگوی سوم — طلا، جواهر و پلاتین (Pattern 3) — STOPPED on ambiguity (founder rule)

Per the dispatch: "If any required field semantics are ambiguous in the PDFs, STOP that item
and list the exact question for the founder's accountant." The gold VAT base is genuinely
ambiguous. Confirmed rules first:

- **Four mandatory fields (جدول ۹ ردیف ۵):** `consfee` (اجرت ساخت), `spro` (سود فروشنده),
  `bros` (حق‌العمل), `tcpbs` (جمع کل اجرت/حق‌العمل/سود). Each اعشاری, 18-int/0-dec. Plus a
  gold-only `cui` (عیار, 0<cui≤1000, جدول ۶۳) whose mandatory-ness is unclear (see Q4).
- **`tcpbs = consfee + bros + spro`** (جدول ۴۹ ردیف ۱: `TAs=TA+TA2+TA3`).
- **`adis = prdis + tcpbs − dis`** (جدول ۴۲ ردیف ۴ — gold-only; general is `prdis − dis`).
- **`vam = ((TAs*10)/100) + ((Es*J)/100)`** (جدول ۴۴ ردیف ۴) — Es=prdis, J=vra, TAs=tcpbs.
- **`odam = TAs*J2/100`, `olam = TAs*J3/100`** (جدول ۴۵ ردیف ۱۲-۱۳) — services only.
- **`tsstam = vam + adis + odam + olam`** (جدول ۵۱ ردیف ۱).
- نوع: اول carries free setm; نوع دوم = cash (type-level). No dedicated گold-weight field
  (`nw` is export-only) — quantity via generic `am`+`mu`.

### Accountant questions (must answer before building — do NOT guess):
1. **The hard-coded `10` in `vam`.** `Ks=((TAs*10)/100)+((Es*J)/100)` uses the numeral 10,
   not `J`, for the services-portion VAT. Is 10% the current statutory gold-services VAT rate,
   and is it truly fixed (or does it track the general rate)? The doc doesn't explain the 10.
2. **Is the raw-gold value (`Es`) actually taxed?** The second term taxes `Es` at the line's
   `J`. Whether `J=0` in practice (raw-gold `sstid`s registered VAT-exempt, جدول ۴۳ ردیف ۲) is
   NOT stated in RC_IITP — it depends on the external stuffid registry. So "VAT only on
   value-added" is an assumption, not proven. Confirm the exempt status of raw-gold item ids.
3. **`tcpbs` ≥ vs =.** جدول ۴۹ ردیف ۱ defines `TAs` as an exact sum but ردیف ۲ says it must be
   «مساوی یا بزرگ‌تر» than the sum — rounding tolerance, or a real inequality?
4. **Is `cui` (عیار) mandatory?** جدول ۹ ردیف ۵'s mandatory list omits it and its table never
   says «الزامی». Does the live org accept a gold invoice without `cui`? (cf. the empty-`mu`
   live-rejection precedent — "spec-optional" ≠ "org-accepts-omission".)
5. **`<` bounds on consfee/spro/bros.** Rules read `TA < TAs` etc.; if only one of the three is
   non-zero then `TA = TAs` and strict `<` is violated. Is it actually `≤`, or must ≥2 of the
   three always be non-zero?

Until 1–2 (the VAT base) are answered, the gold mapper's tax math cannot be built without
guessing — which the dispatch forbids and the ZERO-TOTAL/no-fake laws reinforce.
