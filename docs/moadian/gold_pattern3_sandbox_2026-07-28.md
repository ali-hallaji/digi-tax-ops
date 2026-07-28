# الگوی سوم (طلا) — sandbox verdict, 2026-07-28

**Outcome: SOLVED. The org REGISTERED our gold invoice.** The structure and the
formulas we had were right; the packet was rejected over **one ریال of rounding**.
The org re-derives every computed amount with integer arithmetic and **truncates**
— we rounded half-up. Fixing that turned `FAILED 0204501` into `SUCCESS`.

The same bug governed **ordinary invoices too** (الگوی اول), so this was not a gold
problem — it was a live-merchant problem hiding behind demo data with round numbers.

Environment: نیک‌تجارت **sandbox**, fiscalId `A2HP31`. Eleven submissions, every one
on a fresh reference (rotation law). Script: `digi-tax-ops/scripts/gold_ks_experiment.py`
(re-runnable, one variant per serial).

---

## THE ANSWER, in one block

```
Es  = ⌊am × fee⌋                        pre-discount            (truncate)
Gs  = discount
TAs = TA + TA2 + TA3                    اجرت + حق‌العمل + سود     (exact)
Is  = Es + TAs − Gs                     مبلغ بعد از تخفیف        (adis)
Ks  = ⌊ TAs×goldRate/100 + Es×J/100 ⌋   VAT — SUM FIRST, THEN TRUNCATE
Os  = Ks + Is                           مبلغ کل قلم              (tsstam)
```

- **One line per article.** The gold quartet (`consfee`/`bros`/`spro`/`tcpbs`) is
  **mandatory on EVERY line** of الگوی سوم — zeros are fine, absence is not.
  There is no "put the fee on its own line" split; the org refuses it.
- **The exemption lives in the stuffid**, exactly as the research said: the gold
  line carries `vra = 0` and a zero-rate exempt شناسهٔ کالا, and `Ks` on that line
  is **non-zero** (it is the tax on the workmanship). `vam = 0` is *wrong*.
- **`Is` must include `TAs`.** Leaving the workmanship out of `adis` gives 0204301.

## Verdict table — every variant, in the order it was submitted

| # | Variant (one variable at a time) | taxid | Org verdict |
|---|---|---|---|
| control | single exempt line, trio, `vam` = ⌈۱۰٪×TAs⌉ = 543,934 | …9168B2 | ❌ `0204501` KS invalid |
| V1 | **two lines**: exempt gold (no trio) + taxable «خدمات طلاسازی» line @۱۰٪ | …9168C0 | ❌ `00052/00053/00054/00055` on **both** lines — اجرت/حق‌العمل/سود/TAS «خالی است»; plus `0204501` |
| V1b | two lines, trio on the gold line (`vam` 0) + taxable fee line | …9168D1 | ❌ `0204301` **IS** invalid on the gold line (trio missing from `adis`); trio «خالی» on line 2; `0204501` on both |
| V2 | single exempt line, trio, **`vam` = 0** | …9168E9 | ❌ `0204501` — and note **no** `0204301`: `adis = Es + TAs` was accepted |
| V5 | single exempt line, trio, **`vam` = ⌊۱۰٪×TAs⌋ = 543,933** | …9168F4 | ✅ **SUCCESS** |
| V6 | single exempt line, `vam` = ⌊۹٪×TAs⌋ = 489,540 | …916905 | ❌ `0204501` (rate is ۱۰٪, not ۹٪) |
| V7 | single exempt line, `vam` = ⌈۹٪×TAs⌉ = 489,541 | …916917 | ❌ `0204501` |
| V8 | **mixed** exempt+taxable, discount, non-zero حق‌العمل — Ks floored **per term** (520,000) | …916923 | ❌ `0204501` on line 2 |
| V9 | same invoice — Ks **summed then floored** (520,001) | …916936 | ✅ **SUCCESS** |
| P1H | **الگوی اول**, VAT half-up (100,001) — *what we shipped* | …916941 | ❌ `0204501` |
| P1F | الگوی اول, VAT truncated (100,000) | …916957 | ✅ **SUCCESS** |
| P2H | الگوی اول, fractional qty, `prdis` half-up (1,500,002) | …916978 | ❌ `0204101` **ES** invalid |
| P2F | الگوی اول, fractional qty, `prdis` truncated (1,500,001) | …916969 | ✅ **SUCCESS** |

### The two accepted payloads, verbatim

