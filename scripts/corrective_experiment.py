"""Batch 2 Part 2 — EMPIRICAL corrective experiment on نیک‌تجارت sandbox.

Question the founder blocked on: which corrective (ins=2) item edits does the org
actually ACCEPT? We already know from MOADIAN F (INV-2026-000027, ثبت شد) that
REMOVE-a-line and qty+price+discount are ACCEPTED. This tests the two remaining
locks empirically (EMPIRICAL-TEST LAW):
  (a) ADD a brand-new line to a corrective
  (c) REPLACE a line's شناسه کالا/خدمت (sstid) with a different valid one

For each: create the corrective draft (engine), apply the mutation the UI currently
forbids, finalize, submit to the sandbox, inquire the org's real verdict. Run inside
the api container on dev (DATABASE_URL + sandbox config present). Prints a verdict table.
"""

import asyncio
import os
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.modules.invoice_drafts.application.services import (
    _load_lines,
    _recalculate_totals,
    finalize_invoice_draft_for_tenant,
)
from app.modules.invoice_drafts.infrastructure.models import (
    InvoiceDraft,
    InvoiceDraftLine,
)
from app.modules.moadian.application.send_service import (
    create_corrective,
    refresh_submission,
    submit_invoices,
)

TENANT = "7085fcf2-598e-415a-8d98-2c8d402e6874"
engine = create_async_engine(os.environ["DATABASE_URL"])
maker = async_sessionmaker(engine, expire_on_commit=False)


def _amts(qty, price, vat_rate, discount=0):
    sub = Decimal(str(qty)) * Decimal(str(price)) - Decimal(str(discount))
    vat = (sub * Decimal(str(vat_rate)) / Decimal("100")).quantize(Decimal("1.0000"))
    return sub, vat, sub + vat


async def _recompute(db, corr_id):
    draft = (
        await db.execute(select(InvoiceDraft).where(InvoiceDraft.id == corr_id))
    ).scalar_one()
    lines = await _load_lines(db, draft_id=corr_id)
    await _recalculate_totals(db, draft=draft, lines=lines)
    await db.commit()


async def _finalize_submit_inquire(db, corr_id, label):
    await finalize_invoice_draft_for_tenant(
        db, tenant_id=TENANT, invoice_id=str(corr_id)
    )
    subs = await submit_invoices(db, TENANT, [str(corr_id)])
    sub = subs[0]
    result = {"status": sub.get("status")}
    for _ in range(8):
        await asyncio.sleep(5)
        result = await refresh_submission(db, str(sub["submission_id"]))
        if result.get("status") in ("accepted", "rejected", "unknown"):
            break
    print(
        f"\n### {label}\n  taxid={sub.get('taxid')}\n"
        f"  final_status={result.get('status')}\n"
        f"  status_fa={result.get('status_fa')}\n"
        f"  org_reason={result.get('error_message') or result.get('org_message') or '—'}\n"
        f"  raw_status={result.get('status')}"
    )
    return result


async def experiment_add(original_id):
    async with maker() as db:
        detail = await create_corrective(db, TENANT, original_id)
        corr_id = uuid.UUID(detail["id"])
        existing = (await _load_lines(db, draft_id=corr_id))[0]
        sub, vat, tot = _amts(1, 1000000, 10)
        db.add(
            InvoiceDraftLine(
                tenant_id=existing.tenant_id,
                invoice_draft_id=corr_id,
                line_no=90,
                free_line_title="ردیف افزودهٔ آزمایشی (ADD)",
                product_display_title="ردیف افزودهٔ آزمایشی (ADD)",
                tax_item_id="2800002692993",
                unit_code=existing.unit_code,
                quantity=Decimal("1"),
                unit_price=Decimal("1000000"),
                discount_amount=Decimal("0"),
                vat_rate=Decimal("10"),
                line_subtotal=sub,
                line_vat_amount=vat,
                line_total=tot,
            )
        )
        await db.commit()
        await _recompute(db, corr_id)
        return await _finalize_submit_inquire(db, corr_id, "EXPERIMENT (a) ADD a line")


async def experiment_replace_sstid(original_id, new_sstid):
    async with maker() as db:
        detail = await create_corrective(db, TENANT, original_id)
        corr_id = uuid.UUID(detail["id"])
        line = (await _load_lines(db, draft_id=corr_id))[0]
        old = line.tax_item_id
        line.tax_item_id = new_sstid  # same VAT rate (10%), so amounts unchanged
        await db.commit()
        print(f"\n(replace sstid on corrective: {old} -> {new_sstid})")
        await _recompute(db, corr_id)
        return await _finalize_submit_inquire(
            db, corr_id, "EXPERIMENT (c) REPLACE a line's sstid"
        )


async def main():
    print("=== CORRECTIVE EMPIRICAL EXPERIMENT (نیک‌تجارت sandbox) ===")
    # (a) ADD — corrective of INV-2026-000022 (accepted, 1 line @ 2800002692993/10%)
    try:
        await experiment_add("59a6f1bd-f926-4daa-8dc9-0332bcc91bac")
    except Exception as e:  # noqa: BLE001
        print(f"\n### EXPERIMENT (a) ADD — ERROR: {type(e).__name__}: {e}")
    # (c) REPLACE sstid — corrective of INV-2026-000023 (2800002692993/10% -> 2001666836426/10%)
    try:
        await experiment_replace_sstid(
            "59aa5e89-d4f9-4798-94fd-2e7c0c9eb253", "2001666836426"
        )
    except Exception as e:  # noqa: BLE001
        print(f"\n### EXPERIMENT (c) REPLACE sstid — ERROR: {type(e).__name__}: {e}")
    print("\n=== DONE ===")


asyncio.run(main())
