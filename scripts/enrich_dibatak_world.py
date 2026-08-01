#!/usr/bin/env python3
"""Bring ترازپیشه دیبا (09120000000) to a HARMONIOUS full-module demo state.

Companion to `enrich_dibatak_payroll.py`, same contract: the real HTTP API through
a real password login (never SQL), and **idempotent** — every object is keyed by a
stable marker (SKU, cheque number, or a `note` tag) and skipped when already there,
so re-running after a reseed converges instead of duplicating.

What this closes, module by module, so no screen in the demo is empty or lopsided:
incomes (was 0), treasury transfers (was 0), POS mapping, a dual-unit product,
cheques in every state the UI can show, more purchases/expenses spread across the
fiscal year with a real mix of paid/نسیه/partial, and a برگشت از خرید.

STRICT: no Moadian submission of any kind is performed or implied.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import urllib.error
import urllib.request

MOBILE = "09120000000"
PASSWORD = "Admin@12345"
# Every object this script owns carries the tag in its note, so a human reading the
# demo data can tell enrichment from seed, and so re-runs can find their own work.
TAG = "[enrich-world]"


class Api:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.token: str | None = None

    def __call__(self, path, data=None, method=None):
        r = urllib.request.Request(self.base + path, method=method)
        if self.token:
            r.add_header("Authorization", f"Bearer {self.token}")
        if data is not None:
            r.add_header("Content-Type", "application/json")
            r.data = json.dumps(data).encode()
        try:
            resp = urllib.request.urlopen(r, timeout=120)
            return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            body = e.read()
            try:
                return e.code, json.loads(body)
            except Exception:
                return e.code, {"_raw": body[:300].decode("utf8", "replace")}

    def login(self) -> None:
        """Password flow ONLY — dev-OTP on this number would fire a real SMS."""
        _st, ch = self("/auth/captcha/challenge")
        number = next(
            i
            for i in range(ch["maxnumber"] + 1)
            if hashlib.sha256(f"{ch['salt']}{i}".encode()).hexdigest() == ch["challenge"]
        )
        solution = base64.b64encode(
            json.dumps(
                {
                    "algorithm": ch["algorithm"],
                    "challenge": ch["challenge"],
                    "number": number,
                    "salt": ch["salt"],
                    "signature": ch["signature"],
                }
            ).encode()
        ).decode()
        st, out = self(
            "/auth/login",
            {"username": MOBILE, "password": PASSWORD, "captcha": solution},
        )
        if st != 200:
            raise SystemExit(f"login failed: {st} {out}")
        self.token = out["access_token"]


def rows(payload):
    if isinstance(payload, list):
        return payload
    for key in ("items", "customers", "products", "vendors", "data", "results"):
        if isinstance(payload, dict) and isinstance(payload.get(key), list):
            return payload[key]
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://localhost:8000/api/v1")
    args = ap.parse_args()

    api = Api(args.base_url)
    api.login()
    made: list[str] = []
    skipped = 0

    def create(label, path, payload, seen):
        """POST unless `seen` says it is already there. Loud on failure."""
        nonlocal skipped
        if seen:
            skipped += 1
            return None
        st, out = api(path, payload)
        if st not in (200, 201):
            print(f"  ✗ {label}: {st} {json.dumps(out, ensure_ascii=False)[:200]}")
            return None
        made.append(label)
        print(f"  ✓ {label}")
        return out

    # ── reference data we tie everything else to ─────────────────────────────
    accounts = {a["title"]: a for a in rows(api("/treasury/accounts")[1])}
    customers = {c["name"]: c for c in rows(api("/customers")[1])}
    vendors = {v["name"]: v for v in rows(api("/vendors")[1])}
    cash = accounts["صندوق"]["id"]
    bank = accounts["بانک ملت"]["id"]

    # ── 1. POS mapping — «کارتخوان به کدام حساب می‌ریزد؟» ─────────────────────
    print("\n۱) اتصال کارتخوان به حساب بانک ملت")
    if accounts["بانک ملت"].get("pos_connected"):
        skipped += 1
    else:
        st, _out = api(f"/treasury/accounts/{bank}", {"pos_connected": True}, "PATCH")
        print("  ✓ pos_connected" if st == 200 else f"  ✗ pos {st}")
        made.append("pos mapping")

    # ── 2. A dual-unit product — جعبه ↔ مترمربع ──────────────────────────────
    # The server-room anti-static floor دیباتک resells: bought and stocked by the
    # جعبه, quoted to the customer by the مترمربع. One box covers ۲٫۵ m².
    print("\n۲) کالای دو-واحدی (جعبه ↔ مترمربع)")
    products = {p["name"]: p for p in rows(api("/products")[1])}
    floor_name = "کفپوش آنتی‌استاتیک اتاق سرور"
    create(
        floor_name,
        "/products",
        {
            "name": floor_name,
            "product_type": "goods",
            "sku": "DIBA-FLOOR-AS",
            "unit_name": "جعبه",
            "secondary_unit_name": "مترمربع",
            "secondary_unit_factor": "2.5",
            "default_unit_price": "48000000",
            "default_vat_rate": "10",
            "track_inventory": True,
            "opening_stock_qty": "40",
            "low_stock_threshold": "8",
        },
        seen=floor_name in products,
    )
    products = {p["name"]: p for p in rows(api("/products")[1])}
    floor_id = products.get(floor_name, {}).get("id")

    # ── 3. درآمدهای غیرعملیاتی — the incomes module was completely empty ─────
    print("\n۳) درآمدهای غیرعملیاتی")
    existing_incomes = {i.get("note") for i in rows(api("/incomes")[1])}
    # Every income needs a طرف حساب — the API refuses an anonymous one, and it is
    # right to: «سود سپرده» without naming the bank is an unauditable row. The bank
    # is a legitimate طرف حساب in Iranian bookkeeping, so it gets a vendor record.
    bank_party = "بانک ملت — شعبهٔ ونک"
    if bank_party not in vendors:
        st, out = api("/vendors", {"name": bank_party})
        if st in (200, 201):
            print(f"  ✓ طرف حساب {bank_party}")
            made.append(bank_party)
        vendors = {v["name"]: v for v in rows(api("/vendors")[1])}
    bank_vendor = vendors.get(bank_party, {}).get("id")
    pars = {
        "پارس": customers.get("شرکت راهکارهای ابری پارس", {}).get("id"),
        "کیان": customers.get("توسعهٔ نرم‌افزار کیان", {}).get("id"),
        "البرز": customers.get("بازرگانی داده‌محور البرز", {}).get("id"),
    }
    for category, amount, date, party, note in [
        ("bank_interest", "12400000", "2026-03-29", ("vendor", None),
         "سود سپردهٔ کوتاه‌مدت — پایان اسفند"),
        ("rent", "60000000", "2026-04-05", ("customer", "پارس"),
         "اجارهٔ اتاق سرور به شرکت راهکارهای ابری پارس"),
        ("service_fee", "35000000", "2026-05-11", ("customer", "کیان"),
         "کارمزد نصب خارج از قرارداد پشتیبانی"),
        ("bank_interest", "9800000", "2026-06-30", ("vendor", None),
         "سود سپردهٔ کوتاه‌مدت — پایان خرداد"),
        ("other", "18000000", "2026-07-14", ("customer", "البرز"),
         "فروش تجهیزات مستعمل اتاق سرور"),
    ]:
        tagged = f"{note} {TAG}"
        create(
            f"درآمد {note}",
            "/incomes",
            {
                "category": category,
                "amount": amount,
                "income_date": date,
                "account_id": bank,
                "receipt_method": "transfer",
                "party_type": party[0],
                "vendor_id": bank_vendor if party[0] == "vendor" else None,
                "customer_id": pars.get(party[1]) if party[0] == "customer" else None,
                "note": tagged,
                "vat_rate": "0",
            },
            seen=tagged in existing_incomes,
        )

    # ── 4. هزینه‌ها — spread over the fiscal year, not clumped in two months ──
    print("\n۴) هزینه‌های جاری در طول سال")
    existing_expenses = {e.get("note") for e in rows(api("/expenses")[1])}
    landlord = vendors.get("رضا کارگر", {}).get("id")
    infra = vendors.get("تأمین‌کنندهٔ زیرساخت ابری", {}).get("id")
    hardware = vendors.get("نمایندگی سخت‌افزار سرور", {}).get("id")
    for category, amount, date, method, vendor_id, note in [
        ("rent", "95000000", "2026-03-25", "transfer", landlord, "اجارهٔ دفتر — فروردین"),
        ("rent", "95000000", "2026-04-25", "transfer", landlord, "اجارهٔ دفتر — اردیبهشت"),
        ("rent", "95000000", "2026-05-25", "transfer", landlord, "اجارهٔ دفتر — خرداد"),
        ("marketing", "42000000", "2026-04-18", "card", infra, "تبلیغات نمایشگاه الکامپ"),
        ("transport", "8600000", "2026-05-06", "cash", hardware, "حمل تجهیزات به محل مشتری"),
        ("commission", "3200000", "2026-06-01", "transfer", infra, "کارمزد درگاه پرداخت"),
        ("other", "26500000", "2026-06-19", "transfer", infra, "قبض برق و آب — بهار"),
    ]:
        tagged = f"{note} {TAG}"
        create(
            f"هزینهٔ {note}",
            "/expenses",
            {
                "category": category,
                "amount": amount,
                "expense_date": date,
                "account_id": cash if method == "cash" else bank,
                "payment_method": method,
                "party_type": "vendor",
                "vendor_id": vendor_id,
                "note": tagged,
                "vat_rate": "0",
            },
            seen=tagged in existing_expenses,
        )

    # ── 5. خریدها — a real mix of paid / نسیه / partial ──────────────────────
    print("\n۵) خریدها با وضعیت‌های پرداخت متفاوت")
    purchases = rows(api("/purchases")[1])
    existing_purchases = {p.get("note") for p in purchases}
    hw = vendors.get("نمایندگی سخت‌افزار سرور", {}).get("id")
    cloud = vendors.get("تأمین‌کنندهٔ زیرساخت ابری", {}).get("id")
    plans = [
        (
            "خرید کفپوش آنتی‌استاتیک — ۲۰ جعبه",
            hw,
            "2026-03-18",
            "paid",
            [
                {
                    "product_id": floor_id,
                    "description": floor_name,
                    "qty": "20",
                    "unit_price": "31000000",
                }
            ]
            if floor_id
            else None,
            "620000000",
        ),
        ("تمدید سالانهٔ پهنای باند", cloud, "2026-05-09", "unpaid", None, "0"),
        ("خرید سوییچ و رک — بخشی نقد", hw, "2026-06-15", "partial", None, "150000000"),
    ]
    for note, vendor_id, date, status, lines, paid in plans:
        tagged = f"{note} {TAG}"
        body = {
            "vendor_id": vendor_id,
            "purchase_date": date,
            "payment_status": status,
            "paid_amount": paid,
            "account_id": bank,
            "note": tagged,
            "purchase_vat": "0",
        }
        if lines:
            body["lines"] = lines
        else:
            body["lump_sum_amount"] = (
                "380000000" if status == "unpaid" else "420000000"
            )
            body["lump_sum_description"] = note
        create(f"خرید {note}", "/purchases", body, seen=tagged in existing_purchases)

    # ── 6. چک‌ها در همهٔ وضعیت‌ها ────────────────────────────────────────────
    print("\n۶) چک‌ها در وضعیت‌های مختلف")
    cheques = rows(api("/cheques")[1])
    have = {c.get("cheque_number") for c in cheques}
    wanted = [
        ("DIBA-C880", "received", customers.get("هلدینگ فناوری نوآوران", {}).get("id"),
         None, "88000000", "2026-06-28", "چک دریافتی — در جریان وصول"),
        ("DIBA-C445", "received", customers.get("توسعهٔ نرم‌افزار کیان", {}).get("id"),
         None, "44500000", "2026-05-30", "چک دریافتی — برگشتی"),
        ("DIBA-P320", "issued", None, hw, "320000000", "2026-07-20",
         "چک صادره بابت خرید سوییچ و رک"),
    ]
    created_cheques: dict[str, dict] = {}
    for number, direction, cust, vend, amount, due, note in wanted:
        out = create(
            f"چک {number}",
            "/cheques",
            {
                "direction": direction,
                "customer_id": cust,
                "vendor_id": vend,
                "cheque_number": number,
                "bank_name": "ملت",
                "amount": amount,
                "due_date": due,
                "account_id": bank,
                "note": f"{note} {TAG}",
            },
            seen=number in have,
        )
        if out:
            created_cheques[number] = out

    # Walk the two receivables through REAL state transitions, never a status write:
    # one deposited and waiting, one deposited then bounced — the two states a
    # merchant actually asks about.
    for number, steps in (("DIBA-C880", ["deposit"]), ("DIBA-C445", ["deposit", "bounce"])):
        cid = created_cheques.get(number, {}).get("id")
        if not cid:
            continue
        for step in steps:
            st, out = api(f"/cheques/{cid}/{step}", {"account_id": bank})
            print(
                f"  ✓ {number} → {step}"
                if st in (200, 201)
                else f"  ✗ {number} {step}: {st} {json.dumps(out, ensure_ascii=False)[:160]}"
            )

    # ── 7. انتقال بین حساب‌ها ────────────────────────────────────────────────
    print("\n۷) انتقال وجه بین صندوق و بانک")
    transfers = rows(api("/treasury/transfers")[1])
    note = f"واریز موجودی صندوق به حساب بانکی {TAG}"
    create(
        "انتقال صندوق ← بانک",
        "/treasury/transfers",
        {
            "from_account_id": cash,
            "to_account_id": bank,
            "amount": "120000000",
            "transfer_date": "2026-06-10",
            "note": note,
        },
        seen=any(t.get("note") == note for t in transfers),
    )

    # ── 8. برگشت از خرید — the mirror of the seeded برگشت از فروش ────────────
    print("\n۸) برگشت از خرید")
    returns = rows(api("/returns")[1])
    ret_note = f"برگشت دو جعبه کفپوش معیوب به فروشنده {TAG}"
    target = next(
        (p for p in rows(api("/purchases")[1]) if (p.get("note") or "").startswith("خرید کفپوش")),
        None,
    )
    create(
        "برگشت از خرید",
        "/returns",
        {
            "purchase_id": (target or {}).get("id"),
            "lines": (
                [
                    {
                        "line_id": (target or {}).get("lines", [{}])[0].get("id"),
                        "returned_quantity": "2",
                    }
                ]
                if (target or {}).get("lines")
                else []
            ),
            "return_date": "2026-04-02",
            "refund": True,
            "refund_account_id": bank,
            "note": ret_note,
        },
        seen=any((r.get("note") or "") == ret_note for r in returns),
    )

    print(f"\n{'─' * 60}\nساخته‌شد: {len(made)} | از قبل موجود (رد شد): {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