V5 — a plain gold sale (the research's own worked example, at the current ۱۰٪):

```json
{"header":{"taxid":"A2HP31050B5006AF9168F4","inno":"006AF9168F","indatim":1785110400000,
  "inty":1,"inp":3,"ins":1,"tins":"10320296185","tob":2,"bid":"14008430838",
  "tinb":"14008430838","tprdis":23598000,"tdis":0,"tadis":29037339,"tvam":543933,
  "todam":0,"tbill":29581272,"setm":2},
 "body":[{"sstid":"2001584175153","sstt":"شمش طلا ۱۰۰۰ گرمی","am":1,"fee":23598000,
  "prdis":23598000,"dis":0,"adis":29037339,"vra":0,"vam":543933,"tsstam":29581272,
  "consfee":3539700,"bros":0,"spro":1899639,"tcpbs":5439339}],"payments":[]}
```

V9 — a REAL goldsmith invoice: two articles, one exempt with a discount and one
taxable, non-zero حق‌العمل, and a Ks whose two terms both land on a half Rial:

```json
{"header":{"taxid":"A2HP31050B5006AF916936","inno":"006AF91693","indatim":1785110400000,
  "inty":1,"inp":3,"ins":1,"tins":"10320296185","tob":2,"bid":"14008430838",
  "tinb":"14008430838","tprdis":25000005,"tdis":1000000,"tadis":27750010,
  "tvam":875001,"todam":0,"tbill":28625011,"setm":2},
 "body":[
  {"sstid":"2710000044666","sstt":"النگو طلا ۱۸ عیار","am":2,"fee":10000000,
   "prdis":20000000,"dis":1000000,"adis":22550000,"vra":0,"vam":355000,
   "tsstam":22905000,"consfee":2500000,"bros":300000,"spro":750000,"tcpbs":3550000},
  {"sstid":"2710000050483","sstt":"پودر طلا آلیاژی","am":1,"fee":5000005,
   "prdis":5000005,"dis":0,"adis":5200010,"vra":10,"vam":520001,"tsstam":5720011,
   "consfee":200005,"bros":0,"spro":0,"tcpbs":200005}],"payments":[]}
```

---

## What changed in the code

One line, plus its consequences:

- `converter._rial` now quantizes with **`ROUND_DOWN`** instead of `ROUND_HALF_UP`.
  Everything downstream — الگوی اول, نوع دوم, پیمانکاری and طلا — inherits it,
  because they all go through `_rial`/`_rint`.
- `map_type1_pattern3` needed **no formula change at all**. It already summed the
  two Ks terms before quantizing (which V8/V9 proved is the right placement) and
  already computed `Is = Es + TAs − Gs`. Only the rounding was wrong.
- Tests: `tests/modules/moadian/test_rial_truncation.py` (new — pins the org's
  arithmetic with the sandbox taxids as citations) and the three gold tests that
  asserted half-up now assert the org's answer.

## Research-vs-reality note

| The research said | Reality (org, empirically) |
|---|---|
| `Ks = ((TAs × 10)/100) + ((Es × J)/100)` | ✅ correct — including that the `10` is a rate parameter, not a constant |
| `Is = Es + TAs − Gs` | ✅ correct, and **enforced** (0204301 when TAs is left out) |
| «معافیت اصل طلا … از طریق شناسه کالای معاف اعمال می‌شود» | ✅ correct |
| «اجزای مشمول با نرخ ۱۰٪ ثبت می‌شوند» — read as *a separate taxable line* | ❌ NO. The components are taxed **on the same line** via the quartet. A separate fee line is rejected outright (the quartet is mandatory per line) |
| ترازسامانه example prints ۴۸۹٬۵۴۰ where half-up gives ۴۸۹٬۵۴۱ — logged as a «1-ریال divergence, ours is right» | ❌ **the field source was right and we were wrong.** That single digit was the whole bug |

The lesson worth keeping: the divergence we had already written down *was* the
answer, filed as a footnote because it looked like a rounding nit. The sandbox
turned a footnote into a production bug fix.

## Impact beyond gold — a live bug, now closed

`0204501`/`0204101` would have hit **any ordinary invoice** whose VAT or line
amount fell on half a Rial: an odd unit price with a ۱۰٪ rate, or any fractional
quantity. Our demo/persona data uses round numbers, so every test invoice we ever
sent happened to divide evenly and the bug stayed invisible. It is closed now, and
`test_rial_truncation.py` keeps it closed.

## Still open (small, and honest)

- The **document** side still carries 4-decimal precision (`invoice_drafts._q4`,
  half-up) while the org record is whole-Rial truncated, so a PDF can print ۱ ریال
  more VAT than the tax record holds. Sub-Rial money in an IRR ledger is arguably
  wrong on its own, but changing it touches accounting/journals/reports — that is
  the founder's call, logged rather than done quietly.
- `todam`/`odam` (سایر وجوه قانونی, Ks2/Ks3) are still not modelled — zero in every
  packet. No goldsmith flow we support needs them yet.
