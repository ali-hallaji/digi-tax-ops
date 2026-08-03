#!/usr/bin/env python3
"""EVAL BATCH — enrich دیباتک (09120000000) with coherent payroll-1405 data.

    python3 scripts/enrich_dibatak_payroll.py http://localhost:8000
    python3 scripts/enrich_dibatak_payroll.py https://dev.digiinvoice.ir

Everything goes through the REAL API with the founder's password login (Altcha
PoW solved honestly; captcha stays ON), so every figure is engine-computed and
the treasury moves rial-for-rial. Idempotent: existing pieces are detected and
skipped, so re-running never duplicates.

Creates (only if absent):
  · treasury account «بانک حقوق» with a large opening balance
  · workshop code on the business settings
  · 4 employees: سقف‌شکن (above the insurance ceiling) · دوفرزندی (حق اولاد
    + a 4-day مأموریت) · ساعتی (low base + ۲۶ ساعت اضافه‌کار from the formula)
    · مستعفی (to be settled)
  · payroll runs خرداد+تیر+مرداد ۱۴۰۵ → confirmed → PAID from «بانک حقوق»,
    plus شهریور left as an editable پیش‌نویس
  · insurance-list zip downloaded once (proof; discarded)
  · settlement for مستعفی (resignation, ۹ روز مرخصی) → paid → PDF (proof)
  · payroll_advanced entitlement for the business (admin_manual, founder actor)
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
API = BASE + "/api/v1"
FOUNDER = "09120000000"
PASSWORD = "Admin@12345"


def req(path, data=None, token=None, method=None, raw=False):
    r = urllib.request.Request(API + path, method=method)
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        r.add_header("Content-Type", "application/json")
        r.data = json.dumps(data).encode()
    try:
        resp = urllib.request.urlopen(r, timeout=90)
        body = resp.read()
        return resp.status, (body if raw else json.loads(body or b"{}"))
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:  # noqa: BLE001
            return e.code, {"detail": body[:200].decode(errors="replace")}


def solve_captcha():
    st, ch = req("/auth/captcha/challenge")
    assert st == 200, ch
    n = next(
        i
        for i in range(ch["maxnumber"] + 1)
        if hashlib.sha256(f"{ch['salt']}{i}".encode()).hexdigest() == ch["challenge"]
    )
    return base64.b64encode(
        json.dumps(
            {
                "algorithm": ch["algorithm"],
                "challenge": ch["challenge"],
                "number": n,
                "salt": ch["salt"],
                "signature": ch["signature"],
            }
        ).encode()
    ).decode()


def valid_national_id(seed9: str) -> str:
    """9 digits → append the correct mod-11 check digit."""
    digits = [int(c) for c in seed9]
    s = sum(d * (10 - i) for i, d in enumerate(digits))
    r = s % 11
    check = r if r < 2 else 11 - r
    return seed9 + str(check)


def login() -> str:
    st, out = req(
        "/auth/login",
        {"username": FOUNDER, "password": PASSWORD, "captcha": solve_captcha()},
    )
    assert st == 200 and out.get("access_token"), f"login failed: {st} {out}"
    return out["access_token"]


EMPLOYEES = [
    {
        "full_name": "بهرام سقفی",  # above the insurance ceiling
        "national_id": valid_national_id("990000001"),
        "insurance_number": "70000001",
        "job_title": "مدیر فروش",
        "hire_date": "2025-03-21",
        "base_salary": "1300000000",
        "allowance_bon": "22000000",
        "allowance_housing": "30000000",
        "seniority_base": "5000010",
    },
    {
        "full_name": "لیلا دوفرزندی",  # حق اولاد visible (2 kids × 3×daily)
        "national_id": valid_national_id("990000002"),
        "insurance_number": "70000002",
        "job_title": "حسابدار",
        "hire_date": "2024-09-01",
        "base_salary": "250000000",
        "allowance_bon": "22000000",
        "allowance_housing": "30000000",
        "allowance_marriage": "5000000",
        "allowance_child": "33251100",
        "seniority_base": "5000010",
    },
    {
        "full_name": "حسن ساعتی",  # hourly-style: low base, overtime added per run
        "national_id": valid_national_id("990000003"),
        "insurance_number": "70000003",
        "job_title": "کارگر ساعتی",
        "hire_date": "2026-01-05",
        "base_salary": "90000000",
        "allowance_bon": "22000000",
        "allowance_housing": "30000000",
    },
    {
        "full_name": "مریم مستعفی",  # settled at the end
        "national_id": valid_national_id("990000004"),
        "insurance_number": "70000004",
        "job_title": "کارشناس اداری",
        "hire_date": "2024-07-01",
        "base_salary": "220000000",
        "allowance_bon": "22000000",
        "allowance_housing": "30000000",
        "seniority_base": "5000010",
    },
]


def main() -> None:
    tok = login()
    print(f"✓ login {FOUNDER} on {BASE}")

    # ── treasury account ────────────────────────────────────────────────
    st, accounts = req("/treasury/accounts", token=tok)
    items = accounts.get("items", [])
    bank = next((a for a in items if a["title"] == "بانک حقوق"), None)
    if bank is None:
        st, bank = req(
            "/treasury/accounts",
            {
                "title": "بانک حقوق",
                "account_type": "bank",
                "opening_balance": "60000000000",
            },
            token=tok,
        )
        assert st in (200, 201), bank
        print("✓ treasury «بانک حقوق» created (6,000,000,000 تومان)")
    else:
        print("· treasury «بانک حقوق» exists")

    # ── workshop code ───────────────────────────────────────────────────
    st, blist = req("/businesses", token=tok)
    businesses = blist.get("businesses") or blist.get("items") or []
    biz = next((b for b in businesses if "دیبا" in (b.get("name") or "")), None) or (
        businesses[0] if businesses else None
    )
    assert biz, blist
    biz_id = biz.get("id")
    st, _ = req(
        f"/businesses/{biz_id}/settings",
        {"insurance_workshop_code": "0148430838"},
        token=tok,
        method="PATCH",
    )
    assert st == 200, _
    print(f"✓ workshop code set on «{biz.get('name')}»")

    # ── employees ───────────────────────────────────────────────────────
    st, existing = req("/payroll/employees?limit=100", token=tok)
    by_name = {e["full_name"]: e for e in existing.get("items", [])}
    ids = {}
    for spec in EMPLOYEES:
        if spec["full_name"] in by_name:
            ids[spec["full_name"]] = by_name[spec["full_name"]]["id"]
            print(f"· employee {spec['full_name']} exists")
            continue
        st, out = req("/payroll/employees", spec, token=tok)
        assert st in (200, 201), (spec["full_name"], out)
        ids[spec["full_name"]] = out["id"]
        print(f"✓ employee {spec['full_name']}")

    # ── two paid 1405 runs (خرداد=3، تیر=4) ─────────────────────────────
    st, accounts = req("/treasury/accounts", token=tok)
    bank = next(a for a in accounts["items"] if a["title"] == "بانک حقوق")
    # مرداد (5) is the PAYROLL v2.1 month: اضافه‌کار from hours and a مأموریت
    # line. خرداد/تیر stay as they were — a paid document is never rewritten,
    # so the new behaviour has to arrive on a NEW month, exactly as it would
    # for a real business.
    # شهریور (6) is left as a DRAFT on purpose: every other month is paid and
    # therefore locked, which leaves nowhere to actually TRY «ویرایش ردیف».
    # An eval world with no editable document is a demo you can only look at.
    for month in (3, 4, 5, 6):
        st, run = req(
            "/payroll/runs",
            {"jalali_year": "1405", "jalali_month": month},
            token=tok,
        )
        if st == 409:
            st2, runs = req("/payroll/runs?limit=50", token=tok)
            run = next(
                r
                for r in runs["items"]
                if r["jalali_year"] == "1405" and r["jalali_month"] == month
            )
            print(f"· run 1405/{month} exists ({run['status']})")
        else:
            assert st in (200, 201), run
            print(f"✓ run 1405/{month} created")
        if run["status"] == "paid":
            continue
        # PAYROLL v2.1 — the ساعتی worker's اضافه‌کار now comes from HOURS, so
        # the eval world shows the ماده ۵۹ formula rather than a typed amount
        # (which would render as «اضافه‌کار دستی» and prove nothing).
        hourly_item = next(
            (
                i
                for i in run["items"]
                if i["employee_id"] == ids.get("حسن ساعتی")
            ),
            None,
        )
        if hourly_item and run["status"] == "draft":
            req(
                f"/payroll/runs/{run['id']}/items/{hourly_item['id']}",
                {"overtime_hours": "26"},
                token=tok,
                method="PATCH",
            )
        # …and the حسابدار goes on a 4-day مأموریت: paid, but outside both the
        # insurance base and the taxable base.
        mission_item = next(
            (
                i
                for i in run["items"]
                if i["employee_id"] == ids.get("لیلا دوفرزندی")
            ),
            None,
        )
        if mission_item and run["status"] == "draft":
            req(
                f"/payroll/runs/{run['id']}/items/{mission_item['id']}",
                {"mission_days": "4", "mission_daily_rate": "2500000"},
                token=tok,
                method="PATCH",
            )
        # NEVER confirm/pay a run with no rows. Found the hard way on dev: a
        # stale EMPTY مرداد draft (created 2026-07-29, zero employees) was
        # sitting there, and adding months to this loop confirmed and paid it —
        # turning stale drift into an inert but undeletable «paid» document.
        # An empty payroll document is not a document.
        if not run.get("items"):
            print(f"⚠ run 1405/{month} has no rows — left untouched")
            continue
        if month == 6:
            print("✓ run 1405/6 left as پیش‌نویس — the editable one")
            continue
        if run["status"] == "draft":
            st, run = req(
                f"/payroll/runs/{run['id']}/status",
                {"status": "confirmed"},
                token=tok,
            )
            assert st == 200, run
        st, run = req(
            f"/payroll/runs/{run['id']}/status",
            {"status": "paid", "paid_from_account_id": bank["id"]},
            token=tok,
        )
        assert st == 200, run
        print(
            f"✓ run 1405/{month} paid — net {run['totals']['net_pay']} rial "
            f"از «بانک حقوق»"
        )

    # ── insurance zip (proof download) ──────────────────────────────────
    st, runs = req("/payroll/runs?limit=50", token=tok)
    tir = next(
        r
        for r in runs["items"]
        if r["jalali_year"] == "1405" and r["jalali_month"] == 4
    )
    st, zip_bytes = req(
        f"/payroll/runs/{tir['id']}/insurance-export", token=tok, raw=True
    )
    assert st == 200 and zip_bytes[:2] == b"PK", (st, zip_bytes[:60])
    print(f"✓ insurance zip for تیر: {len(zip_bytes)} bytes (PK ok)")

    # ── settlement for مریم مستعفی ──────────────────────────────────────
    emp_id = ids["مریم مستعفی"]
    st, existing_st = req(f"/payroll/employees/{emp_id}/settlement", token=tok)
    if existing_st.get("settlement"):
        print(f"· settlement exists ({existing_st['settlement']['status']})")
    else:
        st, created = req(
            f"/payroll/employees/{emp_id}/settlement",
            {
                "termination_date": "2026-07-22",  # پایان تیر ۱۴۰۵
                "reason": "resignation",
                "unused_leave_days": "9",
            },
            token=tok,
        )
        assert st in (200, 201), created
        st, paid = req(
            f"/payroll/settlements/{created['id']}/pay",
            {"paid_from_account_id": bank["id"]},
            token=tok,
        )
        assert st == 200, paid
        st, pdf = req(
            f"/payroll/settlements/{created['id']}/pdf", token=tok, raw=True
        )
        assert st == 200 and pdf[:4] == b"%PDF", (st, pdf[:60])
        print(
            "✓ settlement paid — "
            f"سنوات {paid['severance']} · عیدی {paid['eydi']} · "
            f"مرخصی {paid['leave_buyback']} · مالیات {paid['income_tax']} · "
            f"خالص {paid['net_payable']} rial · PDF {len(pdf)}B"
        )

    # ── marketplace state: payroll_advanced active (admin_manual) ───────
    st, out = req(
        f"/admin/businesses/{biz_id}/entitlements/payroll_advanced",
        {"enabled": True, "note": "EVAL BATCH — دادهٔ ارزیابی مؤسس"},
        token=tok,
        method="PUT",
    )
    print(f"✓ payroll_advanced entitlement ({st})")

    print("\nتمام شد — دادهٔ ارزیابی دیباتک آماده است.")


if __name__ == "__main__":
    main()
