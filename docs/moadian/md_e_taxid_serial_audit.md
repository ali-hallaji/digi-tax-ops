# MOADIAN E — RC_DCPS.SN_V1.3 taxid/serial audit + 1300501 root-cause

_Spec now in repo: `digi-tax-ops/docs/moadian/RC_DCPS_SN_V1_3.pdf` (خرداد ۱۴۰۱)._

## 1. Builder audit — CONFIRMED byte-exact

`app/modules/moadian/application/taxid.py` reproduces the RC_DCPS.SN_V1.3 پیوست اول
worked examples exactly. All three are now regression fixtures
(`TAXID_SN_SPEC_EXAMPLES`, `tests/modules/moadian/test_taxid.py`):

| memory | date | serial (dec / hex) | control string (decimal) | Verhoeff | taxid |
|---|---|---|---|---|---|
| DEF5GH | 1399/04/30 → 18463d → `0481F` | 12 / `000000000C` | `68697057172` + `018463` + `000000000012` | **2** | `DEF5GH0481F000000000C2` |
| DEF5GH | 〃 | 8173 / `0000001FED` | … + `000000008173` | **8** | `DEF5GH0481F0000001FED8` |
| DEF5GH | 〃 | 2572613409 / `009956F721` | … + `002572613409` | **1** | `DEF5GH0481F009956F7211` |

Component rules verified against the spec:
- **date** = `floor(indatim_ms / 86_400_000)` (روزهای سپری‌شده از ۱۹۷۰/۰۱/۰۱), 5-hex, §3-1-2.
- **serial** = per-memory ascending counter, 10-hex, §3-1-3.
- **check** = Verhoeff over `ordmap(memory_id) + zfill(days,6) + zfill(serial,12)`, letters→UTF-8 decimal per جدول ۲, §3-1-4. (UTF-8 == ASCII for A–Z, so `ord()` is exact.)

**Robustness fix shipped:** `send_service._date_to_ms` now pins UTC midnight
(`datetime(y,m,d, tzinfo=timezone.utc)`). It was naive → `.timestamp()` used the ambient
TZ, giving day−1 on a Tehran host (the off-by-one the taxid docstring warns about). This is
a **no-op on the deployed container** (already UTC — verified: `days(2020-07-20)=18463`),
but makes the value correct on any host.

## 2. Component-consistency diff on REAL dev payloads — NO mismatch

For every accepted `moadian_submissions` row on dev, the taxid's embedded date and serial
equal the body fields exactly:

| taxid | date-hex → days | body `indatim` → days | serial-hex → dec | body `inno` |
|---|---|---|---|---|
| `A41XRD050B1006A5E4C549` | `050B1`=20657 | 1784764800000=20657 ✓ | `006A5E4C54`=1784564820 | 1784564820 ✓ |
| `A2HP31050B0006A607FE94` | `050B0`=20656 | 1784678400000=20656 ✓ | `006A607FE9`=1784709097 | 1784709097 ✓ |

Added tests: component round-trip (parse taxid → equals body inputs) + ascending-serial
property. **Conclusion: the taxid and the body carry the identical date/serial value — there
is no component-mismatch bug to fix.**

## 3. 1300501 root-cause — HONEST finding (deeper kill blocked-on-founder)

Org message (verbatim, from dev inquiry payloads): «مقدار فیلد «سریال صورتحساب» با اطلاعات
سامانه منطبق نیست.»

Findings:
- 1300501 appears on **both** memories: دیباتک (A41XRD, live) **and** نیک‌تجارت (A2HP31,
  sandbox).
- It appears on **consecutive** epoch serials (…FE91, FE92, … each +1) — so it is **not**
  eliminated by ascending/consecutive serials, and **not** the epoch first-jump alone.
- Every affected submission is **`accepted`** — the warning is non-blocking.
- Both memories are epoch-seeded (`moadian_serial_counters`: A41XRD=1784564821,
  A2HP31=1784709098). Epoch-seeding was adopted because a tiny serial (1, 2, …) is rejected
  with 0100504 (`^[a-fA-F0-9]{10}$`).

