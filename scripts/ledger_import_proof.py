"""End-to-end proof of the ledger importer against the founder's REAL exports.

Runs analyze → commit → revert for BOTH sample files on a throwaway tenant, and
prints what an accountant would see. Usage inside the api container:

    python ledger_import_proof.py /samples
"""

import asyncio
import os
import sys
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import app.modules.fiscal_memories.infrastructure.models  # noqa: F401
import app.modules.fiscal_year.infrastructure.models  # noqa: F401
import app.modules.partners.infrastructure.models  # noqa: F401
import app.modules.products.infrastructure.models  # noqa: F401
import app.modules.taxpayers.infrastructure.models  # noqa: F401
from app.modules.accounting.infrastructure.models import (
    ChartAccount,
    JournalEntry,
    JournalLine,
)
from app.modules.identity.infrastructure.models import User
from app.modules.invoice_drafts.infrastructure.models import InvoiceDraft
from app.modules.ledger_import.application import service as S
from app.modules.ledger_import.infrastructure.models import ImportBatch
from app.modules.tenants.infrastructure.models import Tenant

SAMPLES = sys.argv[1] if len(sys.argv) > 1 else "/samples"
TADBIR = f"{SAMPLES}/فروش حسابداری تدبیر.xls"
SEPIDAR = f"{SAMPLES}/حقوق دستمزد سپيدار.xls"


def money(value) -> str:
    return f"{Decimal(str(value)):,.0f}"


