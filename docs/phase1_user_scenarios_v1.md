# Phase-1 User-Scenario Catalog — Digi Invoice (v1, pending founder review)

Date: 2026-07-04 · Status: **REVIEWED — founder decisions folded in (2026-07-04); build not started**
Parent plan: `phase1_accounting_plan_v1.md` (approved).

## Decisions locked (founder answers + adopted recommendations)

| # | Decision |
|---|---|
| 1 | Inventory: **OUT** (phase 2) — returns and documents are financial-only |
| 2 | Cheque: **MINIMAL** — receive/pay + deposit + clear/bounce; NO صیاد registration/inquiry in phase 1 |
| 3 | Purchases' self-entered `paid_amount`: **migrate into real payment rows** (single source of truth) |
| 4 | Treasury surface name: **«دریافت و پرداخت»** — one merged page (transactions page folds in) |
| 5 | Dead `/app/tax/*` mock tree + orphan mock components: **delete** |
| 6 | Accountant layer: phase 2 (direction: owner-visible «نمای حسابدار»); phase 1 only records complete events |
| 7 | Roles: minimal matrix in phase 1 — **viewer = read-only everywhere; staff = full daily operations but no delete-of-finalized, no settings/members; owner/admin = everything** |
| 8 | Subscriptions/paywall: **post-launch phase 2** |
| 9 | Settlement window on finalize: **skippable** — skipping = full نسیه, one tap |
| 10 | S1-10: cancel-finalized is **BLOCKED** while linked receipts/cheques exist — guided message «این فاکتور دریافت ثبت‌شده دارد؛ ابتدا دریافت را حذف یا منتقل کنید». Money records are never auto-unlinked |
| 11 | S2-03: per-party receipts auto-allocate **oldest-first (FIFO)**; the per-invoice mode of the same dialog IS the manual override — no extra allocation UI |
| 12 | S5-03: refund toggle defaults **OFF** (return credits the customer balance); toggle label «پول را پس دادید؟» |
| 13 | Cheques do **NOT** count toward settlement until وصول — invoice stays تسویه جزئی/نسیه with hint «در انتظار وصول چک» |
| 14 | Expenses take an account picker, **default صندوق** (one untouched field for old muscle memory) |
| 15 | Pre-phase-1 payment rows get **account backfilled to صندوق** in the linkage migration (noted in the migration body) |
| 16 | **Settlement dialog is PROGRESSIVE** (design constraint, ui-ux-pro-max owns it): default face = ONE question «چقدر دریافت کردید؟» with نقد preselected; کارت/انتقال/چک/تقسیم live behind «روش‌های بیشتر». One-dialog architecture unchanged — only its default state is as simple as a cash sale |

---

## Locked Persian terminology (single source — no synonyms anywhere in UI)

