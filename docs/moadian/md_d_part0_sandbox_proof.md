# MOADIAN D — PART 0: Sandbox connection diagnosis + org-proof chains

_2026-07-22 · live on dev (`samad`) · نیک‌تجارت (`7085fcf2-598e-415a-8d98-2c8d402e6874`, fiscal memory `A2HP31`, environment=sandbox)._

## Headline
- Founder's sandbox "proxy-settings error" **root-caused and fixed** → نیک‌تجارت
  cockpit connection test **PASSES** on sandbox.
- Both deferred org-proof chains **accepted by the sandbox کارپوشه with real amounts**,
  including **برگشت از فروش — org-proven for the first time**.

---

## 1. Root cause of the "proxy-settings error"

The cockpit error mapped to `proxy_unreachable` («تنظیمات پروکسی را بررسی کنید»). It was
**not** a proxy misconfiguration — it was **DNS**:

- The api reaches Moadian through `socks5h://172.18.0.1:2080` (autossh `-D` to the Iran
  egress host `158.255.74.141:6543`). `socks5h` resolves the hostname **at the egress host**.
- The egress host's systemd-resolved (`127.0.0.53`) returns **SERVFAIL** for
  `sandboxrc.tax.gov.ir`. The **live** host `tp.tax.gov.ir` already had an `/etc/hosts`
  pin (`77.104.79.101`) — that's why live worked and sandbox didn't.
- On SERVFAIL, `ssh -D` closes the SOCKS channel → `curl "(97) connection to proxy
  closed"` after ~8.4 s → app maps it to `proxy_unreachable`.

Evidence (through the socks proxy, before fix):
| host | result |
|------|--------|
| `tp.tax.gov.ir` (live) | HTTP 500, 0.4 s (org reached — baseline OK) |
| `sandboxrc.tax.gov.ir` (sandbox) | `(97) connection to proxy closed`, 8.4 s |

The Iranian **Shecan** resolver (`178.22.122.100`) resolves `sandboxrc.tax.gov.ir` →
`77.104.79.60` / `77.237.79.38`; both serve the endpoint (TLS OK, HTTP 500 on empty body).

## 2. Fix (same pattern as the live host)

On the egress host `158.255.74.141` (`cp -a /etc/hosts /etc/hosts.bak-md-d` first):

```
77.104.79.60 sandboxrc.tax.gov.ir      # appended; matches the 77.104.79.101 tp pin
```

After the pin: `sandboxrc.tax.gov.ir` via socks5h → **HTTP 500, TLS OK, 0.5 s** (was an 8.4 s hang).

> **Not committed to any repo** — per `current_phase.md` "Do not commit proxy settings".
> The pin is host-local on the egress box.

## 3. Connection test PASS

The app's own `run_connection_test(db, 7085fcf2…)` (the exact cockpit call):

```json
{"ok": true, "mode": "live", "server_time": 1784707927832,
 "encryption_key_id": "6a2bcd88-a871-4245-a393-2843eafe6e02",
 "fiscal_status": "ACTIVE", "economic_code": "10320296185",
 "environment": "sandbox", "profile_status": "approved"}
```

The successful test flipped the profile to **approved** (a passing test IS activation).

---

## 4. Org-proof chains (sandbox, real amounts, tagged آزمایشی)

All subjects **accepted (ثبت شد)** by the sandbox کارپوشه after inquiry.

### Chain A — اصلی → اصلاحی → ابطالی  (invoice INV-2026-000005, 209,000,000 ﷼ / VAT 19,000,000)
| ins | subject | taxid | reference | org status |
|----:|---------|-------|-----------|-----------|
| 1 | اصلی | `A2HP31050B0006A607FE39` | `Uz1MJ8TEJhR6GTrz…` | accepted |
| 2 | اصلاحی | `A2HP31050B0006A607FE46` | `yqPWwsxzuPzJjyru…` | accepted |
| 3 | ابطالی | `A2HP31050B0006A607FE55` | `71OjIX891bYge6PT…` | accepted |