async def main() -> None:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    db = AsyncSession(engine, expire_on_commit=False)
    tid = uuid4()
    db.add(Tenant(id=tid, name="اثبات ورود", slug=f"imp-{tid.hex[:8]}"))
    await db.flush()
    user = User(mobile=f"0912{tid.int % 10_000_000:07d}", role="owner")
    db.add(user)
    await db.commit()

    try:
        # ── 1. تدبیر sales ────────────────────────────────────────────────
        data = open(TADBIR, "rb").read()
        report = await S.analyze(db, tenant_id=tid, file_bytes=data, file_name="tadbir.xls")
        print("=== ANALYZE — تدبیر ===")
        print(f"  profile      : {report['source_label']} ({report['file_format']})")
        print(f"  rows         : {report['row_count']}  importable={report['importable']}")
        print(f"  total        : {money(report['total_amount'])} ریال")
        print(f"  customer hint: {report['with_customer_hint']} rows")
        print(f"  columns      : {len(report['column_mapping'])} mapped")
        for w in report["warnings"][:3]:
            print(f"  ⚠ {w}")
        hinted = [r for r in report["rows"] if r["party_hint"]["mobile"]][:2]
        for r in hinted:
            print(
                f"  hint row {r['row']}: {r['party_hint']['name']} / "
                f"{r['party_hint']['mobile']} → total {money(r['total'])}"
            )

        choices = {
            str(r["row"]): {"action": "create" if r["party_hint"]["mobile"] else "skip"}
            for r in report["rows"]
        }
        result = await S.commit_sales(
            db,
            tenant_id=tid,
            user_id=user.id,
            file_bytes=data,
            file_name="tadbir.xls",
            choices=choices,
        )
        print("=== COMMIT — تدبیر ===")
        print(f"  invoices     : {result['created']}  skipped={result['skipped']}")
        print(f"  customers    : {result['customers_created']}")
        print(f"  total        : {money(result['total_amount'])} ریال")

        drafts = (
            (
                await db.execute(
                    select(InvoiceDraft).where(InvoiceDraft.tenant_id == tid)
                )
            )
            .scalars()
            .all()
        )
        assert len(drafts) == result["created"], "draft count must match"
        assert all(d.invoice_type == "internal_private" for d in drafts), (
            "imported sales must be INTERNAL — never re-submitted to the org"
        )
        stored = sum(Decimal(str(d.total_amount or 0)) for d in drafts)
        print(f"  stored sum   : {money(stored)} ریال  (file said {money(result['total_amount'])})")

        # ── 2. سپیدار payroll ────────────────────────────────────────────
        data2 = open(SEPIDAR, "rb").read()
        report2 = await S.analyze(
            db, tenant_id=tid, file_bytes=data2, file_name="sepidar.xls"
        )
        print("=== ANALYZE — سپیدار ===")
        print(f"  profile      : {report2['source_label']} ({report2['file_format']})")
        print(f"  rows         : {report2['row_count']}")
        print(f"  debit/credit : {money(report2['debit_total'])} / {money(report2['credit_total'])}")
        print(
            f"  balancing    : {money(report2['balancing_amount'])} → "
            f"{report2['balancing_account']['code']} {report2['balancing_account']['title']}"
        )
        for w in report2["warnings"]:
            print(f"  ⚠ {w}")
        for r in report2["rows"]:
            target = next(
                (a for a in report2["accounts"] if a["id"] == r["target_account_id"]),
                None,
            )
            print(
                f"  {r['source_code']:>8} {r['title'][:34]:<34} "
                f"{money(r['debit']):>16} → {(target or {}).get('title', '—')}"
            )

        targets = {str(r["row"]): r["target_account_id"] for r in report2["rows"]}
        from datetime import date

        result2 = await S.commit_voucher(
            db,
            tenant_id=tid,
            user_id=user.id,
            file_bytes=data2,
            file_name="sepidar.xls",
            entry_date=date(2026, 7, 5),
            description="حقوق و دستمزد — ورود از سپیدار",
            targets=targets,
        )
        print("=== COMMIT — سپیدار ===")
        print(f"  entry        : {result2['journal_entry_id']}  lines={result2['lines']}")
        lines = (
            (
                await db.execute(
                    select(JournalLine).where(
                        JournalLine.entry_id == result2["journal_entry_id"]
                    )
                )
            )
            .scalars()
            .all()
        )
        debit = sum(ln.debit for ln in lines)
        credit = sum(ln.credit for ln in lines)
        print(f"  balanced     : debit {money(debit)} == credit {money(credit)} → {debit == credit}")
        assert debit == credit and debit > 0, "the voucher MUST balance"

        # ── 3. undo ───────────────────────────────────────────────────────
        batches = await S.list_batches(db, tenant_id=tid)
        print("=== BATCHES ===")
        for b in batches:
            print(f"  {b['source_label']}: {b['created_count']} created, {b['total_amount']}")
        undo = await S.revert_batch(db, tenant_id=tid, batch_id=batches[0]["id"])
        print(f"=== REVERT newest === removed={undo['removed']} kept={undo['kept']}")
        left = (
            (
                await db.execute(
                    select(JournalEntry).where(
                        JournalEntry.tenant_id == tid, JournalEntry.is_manual.is_(True)
                    )
                )
            )
            .scalars()
            .all()
        )
        print(f"  manual entries remaining: {len(left)}")
        print("\nALL CHECKS PASSED")
    finally:
        await db.execute(delete(JournalLine).where(JournalLine.tenant_id == tid))
        await db.execute(delete(JournalEntry).where(JournalEntry.tenant_id == tid))
        await db.execute(
            text("DELETE FROM manual_entry_events WHERE tenant_id = :t"), {"t": tid}
        )
        await db.execute(
            text("DELETE FROM invoice_draft_lines WHERE tenant_id = :t"), {"t": tid}
        )
        await db.execute(delete(InvoiceDraft).where(InvoiceDraft.tenant_id == tid))
        await db.execute(delete(ImportBatch).where(ImportBatch.tenant_id == tid))
        await db.execute(text("DELETE FROM customers WHERE tenant_id = :t"), {"t": tid})
        for lvl in (4, 3, 2, 1):
            await db.execute(
                delete(ChartAccount).where(
                    ChartAccount.tenant_id == tid, ChartAccount.level == lvl
                )
            )
        await db.execute(text("DELETE FROM users WHERE id = :u"), {"u": user.id})
        await db.execute(delete(Tenant).where(Tenant.id == tid))
        await db.commit()
        await db.close()
        await engine.dispose()


asyncio.run(main())
