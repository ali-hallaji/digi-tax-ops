# MD-D Part 4 — Moadian Invoice Pattern (الگو) Assessment

**Purpose:** research-only assessment of ALL official Moadian invoice patterns (الگوهای صورتحساب)
so the founder can pick what to build next. Nothing here was implemented.

**Current support:** نوع اول (inty=1) + نوع دوم (inty=2), both with **الگوی اول (فروش, inp=1)** only —
the only two combos with `mapped=True` in the normalizer
(`app/modules/moadian/normalizer/patterns.py` L52–87 `("1","1")` and L229–236 `("2","1")`;
support flag derived in `app/modules/moadian/application/invoice_catalog.py` L74–78).

**Primary sources**
- `digi-tax-backend/app/modules/moadian/normalizer/patterns.py` (PATTERN_REQUIREMENTS L51–264)
- `digi-tax-backend/app/modules/moadian/application/invoice_catalog.py` (types/patterns matrix L23–71)
- Official spec **RC_IITP.IS_V7.8** (اردیبهشت ۱۴۰۵), `digi-tax-ops/docs/moadian/RC_IITP_IS_V7_8.pdf`, 112 pp.
  Key rule tables read directly: جدول ۱ «الگوهای صورتحساب» p.13 (full field-by-pattern matrix,
  اجباری/اختیاری/در شرایط خاص اجباری/خارج از الگو per field per الگو); جدول ۲ field→JSON key→header/body
  placement pp.17–21; جدول ۶ نوع p.26; **جدول ۹ الگو pp.29–30**; جدول ۱۰ موضوع pp.30–31;
  **جدول ۱۱ اطلاعات خریدار و فروشنده pp.31–34**. Per-field control tables: §7-10…§7-83, pp.34–90
  (table numbering rule verified: field table جدول N = section §7-(N−2), e.g. §7-12 billid = جدول ۱۴ p.36).
- Segments: `digi-tax-ops/docs/business_scope_freeze_v1.md` (Target Users table, L29–42) and
  `docs/product_master_blueprint_v4_2.md` §4.1.1 کاسب و صنف (L276–318: موبایل‌فروشی، سوپرمارکت،
  لوازم خانگی، خدماتی/تعمیرکار، کارگاه و پخش کوچک) and §4.1.2 شرکت کوچک/متوسط (L320–332: خدمات IT،
  **پیمانکار کوچک**، شرکت بازرگانی، فروش B2B، تولیدی کوچک).

---

## 1. Pattern-by-pattern table

Notes on columns:
- **Field spec in PDF?** — every pattern has a complete spec: جدول ۱ (p.13) marks each of the 99 fields
  as اجباری/اختیاری/در شرایط خاص اجباری/خارج از الگو **per pattern**, and each pattern-specific field has
  its own control table (§7-N, pp.34–90). So the answer is *yes* for all; the جدول/§ refs listed are the
  pattern-specific ones you'd implement from.
- **Extra fields** — beyond what الگوی اول already sends (patterns.py L58–85). JSON keys per جدول ۲ pp.17–21.
- **Effort**: S = header field(s) + validation only, reuses الگوی اول math · M = new body/line fields +
  modest math changes · L = new tax-math model or external data · XL = new domain model.

