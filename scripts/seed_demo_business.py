#!/usr/bin/env python3
"""Seed realistic demo data into one DigiTax business via the public API.

API-based, standard-library only. Logs in through the dev OTP flow (dev returns
the OTP in the response), lets you pick a business, then fills it with products,
customers, vendors, purchases, expenses and credit invoices — deliberately
leaving some vendor debts and customer receivables OPEN so the «تسویه‌های باز»
settlement cockpit has rows to show.

Usage:
    python3 scripts/seed_demo_business.py
    DIGI_API_BASE=http://localhost:8000/api/v1 python3 scripts/seed_demo_business.py

Re-runnable: identity numbers are randomly generated (valid) on every run, so
re-seeding does not collide on the customer national_id unique constraint. Any
per-record API error is reported and skipped — the script never aborts midway.
"""

from __future__ import annotations

import datetime
import json
import os
import random
import sys
import urllib.error
import urllib.request

API_BASE = os.environ.get("DIGI_API_BASE", "http://localhost:8000/api/v1").rstrip("/")
DEFAULT_MOBILE = "09120000000"

# Real Iranian operator prefixes (subset of the whitelist in CLAUDE.md §7.5).
MOBILE_PREFIXES = [
    "0912", "0919", "0910", "0913", "0935", "0936", "0937",
    "0901", "0902", "0903", "0990", "0991", "0933", "0938",
]

TODAY = datetime.date.today()


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def api(method, path, token=None, body=None):
    """Return (status_code, parsed_json|None). Never raises on HTTP errors."""
    url = API_BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}
    except urllib.error.URLError as exc:
        print(f"  ✗ network error talking to {url}: {exc.reason}")
        sys.exit(1)


def ok(status):
    return 200 <= status < 300


# --------------------------------------------------------------------------- #
# Valid identity generators
# --------------------------------------------------------------------------- #
def gen_national_id():
    """10-digit کد ملی with a real mod-11 checksum; never all-same-digit."""
    while True:
        digits = [random.randint(0, 9) for _ in range(9)]
        s = sum(d * (10 - i) for i, d in enumerate(digits))
        r = s % 11
        check = r if r < 2 else 11 - r
        nid = "".join(map(str, digits)) + str(check)
        if len(set(nid)) > 1:
            return nid


def gen_legal_id():
    """11-digit شناسه ملی — length-only per app rules; never all-same-digit."""
    while True:
        nid = "".join(str(random.randint(0, 9)) for _ in range(11))
        if len(set(nid)) > 1:
            return nid


def gen_economic_id():
    """12-digit کد اقتصادی."""
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def gen_mobile():
    return random.choice(MOBILE_PREFIXES) + "".join(
        str(random.randint(0, 9)) for _ in range(7)
    )


def days_ago(n):
    return (TODAY - datetime.timedelta(days=n)).isoformat()


# --------------------------------------------------------------------------- #
# Demo content
# --------------------------------------------------------------------------- #
PRODUCTS = [
    ("لپ‌تاپ ایسوس VivoBook", "goods", "35000000"),
    ("ماوس بی‌سیم لاجیتک", "goods", "850000"),
    ("کیبورد مکانیکی", "goods", "2400000"),
    ("مانیتور ال‌جی ۲۴ اینچ", "goods", "12000000"),
    ("هارد اکسترنال ۱ ترابایت", "goods", "3200000"),
    ("کابل HDMI", "goods", "450000"),
    ("پرینتر لیزری اچ‌پی", "goods", "8500000"),
    ("خدمات نصب و راه‌اندازی", "service", "1500000"),
    ("پشتیبانی فنی ماهانه", "service", "2000000"),
    ("طراحی وب‌سایت فروشگاهی", "service", "25000000"),
]

# (display name, customer_type)
CUSTOMERS = [
    ("علی محمدی", "individual"),
    ("شرکت فناوری پارس", "legal"),
    ("مریم حسینی", "individual"),
    ("بازرگانی آرین", "legal"),
    ("رضا کریمی", "individual"),
    ("فروشگاه مرکزی نمونه", "legal"),
    ("زهرا احمدی", "individual"),
    ("شرکت داده‌پرداز شرق", "legal"),
]

