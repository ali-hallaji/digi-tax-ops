"""FINISH-LINE Part 1 — EMPIRICAL: does omitting inp/inty kill 14007/14004?

Standing question (MOADIAN F, matrix E3 follow-up): a نوع دوم corrective REGISTERS
(«ثبت شد») but the org returns a non-blocking تذکر that «الگوی صورتحساب» (inp) and
«نوع صورتحساب» (inty) are «خارج از الگو» — codes 14007 / 14004. Our packet blanks
only the BUYER on referring subjects (ins 2/3/4, جدول ۱۰ ردیف ۴); the org's ideal
appears to also want inty/inp gone on a corrective.

Per the EMPIRICAL-TEST LAW we ask the org instead of the PDF. Two correctives off
registered originals on the نیک‌تجارت SANDBOX:

    A (control)  inp/inty exactly as today
    B (variant)  inp/inty omitted from the header

For each: create corrective → finalize → submit → inquire → record the org's real
verdict and its full warning list. The comparison decides the product:
  * B registers with NO 14007/14004  → adopt omission for referring subjects.
  * B rejected / new errors          → keep today's packet, document as org-side
                                       noise, and close the item as EXPLAINED.

Sandbox only. Run inside the api container on dev:
    docker compose exec -T api python /app/scripts/corrective_fields_experiment.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

import app.modules.identity.infrastructure.models  # noqa: F401
import app.modules.partners.infrastructure.models  # noqa: F401
import app.modules.tenants.infrastructure.models  # noqa: F401
from sqlalchemy import select

from app.database.session import async_session_maker
from app.modules.invoice_drafts.application.services import (
    finalize_invoice_draft_for_tenant,
)
from app.modules.invoice_drafts.infrastructure.models import InvoiceDraft
from app.modules.moadian.infrastructure.models import MoadianSubmission
from app.modules.moadian.application import send_service as SS  # noqa: N812
from app.modules.moadian.application.send_service import (
    create_corrective,
    refresh_submission,
    submit_invoices,
)

TENANT = os.environ.get("EXP_TENANT", "7085fcf2-598e-415a-8d98-2c8d402e6874")

# Two DIFFERENT registered originals: the org allows only ONE open corrective per
# invoice, so the control and the variant cannot share a parent.
ORIGINALS = {
    "A_control": os.environ.get("EXP_ORIG_A", "0229a545-814d-40b2-9bd6-501db7000a3e"),
    "B_omit": os.environ.get("EXP_ORIG_B", "ac9acaf7-db81-4cf7-bcc9-600ee720eb58"),
}

_REFERRING = (2, 3, 4)  # اصلاحیه / ابطال / برگشت از فروش


def patch_omit_inp_inty() -> None:
    """Variant B — drop inp/inty from the packet on REFERRING subjects only.

    Wraps `build_submission_payload` (the ONE place the org-shaped data is
    produced) rather than shipping a flag: an unproven packet change is exactly
    what the EMPIRICAL-TEST LAW exists to prevent. If the org blesses it, it
    becomes real code in the same batch.
    """
    original = SS.build_submission_payload

    async def wrapped(*args, **kwargs):
        data = await original(*args, **kwargs)
        if int(data.get("ins") or 1) in _REFERRING:
            data.pop("inp", None)
            data.pop("inty", None)
            print("   [variant] inp/inty removed from packet")
        return data

    SS.build_submission_payload = wrapped


async def _run_one(db, label: str, original_id: str) -> dict:
    corr = await create_corrective(db, tenant_id=TENANT, invoice_id=original_id)
    corr_id = corr["id"] if isinstance(corr, dict) else str(corr)
    print(f"[{label}] corrective draft {corr_id}")

    await finalize_invoice_draft_for_tenant(db, tenant_id=TENANT, invoice_id=corr_id)
    draft = (
        await db.execute(select(InvoiceDraft).where(InvoiceDraft.id == corr_id))
    ).scalar_one()
    print(f"[{label}] finalized as {draft.document_number}")

    await submit_invoices(db, tenant_id=TENANT, invoice_ids=[corr_id])
    # Read the submission back from the DB rather than trusting a return shape —
    # the org verdict lives on the row and that is what we are here to record.
    await asyncio.sleep(10)
    sub = (
        await db.execute(
            select(MoadianSubmission)
            .where(MoadianSubmission.invoice_id == corr_id)
            .order_by(MoadianSubmission.created_at.desc())
            .limit(1)
        )
    ).scalar_one()
    try:
        await refresh_submission(db, str(sub.id))
        await db.refresh(sub)
    except Exception as exc:  # noqa: BLE001 — the row already carries the verdict
        print(f"[{label}] refresh note: {type(exc).__name__}")

    payload = sub.inquiry_payload_json or sub.response_payload_json or {}
    data = payload.get("data", payload) if isinstance(payload, dict) else {}
    return {
        "label": label,
        "document_number": draft.document_number,
        "submission_id": str(sub.id),
        "status": sub.status,
        "taxid": sub.taxid,
        "errors": data.get("error"),
        "warnings": data.get("warning"),
    }


async def main() -> int:
    variant = sys.argv[1] if len(sys.argv) > 1 else "both"
    results = []
    async with async_session_maker() as db:
        if variant in ("both", "A"):
            results.append(await _run_one(db, "A_control", ORIGINALS["A_control"]))
        if variant in ("both", "B"):
            patch_omit_inp_inty()
            results.append(await _run_one(db, "B_omit", ORIGINALS["B_omit"]))

    print("\n===== VERDICT TABLE =====")
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
