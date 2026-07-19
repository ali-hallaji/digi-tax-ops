# کاتالوگ شناسهٔ کالا و خدمت (STUFFID)

This folder holds the **official Tax Organization stuff-id catalog archive** (شناسه کالا
و خدمت). The archive is **gitignored** (~150 MB compressed / ~2 GB raw CSV) — only this
README is committed. The folder is mounted read-only into the `api` container at
`/data/stuffid`; on every api startup a **non-blocking background task** scans it, and if
the newest archive (by the Jalali date in its name) has a sha256 not yet recorded as a
successful import in `catalog_imports`, it stream-imports it into `tax_stuff_ids`.
Nothing else to do — **drop the archive here and (re)start the api.**

The same contract holds on the laptop, the dev server, and future prod.

## Naming convention (the importer keys on this)

```
stuffid_catalog_YYYYMMDD.tar.zst        # Jalali date, e.g. stuffid_catalog_14050428.tar.zst
```

The importer picks the **newest archive by the date in the name** (not mtime). Keep old
archives around if you like — they are skipped.

## Producing a new archive (operator steps)

1. Go to **https://stuffid.tax.gov.ir** and export the full catalog CSVs
   (کالا + خدمت, «دریافت فایل کامل» — arrives as several `product_all_*.csv` parts,
   ~1M rows each, UTF-8 with BOM, header
   `ID,DescriptionOfID,Vat,Taxable,RunDate,ExpirationDate,CreateDate,LastEditDate,Type,PricingDescription`).
2. Pack all parts into one archive (from the folder containing the CSVs):

   ```bash
   tar -cf - product_all_*.csv | zstd -19 -T0 -o stuffid_catalog_<جلالی YYYYMMDD>.tar.zst
   ```

3. Place it in this folder (`digi-tax-ops/data/stuffid/`) on the target machine:

   ```bash
   # one-liner for any server (from the machine holding the archive):
   scp stuffid_catalog_14050428.tar.zst <host>:<digi-tax-ops>/data/stuffid/
   ```

4. Restart the api (`docker compose restart api`) **or** upload the archive through the
   admin page «شناسه‌های کالا و خدمت» — both run the same pipeline. Progress and history
   show on the admin system-health page and in `catalog_imports`.

## Notes

- Re-importing the same archive is a **silent skip** (sha256 already recorded → fast boot).
- Rows are deduplicated by code, keeping the latest `LastEditDate`; a newer archive
  upserts by code (idempotent).
- Never commit an archive; never rename away from the convention above.
