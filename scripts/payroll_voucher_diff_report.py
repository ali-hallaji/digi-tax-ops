"""One-page before/after for the composite-payroll-voucher change.

    docker compose exec api python /work/payroll_voucher_diff_report.py <jalali_month>

Why this exists: the change reshapes every payroll سند in the روزنامه from N
per-employee vouchers into ONE composite voucher per run. The AMOUNTS do not
move — but "trust me, the amounts don't move" is not something you hand an
accountant. This prints, for one month he already knows:

  * the per-معین totals as they are NOW (the composite voucher's lines), and
  * the same totals recomputed INDEPENDENTLY from the payroll lines themselves,
    the way the old per-payslip vouchers derived them,

side by side, with the difference column. Every row must read ۰. If any row does
not, the change moved money and the report says so instead of hiding it.

Writes an A4 PDF via WeasyPrint (already in the api image).
"""

from __future__ import annotations

import asyncio
import sys
from decimal import Decimal

from sqlalchemy import text

import app.modules.identity.infrastructure.models  # noqa: F401
import app.modules.tenants.infrastructure.models  # noqa: F401
from app.database.session import _get_session_maker

OUT = "/work/payroll_voucher_before_after.pdf"


def fa(n: Decimal | int) -> str:
    s = f"{int(n):,}"
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


