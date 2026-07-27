# Card padding scale (PRIORITY BATCH Part 2)

The rule for how much air a card gets. Written because an audit found **207 card
containers across 104 files** using `p-4` / `p-5` / `p-6` / `p-8` with no stated
reason, and a measured break on the most-viewed screen in the product.

---

## The measured problem

`/app` (the merchant dashboard), 9 top-level card surfaces side by side:

| padding | cards |
|---------|-------|
| 20px (`p-5`) | 5 — کسب‌وکار فعال · کارهای پیشنهادی · نقدینگی و مطالبات · تازه‌ها · امکانات بیشتر |
| 16px (`p-4`) | 1 — یادآورهای پیش رو |
| 14px (`py-3.5`) | 1 — وضعیت مالیاتی |
| 0px | 2 — روند فروش · روند سود |

Five cards agree; three do not. That is what "no rhythm" looks like in practice.

---

## The scale — three tiers, each with a REASON

| Tier | Value | Use for |
|------|-------|---------|
| **surface** | `p-5` (20px) | The default. Any full card that is its own block on a page: dashboard widgets, form sections, list containers, detail panels. **If you are unsure, it is this one.** |
| **compact** | `p-4` (16px) | Cards rendered *inside* another surface, or repeated many times in a dense list (e.g. the mobile row-cards in `DataTable`). Never for a top-level page card. |
| **strip** | `px-5 py-3.5` | A deliberately short horizontal bar whose whole point is to take little vertical space — e.g. `tax-status-strip`. Opting out is legitimate here; the tier exists so it is a DECISION, not drift. |

**`p-0` is not a violation** when the card pads its own inner sections instead
(chart cards, tables with their own cell padding). What matters is that the
*visible inset* is consistent, not the class on the outermost div.

---

## What was changed, and what deliberately was not

- ✅ `reminders-widget` `p-4 → p-5` — a full dashboard surface sitting next to five
  `p-5` siblings. No reason to differ; now matches.
- ⏸️ `tax-status-strip` stays `px-5 py-3.5` — it is a **strip** by design, and making
  it as tall as a surface card would push the real content further down the fold.
  Recorded here as an intentional tier, not an oversight.
- ⏸️ The remaining ~200 sites were **not** mass-rewritten. A blind
  `p-6 → p-5` sweep across 104 files is a large, unreviewable visual change that no
  screenshot pass could honestly verify, and the founder's brief for this part was
  "consistency only, no redesign". The scale above is now the written rule; surfaces
  get moved onto it as they are touched, with the change visible in a small diff.

---

## For reviewers

A new card should say which tier it is by using the tier's value. If a card needs a
value that is not on this list, that is fine — but the reason belongs in a comment
next to it, the way `tax-status-strip` does. Silent one-off padding is the thing this
document exists to stop.
