"""Batch 2 Part 5 — EMPIRICAL wire probe for the PDF re-mine findings #3/#4/#6.

Per the EMPIRICAL-TEST LAW: three questions the PDFs cannot settle, answered by
the org itself on the نیک‌تجارت sandbox. Read-only — this script NEVER submits an
invoice, so the ZERO-TOTAL rule is not in play.

  #3  حد مجاز فروش (sales ceiling) — does GET_FISCAL_INFORMATION actually carry a
      sales-limit field on the wire? (prose + SDK model say yes; the concrete REST
      example does not show it)
  #4  taxpayerStatus enum — which values does GET_ECONOMIC_CODE_INFORMATION really
      return, and does our TAXPAYER_STATUS_FA map cover them?
  #6  article6Status — does the invoice-status inquiry carry it? Checked BOTH
      against every inquiry response we ever recorded (submissions.inquiry_payload_json)
      AND against a fresh live inquiry.

Run inside the api container on dev (DATABASE_URL + sandbox creds present):
  docker compose exec -T api python /tmp/remine_wire_probe.py
"""

import asyncio
import json
import os

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.modules.moadian.application.send_service import (
    _get_signing_material,
    _load_profile_row,
    _selftsp_base,
)
from app.modules.moadian.application.proxy import build_moadian_transport
from app.modules.moadian.application.response_interpreter import TAXPAYER_STATUS_FA
from app.modules.moadian.application.transport_selftsp import (
    SelfTspError,
    SelfTspTransport,
)
from app.modules.moadian.infrastructure.models import MoadianSubmission
from app.core.config import settings

TENANT = os.environ.get("PROBE_TENANT", "7085fcf2-598e-415a-8d98-2c8d402e6874")

# Economic codes to inquire for #4. The first is the sandbox seller itself; the
# rest are real buyers we have already used, plus two deliberately bogus ones so
# the org gets a chance to answer with a non-ACTIVE state.
PROBE_CODES = [
    c
    for c in os.environ.get("PROBE_CODES", "").split(",")
    if c.strip()
] or [
    "14008430838",  # ترازپیشه دیبا (real legal id)
    "10100000000",  # well-formed but almost certainly unallocated
    "11111111111",  # well-formed, deliberately bogus
]

# Anything whose key hints at a limit/ceiling — we do not know the org's spelling,
# so match loosely and print whatever we find.
LIMIT_HINTS = ("limit", "ceiling", "max", "sale", "threshold", "quota", "article")

engine = create_async_engine(os.environ["DATABASE_URL"])
maker = async_sessionmaker(engine, expire_on_commit=False)


def _flat_keys(obj, prefix=""):
    """Every leaf path in a nested dict/list, so no field can hide."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(_flat_keys(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            out.update(_flat_keys(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def _report(label, raw):
    print(f"\n--- {label} ---")
    print(f"raw = {json.dumps(raw, ensure_ascii=False)[:2000]}")
    flat = _flat_keys(raw)
    print(f"keys ({len(flat)}): {sorted(flat.keys())}")
    hits = {
        k: v
        for k, v in flat.items()
        if any(h in k.lower() for h in LIMIT_HINTS)
    }
    print(f"limit/article-shaped keys: {hits or 'NONE'}")
    return flat


async def _transport(db):
    profile = await _load_profile_row(db, TENANT)
    if profile is None or not profile.fiscal_memory_id:
        raise SystemExit("tenant has no Moadian connection — cannot probe")
    private_pem, _cert = await _get_signing_material(db, TENANT)
    env = getattr(profile, "environment", None) or "live"
    print(f"tenant={TENANT} environment={env} mode={settings.moadian_mode}")
    if settings.moadian_mode == "mock":
        raise SystemExit("MOADIAN_MODE=mock — a mock answer is NOT wire evidence")
    return SelfTspTransport(
        base_url=_selftsp_base(env),
        private_key_pem=private_pem,
        fiscal_id=profile.fiscal_memory_id,
        timeout=settings.moadian_timeout_seconds,
        httpx_transport=build_moadian_transport(),
    )


async def probe_fiscal(db, transport, token):
    """#3 — does GET_FISCAL_INFORMATION carry a sales ceiling?"""
    print("\n\n=== FINDING #3 — حد مجاز فروش on GET_FISCAL_INFORMATION ===")
    try:
        raw = await transport.fiscal_information(token=token)
    except SelfTspError as exc:
        print(f"ORG ERROR: {exc}")
        return
    flat = _report("GET_FISCAL_INFORMATION (live sandbox)", raw)
    print(
        "VERDICT #3: "
        + (
            "sales-limit field PRESENT"
            if any("limit" in k.lower() for k in flat)
            else "NO sales-limit field on the wire"
        )
    )


