"""FINISH-LINE Part 1 — the clean end-to-end proof of the inp/inty omission.

The A/B experiment answered the WARNING question decisively (present → 14007+14004,
omitted → []), but both variants also hit an unrelated `0300601` («شمارهٔ مالیاتی
صورتحساب مرجع منطبق نیست») because their reference invoices are old sandbox rows.

This proves the whole chain on FRESH data with the shipped code:
    1. create + finalize + submit a NEW original  → register it, capture its taxid
    2. issue a corrective off THAT original       → submit
    3. read the org verdict: registered, and «warning»: [] (no 14007/14004)

Sandbox only. Run inside the api container on dev:
    docker compose exec -T api python - < scripts/corrective_clean_proof.py
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import date
from decimal import Decimal

import app.modules.identity.infrastructure.models  # noqa: F401
import app.modules.partners.infrastructure.models  # noqa: F401
import app.modules.tenants.infrastructure.models  # noqa: F401
from sqlalchemy import select

from app.database.session import async_session_maker
from app.modules.invoice_drafts.application.services import (
    finalize_invoice_draft_for_tenant,
)
from app.modules.invoice_drafts.infrastructure.models import InvoiceDraft, InvoiceDraftLine
from app.modules.moadian.application.send_service import (
    create_corrective,
    refresh_submission,
    submit_invoices,
)
from app.modules.moadian.infrastructure.models import MoadianSubmission

TENANT = os.environ.get("EXP_TENANT", "7085fcf2-598e-415a-8d98-2c8d402e6874")
SSTID = os.environ.get("EXP_SSTID", "2800002692993")


async def _verdict(db, invoice_id, label: str) -> dict:
    await asyncio.sleep(10)
    sub = (
        await db.execute(
            select(MoadianSubmission)
            .where(MoadianSubmission.invoice_id == invoice_id)
            .order_by(MoadianSubmission.created_at.desc())
            .limit(1)
        )
    ).scalar_one()
    try:
        await refresh_submission(db, str(sub.id))
        await db.refresh(sub)
    except Exception as exc:  # noqa: BLE001
        print(f"[{label}] refresh note: {type(exc).__name__}")
    payload = sub.inquiry_payload_json or sub.response_payload_json or {}
    data = payload.get("data", payload) if isinstance(payload, dict) else {}
    header = (sub.request_payload_json or {}).get("header", {})
    return {
        "label": label,
        "status": sub.status,
        "taxid": sub.taxid,
        "ins_sent": header.get("ins"),
        "inp_in_packet": "inp" in header,
        "inty_in_packet": "inty" in header,
        "errors": data.get("error") or [],
        "warnings": data.get("warning") or [],
    }


async def main() -> int:
    out = []
    async with async_session_maker() as db:
        # ── 1. a fresh نوع دوم original (walk-in — no buyer identity needed) ──
        draft = InvoiceDraft(
            tenant_id=TENANT,
            kind="tax_reportable",
            status="draft",
            issue_date=date.today(),
            moadian_type_override="2",
        )
        db.add(draft)
        await db.flush()
        db.add(
            InvoiceDraftLine(
                draft_id=draft.id,
                tenant_id=TENANT,
                free_line_title="کالای تست اصلاحیه",
                tax_item_id=SSTID,
                unit_code="1627",
                quantity=Decimal("2"),
                unit_price=Decimal("1000000"),
                discount_amount=Decimal("0"),
                vat_rate=Decimal("10"),
            )
        )
        await db.commit()

        await finalize_invoice_draft_for_tenant(
            db, tenant_id=TENANT, invoice_id=str(draft.id)
        )
        await db.refresh(draft)
        print(f"[original] finalized {draft.document_number}")
        await submit_invoices(db, tenant_id=TENANT, invoice_ids=[str(draft.id)])
        orig = await _verdict(db, draft.id, "1_original")
        out.append(orig)
        print(f"[original] {orig['status']} taxid={orig['taxid']}")

        if orig["status"] not in ("accepted", "registered"):
            print("[stop] original did not register — cannot correct it")
            print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
            return 1

        # ── 2. a corrective off THAT original, with the shipped omission ──
        corr = await create_corrective(
            db, tenant_id=TENANT, invoice_id=str(draft.id)
        )
        corr_id = corr["id"] if isinstance(corr, dict) else str(corr)
        await finalize_invoice_draft_for_tenant(
            db, tenant_id=TENANT, invoice_id=str(corr_id)
        )
        cdraft = (
            await db.execute(select(InvoiceDraft).where(InvoiceDraft.id == corr_id))
        ).scalar_one()
        print(f"[corrective] finalized {cdraft.document_number}")
        await submit_invoices(db, tenant_id=TENANT, invoice_ids=[str(corr_id)])
        out.append(await _verdict(db, corr_id, "2_corrective"))

    print("\n===== CLEAN PROOF =====")
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
