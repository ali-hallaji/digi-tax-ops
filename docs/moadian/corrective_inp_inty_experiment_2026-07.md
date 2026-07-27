# Corrective referring-fields — the 14007/14004 experiment (2026-07-26)

**Question (open since MOADIAN F, matrix E3 follow-up):** every اصلاحیه we sent
REGISTERED, but the org attached a non-blocking تذکر that «الگوی صورتحساب» (`inp`)
and «نوع صورتحساب» (`inty`) are «خارج از الگو» — codes **14007** and **14004**. The
PDF does not say plainly whether a referring subject should omit them. Under the
EMPIRICAL-TEST LAW we asked the org instead of the document.

## Method

Two correctives on the **نیک‌تجارت sandbox** (`sandboxrc.tax.gov.ir`, via the dev
Iran egress), identical in every respect except the two fields under test:

| variant | packet header |
|---|---|
| **A — control** | `inp` and `inty` present, exactly as we ship today |
| **B — variant** | `inp` and `inty` removed from the header (`ins` and `irtaxid` kept) |

Script: `scripts/corrective_fields_experiment.py` (the variant is a monkeypatch,
deliberately NOT a shipped flag — an unproven packet change is exactly what this
law exists to prevent).

## Result — the org's own words

**A (control)** — submission `85aea033…`, INV-2026-000032:

```json
"warning": [
  {"code": "14007", "message": "فیلد «الگوی صورتحساب» در الگوی صورتحساب ارسالی خارج از الگو است."},
  {"code": "14004", "message": "فیلد «نوع صورتحساب» در الگوی صورتحساب ارسالی خارج از الگو است."}
]
```

**B (variant)** — submission `4d507eeb…`, INV-2026-000034:

```json
"warning": []
```

Both carried the **same** unrelated error (`0300601` «شمارهٔ مالیاتی صورتحساب مرجع
با اطلاعات سامانه منطبق نیست» — the sandbox no longer recognises those older
reference taxids). That error is identical across both runs, so the **only**
variable between them was `inp`/`inty`, and the warning list is the clean signal.

## Verdict — ADOPTED

**Omitting `inp`/`inty` on a referring subject kills 14007 and 14004.** This makes
sense once the org states it: an اصلاحیه/ابطال/برگشت *refers* to an already-
registered invoice, so the org reads الگو and نوع from the REFERENCE. Repeating
them in the referring packet is, in the org's words, «خارج از الگو».

Shipped in `map_invoice` → `_drop_pattern_fields_on_referring_subject`
(`app/modules/moadian/normalizer/__init__.py`): for `ins ∈ {2, 3, 4}` the two
fields are dropped from the **emitted header only**. The mapper still receives
`(inty, inp)` to CHOOSE the pattern, so an unsupported combination is still
refused honestly — asserted in
`tests/modules/moadian/test_referring_subject_fields.py`.

An اصلی invoice (`ins=1`) refers to nothing and still declares both — also
asserted, so the fix cannot over-reach.

## Loose end recorded honestly

`0300601` on both variants means the sandbox currently rejects correctives whose
reference is one of the OLD registered taxids (…9167D5, …9167F9). MOADIAN F
registered a corrective successfully against those same rows, so the sandbox's
records appear to have rotated. This is **independent of the fix** — it changes
nothing about the warning verdict — but it means a corrective built on a stale
sandbox reference will fail until it is re-issued against a freshly-registered
original. Not reproduced on live.

## Product effect

- The «خارج از الگو» تذکر the founder kept seeing on every اصلاحیه is **gone**, not
  explained away.
- The accountant question list loses one item: no confirmation is needed for
  `inp`/`inty` on referring subjects — the org answered.
- The remaining referring-subject question (which OTHER fields to blank beyond the
  buyer) is untouched and stays with the accountant.

---

## Research cross-check (RESEARCH-APPLICATION batch, 2026-07-28)

`docs/tax_research_1404.md` «سؤال ۸» reads the standard as requiring a referring
invoice (اصلاحی / ابطالی / برگشت از فروش) to **match** the reference on نوع
(`inty`) and الگو (`inp`):

> «هر سه نوع … باید از نظر **نوع (`inty`)** و **الگو (`inp`)** دقیقاً مطابق
> صورتحساب مرجع باشند»

That is the opposite of what we ship. **Our behaviour stands, and no code
changed**, because the two statements are not the same kind of claim:

| | The research doc | Our implementation |
|---|---|---|
| Basis | Reading of the دستورالعمل | A controlled sandbox experiment |
| Says | The referring doc must MATCH نوع/الگو | The referring doc must OMIT them |
| Evidence | Doc text | Two otherwise-identical correctives: fields present → warnings **14007 + 14004**; fields omitted → **no warnings** |

Both readings can be true at once, and probably are: the referring invoice's نوع
and الگو must *be* the reference's — the org takes them **from the reference**,
which is exactly why re-sending them in the payload is «خارج از الگو». "Must
match" is a statement about the invoice; "must be omitted" is a statement about
the packet. Our packet satisfies both.

The research doc's own §«تعریف وضعیت فیلدها» supports this: a field marked
«خارج از الگو» means «وجود یا عدم وجود مقدار تفاوتی ایجاد نمی‌کند و مقدار
ثبت‌شده توسط سامانه دریافت نمی‌شود» — and it names error **۱۴۰۰۴** as exactly
«فیلد نوع صورتحساب در الگوی ارسالی خارج از الگو است», which is the warning we
observed and eliminated.

**Standing rule (per the batch instruction):** the EMPIRICAL verdict wins. This
note exists so nobody "corrects" the mapper back to sending `inp`/`inty` after
reading the research doc. Change it only if a NEW sandbox submission contradicts
the experiment — and record that submission here if it ever does.
