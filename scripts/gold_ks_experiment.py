"""CONTINUATION 2 Part A — controlled KS experiment for الگوی سوم (طلا).

EMPIRICAL-TEST LAW. The org accepted our pattern-3 packet shape, taxid, signing and
transport, but rejected ONE numeric field on a single-line exempt-gold invoice:

    0204501 — «مقدار فیلد «مبلغ مالیات بر ارزش افزوده(KS)» در قلم کالای «1»
               صورتحساب از لحاظ قواعد محاسباتی و منطقی معتبر نیست.»

This script submits the bounded hypothesis space to the نیک‌تجارت **sandbox**, ONE
variable at a time, on fresh serials (rotation law). Every variant keeps the SAME
money (tadis 29,037,339 / tbill as derived), the SAME buyer/seller/settlement header
and the SAME issue date as the rejected control — only the LINE STRUCTURE and the KS
value change, so the org's verdict is attributable.

Variants (see docs/moadian/gold_pattern3_sandbox_2026-07-28.md for the write-up):

  V1  two lines — exempt gold line (vra 0, vam 0, NO gold trio) + a taxable
      «خدمات طلاسازی» line carrying اجرت+سود at vra 10 with vam on it.
      This is what the research's own product advice literally describes.
  V1b two lines as V1, but the gold trio (consfee/bros/spro/tcpbs) is ALSO
      declared on the exempt gold line with vam 0 — in case the schema binds the
      trio to the gold line while the VAT is carried by the fee line.
  V2  single exempt line, trio declared, vam = 0 (the org computes/expects zero
      VAT on a line whose stuffid rate is zero; fee taxation implicit via tcpbs).
  V3  the rejected control, re-sent on a fresh reference — proves the rejection is
      about the value and not a stale/duplicated reference.
  V4  single exempt line, trio declared, vam = 9% of TAs (the ترازسامانه worked
      example's own literal 489,540) — probes whether the org holds a gold rate
      that differs from the general rate we apply.

Usage (inside the api container on dev, which has DATABASE_URL + sandbox config):

    python gold_ks_experiment.py V1 V1b V2        # run a subset, in order
    python gold_ks_experiment.py all
"""

import asyncio
import json
import os
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.modules.moadian.application import taxid as taxid_mod
from app.modules.moadian.application.send_service import (
    _build_invoice_packet,
    _get_signing_material,
    _next_inno,
    _selftsp_base,
)
from app.modules.moadian.application.proxy import build_moadian_transport
from app.modules.moadian.application.transport_selftsp import SelfTspTransport
from app.core.config import settings

TENANT = "7085fcf2-598e-415a-8d98-2c8d402e6874"  # نیک‌تجارت sandbox (A2HP31)

# ── The control's exact money and header identity (attempt 2, taxid …9168B2) ──
INDATIM = 1785110400000
TINS = "10320296185"
BID = "14008430838"
SETM = 2

GOLD_SSTID = "2001584175153"  # شمش طلا، خلوص 99.5٪ — vat_rate 0, tax_status exempt
GOLD_TITLE = "شمش طلا ۱۰۰۰ گرمی"
FEE_SSTID = "2330003069611"  # خدمات طلاسازی/حق‌العمل ساخت زیورآلات — vat_rate 10
FEE_TITLE = "اجرت ساخت و سود فروشنده"

ES = 23_598_000  # ارزش طلای خام (معاف)
TA = 3_539_700  # اجرت ساخت
TA2 = 0  # حق‌العمل
TA3 = 1_899_639  # سود فروشنده
TAS = TA + TA2 + TA3  # 5,439,339
KS10 = 543_934  # ۱۰٪ × TAs, half-up
KS9 = 489_540  # ۹٪ × TAs truncated — the ترازسامانه example's literal


def _header(*, tprdis, tdis, tadis, tvam, tbill):
    """Header identical to the control except the derived totals."""
    return {
        "inno": None,  # filled per-variant with the fresh serial
        "indatim": INDATIM,
        "inty": 1,
        "inp": 3,
        "ins": 1,
        "tins": TINS,
        "tob": 2,
        "bid": BID,
        "tinb": BID,
        "tprdis": tprdis,
        "tdis": tdis,
        "tadis": tadis,
        "tvam": tvam,
        "todam": 0,
        "tbill": tbill,
        "setm": SETM,
    }