### Chain B — اصلی → برگشت از فروش  (invoice INV-2026-000006, 313,500,000 ﷼ / VAT 28,500,000)
| ins | subject | taxid | reference | org status |
|----:|---------|-------|-----------|-----------|
| 1 | اصلی | `A2HP31050B0006A607FE62` | `AGXU9VjYH4-sll_u…` | accepted |
| 4 | برگشت از فروش | `A2HP31050B0006A607FE77` | `Cv0M4DWTVquLEBkL…` | accepted (partial: 1 of 3 units, 104,500,000 ﷼ / VAT 9,500,000) |

**برگشت از فروش (ins=4) had never been org-proven — now accepted end-to-end.**

---

## 5. TWO real defects the sandbox surfaced (نوع اول submissions)

The first اصلی attempt was **rejected** (`A2HP31050B000000000011`) with two org errors —
both genuine and both would block a real newly-connected مؤدی on LIVE:

### 5a. CRITICAL CODE BUG — `_next_inno` seeds tiny serials for a new fiscal memory
- Org `0100504`: «سریال صورتحساب» must match `^[a-fA-F0-9]{10}$` (10 hex chars).
- `send_service._next_inno` first-insert hardcodes `VALUES (:fm, 2, now())` → the first
  `inno` for any **newly-connected** fiscal memory is `1`, `2`, … (1–2 chars) → **rejected**.
- The docstring's stated intent is "epoch-seconds at first submission"; the live proof
  (دیباتک, `A41XRD`) works **only** because a migration seeded its counter to
  `1784564819` (10 digits, which also satisfies the hex pattern). New مؤدیان get no such seed.
- **Impact:** every business that connects to Moadian after us — via the cockpit — has its
  first invoices rejected until its serial counter reaches 10 digits. Ship-blocking for onboarding.
- **Proposed fix:** seed a new counter with `int(time.time())` (epoch-seconds) instead of `2`,
  and add a migration that bumps any existing counter whose `next_serial < 1_000_000_000` up to
  `epoch-seconds`. (For this proof, نیک‌تجارت's counter was reset to epoch-seconds by hand on dev.)

### 5b. Buyer economic code (`tinb`) — 11-digit vs our 12-digit rule
- Org `0101204`: «شماره اقتصادی خریدار» (`tinb`) must match `^\d{11}$`.
- The test buyer had a 12-digit legacy economic code; the org's new-regime economic code for a
  legal buyer is the **11-digit شناسه ملی**. The converter passes `economic_id` through verbatim
  (correct not to pad/truncate) — the **data** was legacy-format.
- **Tension to resolve:** our identity rule (`CLAUDE.md §7.5`: کد اقتصادی = **12** digits) does
  not match the org's `tinb` = 11 digits. Needs a founder decision (likely: economic code for
  legal = شناسه ملی (11), for individual = کد ملی (10); drop the 12-digit rule). For this proof
  the buyer's economic_id was set to its 11-digit شناسه ملی on dev.

---

## 6. Dev data touched (reseed to restore §4.5 / persona contract)
- `moadian_serial_counters` A2HP31 → `next_serial = <epoch>` (this is the *correct* value; keep).
- customer `bb1c2625` (شرکت ساختمانی پارس) economic_id `630003330003` → `14003330003`.
- INV-2026-000004 line `tax_item_id` set to `2001114835894` (was NULL).
- New sandbox invoices INV-2026-000005 / -000006 + 6 sandbox submission rows on نیک‌تجارت.
- نیک‌تجارت Moadian profile flipped to `approved` by the connection test.

## 7. Egress / tunnel follow-ups (infra, not code)
1. The autossh tunnel is launched **manually** (not systemd/cron) → **not reboot-persistent**.
   Recommend a systemd unit so a dev reboot restores `-D 172.18.0.1:2080`.
2. Egress `/etc/hosts` pins (live + sandbox) are host-local. Document them in the runbook
   (without committing IPs) so a rebuilt egress host restores both.
3. Minor: connection-test `transport.target` is `null` because `moadian_transport_info()`
   reads the empty `MOADIAN_BASE_URL` (default fallback). Cosmetic; `proxy:true` is correct.