async def probe_taxpayer(db, transport, token):
    """#4 — which taxpayerStatus values does the org really return?"""
    print("\n\n=== FINDING #4 — taxpayerStatus enum on GET_ECONOMIC_CODE_INFORMATION ===")
    seen = {}
    for code in PROBE_CODES:
        try:
            raw = await transport.economic_code_information(code, token=token)
        except SelfTspError as exc:
            print(f"\n--- economicCode={code} ---\nORG ERROR: {exc}")
            continue
        flat = _report(f"economicCode={code}", raw)
        status = str(raw.get("taxpayerStatus") or "").upper()
        if status:
            seen[status] = flat
    print(f"\nstatuses observed: {sorted(seen) or 'NONE'}")
    print(f"our map covers: {sorted(TAXPAYER_STATUS_FA)}")
    missing = [s for s in seen if s not in TAXPAYER_STATUS_FA]
    print(f"VERDICT #4: unmapped statuses = {missing or 'NONE'}")


async def probe_article6(db, transport, token):
    """#6 — article6Status on the invoice-status inquiry. Recorded + fresh."""
    print("\n\n=== FINDING #6 — article6Status on the invoice-status inquiry ===")

    # (a) every inquiry response we have EVER recorded, on any tenant.
    rows = (
        await db.execute(
            text(
                "SELECT inquiry_payload_json FROM moadian_submissions "
                "WHERE inquiry_payload_json IS NOT NULL"
            )
        )
    ).all()
    all_keys, art_hits = set(), []
    for (payload,) in rows:
        try:
            obj = json.loads(payload)
        except Exception:  # noqa: BLE001
            continue
        flat = _flat_keys(obj)
        all_keys.update(flat)
        for k, v in flat.items():
            if "article" in k.lower():
                art_hits.append((k, v))
    print(f"recorded inquiry responses examined: {len(rows)}")
    print(f"distinct keys ever seen: {sorted(all_keys)}")
    print(f"article-shaped keys ever seen: {art_hits or 'NONE'}")

    # (b) a fresh live inquiry on the newest submission that has a reference.
    sub = (
        (
            await db.execute(
                select(MoadianSubmission)
                .where(
                    MoadianSubmission.reference_number.isnot(None),
                    MoadianSubmission.mode == "selftsp",
                )
                .order_by(MoadianSubmission.created_at.desc())
            )
        )
        .scalars()
        .first()
    )
    if sub is None:
        print("no submission with a reference number — fresh inquiry skipped")
        return
    print(f"\nfresh inquiry on reference={sub.reference_number} taxid={sub.taxid}")
    try:
        fresh = await transport.inquiry_by_reference(
            [sub.reference_number], token=token
        )
    except SelfTspError as exc:
        print(f"ORG ERROR: {exc}")
        return
    flat = _report("INQUIRY_BY_REFERENCE_NUMBER (live sandbox)", fresh)
    print(
        "VERDICT #6: "
        + (
            "article6Status PRESENT"
            if any("article" in k.lower() for k in flat) or art_hits
            else "NO article6Status on the wire"
        )
    )


async def main():
    print("=== PDF RE-MINE WIRE PROBE (نیک‌تجارت sandbox, read-only) ===")
    async with maker() as db:
        transport = await _transport(db)
        token = (await transport.get_token())["token"]
        print("token acquired ✓")
        await probe_fiscal(db, transport, token)
        await probe_taxpayer(db, transport, token)
        await probe_article6(db, transport, token)
    print("\n=== DONE ===")


asyncio.run(main())
