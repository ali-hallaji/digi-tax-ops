"""PART 4.3 — re-walk the lifecycle matrix rows on a FRESH reference.

The matrix's اصلاحیه/ابطال/برگشت rows cite taxids from before the sandbox
reference rotation. A rotated reference answers `0300601` («صورتحساب مرجع یافت
نشد») to every lifecycle operation, so those rows could no longer be reproduced
— not because the product regressed, but because the thing they pointed at is
gone. The fix is a walk, not a code change: register a NEW اصلی and run the
whole chain against it.

Sends, in order, all against the same fresh original:
    اصلی (ins=1) → اصلاحیه (ins=2) → برگشت از فروش (ins=4) → ابطال (ins=3)

Run inside the api container on dev:  python rotation_rewalk.py
"""

import asyncio
import json
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.modules.moadian.application import taxid as taxid_mod
from app.modules.moadian.application.proxy import build_moadian_transport
from app.modules.moadian.application.send_service import (
    _build_invoice_packet,
    _get_signing_material,
    _next_inno,
    _selftsp_base,
)
from app.modules.moadian.application.transport_selftsp import SelfTspTransport

TENANT = "7085fcf2-598e-415a-8d98-2c8d402e6874"  # نیک‌تجارت sandbox (A2HP31)
FISCAL_ID = "A2HP31"
INDATIM = 1785196800000
TINS = "10320296185"
BID = "14008430838"
SSTID = "2800002692993"  # Server — taxable, registered rate ۱۰٪

# Whole Rials with an exact ۱۰٪ so nothing here is also testing the rounding rule.
FEE = 1_000_000
VAT = 100_000


def _line(fee, vat):
    return {
        "sstid": SSTID,
        "sstt": "کالای آزمایشی — بازپیمایش چرخهٔ عمر",
        "am": 1,
        "fee": fee,
        "prdis": fee,
        "dis": 0,
        "adis": fee,
        "vra": 10,
        "vam": vat,
        "tsstam": fee + vat,
    }


def _packet_data(*, ins, irtaxid, fee, vat):
    """A لحظه-consistent header for one lifecycle subject.

    A REFERRING subject (اصلاحی/ابطالی/برگشتی) carries the مرجع taxid and NO
    buyer identity — the org re-fetches the buyer from the reference and treats
    a repeated tob/bid/tinb as «خارج از الگو» (warning 14xxx, proven earlier).
    """
    header = {
        "indatim": INDATIM,
        "inty": 1,
        "inp": 1,
        "ins": ins,
        "tins": TINS,
        "tprdis": fee,
        "tdis": 0,
        "tadis": fee,
        "tvam": vat,
        "todam": 0,
        "tbill": fee + vat,
        "setm": 2,
    }
    if ins == 1:
        header.update({"tob": 2, "bid": BID, "tinb": BID})
    else:
        header["irtaxid"] = irtaxid
    return header, [_line(fee, vat)]


async def _send(db, transport, key, token, *, label, ins, irtaxid, fee, vat, pem):
    serial = await _next_inno(db, FISCAL_ID)
    await db.commit()
    header, body = _packet_data(ins=ins, irtaxid=irtaxid, fee=fee, vat=vat)
    header["inno"] = f"{serial:010X}"
    tax_id = taxid_mod.generate_taxid(
        memory_id=FISCAL_ID, indatim_ms=INDATIM, serial=serial
    )
    header = {"taxid": tax_id, **header}
    data = {"header": header, "body": body, "payments": []}
    packet = _build_invoice_packet(data, fiscal_id=FISCAL_ID, private_pem=pem)
    resp = await transport.send_invoice_packets(
        [packet],
        org_public_key_b64=key.get("key"),
        org_key_id=str(key.get("id")),
        token=token,
    )
    resp.raise_for_status()
    rows = resp.json().get("result") or [{}]
    row = rows[0] if isinstance(rows, list) else {}
    print(f"\n=== {label} (ins={ins}) ===")
    print(f"  taxid     : {tax_id}")
    print(f"  irtaxid   : {irtaxid or '—'}")
    print(f"  send      : {json.dumps(row, ensure_ascii=False)}")
    return tax_id, row.get("referenceNumber")


async def main():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        pem, _cert = await _get_signing_material(db, TENANT)
        transport = SelfTspTransport(
            base_url=_selftsp_base("sandbox"),
            private_key_pem=pem,
            fiscal_id=FISCAL_ID,
            timeout=settings.moadian_timeout_seconds,
            httpx_transport=build_moadian_transport(),
        )
        server = await transport.server_information()
        key = (server.get("publicKeys") or [{}])[0]
        token = (await transport.get_token())["token"]

        sent = []
        original, ref = await _send(
            db, transport, key, token,
            label="اصلی — the FRESH reference everything below points at",
            ins=1, irtaxid=None, fee=FEE, vat=VAT, pem=pem,
        )
        sent.append(("اصلی", original, ref))

        # The org needs the original registered before it will accept a referrer.
        print("\n… waiting 40s for the original to register …")
        await asyncio.sleep(40)
        token = (await transport.get_token())["token"]

        for label, ins, fee, vat in (
            ("اصلاحیه", 2, FEE + 500_000, 150_000),
            ("برگشت از فروش", 4, 400_000, 40_000),
            ("ابطال", 3, FEE + 500_000, 150_000),
        ):
            _tid, r = await _send(
                db, transport, key, token,
                label=label, ins=ins, irtaxid=original, fee=fee, vat=vat, pem=pem,
            )
            sent.append((label, _tid, r))
            await asyncio.sleep(3)

        print("\n… waiting 45s for the org to judge the chain …")
        await asyncio.sleep(45)
        token = (await transport.get_token())["token"]

        print("\n\n#### ROTATION RE-WALK VERDICTS ####")
        for label, tax_id, reference in sent:
            if not reference:
                print(f"\n--- {label}: NOT SENT — {tax_id}")
                continue
            result = await transport.inquiry_by_reference([reference], token=token)
            row = (result or [{}])[0] if isinstance(result, list) else {}
            data = row.get("data") or {}
            errors = data.get("error") or []
            print(f"\n--- {label}  taxid={tax_id}")
            print(f"    status : {row.get('status')}")
            if errors:
                for e in errors:
                    print(f"    error  : {e.get('code')} — {e.get('message')}")
            for w in data.get("warning") or []:
                print(f"    warning: {w.get('code')} — {w.get('message')}")
    await engine.dispose()


asyncio.run(main())