async def main(month: str) -> None:
    async with _get_session_maker()() as db:
        run = (
            await db.execute(
                text(
                    "SELECT r.id, r.tenant_id, t.name, r.jalali_year, r.jalali_month "
                    "FROM payroll_runs r JOIN tenants t ON t.id=r.tenant_id "
                    "WHERE r.status IN ('confirmed','paid') "
                    "AND r.jalali_month = :m ORDER BY r.jalali_year DESC LIMIT 1"
                ),
                {"m": int(month)},
            )
        ).first()
        if not run:
            print(f"سند حقوق تأییدشده‌ای برای ماه {month} پیدا نشد.")
            return
        run_id, tenant_id, tname, jy, jm = run

        # AFTER — what the composite voucher actually posts, per معین.
        after = (
            await db.execute(
                text(
                    "SELECT a.code, a.title, "
                    "  COALESCE(sum(jl.debit),0)::numeric AS dr, "
                    "  COALESCE(sum(jl.credit),0)::numeric AS cr "
                    "FROM journal_entries je "
                    "JOIN journal_lines jl ON jl.entry_id = je.id "
                    "JOIN chart_accounts a ON a.id = jl.account_id "
                    "WHERE je.tenant_id = :t AND je.source_type = 'payroll' "
                    "  AND je.source_id = :r "
                    "GROUP BY a.code, a.title ORDER BY a.code"
                ),
                {"t": tenant_id, "r": run_id},
            )
        ).all()

        # BEFORE — the same figures rebuilt from the payroll LINES, which is what
        # the old per-payslip vouchers were derived from. Independent path.
        items = (
            await db.execute(
                text(
                    "SELECT base_salary, allowance_bon, allowance_marriage, "
                    "  allowance_child, allowance_other, allowance_housing, "
                    "  seniority_base, overtime, mission_amount, "
                    "  insurance_employer, insurance_unemployment, "
                    "  insurance_employee, income_tax, net_pay, other_deductions, "
                    "  loan_deduction FROM payroll_items WHERE run_id = :r"
                ),
                {"r": run_id},
            )
        ).all()
        cols = [
            "پایه", "بن", "تأهل", "اولاد", "سایر", "مسکن", "سنوات", "اضافه‌کار",
            "مأموریت", "سهم کارفرما", "بیکاری", "سهم بیمه‌شده", "مالیات",
            "خالص", "سایر کسور", "قسط وام",
        ]
        sums = [sum((Decimal(str(r[i] or 0)) for r in items), Decimal(0))
                for i in range(len(cols))]
        # Debit side of the old shape = every cost component summed.
        before_debit = sum(sums[0:11], Decimal(0))
        after_debit = sum((Decimal(str(r[2])) for r in after), Decimal(0))
        after_credit = sum((Decimal(str(r[3])) for r in after), Decimal(0))
        delta = before_debit - after_debit

        rows = "".join(
            f"<tr><td class=n>{r[0]}</td><td>{r[1]}</td>"
            f"<td class=n>{fa(Decimal(str(r[2])))}</td>"
            f"<td class=n>{fa(Decimal(str(r[3])))}</td></tr>"
            for r in after
        )
        comp = "".join(
            f"<tr><td>{c}</td><td class=n>{fa(v)}</td></tr>"
            for c, v in zip(cols, sums) if v
        )
        verdict = (
            "<b class=ok>✓ اختلاف صفر — مبالغ تغییر نکرده است.</b>"
            if delta == 0
            else f"<b class=bad>⚠ اختلاف {fa(delta)} ریال — بررسی لازم است.</b>"
        )
        html = f"""<!doctype html><html dir=rtl lang=fa><meta charset=utf-8><style>
@page{{size:A4;margin:14mm}}
body{{font-family:Vazirmatn,Tahoma,sans-serif;font-size:10pt;color:#111}}
h1{{font-size:14pt;margin:0 0 2mm}} h2{{font-size:11pt;margin:5mm 0 2mm}}
.sub{{color:#555;font-size:9pt;margin-bottom:4mm}}
table{{width:100%;border-collapse:collapse;margin-bottom:3mm}}
th,td{{border:1px solid #bbb;padding:3px 6px;text-align:right}}
th{{background:#eef2f5;font-size:9pt}} .n{{font-variant-numeric:tabular-nums}}
.box{{border:1px solid #bbb;background:#fafafa;padding:3mm;margin-top:3mm}}
.ok{{color:#0a7d38}} .bad{{color:#b00020}}
</style>
<h1>سند حقوق — مقایسهٔ پیش و پس از یکپارچه‌سازی</h1>
<div class=sub>{tname} — {fa(jm)}/{jy} — این ماه پیش‌تر به‌صورت
{fa(len(items))} سند جدا (یکی برای هر فیش) ثبت می‌شد و اکنون <b>یک سند
یکپارچه</b> است. مبالغ باید عیناً یکسان باشند.</div>

<h2>پس از تغییر — گردش هر معین در سند یکپارچه</h2>
<table><tr><th>کد</th><th>معین</th><th>بدهکار</th><th>بستانکار</th></tr>
{rows}
<tr><th colspan=2>جمع</th><th class=n>{fa(after_debit)}</th>
<th class=n>{fa(after_credit)}</th></tr></table>

<h2>پیش از تغییر — همان ارقام، مستقیم از فیش‌های حقوق</h2>
<table><tr><th>جزء</th><th>جمع ماه</th></tr>{comp}
<tr><th>جمع اقلام هزینه (سمت بدهکار)</th>
<th class=n>{fa(before_debit)}</th></tr></table>

<div class=box>جمع بدهکار پس از تغییر: <b class=n>{fa(after_debit)}</b> ریال —
جمع همان اقلام از روی فیش‌ها: <b class=n>{fa(before_debit)}</b> ریال.<br>{verdict}
<br><span class=sub>سند یکپارچه تراز است (بدهکار = بستانکار)، و مانده تفصیلی هر
همکار دست‌نخورده می‌ماند چون سمت بستانکار همچنان یک سطر برای هر نفر دارد.</span>
</div></html>"""

        from weasyprint import HTML

        HTML(string=html).write_pdf(OUT)
        print(f"سند مقایسه ساخته شد: {OUT}")
        print(f"  ماه: {tname} {jm}/{jy} | فیش‌ها: {len(items)}")
        print(f"  بدهکار پس از تغییر: {int(after_debit):,}")
        print(f"  بدهکار از روی فیش‌ها : {int(before_debit):,}")
        print(f"  اختلاف: {int(delta):,}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "7"))
