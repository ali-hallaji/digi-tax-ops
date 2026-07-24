# MOADIAN F — صورتحساب اصلاحی (subject=2 corrective): the org spec, with citations

_Source: `RC_IITP_IS_V7_8.pdf` (اردیبهشت ۱۴۰۵) — the ONLY org authority. Every rule
below is quoted/cited from the PDF; nothing invented. Where the PDF is silent it is
marked **«سند ساکت است»** with the safest behavior chosen._

This doc is the permanent contract for the TRUE editable اصلاحیه flow (MOADIAN F
Part 1). It replaces the immediate no-edit corrective (which looked like a
cancellation in the کارپوشه).

---

## 1. What a corrective IS (§5-2, p.14-15)

> §5-2 «صورتحساب الکترونیکی اصلاحی»: «چنانچه پس از صدور و ثبت صورتحساب فروش، نیاز به
> اصلاح اقلام اطلاعاتی صورتحساب **به غیر از** اقلام اطلاعاتی مربوط به خریدار و یا اقلام
> اطلاعاتی مربوط به کالا/خدمت باشد، صادرکننده … می‌بایست **صورتحساب جدید (اصلاحی)** که
> از نظر **نوع و الگوی صورتحساب مطابق صورتحساب اصلی (مرجع)** بوده و **حاوی شماره منحصر به
> فرد مالیاتی صورتحساب مرجع** است را صادر و در سامانه مؤدیان ثبت نماید.»

Distilled:
- A corrective is a **FULL NEW invoice** (its own new serial + new taxid), **not a
  delta**. It carries the whole corrected line set.
- It **references** the original by embedding the original's official 22-char taxid
  as `irtaxid`.
- Its **نوع (type/`inty`)** and **الگو (pattern/`inp`)** MUST equal the reference's.

### صورتحساب مرجع vs ارجاعی (§5 intro, p.14)
- **مرجع (reference):** any اصلی in any status (تایید/رد/عدم‌نیاز‌به‌واکنش), OR any
  اصلاحی/برگشت that is (تایید‌شده / عدم‌نیاز‌به‌واکنش).
- **ارجاعی (referring):** an invoice whose موضوع is اصلاحی، ابطالی، or برگشت‌از‌فروش.

---

## 2. Editability rules — MAY change / MUST NOT change / سند ساکت است

Authority: §5-2 نکات (p.15) + جدول ۱۰ ردیف ۳/۴ (§7-8, p.30) + جدول ۱۱ (§7-9, p.31).

| Field (our column) | packet | اصلاحی؟ | Citation |
|---|---|---|---|
| **نوع صورتحساب** (`inty`, moadian_type_override) | header | **MUST NOT** — must equal مرجع | §5-2 نکته ۱; جدول ۱۰ ردیف ۳ |
| **الگوی صورتحساب** (`inp`, moadian_pattern) | header | **MUST NOT** — must equal مرجع | §5-2 نکته ۱; جدول ۱۰ ردیف ۳ |
| **اطلاعات خریدار** (buyer name/id/tob/bpc — `bid`/`tinb`/`tob`/`bpc`) | header | **MUST NOT**, and **omitted from the packet** («خارج از الگو») | §5-2 نکته ۱; **جدول ۱۰ ردیف ۴** |
| **شناسهٔ کالا/خدمت per line** (`sstid`, tax_item_id) | body | **MUST NOT** | §5-2 نکته ۱ |
| **نرخ ارزش افزوده per line** (`vra`, vat_rate) | body | **MUST NOT** | §5-2 نکته ۱ |
| **افزودن ردیف جدید** (new شناسهٔ کالا/خدمت) | body | **MUST NOT** — «امکان افزودن شناسه کالا/خدمت جدید در صورتحساب اصلاحی وجود ندارد» | §5-2 نکته ۲.a |
| **تعداد/مقدار per line** (`am`, quantity) | body | **MAY** (increase and decrease) | §5-2 نکته ۲ |
| **مبلغ واحد** (`fee`, unit_price) | body | **MAY** (not in the forbidden list) | §5-2 نکته ۱ (exhaustive forbidden list) |
| **تخفیف ردیف** (`dis`, discount) | body | **MAY** (not forbidden) | §5-2 نکته ۱ |
| **روش تسویه** (`setm`) / پرداخت‌ها | header | **MAY** (not forbidden) | §5-2 نکته ۱ |
| **حذف کامل یک ردیف موجود** | body | **MAY — سند ساکت است.** Safest: allowed, because the corrective may only be a **subset** of the reference's شناسه‌ها (adding new is forbidden), so removing an existing line = a quantity-to-zero reduction, which نکته ۲.b permits (خطای ثبت). NOT a substitute for برگشت از فروش when goods physically returned. | §5-2 نکته ۲.b (کاهش) |
| **تاریخ صدور / سررسید / یادداشت / crn** | header | **MAY** (not forbidden). crn still validated & must match کارپوشه. | §5-2 نکته ۱ |