| inp | الگو (Persian name) | What it's for / who may use it | Field spec in PDF | Extra header/body fields vs الگوی اول | Extra data we don't model today | Effort | Merchant segments that need it | Relevance for a small-merchant SaaS |
|---|---|---|---|---|---|---|---|---|
| **1** | الگوی اول (فروش) | General sale — «قابل استفاده برای ثبت فروش کلیه فروشندگان کالا/خدمت» (جدول ۹ ردیف ۳, p.29) | Yes — جدول ۱ p.13; worked example پیوست ۸-۱/۸-۳ pp.91–93 | — (baseline) | — | **Done** (patterns.py L52–87, L229–236) | Everyone | — |
| **2** | الگوی دوم (فروش ارز) | FX sale — «مختص ثبت فروش ارز واحدهای صرافی و بانک‌های دارای مجوز مبادله ارز» (جدول ۹ ردیف ۴, p.29) | Yes — body: cfee میزان ارز جدول ۳۵ p.52 · cut نوع ارز جدول ۳۶ p.52 · exr نرخ برابری/نرخ فروش ارز جدول ۳۷ p.53 (rule changed in v7.8 — changelog p.2) · cpr نرخ خرید ارز §7-63 p.78 · sovat ماخذ VAT §7-64 p.79; buyer-identity rules جدول ۱۱ ردیف ۱۴–۱۶ p.33 | Body replaces normal line shape: `cut, cfee, exr, cpr, sovat` (patterns.py L93); buyer bid/گذرنامه rules for اتباع (جدول ۱۱ ر۱۵) | Currency-code list, buy/sell FX rates per line, FX-specific VAT base — none modeled | **L** — a different line model (currency, two rates), not a product variant | صرافی‌های مجاز، بانک‌ها | **Low** — licensed exchanges are a closed, regulated niche outside our اصناف/SME target; they run dedicated صرافی software |
| **3** | الگوی سوم (طلا، جواهر و پلاتین) | Gold/jewellery/platinum sales; VAT effectively rides on the *services* portion (اجرت/سود/حق‌العمل), not the metal value | Yes — consfee اجرت ساخت جدول ۴۶ p.64 · spro سود فروشنده جدول ۴۷ p.65 · bros حق‌العمل جدول ۴۸ p.66 · tcpbs جمع کل اجرت/حق‌العمل/سود جدول ۴۹ p.67 · cui عیار جدول ۶۳ p.77; «ثبت فیلد اجرت ساخت، سود فروشنده، حق‌العمل و جمع کل الزامی است» جدول ۹ ردیف ۵ p.29 | Body per line: `consfee, spro, bros, tcpbs` (required — patterns.py L102, L242) + `cui` عیار; VAT math shifts to the services base | Per-product gold attributes (عیار, وزن), per-line اجرت/سود/حق‌العمل amounts, changed VAT base — products/invoice lines don't carry these | **M/L** — line-model extension + one VAT-base rule; totals/header shape unchanged | **طلافروش، جواهرفروش** (a large, nationwide guild) | **High** — huge اصناف segment, legally forced onto Moadian, poorly served by generic tools; also valid in نوع دوم (retail walk-in, جدول ۹ ردیف ۲ p.29; patterns.py L237–245) which matches shop reality |
| **4** | الگوی چهارم (قرارداد پیمانکاری) | Contractor-contract invoices | Yes — crn شماره قرارداد پیمانکاری: جدول ۱۱ (field row p.32, حداکثر ۱۲, رشته عددی; rules ردیف ۸–۹ p.32: الزامی و باید با شماره قرارداد موجود در کارپوشه یکسان باشد) | Header: `crn` only (patterns.py L111–120); body identical to الگوی اول | A contract-number on the invoice + the merchant must have registered the contract in their کارپوشه (we validate format only; the org matches it) | **S** — one required header field + form field + honest error copy | **پیمانکار کوچک**, ساختمانی/تاسیساتی, service contractors billing legal buyers | **High/Med** — «پیمانکار کوچک» is an explicit target persona (blueprint §4.1.2 L322); near-zero build cost |
| **5** | الگوی پنجم (قبوض خدماتی) | Utility/service bills (water, power, gas, telecom) issued by بهره‌بردار operators | Yes — billid شماره اشتراک/شناسه قبض جدول ۱۴ p.36; forced cash settle (روش تسویه جدول ۲۴ p.43, patterns.py L128–133); اصلاحی rule جدول ۱۰ ردیف ۵ p.30 | Header: `billid`; `setm` forced to 1 | Subscriber/bill-id ledger — a billing-operator concept | **S** technically | شرکت‌های آب/برق/گاز/مخابرات و بهره‌برداران قبوض | **Low** — issuers are utilities/telcos, not small merchants; not our market |
| **6** | الگوی ششم (بلیط هواپیما) | Air tickets — «مختص ثبت فروش شرکت‌های هواپیمایی و آژانس‌های مسافرتی صادرکننده بلیط هواپیما» (جدول ۹ ردیف ۶, p.29) | Yes — ft نوع پرواز (داخلی ۱/خارجی ۲) جدول ۱۱ p.31 + rules ردیف ۱۰–۱۳ p.33 (domestic → passenger identity; tax credit → buyer economic code; «مسافر و خریدار بلیط یکسان نیستند») · bpn گذرنامه جدول ۱۱ p.31 · tinc شماره اقتصادی آژانس §7-62 p.78 | Header: `ft` (+ conditional passenger bid/bpn, tinc) (patterns.py L141) | Passenger-vs-buyer split, flight type, passport numbers — not in our invoice model | **M** | آژانس‌های مسافرتی، شرکت‌های هواپیمایی | **Med/Low** — آژانس مسافرتی is a real guild niche, but most sell through GDS/charter systems that already issue; airlines are enterprise |
| **7** | الگوی هفتم (صادرات) | Exports; buyer info NOT required (جدول ۱۱ ردیف ۲ p.32); ins limited to اصلی/اصلاحی/ابطالی — no برگشت از فروش (جدول ۱۰ ردیف ۲ p.30; patterns.py L149) | Yes — scln پروانه گمرکی (حداکثر ۱۴) + scc کد گمرک (۵) جدول ۱۱ p.32 · cdcn/cdcd شماره/تاریخ کوتاژ اظهارنامه گمرکی جدول ۱۲ p.34 / جدول ۱۳ p.35 (zero-VAT exemption is matched 1:1 against the کوتاژ — جدول ۱۲ ردیف ۲ p.34) · body ssrv/sscv ارزش ریالی/ارزی کالا جدول ۳۸ p.54/جدول ۳۹ p.55 · nw وزن خالص جدول ۳۳ p.51 · totals tonw/torv/tocv جدول ۲۱–۲۳ pp.40–42; date rule indatim ≥ تاریخ کوتاژ (جدول ۴ ردیف ۸ p.24; جدول ۱۰ ردیف ۶ p.30) | Header: `scln, scc` (+ cdcn/cdcd) — buyer block dropped; body: `ssrv, sscv, nw` (patterns.py L153–163); tbill = مجموع ارزش ریالی + tvam + todam (جدول ۲۲ ردیف ۳ p.41) | Customs declaration (کوتاژ) numbers/dates, per-line currency value + net weight, zero-rate VAT path | **M/L** — new required refs + per-line FX value/weight; simpler on the buyer side (none) | شرکت‌های بازرگانی/صادرکننده, تولیدی‌های صادراتی | **Med** — «شرکت بازرگانی» is a named SME persona (blueprint §4.1.2 L326); export zero-rating is high-value for them, but the sub-segment is smaller than اصناف |
| **8** | الگوی هشتم (بارنامه) | Waybills — «مختص شرکت‌های متولی حمل و نقل (باربری)» جاده‌ای/ریلی/دریایی/هوایی (جدول ۹ ردیف ۸ p.29; جدول ۱۱ ردیف ۱۸–۱۹ p.33: seller AND requester economic codes required) | Yes — lno/lrno شماره بارنامه/مرجع §7-65/66 p.80 · ocu/oci/dco/dci کشور/شهر مبدا و مقصد §7-67…70 pp.81–82 (+ coding tables پیوست ۸-۴/۸-۵ pp.94–111) · tid/rid فرستنده/گیرنده §7-71/72 p.83 · lt نوع بارنامه/حمل §7-73 p.84 · cno ناوگان §7-74 p.84 · did راننده §7-75 p.85 · sg/sgid/sgt کالاهای حمل شده §7-76…78 pp.85–86 | Large new header block: `tid, rid, lno, cno, did` + origin/destination + cargo sub-array (patterns.py L172–184 lists the required core) | Fleet numbers, driver national ids, sender/receiver parties, city/country code tables, cargo manifest — an entire logistics domain | **XL** | شرکت‌های باربری و حمل‌ونقل | **Low** — باربری firms use dedicated بارنامه systems tied to transport-ministry issuance; far outside our invoice-first product |
| **9** | الگوی نهم (فرآورده‌های نفتی) | «صرفاً توسط شرکت ملی پالایش و پخش… و شرکت ملی پخش فرآورده‌های نفتی ایران» (جدول ۱۱ ردیف ۲۰ p.33) | Yes — no extra fields beyond الگوی اول shape (patterns.py L193) | None | None | S (moot) | Two state oil companies only | **None** — legally unusable by any customer of ours |
| **11** | الگوی یازدهم (بورس کالا) | Sales via commodity-securities exchange (گواهی سپرده) — جدول ۹ ردیف ۹ p.30; buyer info not needed (جدول ۱۱ ردیف ۱۷ p.33); cash settle; اصلاحی reference restricted (جدول ۱۰ ردیف ۷ pp.30–31); ins 1–3 | Yes — asn/asd شماره/تاریخ اعلامیه فروش بورس §7-79/80 p.87; date rule جدول ۴ ردیف ۱۱ p.24 | Header: `asn, asd`; forced setm=1 (patterns.py L200–206) | Exchange sale-announcement refs; cross-check with بورس اعلامیه (جدول ۱ underlined note p.11: mismatch ⇒ lose exemption, می‌تواند اعتراض ثبت کند) | **M** | فروشندگان از طریق بورس کالا (تولیدی‌های بزرگ) | **Low** — exchange sellers are mid/large industry with broker-side tooling |
| **13** | الگوی سیزدهم (خدمات بیمه‌ای) | Insurance-service sales; also valid in نوع دوم (جدول ۹ ردیف ۲ p.29) | Yes — in شناسه یکتای بیمه‌نامه §7-81 p.88 · an شناسه یکتای الحاقیه §7-82 p.88 | Header: `in` (+ optional `an`) (patterns.py L212) | Central-insurance unique policy ids | **S/M** | شرکت‌های بیمه (صادرکننده اصلی) | **Low** — the *insurer* issues these, not نمایندگی‌های کوچک; insurers are enterprise with core systems |
| **14** | الگوی چهاردهم (فروش زنجیره‌ای) | Chain sales by persons on the تبصره ۵ ماده ۱۷ VAT-law list; seller (and for اصلی the buyer too) must be on the official chain list (جدول ۱۱ ردیف ۲۱–۲۴ pp.33–34) | Yes — vba مبلغ پایه مالیات بر ارزش افزوده §7-83 p.90 (body field, جدول ۲ ردیف ۹۹ p.21) | Body: `vba` (patterns.py L222) | Membership in the official chain list; alternate VAT base per line | **M** (S mechanically, but gated on a list we can't verify) | اشخاص زنجیره تبصره ۵ ماده ۱۷ (distribution chains) | **Low** — closed regulated list, not general merchants |

**نوع سوم (inty=3)** carries **no** کالا/خدمت pattern at all (invoice_catalog.py L67–71 `TYPE_PATTERNS[3] = []`) — see §3.

---

## 2. Ranked recommendation (build order)

Ranking = (segment demand among OUR target users — blueprint §4.1 اصناف + SME) × (effort). All efforts
assume the existing (1,1)/(2,1) mapper, taxid generator, and validator are reused; each new pattern is
mostly a `PATTERN_REQUIREMENTS` entry flipped to `mapped=True` plus its mapper, form fields, and tests.

### Build — in this order

**1. الگوی سوم — طلا، جواهر و پلاتین (inp=3), نوع اول AND نوع دوم — effort M/L.**
The single biggest underserved guild segment: طلافروش/جواهرفروش shops are numerous nationwide, under
heavy legal pressure to issue via Moadian, and generic invoicing tools can't express اجرت/سود/حق‌العمل
line math (VAT rides on the services portion, not the metal — جدول ۴۶–۴۹ pp.64–67). Because the org
also allows it in نوع دوم (walk-in retail, جدول ۹ ردیف ۲ p.29), it matches how a gold shop actually
sells, and our نوع دوم mapper skeleton (patterns.py L407–467) is directly reusable. This is the one
pattern that could *acquire a segment*, not just serve existing users.

**2. الگوی چهارم — قرارداد پیمانکاری (inp=4) — effort S.**
The cheapest real win: exactly one extra required header field (`crn`, ≤12 digits, جدول ۱۱ p.32) with
the rule that it must match the contract registered in the merchant's کارپوشه (ردیف ۸–۹ p.32) — we
validate format and pass through. «پیمانکار کوچک» is an explicitly named target persona (blueprint
§4.1.2 L322), and service businesses billing legal buyers under contract are squarely inside our
اصناف/SME base. Roughly a day-scale mapper change plus a contract-number field on the invoice form.

**3. الگوی هفتم — صادرات (inp=7) — effort M/L.**
«شرکت بازرگانی» is a named SME persona (blueprint §4.1.2 L326) and export zero-rating is where Moadian
correctness has direct money value (the zero-VAT exemption is matched 1:1 against the کوتاژ — جدول ۱۲
ردیف ۲ p.34). Needs customs refs (scln/scc/cdcn/cdcd), per-line ریالی/ارزی value + net weight, the
`tbill = torv + tvam + todam` total rule (جدول ۲۲ ردیف ۳ p.41), and ins limited to 1–3 — but NO buyer
identity at all (جدول ۱۱ ردیف ۲ p.32), which removes the hardest part of الگوی اول. Build after 1–2,
when a real exporting customer asks.

**4. (Optional, demand-driven) الگوی ششم — بلیط هواپیما (inp=6) — effort M.**
آژانس مسافرتی is a genuine guild niche and the fields are modest (`ft`, passenger identity, tinc), but
most agencies sell through charter/GDS platforms that issue for them, and the passenger≠buyer rules
(جدول ۱۱ ردیف ۱۰–۱۳ p.33) add UX complexity. Only build against a concrete paying-customer request.

### Do NOT build (and why)

- **الگوی دوم فروش ارز (inp=2)** — restricted to licensed صرافی/banks (جدول ۹ ردیف ۴ p.29); a closed
  regulated niche with dedicated software; needs a whole FX line model (cut/cfee/exr/cpr/sovat) for
  customers we will never have. patterns.py L88–95 already gives them an honest "unsupported" error.
- **الگوی پنجم قبوض خدماتی (inp=5)** — issuers are utilities/telcos (بهره‌بردار), not merchants. L124–134.
- **الگوی هشتم بارنامه (inp=8)** — XL logistics domain (fleet, driver, cargo, city/country code tables
  pp.80–86, 94–111) restricted to باربری companies (جدول ۱۱ ردیف ۱۸–۱۹ p.33). Wrong product for us.
- **الگوی نهم فرآورده‌های نفتی (inp=9)** — legally usable by exactly two state companies (جدول ۱۱
  ردیف ۲۰ p.33). Never.
- **الگوی یازدهم بورس کالا (inp=11)** — exchange-mediated sellers with broker tooling; mismatch-with-
  اعلامیه risk (p.11) makes half-support dangerous. L197–207.
- **الگوی سیزدهم بیمه (inp=13)** — issued by insurance *companies* (enterprise core systems), not the
  small نمایندگی‌ها who might use us. L208–215.
- **الگوی چهاردهم فروش زنجیره‌ای (inp=14)** — gated on the official تبصره ۵ ماده ۱۷ list (جدول ۱۱
  ردیف ۲۱–۲۴ pp.33–34) that we cannot verify; mechanically small (`vba`) but wrong audience. L216–225.

---

## 3. Already supported + what نوع سوم would take

**Already supported (do not rebuild):**
- **(نوع اول، الگوی اول)** — full mapper `map_type1_pattern1` (patterns.py L337–404): taxid generation,
  ins/irtaxid rules (جدول ۸ p.28), buyer tob/bid/tinb logic, totals, setm/cap/insp (§7-23/24 pp.44–45).
- **(نوع دوم، الگوی اول)** — `map_type2_pattern1` (patterns.py L407–467): same body math via the shared
  helper `_body_and_totals` (L296–334), buyer identity omitted, ins limited to 1–3, `setm` omitted
  (org warning 14028, verified live — L229–236, L461–463).
- Type selection is automatic from the buyer (`invoice_type_from_customer`, L286–293) — keep this rule
  for any new pattern.

**نوع سوم (inty=3):** per §3-3 p.11 and invoice_catalog.py L41–47, it is the **payment receipt** of a
bank POS/گیت‌وی accepted as a پایانه فروشگاهی — only the payment amount + acceptor identifiers
(شماره سوییچ `iinn`, پذیرنده `acn`, پایانه `trmn`, پیگیری `trn`, تاریخ/زمان — the اطلاعات پرداخت block,
جدول ۲ ردیف ۶۸–۷۶ p.20, field tables جدول ۵۴–۶۲ pp.72–76), plus a taxid; **no کالا/خدمت body, no الگو**
(`TYPE_PATTERNS[3] = []`, invoice_catalog.py L67–71), and no buyer tax credit. Building it would mean
ingesting PSP/switch receipt data rather than extending the invoice form — a different data pipeline
(likely a PSP integration), not a mapper variant. Out of scope for the invoice product until there is a
POS-receipt story; the catalog already presents it honestly as coming_soon.

---

*Research-only document. No code, schema, or catalog flags were changed.*