def _line(sstid, sstt, *, fee, adis, vra, vam, tsstam, trio=False):
    row = {
        "sstid": sstid,
        "sstt": sstt,
        "am": 1,
        "fee": fee,
        "prdis": fee,
        "dis": 0,
        "adis": adis,
        "vra": vra,
        "vam": vam,
        "tsstam": tsstam,
    }
    if trio:
        row.update({"consfee": TA, "bros": TA2, "spro": TA3, "tcpbs": TAS})
    return row


def variant_v1():
    """Exempt gold line (no trio) + taxable fee line carrying the VAT."""
    gold = _line(GOLD_SSTID, GOLD_TITLE, fee=ES, adis=ES, vra=0, vam=0, tsstam=ES)
    fee = _line(
        FEE_SSTID, FEE_TITLE, fee=TAS, adis=TAS, vra=10, vam=KS10, tsstam=TAS + KS10
    )
    return _header(
        tprdis=ES + TAS,
        tdis=0,
        tadis=ES + TAS,
        tvam=KS10,
        tbill=ES + TAS + KS10,
    ), [gold, fee]


def variant_v1b():
    """As V1 but the trio is ALSO declared on the gold line (vam still 0)."""
    gold = _line(
        GOLD_SSTID, GOLD_TITLE, fee=ES, adis=ES, vra=0, vam=0, tsstam=ES, trio=True
    )
    fee = _line(
        FEE_SSTID, FEE_TITLE, fee=TAS, adis=TAS, vra=10, vam=KS10, tsstam=TAS + KS10
    )
    return _header(
        tprdis=ES + TAS,
        tdis=0,
        tadis=ES + TAS,
        tvam=KS10,
        tbill=ES + TAS + KS10,
    ), [gold, fee]


def _single(vam):
    """Single exempt line with the trio — Is = Es + TAs − Gs, Os = Ks + Is."""
    adis = ES + TAS
    line = _line(
        GOLD_SSTID,
        GOLD_TITLE,
        fee=ES,
        adis=adis,
        vra=0,
        vam=vam,
        tsstam=adis + vam,
        trio=True,
    )
    return _header(
        tprdis=ES, tdis=0, tadis=adis, tvam=vam, tbill=adis + vam
    ), [line]


def variant_v2():
    return _single(0)


def variant_v3():
    return _single(KS10)  # the rejected control, fresh reference


def variant_v4():
    return _single(KS9)  # 9% probe


# ── ROUND 2 ──────────────────────────────────────────────────────────────────
# Round 1 settled the STRUCTURE and left exactly one unknown: the KS value.
#   V1  → 00052/00053/00054/00055 on BOTH lines: the gold quartet is mandatory on
#         EVERY line of الگوی سوم, so a "fee on its own taxable line" split is
#         impossible — the org will not accept a pattern-3 line without the trio.
#   V1b → 0204301 on the gold line: IS **must** include TAs
#         (Is = Es + TAs − Gs, exactly the sourced formula).
#   V2  → IS accepted (no 0204301) with adis = Es + TAs, but KS = 0 rejected.
# So: one line, trio declared, adis = Es + TAs − Gs, and KS is a NON-ZERO value
# that is not 543,934. The remaining candidates are all rounding/rate variants of
# the same sourced formula — note the ترازسامانه example truncates (۹٪ ×
# 5,439,339 = 489,540.51 → «۴۸۹٬۵۴۰»), which is the one thing we never tried.
KS10_TRUNC = 543_933  # ۱۰٪ × TAs, truncated (the doc example's rounding)
KS9_HALFUP = 489_541  # ۹٪ × TAs, half-up


def variant_v5():
    return _single(KS10_TRUNC)


def variant_v6():
    return _single(KS9)


def variant_v7():
    return _single(KS9_HALFUP)


# ── ROUND 3 — generalization + rounding placement ────────────────────────────
# V5 was REGISTERED (SUCCESS), settling the shape: one line per article, the gold
# quartet on EVERY line, Is = Es + TAs − Gs, and Ks TRUNCATED rather than half-up
# (5,439,339 × ۱۰٪ = 543,933.9 → 543,933 — integer arithmetic, (TAs*rate)//100).
# Round 3 proves the rule on a REAL goldsmith invoice — two lines, an exempt
# article AND a taxable one, a discount, a non-zero حق‌العمل — and discriminates
# WHERE the truncation happens, since Ks has two terms:
#     per-term floor : ⌊TAs×r/100⌋ + ⌊Es×J/100⌋  = 20,000 + 500,000 = 520,000
#     sum-then-floor : ⌊TAs×r/100  +  Es×J/100⌋  = ⌊520,001.0⌋      = 520,001
# The line-2 amounts below are chosen so the two answers differ by exactly ۱ ریال.
G2_SSTID = "2710000044666"  # النگو طلا — شناسه عمومی, vat_rate 0, exempt
G2_TITLE = "النگو طلا ۱۸ عیار"
G3_SSTID = "2710000050483"  # پودر طلا آلیاژی — شناسه عمومی, vat_rate 10, taxable
G3_TITLE = "پودر طلا آلیاژی"