Since the taxid↔body components are provably consistent, 1300501 is the org comparing our
serial against **its own expected next serial for that memory**, which we never meet.
RC_DCPS.SN_V1.3 defines only the taxid **format** (ascending + unique + 10-hex, which we
satisfy) — it does **not** define the org's per-memory serial-reconciliation. So the
definitive kill cannot be derived from this document.

**Two open questions for the founder / org contact (do NOT guess/flip in code — accepted
submissions must not be risked):**
1. **Body `inno` encoding.** The taxid's serial component is HEX (`006A5E4C54`) while the
   body `inno` is the DECIMAL string (`1784564820`). Both currently satisfy
   `^[a-fA-F0-9]{10}$` and submissions are accepted, but if the org expects the body serial
   in the **same 10-hex form as the taxid**, that discrepancy is a candidate cause of
   «سریال … منطبق نیست». Needs the RC_IITP `inno` field-format confirmation before any change.
2. **Fresh-memory expectation.** Does the org expect a memory's serial sequence to begin at
   a specific value it assigns at registration (making our epoch-seed always "non-matching"),
   and can a **brand-new** fiscal memory that emits a clean sequence from serial 1 (padded
   10-hex) avoid both 0100504 and 1300501? This tension (0100504 length vs 1300501 continuity)
   is the crux and is unresolved by RC_DCPS.SN.

**Status (superseded by §4): 1300501 renders as a calm non-blocking تذکر (interpreter
updated); the definitive kill was blocked on the two founder questions above.**

## 4. CONTROLLED EXPERIMENT (2026-07-24) — ROOT CAUSE FOUND, FIXED

Ran the exact controlled test §3 proposed, on sandbox نیک‌تجارت (A2HP31): three
otherwise-identical invoices (cloned lines/buyer/type from the last accepted
submission), differing ONLY in serial handling:

| arm | body `inno` sent | serial value | org result |
|---|---|---|---|
| **A** control | `1784709098` (DECIMAL — the shipped behavior) | 1784709098 | **accepted + 1300501** |
| **B** variable | `006A607FEB` (10-HEX — the taxid's own serial component, byte-sliced) | 1784709099 | **accepted, NO warning — «ثبت شد» clean** |
| **C** fresh region | `1794709100` (DECIMAL, counter bumped +10M first) | 1794709100 | **accepted + 1300501** |

**Verdict — answers §3's two questions empirically:**
1. **YES — the org expects the body `inno` in the same 10-hex form as the taxid's
   serial component.** It parses `inno` AS HEX and reconciles it against the
   taxid; a decimal string never matches its own taxid, hence «سریال … منطبق
   نیست» on every row. (Note the irony: the RC_TICS.IS p.20 worked example
   prints the DECIMAL serial in the body — the doc example and the org's live
   reconciliation disagree; the org wins.)
2. **NO org-assigned starting value exists** — a brand-new counter region still
   warns in decimal (arm C), so 1300501 was never about continuity or the
   epoch-seed; it was pure representation.

**ADOPTED:** `normalizer/patterns.py` now emits `inno = f"{serial:010X}"` (the
`_inno_hex` helper) in both mappers — the body inno IS the taxid's serial slice,
asserted by `test_body_inno_equals_taxid_serial_component`. The doc-example
fixture records the deliberate divergence. Org acceptance of the hex form is
proven (arm B accepted + registered). The 1300501 interpreter entry stays for
historical rows. **Item CLOSED: fixed client-side, not org noise.**

_Experiment drift on dev نیک‌تجارت: 3 finalized clones titled «آزمایش ۱۳۰۰۵۰۱ — …»
(+1 unsubmitted from an aborted run) and the A2HP31 counter advanced +10M (safe:
ascending). A reseed clears them._