**One-liner for the UI locks:** نوع، الگو، خریدار، شناسهٔ کالا/خدمت، و نرخ ارزش افزوده
غیرقابل اصلاح‌اند؛ برای تغییر آن‌ها باید صورتحساب مرجع **ابطال** و صورتحساب جدید صادر شود
(§5-2 نکته ۱). افزودن ردیف/شناسهٔ جدید در اصلاحیه ممکن نیست.

### Packet consequence (جدول ۱۰ ردیف ۴, p.30)
> «در صورت صورتحساب‌های الکترونیکی با موضوع **اصلاحی، ابطالی و برگشت از فروش** کلیه
> اطلاعات مربوط به خریدار **خارج از الگو** خواهند بود.»

⇒ For `ins ∈ {2,3,4}` the packet builder MUST **omit** buyer identity fields
(`tob`, `bid`, `tinb`, `bpc`, `sbc`/`bbc`/`bpn`). (جدول ۱۰ ردیف ۳ additionally: for
**ابطالی**, `inty`/`inp` are خارج از الگو too.) Sending buyer fields on a corrective
draws the org's `14xxx` «خارج از الگو» تذکر family (same non-blocking notices seen on
برگشت); stripping them keeps the corrective کارپوشه-clean.

---

## 3. Blocked states / guard rails (§5 intro + §5-2 نکته ۳/۴ + §5-3 نکته ۳)

1. **Reference must be a valid مرجع** — accepted (تایید‌شده / تایید‌سیستمی /
   عدم‌نیاز‌به‌واکنش). A مرجع that is itself اصلاحی/برگشت must be in one of those
   statuses (§5-2 نکته ۴).
2. **Cannot correct a cancelled invoice.** An ابطالی can never be a مرجع (§5-3 نکته ۲);
   and if a مرجع is cancelled, its un-approved correctives/returns are themselves
   cancelled (§5-3 نکته ۳). ⇒ block «صدور اصلاحیه» on any ابطال‌شده invoice.
3. **One open corrective per reference at a time.** «به صورت همزمان امکان استفاده از یک
   صورتحساب مرجع در صورتحساب اصلاحی و یا برگشت از فروش ابطال‌نشده وجود ندارد» (§5 intro).
   ⇒ refuse a 2nd open corrective draft for the same original with a friendly message.
4. **Corrective-on-corrective (chain) is allowed**, and the **last approved** corrective
   is the reference (§5-2 نکته ۳). (Our flow always links to the currently-registered
   taxid, so a chain naturally references the latest.)
5. **Cancelling the corrective DRAFT leaves the original untouched** — a draft has no
   org footprint; only a submitted corrective changes the کارپوشه.

---

## 4. برگشت از فروش review (§5-4, p.16) — NO CHANGE NEEDED

§5-4: the seller issues a برگشت when part of the goods is reduced; the packet matches
the reference's نوع/الگو, carries the reference taxid, and contains **sold-minus-
returned** items. Our `submit_return` already builds exactly this from the return
document (progress.md: «برگشت از فروش org-proven»; matrix C7/C8 green). The editable-
corrective rebuild does NOT touch the return path. **Verified: برگشت needs no change.**
(The one alignment it shares: برگشت is also `ins=4` → buyer fields omitted per جدول ۱۰
ردیف ۴ — folded into the shared packet fix.)

---

## 5. Implementation contract (what the rebuild must do)

1. **Migration** `invoice_drafts.corrective_of_invoice_id` (FK→invoice_drafts, nullable)
   + `corrective_reference_taxid` (VARCHAR, the frozen مرجع taxid). A draft with
   `corrective_of_invoice_id` set is an اصلاحیه draft.
2. **«صدور اصلاحیه»** on a registered invoice → confirm dialog → server creates a
   DRAFT deep-copy of the original (lines + line tax profiles + type + pattern + crn +
   buyer snapshot) with `corrective_of_invoice_id` = original.id and
   `corrective_reference_taxid` = the original's registered taxid; status `draft`.
   Guard rails §3 enforced server-side (friendly Persian on each).
3. **The wizard** opens the corrective draft with everything editable EXCEPT the §2
   MUST-NOT fields, which are locked with a one-line reason. The «+ افزودن ردیف» is
   disabled. Type/pattern/buyer controls are read-only.
4. **Finalize → submit** goes as `ins=2` with `irtaxid = corrective_reference_taxid`;
   the packet omits buyer fields (§4). Org result renders on the CORRECTIVE draft.
5. **Bidirectional timeline:** the original's Moadian panel shows «اصلاح شد →
   [شماره جدید]» linking to the corrective; the corrective shows «اصلاحیهٔ [شمارهٔ
   مرجع]» linking back.
6. **Remove** the old immediate-submit corrective button/path from the finalized panel.
