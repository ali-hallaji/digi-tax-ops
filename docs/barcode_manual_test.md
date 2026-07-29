# اسکن بارکد — تست دستی روی گوشی (یک دقیقه)

Playwright already proves the decoder works: `e2e/specs/12-barcode-scan.spec.ts`
feeds Chrome a generated video containing a real EAN-13 and asserts the digits
land in the search box, plus the three fallback paths. What it CANNOT prove is
how it feels holding a phone at a shelf — focus distance, glare, how long a read
takes on a real sensor. That is a two-minute check and it is yours.

---

## ⚠️ It needs HTTPS

`getUserMedia` only works in a **secure context**. On a phone, `http://<laptop-ip>:8080`
is NOT one, so **the scan button will not appear at all** (deliberately — a dead
button is worse than no button).

Use the dev server, which is already on HTTPS:

```
https://<dev-host>/app/products
```

Log in as any persona, then either:
- **products list** → the ⌷ scan button beside the search box, or
- **a draft invoice** → «عنوان کالا یا خدمت» → the ⌷ button beside it.

---

## The two-minute walk

1. **Give a product a barcode.** کالا و خدمات → any product → ویرایش → «بارکد»
   → tap the scan button → hold any real product barcode up → the digits fill
   the field → ذخیره.
2. **Find it by scanning.** Back on the products list → tap the scan button →
   scan the SAME item → the search box fills and the product appears alone.
3. **Sell it by scanning.** Open a draft invoice → the line's scan button →
   scan the item → the title and price fill themselves (barcode beats name, so
   it is one read, not a picker).

## What to look for

| | good | tell us if |
|---|---|---|
| Read time | under ~۲ ثانیه at arm's length | it takes more than ۵ ثانیه or needs odd angles |
| Distance | ۱۰–۳۰ سانتی‌متر works | only works almost touching the label |
| Camera | the **rear** camera opens | the selfie camera opens |
| Glare | reads through shelf lighting | a glossy wrapper defeats it every time |
| After a read | the dialog closes itself | you have to close it by hand |

## The fallbacks (worth one deliberate try)

- **Deny the camera permission** → «اجازهٔ دسترسی به دوربین داده نشده است…» plus
  a line saying manual search still works. Typing must behave normally after.
- **Open over plain http** → no scan button anywhere; the search box is untouched.
- **A barcode already used by another product** → «این بارکد قبلاً برای کالای
  دیگری در این کسب‌وکار ثبت شده است.»

## Known v1 limits (by design)

- **1D retail symbologies only** — EAN-13/8, UPC-A/E, Code 128/39, ITF. QR is
  deliberately excluded so shelf clutter cannot produce a false read.
- **One product per barcode per business.** Two businesses may share one; the
  same business may not, or a scan would be ambiguous.
- **The field is free text**, so in-house Code-128 labels work. A digit check
  would have made the button useless for shops that print their own labels.