def _mixed(ks_line2):
    """Two lines: exempt article with a discount + taxable article."""
    l1_prdis, l1_dis = 20_000_000, 1_000_000
    l1_trio = (2_500_000, 300_000, 750_000)
    l1_tas = sum(l1_trio)
    l1_adis = l1_prdis + l1_tas - l1_dis
    l1_ks = l1_tas * 10 // 100
    line1 = {
        "sstid": G2_SSTID,
        "sstt": G2_TITLE,
        "am": 2,
        "fee": 10_000_000,
        "prdis": l1_prdis,
        "dis": l1_dis,
        "adis": l1_adis,
        "vra": 0,
        "vam": l1_ks,
        "tsstam": l1_adis + l1_ks,
        "consfee": l1_trio[0],
        "bros": l1_trio[1],
        "spro": l1_trio[2],
        "tcpbs": l1_tas,
    }
    l2_prdis, l2_tas = 5_000_005, 200_005
    l2_adis = l2_prdis + l2_tas
    line2 = {
        "sstid": G3_SSTID,
        "sstt": G3_TITLE,
        "am": 1,
        "fee": l2_prdis,
        "prdis": l2_prdis,
        "dis": 0,
        "adis": l2_adis,
        "vra": 10,
        "vam": ks_line2,
        "tsstam": l2_adis + ks_line2,
        "consfee": l2_tas,
        "bros": 0,
        "spro": 0,
        "tcpbs": l2_tas,
    }
    body = [line1, line2]
    return _header(
        tprdis=l1_prdis + l2_prdis,
        tdis=l1_dis,
        tadis=l1_adis + l2_adis,
        tvam=l1_ks + ks_line2,
        tbill=sum(r["tsstam"] for r in body),
    ), body


def variant_v8():
    return _mixed(520_000)  # per-term floor


def variant_v9():
    return _mixed(520_001)  # sum-then-floor


# ── ROUND 4 — does the truncation rule also govern الگوی اول? ────────────────
# The gold finding raises a question about EVERY normal invoice we send: our
# pattern-1 mapper rounds VAT HALF-UP (converter._rial). If the org truncates
# there too, any line whose VAT lands on a half Rial would be rejected with the
# same 0204501 — a live-merchant bug hiding behind amounts that happen to divide
# evenly. adis = 1,000,005 at ۱۰٪ = 100,000.5, so half-up and floor differ by ۱.
P1_SSTID = "2800002692993"  # Server — شناسه اختصاصی, vat_rate 10, taxable
P1_TITLE = "کالای آزمایشی نرخ ۱۰٪"


def _plain(vam):
    prdis = 1_000_005
    line = {
        "sstid": P1_SSTID,
        "sstt": P1_TITLE,
        "am": 1,
        "fee": prdis,
        "prdis": prdis,
        "dis": 0,
        "adis": prdis,
        "vra": 10,
        "vam": vam,
        "tsstam": prdis + vam,
    }
    header, _ = _header(
        tprdis=prdis, tdis=0, tadis=prdis, tvam=vam, tbill=prdis + vam
    ), None
    header["inp"] = 1
    return header, [line]


def variant_p1_halfup():
    return _plain(100_001)


def variant_p1_floor():
    return _plain(100_000)


# ── ROUND 5 — fractional quantity: how is Es (prdis) rounded? ────────────────
# Gold is sold by the gram, so am is routinely fractional and am × fee lands off
# a whole Rial. VAT truncation is settled; this isolates prdis alone
# (1.5 × 1,000,001 = 1,500,001.5 → floor 1,500,001 vs half-up 1,500,002), with
# vam truncated in BOTH so only one variable moves.
def _fractional(prdis):
    vam = prdis * 10 // 100
    line = {
        "sstid": P1_SSTID,
        "sstt": P1_TITLE,
        "am": 1.5,
        "fee": 1_000_001,
        "prdis": prdis,
        "dis": 0,
        "adis": prdis,
        "vra": 10,
        "vam": vam,
        "tsstam": prdis + vam,
    }
    header, _ = _header(
        tprdis=prdis, tdis=0, tadis=prdis, tvam=vam, tbill=prdis + vam
    ), None
    header["inp"] = 1
    return header, [line]