VENDORS = [
    "تأمین‌کننده قطعات رایانه",
    "پخش لوازم اداری تهران",
    "شرکت واردات الکترونیک",
    "توزیع‌کننده ملزومات اداری",
]

# category enum: rent|salary|transport|marketing|commission|other
EXPENSES = [
    ("rent", "8000000", "اجاره دفتر کار - خرداد"),
    ("salary", "45000000", "حقوق کارمندان"),
    ("transport", "1200000", "هزینه حمل و نقل مرسولات"),
    ("marketing", "5000000", "تبلیغات اینستاگرام"),
    ("commission", "3500000", "کمیسیون فروش نمایندگان"),
    ("other", "650000", "قبض برق دفتر"),
    ("other", "890000", "قبض اینترنت و تلفن"),
    ("other", "1400000", "خرید ملزومات اداری"),
]


def prompt(label, generator):
    """Prompt for an identity value; blank input → auto-generate a valid one."""
    try:
        raw = input(f"  {label} (Enter = auto-generate valid): ").strip()
    except EOFError:
        raw = ""
    if raw:
        return raw
    return generator()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    random.seed()
    print(f"\n🌱 DigiTax demo seeder → {API_BASE}\n")

    # 1. Login via dev OTP
    try:
        mobile = input(f"Mobile to log in as [{DEFAULT_MOBILE}]: ").strip() or DEFAULT_MOBILE
    except EOFError:
        mobile = DEFAULT_MOBILE

    status, body = api("POST", "/auth/otp/request", body={"mobile": mobile})
    if not ok(status) or not body or "dev_otp" not in body:
        print(f"✗ OTP request failed ({status}): {body}")
        sys.exit(1)
    dev_otp = body["dev_otp"]
    print(f"  → dev OTP: {dev_otp}")

    status, body = api("POST", "/auth/otp/verify", body={"mobile": mobile, "otp": dev_otp})
    if not ok(status) or not body or "access_token" not in body:
        print(f"✗ OTP verify failed ({status}): {body}")
        sys.exit(1)
    token = body["access_token"]
    print(f"  ✓ logged in as {mobile}")

    # 2. Pick a business
    status, body = api("GET", "/businesses", token=token)
    businesses = (body or {}).get("businesses", []) if isinstance(body, dict) else []
    if not businesses:
        print("✗ no businesses found for this user")
        sys.exit(1)
    print("\nBusinesses:")
    for i, b in enumerate(businesses, 1):
        print(f"  {i}) {b['name']}  ({b['id']})")
    try:
        choice = input(f"Which business to fill? [1-{len(businesses)}, default 1]: ").strip()
    except EOFError:
        choice = ""
    idx = (int(choice) - 1) if choice.isdigit() and 1 <= int(choice) <= len(businesses) else 0
    business = businesses[idx]
    print(f"  ✓ seeding into: {business['name']}")

    status, body = api(
        "POST", "/businesses/select", token=token, body={"business_id": business["id"]}
    )
    if not ok(status) or not body or "access_token" not in body:
        print(f"✗ business select failed ({status}): {body}")
        sys.exit(1)
    t = body["access_token"]  # business-scoped token

    # 3. Optional identity values (used for the first individual/legal customer)
    print("\nOptional identity values for featured customers:")
    featured_national = prompt("کد ملی (individual)", gen_national_id)
    featured_legal = prompt("شناسه ملی (legal)", gen_legal_id)
    featured_mobile = prompt("موبایل", gen_mobile)

    counts = {k: 0 for k in
              ("products", "customers", "vendors", "purchases", "expenses",
               "invoices", "payments")}

    # 4. Products
    print("\nProducts…")
    product_ids = []  # (id, price)
    for name, ptype, price in PRODUCTS:
        st, b = api("POST", "/products", token=t, body={
            "name": name, "product_type": ptype,
            "default_unit_price": price, "currency": "IRR",
            "default_vat_rate": "9" if ptype == "goods" else "0",
        })
        if ok(st):
            product_ids.append((b["id"], price))
            counts["products"] += 1
        else:
            print(f"  ⚠ product '{name}' failed ({st}): {b}")

    # 5. Customers
    print("Customers…")
    customer_ids = []  # (id, name, type)
    used_featured_ind = used_featured_legal = False
    for name, ctype in CUSTOMERS:
        payload = {"name": name, "customer_type": ctype, "mobile": gen_mobile()}
        if ctype == "individual":
            if not used_featured_ind:
                payload["national_id"] = featured_national
                payload["mobile"] = featured_mobile
                used_featured_ind = True
            else:
                payload["national_id"] = gen_national_id()
        else:  # legal
            payload["national_id"] = (
                featured_legal if not used_featured_legal else gen_legal_id()
            )
            used_featured_legal = True
            payload["economic_id"] = gen_economic_id()
        st, b = api("POST", "/customers", token=t, body=payload)
        if ok(st):
            customer_ids.append((b["id"], name, ctype))
            counts["customers"] += 1
        else:
            print(f"  ⚠ customer '{name}' failed ({st}): {b}")

    # 6. Vendors
    print("Vendors…")
    vendor_ids = []
    for name in VENDORS:
        st, b = api("POST", "/vendors", token=t, body={
            "name": name, "phone": gen_mobile(), "note": "تأمین‌کننده نمونه",
        })
        if ok(st):
            vendor_ids.append((b["id"], name))
            counts["vendors"] += 1
        else:
            print(f"  ⚠ vendor '{name}' failed ({st}): {b}")

    # 7. Purchases — mix of paid / unpaid / partial; some with line items.
    #    unpaid + partial leave OPEN vendor debt for the cockpit.
    print("Purchases…")
    if vendor_ids and product_ids:
        plans = [
            # (status, use_lines, paid_fraction)
            ("unpaid", False, 0.0),
            ("partial", True, 0.4),
            ("paid", True, 1.0),
            ("unpaid", True, 0.0),
            ("partial", False, 0.5),
            ("paid", False, 1.0),
            ("unpaid", False, 0.0),
            ("partial", True, 0.3),
            ("paid", True, 1.0),
            ("unpaid", True, 0.0),
        ]
        for i, (pstatus, use_lines, paid_frac) in enumerate(plans):
            vendor_id, _ = vendor_ids[i % len(vendor_ids)]
            body = {
                "vendor_id": vendor_id,
                "purchase_date": days_ago(random.randint(3, 150)),
                "payment_status": pstatus,
                "purchase_vat": "0",
            }
            if use_lines:
                lines = []
                total = 0
                for pid, price in random.sample(product_ids, k=random.randint(1, 3)):
                    qty = random.randint(1, 5)
                    lines.append({
                        "product_id": pid,
                        "description": "خرید کالا",
                        "qty": str(qty),
                        "unit_price": price,
                    })
                    total += qty * int(price)
                body["lines"] = lines
            else:
                total = random.randint(2, 30) * 1_000_000
                body["lump_sum_amount"] = str(total)
                body["lump_sum_description"] = "خرید عمده ملزومات"
            if pstatus == "partial":
                body["paid_amount"] = str(int(total * paid_frac))
            elif pstatus == "paid":
                body["paid_amount"] = str(total)
            else:
                body["paid_amount"] = "0"
            st, b = api("POST", "/purchases", token=t, body=body)
            if ok(st):
                counts["purchases"] += 1
            else:
                print(f"  ⚠ purchase #{i + 1} ({pstatus}) failed ({st}): {b}")

    # 8. Expenses
    print("Expenses…")
    methods = ["cash", "card", "transfer", None]
    for cat, amount, note in EXPENSES:
        st, b = api("POST", "/expenses", token=t, body={
            "category": cat, "amount": amount,
            "expense_date": days_ago(random.randint(2, 120)),
            "payment_method": random.choice(methods),
            "note": note,
        })
        if ok(st):
            counts["expenses"] += 1
        else:
            print(f"  ⚠ expense '{note}' failed ({st}): {b}")

    # 9. Credit invoices → finalize → partial receipt → OPEN customer receivable.
    print("Credit invoices (for open receivables)…")
    # Use the first 4 customers; leave 3 of them with an open receivable.
    for n, (cid, cname, _ctype) in enumerate(customer_ids[:4]):
        st, draft = api("POST", "/invoice-drafts", token=t, body={
            "invoice_type": "internal_private",
            "customer_id": cid,
            "title": f"فاکتور فروش به {cname}",
            "issue_date": days_ago(random.randint(5, 60)),
            "currency": "IRR",
        })
        if not ok(st):
            print(f"  ⚠ invoice draft for '{cname}' failed ({st}): {draft}")
            continue
        inv_id = draft["id"]
        # add 1–2 lines
        invoice_total = 0
        for pid, price in random.sample(product_ids, k=random.randint(1, 2)):
            qty = random.randint(1, 3)
            la, lb = api("POST", f"/invoice-drafts/{inv_id}/lines", token=t, body={
                "product_id": pid,
                "quantity": str(qty),
                "unit_price": price,
                "vat_rate": "0",
            })
            if ok(la):
                invoice_total += qty * int(price)
            else:
                print(f"  ⚠ invoice line failed ({la}): {lb}")
        fa, fb = api("POST", f"/invoice-drafts/{inv_id}/finalize", token=t)
        if not ok(fa):
            print(f"  ⚠ finalize for '{cname}' failed ({fa}): {fb}")
            continue
        counts["invoices"] += 1
        # Record a partial receipt for the first 3 → leaves an open receivable.
        # The 4th gets a full receipt → fully settled (shows the settled path).
        if invoice_total > 0:
            frac = 1.0 if n == 3 else random.choice([0.3, 0.4, 0.5])
            amt = int(invoice_total * frac)
            pa, pb = api("POST", "/payments", token=t, body={
                "party_type": "customer",
                "customer_id": cid,
                "amount": str(amt),
                "payment_date": days_ago(random.randint(1, 20)),
                "payment_method": "transfer",
                "note": "دریافت بخشی از طلب",
            })
            if ok(pa):
                counts["payments"] += 1
            else:
                print(f"  ⚠ receipt for '{cname}' failed ({pa}): {pb}")

    # 10. A couple of partial vendor payments → transaction history, debt stays open.
    print("Vendor part-payments…")
    for vendor_id, vname in vendor_ids[:2]:
        st, b = api("POST", "/payments", token=t, body={
            "party_type": "vendor",
            "vendor_id": vendor_id,
            "amount": str(random.randint(1, 3) * 1_000_000),
            "payment_date": days_ago(random.randint(1, 30)),
            "payment_method": "transfer",
            "note": "پرداخت بخشی از بدهی",
        })
        if ok(st):
            counts["payments"] += 1
        else:
            print(f"  ⚠ vendor payment for '{vname}' failed ({st}): {b}")

    # --------------------------------------------------------------------- #
    # Summary + verification
    # --------------------------------------------------------------------- #
    print("\n✅ Seeding complete:")
    for k, v in counts.items():
        print(f"    {k:>10}: {v}")

    print("\n🔎 Verifying open settlements via the API…")
    _, vresp = api("GET", "/vendors?limit=100", token=t)
    vendors_live = (vresp or {}).get("items", []) if isinstance(vresp, dict) else []
    open_vendor_debts = [v for v in vendors_live if float(v.get("total_unpaid", "0")) > 0]
    print(f"    vendors with open debt: {len(open_vendor_debts)}")
    for v in open_vendor_debts:
        print(f"      • {v['name']}: total_unpaid={v['total_unpaid']}")

    _, cresp = api("GET", "/customers?limit=100", token=t)
    if isinstance(cresp, dict):
        customers_live = cresp.get("items", cresp.get("customers", []))
    else:
        customers_live = cresp or []
    open_recv = [c for c in customers_live if float(c.get("total_receivable", "0")) > 0]
    print(f"    customers with open receivable: {len(open_recv)}")
    for c in open_recv:
        print(f"      • {c['name']}: total_receivable={c['total_receivable']}")

    if open_vendor_debts and open_recv:
        print("\n🎉 «تسویه‌های باز» cockpit will have both vendor and customer rows.")
    else:
        print("\n⚠ Expected open vendor debts AND customer receivables — check warnings above.")


if __name__ == "__main__":
    main()