| Concept | Locked term | Never use |
|---|---|---|
| Sale invoice | فاکتور فروش | صورتحساب (reserved for official/Moadian contexts), سند فروش |
| Proforma | پیش‌فاکتور | پیش‌نویس فروش |
| Internal record | سند داخلی | فاکتور شخصی |
| Official (tax-reportable) | فاکتور رسمی | — |
| Finalize | نهایی‌سازی | قطعی کردن، ثبت نهایی |
| Money in | دریافت | وصولی، ورودی |
| Money out | پرداخت | خروجی |
| Treasury page | دریافت و پرداخت | خزانه‌داری، تراکنش‌ها |
| Settlement window (sale) | دریافت وجه | تسویه‌حساب |
| Settlement window (purchase) | پرداخت وجه | — |
| Credit remainder | نسیه | اعتباری، بدهی باز |
| Settlement statuses | تسویه‌شده / تسویه جزئی / نسیه | پرداخت‌شده (kept only for purchases' وضعیت پرداخت) |
| Received / issued cheque | چک دریافتی / چک پرداختی | چک ورودی/خروجی |
| Cheque states | در جریان → واگذار به بانک → وصول‌شده / برگشتی | پاس‌شده |
| Cash box | صندوق | نقد در دست |
| Bank account | حساب بانکی | — |
| POS | کارت‌خوان | پوز، POS |
| Inter-account transfer | جابه‌جایی بین حساب‌ها | انتقال داخلی |
| Opening balance | موجودی اولیه | مانده افتتاحیه (accounting jargon) |
| Return docs | برگشت از فروش / برگشت از خرید | مرجوعی (allowed as helper word in body copy only) |
| Customer credit (overpay/advance) | بیعانه / اعتبار مشتری | پیش‌دریافت (jargon) |
| Who owes me / whom I owe | طلب شما / بدهی شما | بدهکاران/بستانکاران (report title only: «بدهکاران و بستانکاران») |
| Due date | سررسید | موعد |
| Buy / expense | خرید / هزینه | — |
| Vendor | تأمین‌کننده | فروشنده |
| Walk-in customer | مشتری گذری | مشتری متفرقه |
| Party opening balance (from paper books) | مانده اولیه | مانده اول دوره، افتتاحیه |
| Settlement methods expander | روش‌های بیشتر | + روش دیگر |

Actors: **Owner** (مالک), **Admin**, **Staff** (کارمند), **Viewer** (مشاهده‌گر), **SysAdmin** (پنل ادمین). Per decision 7: scenarios marked Staff+ = owner/admin/staff; Owner/Admin = those two only.

Screen registry (the ONLY phase-1 surfaces; every scenario maps onto these — anything else is a duplicate):
`DASH` داشبورد · `INV-L` فهرست فاکتورها · `INV-N` صدور فاکتور · `INV-D` جزئیات فاکتور · `SETL-R` دیالوگ دریافت وجه · `SETL-P` دیالوگ پرداخت وجه · `PAY` دریافت و پرداخت (merged) · `CHQ` چک‌ها · `PUR` خرید و هزینه · `ACC` حساب‌های من · `RPT` گزارش‌ها · `CUS` مشتریان · `VEN` تأمین‌کنندگان · `PRD` کالا/خدمات · `SET` تنظیمات · `MEM` کاربران و دسترسی‌ها · `BIZ` کسب‌وکارها

---

## Group 1 — فروش (Selling)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه (hidden) | End-state merchant sees | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S1-01 | فروش نقدی کامل | Staff+ | «جنس فروختم، پول نقد گرفتم» | INV-N → lines → «نهایی‌سازی» → SETL-R: نقد = کل مبلغ → «ثبت دریافت» | finalize event; payment row (method نقد, account صندوق, invoice_id set); receivable net 0; event log | فاکتور با پیل **تسویه‌شده**؛ موجودی صندوق +X در DASH | SETL-R is THE only settlement UI — never a second dialog on PAY |
| S1-02 | فروش با کارت | Staff+ | «با کارت‌خوان کشید» | Same, row کارت + انتخاب کارت‌خوان | payment row → mapped حساب بانکی | تسویه‌شده؛ موجودی بانک +X | POS is a mapping on ACC, not a new account type UI |
| S1-03 | فروش با انتقال بانکی | Staff+ | «به حسابم واریز کرد» | Same, row انتقال + حساب مقصد | payment row → bank | تسویه‌شده | — |
| S1-04 | فروش با چک | Staff+ | «چک گرفتم» | SETL-R row چک: مبلغ، بانک، سررسید → «ثبت» | **cheque entity (دریافتی، در جریان)، NO payment row yet**; receivable stays until وصول | فاکتور: **تسویه جزئی/نسیه** + hint «۱ چک در جریان»؛ چک در CHQ | cheque creation ONLY via SETL-R or CHQ — same form component |
| S1-05 | فروش نسیه کامل | Staff+ | «بعداً حساب می‌کنیم» | INV-N → «نهایی‌سازی» → SETL-R → «بعداً تسویه می‌کنم» (skip, decision 9) | finalize; no payment; receivable +X | پیل **نسیه**؛ CUS shows طلب شما +X | skip path must NOT open PAY — one tap out |
| S1-06 | فروش ترکیبی | Staff+ | «نصف نقد، یه چک، بقیه نسیه» | SETL-R: چند ردیف + خط زندهٔ «باقی‌مانده به‌صورت نسیه: …» → «ثبت دریافت» | N payment rows + cheque entities, one shared settlement_group ref; remainder untouched receivable | پیل تسویه جزئی + breakdown روی INV-D | live remainder = computed client-side display only; server is truth |
| S1-07 | پیش‌فاکتور → فاکتور | Staff+ | «اول استعلام، بعد قطعی» | INV-N type پیش‌فاکتور → share PDF → later INV-D «تبدیل به فاکتور فروش» → نهایی‌سازی | type conversion event; no financial effect until finalize | فاکتور نهایی از دل پیش‌فاکتور، بدون دوباره‌کاری | conversion happens IN INV-D — no separate «تبدیل» page |
| S1-08 | فاکتور خدمات | Staff+ | «خدمت انجام دادم» | INV-N with service lines (or free lines) | identical pipeline — service is a line property, not a doc type | مثل هر فاکتور | NO separate «فاکتور خدمات» menu/type |
| S1-09 | ویرایش پیش از نهایی‌سازی | Staff+ | «اشتباه زدم» | INV-D (status پیش‌نویس) → edit lines/header → save | draft mutation only | totals recomputed live | editing locked after finalize — no parallel edit surface |
| S1-10 | ابطال فاکتور نهایی‌شده | Owner/Admin | «معامله به هم خورد» | INV-D → «ابطال فاکتور» → confirm | **blocked if linked دریافت/چک در جریان exists** → friendly msg «اول دریافت‌های این فاکتور را حذف کنید»; else cancel event, receivable −X | وضعیت باطل‌شده؛ طلب اصلاح شد | cancellation ≠ برگشت از فروش — copy must distinguish (ابطال = never happened; برگشت = goods came back) |
| S1-11 | سند داخلی | Staff+ | «برای خودم ثبت کنم» | INV-N type سند داخلی | same pipeline, excluded from official surfaces | در فهرست با بج «داخلی» | — |
| S1-12 | چاپ/PDF | Staff+ | «پرینت بده مشتری» | INV-D → «دریافت PDF» / چاپ | existing renderer; amounts always ریال on official docs | PDF ذخیره/چاپ شد | keep the ONE existing print pipeline |
| S1-13 | فروش به مشتری گذری | Staff+ | «مشتری رهگذر است، ثبتش نمی‌کنم» | INV-N **بدون انتخاب مشتری** → نهایی‌سازی → SETL-R | invoice with `customer_id NULL` (core supports it); no receivable is possible without a party → **ردیف نسیه hidden; full settlement required to finalize** (otherwise stays پیش‌نویس with friendly hint) | فاکتور تسویه‌شده بدون مشتری | walk-in = the SAME INV-N flow — no «فروش سریع» page (dead `new-sale-sheet` stays dead) |

## Group 2 — وصول مطالبات (Getting paid later)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S2-01 | دریافت برای فاکتور مشخص | Staff+ | «بابت اون فاکتور پول داد» | INV-D → «ثبت دریافت» → SETL-R (pre-linked to this invoice) | payment row with invoice_id; status derived | پیل فاکتور → تسویه‌شده/جزئی | SAME SETL-R dialog as at-finalize — one component |
| S2-02 | دریافت جزئی سپس تکمیل | Staff+ | «قسط اول را داد» (colloquial; NOT the اقساط feature) | S2-01 twice | two payment rows, cumulative derivation | جزئی → تسویه‌شده | no schedule UI — that's phase-2 اقساط |
| S2-03 | تسویه از صفحه دریافت و پرداخت | Staff+ | «فلانی کل بدهی‌اش را داد» | PAY → کارت «تسویه‌های باز» مشتری → «ثبت دریافت» → SETL-R (party mode) | **auto-allocation oldest-invoice-first** across open invoices; overflow → اعتبار مشتری | کارت از فهرست باز حذف؛ فاکتورها تسویه شدند | party-mode and invoice-mode are ONE dialog with a pre-selection difference |
| S2-04 | دریافت بیش از بدهی / بیعانه | Staff+ | «بیشتر داد بمونه حسابش» | S2-03 with amount > طلب → confirm «مازاد به‌عنوان بیعانه ذخیره شود؟» | unallocated payment remainder = credit; aggregate طلب floors at 0, credit tracked | CUS نشان می‌دهد «بیعانه: X» | credit is data + display only in phase 1; auto-apply UX = phase 2 |
| S2-05 | بیعانه قبل از فاکتور | Staff+ | «پیش‌پرداخت گرفتم هنوز فاکتور نزدم» | PAY → «ثبت دریافت» بدون فاکتور (party only) | unallocated payment (invoice_id NULL) — the prepayment model from the plan | «بیعانه» روی مشتری | NOT a new doc type — it's an unallocated دریافت |
| S2-06 | اصلاح/حذف دریافت/پرداخت اشتباه | Owner/Admin | «مبلغ را اشتباه زدم» (P0 — daily fat-finger) | PAY → history → ویرایش/حذف → confirm — **both directions** (دریافت و پرداخت) | update/delete payment row; re-derive invoice/purchase status + party balances + account balance. **Rows created by cheque وصول are locked — corrected only via the cheque itself** (keeps cheque↔money consistent) | اعداد همه‌جا برگشتند | edit lives ONLY in PAY history (not on INV-D/PUR) |

## Group 3 — چک‌ها (Cheques)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S3-01 | دریافت چک از مشتری | Staff+ | «چک داد» | SETL-R row چک (S1-04) **یا** CHQ → «ثبت چک دریافتی» (party + optional invoice link) | cheque entity در جریان; no money movement | چک در تب دریافتی، مرتب بر سررسید | ONE cheque form, two entry points |
| S3-02 | واگذاری چک به بانک | Staff+ | «بردم بانک گذاشتم» | CHQ → کارت چک → «به بانک سپردم» → انتخاب حساب | state → واگذار به بانک (target account stored); still no money | پیل «واگذار به بانک» | state transitions are buttons on the cheque card — no separate workflow page |
| S3-03 | وصول چک | Staff+ | «چک پاس شد» | CHQ → «وصول شد» | state → وصول‌شده; **payment row created NOW** (account = deposit bank, invoice link inherited); receivable/settlement re-derived | موجودی بانک +X؛ فاکتور مرتبط تسویه شد | the ONLY place a cheque becomes money — prevents double-count with PAY |
| S3-04 | برگشت چک دریافتی | Staff+ | «چک برگشت خورد» | CHQ → «برگشت خورد» | state → برگشتی; no payment ever created (nothing to reverse); dashboard alert event | پیل قرمزِ آرام «برگشتی»؛ DASH هشدار؛ طلب همچنان باقی | bounce ≠ delete — history stays; no manual receivable fix needed |
| S3-05 | پرداخت به تأمین‌کننده با چک | Staff+ | «به فروشنده چک دادم» | SETL-P row چک **یا** CHQ → «ثبت چک پرداختی» | issued cheque در جریان; vendor بدهی unchanged until وصول | چک در تب پرداختی | mirror of S3-01 — same component, direction flag |
| S3-06 | وصول چک پرداختی | Staff+ | «چکم پاس شد» | CHQ → تب پرداختی → «وصول شد» | payment row OUT of the cheque's bank account (purchase/party link inherited); vendor بدهی re-derived | موجودی بانک −X؛ بدهی تأمین‌کننده صاف شد | — |
| S3-07 | چک‌های نزدیک سررسید | Any | «این هفته چی سررسید داره؟» | DASH strip «چک‌های نزدیک سررسید» → CHQ filtered | read query (due within N days, در جریان/واگذار) | فهرست مرتب + رنگ سررسید گذشته | strip links INTO CHQ — no mini-list duplicate with its own logic |
| S3-08 | ویرایش جزئیات چک | Staff+ | «سررسید را اشتباه زدم» | CHQ → کارت → ویرایش (only while در جریان) | field update; locked after واگذاری | اصلاح شد | — |
| S3-09 | برگشت چک پرداختی ما | Staff+ | «چک خودم برگشت خورد» (payable-side bounce) | CHQ → تب پرداختی → «برگشت خورد» | state برگشتی; NO money ever moved; vendor بدهی remains; **prominent-but-calm alert** (چک برگشتیِ صادرشده پیامد قانونی دارد — پیگیری فوری) | پیل برگشتی + هشدار در DASH؛ بدهی همچنان باقی | payable-side bounce reuses the SAME transition UI as received-side (S3-04) — one component, direction-aware copy |

## Group 4 — خرید و پرداخت (Buying & paying)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S4-01 | خرید با اقلام | Staff+ | «جنس خریدم، ریز اقلام دارم» | PUR → «ثبت خرید» → اقلام | purchase + lines (existing); بدهی تأمین‌کننده derived | خرید ثبت شد؛ VEN بدهی +X | — |
| S4-02 | خرید مبلغ کلی | Staff+ | «فقط مبلغ کل را دارم» | PUR → «ثبت خرید» → مبلغ کل | lump-sum purchase (existing) | همان | lump-sum vs lines = one form with a toggle (existing) — keep |
| S4-03 | پرداخت هنگام خرید | Staff+ | «همان‌جا حساب کردم» | after save → SETL-P: نقد/انتقال/چک، باقی‌مانده نسیه | payment rows with purchase_id (**replaces self-entered paid_amount — decision 3**) | خرید با وضعیت پرداخت‌شده/جزئی | SETL-P mirrors SETL-R — shared internals, mirrored labels |
| S4-04 | خرید نسیه، پرداخت بعدی | Staff+ | «سر ماه تسویه می‌کنم» | skip SETL-P; later PAY → کارت تأمین‌کننده → «ثبت پرداخت» | unpaid purchase; later payment allocated oldest-first | بدهی شما صفر شد | party-mode SETL-P — same dialog |
| S4-05 | پرداخت جزئی به تأمین‌کننده | Staff+ | «نصفش را دادم» | S4-04 with partial amount | partial allocation; purchase جزئی | وضعیت جزئی | — |
| S4-06 | ثبت هزینه | Staff+ | «قبض/اجاره دادم» | PUR tab هزینه → «ثبت هزینه» + **انتخاب حساب (پیش‌فرض صندوق)** | expense row + account balance −X (new: account link) | هزینه ثبت؛ موجودی حساب کم شد | expense stays a PUR tab — NOT a new page, NOT in PAY |
| S4-07 | اصلاح/حذف خرید | Owner/Admin | «اشتباه بود» | PUR → ویرایش/حذف → confirm | existing recompute; delete blocked if linked payments exist (same rule as S1-10) | اعداد اصلاح شد | — |

## Group 5 — برگشت‌ها (Returns)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S5-01 | برگشت از فروش کامل | Staff+ | «مشتری همه را پس آورد» | INV-D (نهایی) → «برگشت از فروش» → همه اقلام → ثبت | return doc referencing invoice; receivable −X (or credit if already settled); printable | سند برگشت با شماره؛ طلب/اعتبار اصلاح شد | return is an ACTION on INV-D + filter on INV-L — no «برگشت‌ها» menu |
| S5-02 | برگشت از فروش جزئی | Staff+ | «یک قلم را پس داد» | same, select lines/qty | partial return doc | همان | — |
| S5-03 | برگشت با استرداد وجه | Staff+ | «پولش را پس دادم» | inside return flow: toggle «استرداد وجه» → روش + حساب | return doc + refund payment row (money out, linked to return) | موجودی −X؛ حساب مشتری صاف | refund uses the SETL machinery (negative direction) — no third dialog |
| S5-04 | برگشت از خرید | Staff+ | «جنس معیوب را پس فرستادم» | PUR → خرید → «برگشت از خرید» | mirror of S5-01 on purchases; بدهی −X | سند برگشت خرید | — |
| S5-05 | برگشت خرید با دریافت وجه | Staff+ | «فروشنده پولم را برگرداند» | toggle «دریافت وجه» در همان flow | return + refund payment row (money in) | موجودی +X | — |

## Group 6 — خزانه (Treasury)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S6-01 | افزودن حساب بانکی | Owner/Admin | «حساب بانکی‌ام را اضافه کنم» | ACC → «افزودن حساب» (نام بانک + ۴ رقم آخر + موجودی اولیه) | account entity; opening balance = plain field, not a journal concept | کارت حساب با موجودی | ACC is the only account CRUD; SETL dialogs only *pick* accounts |
| S6-02 | مشاهده موجودی‌ها | Any | «چقدر پول کجاست؟» | ACC (و خلاصه در DASH) | balance = opening + Σ signed payments + transfers | کارت‌ها با موجودی زنده | DASH shows the same computed figures — one backend source |
| S6-03 | جابه‌جایی بین حساب‌ها | Staff+ | «پول صندوق را بردم بانک» | ACC → «جابه‌جایی بین حساب‌ها» (مبدأ/مقصد/مبلغ) | transfer row (paired movement, no party) | هر دو موجودی به‌روز | transfer is NOT a payment — must not appear as دریافت/پرداخت in PAY history |
| S6-04 | اتصال کارت‌خوان | Owner/Admin | «کارت‌خوان به کدام حساب؟» | ACC → روی حساب → «کارت‌خوان دارد» | POS flag/mapping on bank account | ردیف کارت در SETL-R مقصدش معلوم است | no separate POS entity/page |
| S6-05 | اصلاح موجودی اولیه | Owner/Admin | «موجودی اولش را غلط زدم» | ACC → ویرایش حساب | opening-balance update event (kept in history) | موجودی اصلاح شد | — |

### Group 6b — اول دوره: کوچ از دفتر کاغذی (opening balances — Holoo/Sepidar treat this as a full chapter)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S6-06 | مانده اولیه مشتری | Owner/Admin | «از دفتر قبلی، فلانی از قبل بدهکار است» | CUS → مشتری → فیلد «مانده اولیه (طلب از قبل)» | `opening_balance` on customer feeds the receivable formula (= مانده اولیه + Σ فاکتورهای نهایی − Σ دریافت‌ها); **FIFO allocation treats it as the oldest item** so old debt clears first | «طلب شما» شامل بدهی قدیم؛ گزارش بدهکاران درست است از روز اول | a plain field on the customer — NOT an opening «سند افتتاحیه» document, NOT a fake invoice |
| S6-07 | مانده اولیه تأمین‌کننده | Owner/Admin | «به فلانی از قبل بدهکارم» | VEN → تأمین‌کننده → فیلد «مانده اولیه (بدهی از قبل)» | mirror on vendor payable formula; FIFO same rule | «بدهی شما» شامل قدیم | same rule — plain field, no document |

## Group 7 — دیدن حقیقت (Dashboard & reports)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S7-01 | داشبورد واقعی | Any | «اوضاع چطوره؟» | DASH: موجودی حساب‌ها، طلب شما، بدهی شما، فروش این ماه، چک‌های نزدیک سررسید | real aggregation endpoints replace sha256-seeded stubs | اعداد واقعی، لمس هر کارت → صفحه مربوط | every KPI deep-links to its owning page; no dead-end numbers |
| S7-02 | سود و زیان ساده | Owner/Admin | «این ماه سود کردم؟» | RPT → «سود و زیان ساده» (فروش − برگشت فروش − خرید − هزینه) | simple cash-basis P/L; NO ledger involved | یک عدد بزرگ + سه ردیف اجزا | formula documented once server-side; DASH «سود ماه» uses the SAME endpoint |
| S7-03 | گزارش فروش | Owner/Admin | «چی/به‌کی بیشتر فروختم؟» | RPT → «گزارش فروش» (بازه/مشتری/کالا) | aggregation over finalized invoices minus returns | جدول + یک نمودار ساده | — |
| S7-04 | بدهکاران و بستانکاران | Owner/Admin | «کی به من بدهکاره؟ من به کی؟» | RPT → «بدهکاران و بستانکاران» | party balances (already denormalized) + drill to docs | دو فهرست مرتب با جمع | same figures as CUS/VEN columns — one source |
| S7-05 | گزارش چک‌ها | Owner/Admin | «وضعیت چک‌هام» | RPT → «چک‌ها» (وضعیت/سررسید) | cheque query | فهرست فیلترشده | thin view over CHQ data — reuse list component |
| S7-06 | لایه حسابدار (آینده) | — | — | NO UI in phase 1 | phase 1 guarantees complete typed events (payments+allocation, cheque transitions, returns, transfers, opening balances) so phase-2 generates سند/دفاتر without data loss | — | never leak debit/credit into any merchant screen |

## Group 8 — دسترسی و تنظیمات (Access & housekeeping)

| ID | سناریو | Actor | Trigger | Flow → primary action | پشت صحنه | End-state | Duplicate-risk |
|---|---|---|---|---|---|---|---|
| S8-01 | دعوت کاربر | Owner/Admin | «فروشنده‌ام هم ثبت کند» | MEM → «افزودن کاربر» (mobile + نقش) | membership row; server-side 403 guard for non-admin callers | کاربر در فهرست | — |
| S8-02 | تغییر نقش | Owner/Admin | «دسترسی‌اش را کم/زیاد کنم» | MEM → کاربر → تغییر نقش | role update | نقش جدید | — |
| S8-03 | غیرفعال‌سازی کاربر | Owner/Admin | «دیگر با ما نیست» | MEM → «غیرفعال‌سازی» → confirm | soft revoke (is_active=false), sessions invalid on next check | بج غیرفعال | deactivate ≠ delete — history intact |
| S8-04 | تجربه نقش محدود | Staff / Viewer | staff می‌فروشد؛ viewer فقط می‌بیند | Staff: all daily ops, no settings/members/delete-finalized. Viewer: read-only everywhere (buttons hidden, server 403 backup) | role matrix per decision 7, enforced server-side | بدون گزینه‌های ممنوع — نه خطای قرمز | hide, don't disable-with-error; locked pattern (§8.4) |
| S8-05 | واحد نمایش ریال/تومان | Owner/Admin | «تومانی ببینم» | SET → «واحد نمایش مبالغ» (built, Stage A2) | display-only; canonical ریال | همه صفحات فوراً برمی‌گردند | — |
| S8-06 | چند کسب‌وکار | Owner | «مغازه دومم» | BIZ → انتخاب/ساخت | tenant switch (existing) | داده‌ها کاملاً جدا | — |
| S8-07 | بررسی ادمین سیستم | SysAdmin | تأیید پروفایل مالیاتی | /admin queue (existing) | approve/reject workflow | وضعیت مؤدی تغییر کرد | admin panel untouched by phase 1 except real data flows |

**Count: 55 scenarios.** (Founder's five additions verified: mistaken-payment edit was S2-06 → broadened to both directions + cheque-row lock; issued-cheque bounce split out as S3-09; partial return already existed as S5-02; walk-in sale added as S1-13; opening balances added as S6-06/S6-07.)

---

## Master user-journey map (build & UX order)

The merchant's real arc — each stage only uses screens introduced before it:

```
راه‌اندازی            S6-01..07 (ACC + اول دوره) ، S8-05..06   ← «پول‌هایم کجاست، از قبل کی بدهکار است»
      ↓
فروش روزانه           S1-01..12 (INV-N/D + SETL-R)       ← «فروختم»
      ↓
وصول                  S2-01..06 (INV-D / PAY)            ← «پولم را گرفتم»
      ↓
چک                    S3-01..08 (CHQ + SETL rows)        ← «چک گرفتم/دادم»
      ↓
خرید و هزینه          S4-01..07 (PUR + SETL-P)           ← «خریدم و پرداختم»
      ↓
ناخوشایندها           S5-01..05 ، S1-10 ، S3-04/06       ← «پس آورد / برگشت خورد»
      ↓
حقیقت                 S7-01..05 (DASH + RPT)             ← «اوضاع چطور است»
      ↓
تیم                   S8-01..04 (MEM)                    ← «کارمندم هم کار کند»
```

Maps to plan Part D steps: Step 0 (de-dup) precedes all; Step 1 = راه‌اندازی; Steps 2–3 = فروش/وصول; Step 4 = چک; (خرید rides Steps 2–3 mirrors); Step 5 = ناخوشایندها; Step 6 = حقیقت.

### Shared-screen matrix (duplicate prevention)

| Screen | Used by scenarios | Sharing rule |
|---|---|---|
| SETL-R «دریافت وجه» | S1-01..06, S1-13, S2-01..05, S5-03(refund reverse) | ONE component; modes: at-finalize / per-invoice / per-party. Never re-implemented in PAY. **PROGRESSIVE (decision 16):** default face = one question «چقدر دریافت کردید؟», نقد preselected; کارت/انتقال/چک/تقسیم behind «روش‌های بیشتر»; walk-in mode hides نسیه |
| SETL-P «پرداخت وجه» | S4-03..05, S5-05 | mirror of SETL-R (shared internals, mirrored labels) |
| Cheque form | S1-04, S3-01, S3-05, S4-03 | one form, `direction` prop; entry from SETL rows or CHQ |
| PAY (merged) | S2-03..06, S4-04..05, S3 history visibility | open-settlement cards + unified history; **transfers (S6-03) excluded** |
| CHQ | S3-*, S7-05, DASH strip | list component reused by report + dashboard strip |
| INV-D | S1-07..10, S2-01, S5-01..03 | returns & receipts are actions here — no satellite pages |
| ACC | S6-*, account pickers in SETL/expense | CRUD only here; everywhere else just picks |
| RPT/DASH figures | S7-* | every number has exactly one backend endpoint; DASH reuses RPT endpoints |

---

## Accounting-literacy flags (and how we hide each)

| Concept | Where it lurks | How we hide it |
|---|---|---|
| Allocation (which invoice a receipt settles) | S2-03 party-mode | auto oldest-first («قدیمی‌ترین حساب اول صاف می‌شود» — one calm sentence); no manual allocation grid in phase 1 |
| Prepayment/credit account | S2-04/05 | shown only as «بیعانه: X» on the customer card — never «بستانکار» |
| Cheque ≠ money until cleared | S1-04, S3-* | language does the work: «در جریان» + invoice hint «در انتظار وصول چک»; totals simply don't move early |
| Contra/negative documents (returns) | S5-* | a «برگشت از فروش» doc with positive numbers and a clear arrow direction — never negative amounts on screen |
| Opening balance equity | S6-01/05 | plain «موجودی اولیه» field; the equity side exists only in the phase-2 generator |
| Journal/debit/credit | everywhere | never rendered; events recorded silently (S7-06) |
| Cash-basis vs accrual P/L | S7-02 | fixed simple formula with plain-Persian row labels; no method selector |

---

## Ambiguity resolutions (founder review, 2026-07-04 — all closed)

1. **S1-10 ابطال** — BLOCK while linked receipts/cheques exist; guided message «این فاکتور دریافت ثبت‌شده دارد؛ ابتدا دریافت را حذف یا منتقل کنید». Money records are never auto-unlinked. *(founder)*
2. **S2-03 allocation** — oldest-first (FIFO) confirmed; per-invoice mode of the same dialog is the manual override, no extra UI. *(founder)*
3. **S3 cheque vs settlement status** — cheques do NOT count until وصول; invoice stays جزئی/نسیه with «در انتظار وصول چک». *(adopted recommendation)*
4. **S4-06 expense account** — account picker, default صندوق. *(adopted recommendation)*
5. **Existing payment rows** — backfill account = صندوق in the linkage migration, noted in the migration body. *(adopted recommendation)*
6. **S5-03 refund default** — toggle OFF by default (return credits the customer); toggle copy «پول را پس دادید؟». *(founder)*

All six are mirrored in the decisions table at the top of this document.

---

*Catalog ends. Planning only — no code changed. Decisions final; next step is the Step-0 build prompt.*