def variant_p2_floor():
    return _fractional(1_500_001)


def variant_p2_halfup():
    return _fractional(1_500_002)


VARIANTS = {
    "P2F": ("الگوی اول, fractional qty — prdis truncated (1,500,001)", variant_p2_floor),
    "P2H": ("الگوی اول, fractional qty — prdis half-up (1,500,002)", variant_p2_halfup),
    "P1H": ("الگوی اول, VAT half-up (100,001) — what we ship today", variant_p1_halfup),
    "P1F": ("الگوی اول, VAT truncated (100,000)", variant_p1_floor),
    "V1": ("two lines: exempt gold (no trio) + taxable fee line @10%", variant_v1),
    "V1b": ("two lines: trio on the gold line (vam 0) + taxable fee line", variant_v1b),
    "V2": ("single exempt line, trio declared, vam = 0", variant_v2),
    "V3": ("single exempt line, vam = 10% of TAs half-up (the control)", variant_v3),
    "V4": ("single exempt line, vam = 9% of TAs truncated", variant_v4),
    "V5": ("single exempt line, vam = 10% of TAs TRUNCATED (543,933)", variant_v5),
    "V6": ("single exempt line, vam = 9% of TAs truncated (489,540)", variant_v6),
    "V7": ("single exempt line, vam = 9% of TAs half-up (489,541)", variant_v7),
    "V8": ("mixed exempt+taxable, discount — KS per-term floor", variant_v8),
    "V9": ("mixed exempt+taxable, discount — KS sum-then-floor", variant_v9),
}


async def run(names):
    engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        private_pem, _cert = await _get_signing_material(db, TENANT)
        fiscal_id = "A2HP31"
        transport = SelfTspTransport(
            base_url=_selftsp_base("sandbox"),
            private_key_pem=private_pem,
            fiscal_id=fiscal_id,
            timeout=settings.moadian_timeout_seconds,
            httpx_transport=build_moadian_transport(),
        )
        server = await transport.server_information()
        key = (server.get("publicKeys") or [{}])[0]
        token = (await transport.get_token())["token"]

        sent = []
        for name in names:
            label, builder = VARIANTS[name]
            header, body = builder()
            serial = await _next_inno(db, fiscal_id)
            await db.commit()
            header["inno"] = f"{serial:010X}"
            header["taxid"] = taxid_mod.generate_taxid(
                memory_id=fiscal_id, indatim_ms=INDATIM, serial=serial
            )
            # taxid first, in the doc's field order.
            header = {"taxid": header.pop("taxid"), **header}
            data = {"header": header, "body": body, "payments": []}
            packet = _build_invoice_packet(
                data, fiscal_id=fiscal_id, private_pem=private_pem
            )
            resp = await transport.send_invoice_packets(
                [packet],
                org_public_key_b64=key.get("key"),
                org_key_id=str(key.get("id")),
                token=token,
            )
            resp.raise_for_status()
            rows = (resp.json().get("result") or [{}])
            row = rows[0] if isinstance(rows, list) else {}
            print(f"\n=== {name} — {label} ===")
            print("PAYLOAD: " + json.dumps(data, ensure_ascii=False))
            print(f"SEND: {json.dumps(row, ensure_ascii=False)}")
            sent.append((name, label, header["taxid"], row.get("referenceNumber")))

        print("\n… waiting 45s for the org to process …")
        await asyncio.sleep(45)

        token = (await transport.get_token())["token"]
        print("\n\n#### VERDICT TABLE ####")
        for name, label, tax_id, reference in sent:
            if not reference:
                print(f"\n--- {name}: NOT SENT (no referenceNumber) — {tax_id}")
                continue
            result = await transport.inquiry_by_reference([reference], token=token)
            print(f"\n--- {name} — {label}")
            print(f"    taxid={tax_id} reference={reference}")
            print("    " + json.dumps(result, ensure_ascii=False))
    await engine.dispose()


if __name__ == "__main__":
    args = sys.argv[1:] or ["V1", "V1b", "V2"]
    if args == ["all"]:
        args = list(VARIANTS)
    unknown = [a for a in args if a not in VARIANTS]
    if unknown:
        raise SystemExit(f"unknown variant(s): {unknown}; known: {list(VARIANTS)}")
    asyncio.run(run(args))
