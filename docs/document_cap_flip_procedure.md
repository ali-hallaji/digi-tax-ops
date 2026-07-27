# Turning on the document cap (`DOCUMENT_CAP_ENFORCED`)

The flag is **OFF** and stays off until the founder decides otherwise, with real
usage data in hand. This is the procedure for the day that changes.

---

## What the flag actually does

| | Flag OFF (today) | Flag ON |
|---|---|---|
| Monthly usage counted | ✅ yes | ✅ yes |
| Usage card shown to merchant | ✅ yes («X از Y سند») | ✅ yes |
| Creating a document past the allowance | **allowed** | **blocked** with a calm 402 + upgrade/pack prompt |
| Purchased «بستهٔ افزایش سند» units consumed | **no** | **yes** |

That last row is the one people get wrong, so it is worth stating plainly:
**with the cap off, a purchased pack adds visible headroom but never depletes.**
Nothing is being blocked, so there is nothing to spend the units on. Turning the
flag on is what starts consumption. A merchant who buys a pack today keeps its
full balance until the day enforcement begins.

---

## Before flipping — the checks that must pass

1. **Look at real usage first.** For at least one full Jalali month:

   ```sql
   -- how many businesses would have been blocked last month?
   SELECT count(*) FROM (
     SELECT tenant_id, count(*) AS docs
       FROM invoice_drafts
      WHERE created_at >= <month start> AND created_at < <next month>
      GROUP BY tenant_id
   ) t
   WHERE docs > <the allowance those tenants actually have>;
   ```

   If that number is not small and expected, the allowance is wrong — fix the
   allowance, not the merchants.

2. **Every allowance is deliberate.** `BASE_PLAN_INCLUDED_DOCS_PER_MONTH` is the
   env default; `tenant_plan_limits.monthly_document_allowance` overrides it per
   business. Confirm no business is sitting on an accidental low override:

   ```sql
   SELECT t.name, l.monthly_document_allowance
     FROM tenant_plan_limits l JOIN tenants t ON t.id = l.tenant_id
    WHERE l.monthly_document_allowance IS NOT NULL
    ORDER BY l.monthly_document_allowance;
   ```

3. **The pack SKU is priced and purchasable**, otherwise a blocked merchant has
   no way out at 2am:

   ```sql
   SELECT feature, monthly_price, pack_units, active
     FROM module_prices WHERE feature = 'document_pack';
   ```

   `monthly_price` NULL or `active=false` ⇒ **do not flip.** A hard cap with no
   purchasable relief is a dead end, which is exactly what §8.4 forbids.

4. **Tell merchants first.** A cap that appears without warning reads as a
   product breaking, not a plan working.

---

## The flip

`DOCUMENT_CAP_ENFORCED=true` in the server `.env`, then restart the API:

```bash
cd /usr/local/digi-tax-ops
# edit .env → DOCUMENT_CAP_ENFORCED=true
docker compose up -d api          # no rebuild needed: env-only change
curl -s http://127.0.0.1:8000/health/check
```

No migration, no data change. It is a runtime read
(`settings.document_cap_enforced`), checked at document creation by
`require_document_capacity`.

---

## Rolling back

Set it back to `false` and restart. Because packs only decrement while the flag
is on, a short enforced window leaves a truthful `units_used` behind — the units
spent during it were really spent, and rolling back does not refund them. If a
flip is reverted as a mistake and units should be returned, that is a deliberate
admin correction (add a compensating pack with `source='admin'` and a note),
never a silent UPDATE of `units_used`.

---

## What to watch in the first 24 hours

- 402s on document creation — expect a handful, investigate a flood.
- `document_quota_packs` rows appearing (merchants buying their way past the cap
  is the system working, not failing).
- Support messages about «سند ثبت نمی‌شود» — the block copy should already answer
  it; if it doesn't, fix the copy before widening the rollout.
