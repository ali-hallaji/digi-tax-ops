# MD-1 — Moadian Stage D, Part 1: plan as found (T0 AUDIT-FIRST)

Canonical source PDFs now live beside this file:
- `RC_IITP_IS_V7_8.pdf` (112pp) — the electronic-invoice standard: field dictionary
  (99 fields), invoice patterns, taxid format, per-field validation rules, worked
  examples (نوع اول/دوم, pp. 91–93).
- `دستورالعمل_فنی_اتصال_به_سامانه_مودیان_شهریور_ماه.pdf` (RC_TICS.IS_v1.6, 49pp) —
  the API v2 connection spec: nonce → auth JWS → server-information → invoice
  JWS → JWE → POST invoice → inquiry.

Golden rule (a) governs everything below: implement ONLY what these docs specify;
**ambiguity ⇒ flag, never guess.** Two flags below are load-bearing and block the
crypto core until the founder/sandbox resolves them.

Positioning (founder-locked, golden rule b): we are NOT a «شرکت معتمد»/TSP and the
words شرکت معتمد/TSP must never appear in any merchant-facing copy. Both send modes
are the taxpayer's own self-issuance (their fiscal memory, their کارپوشه, their
keys). A neutral internal enum value is fine.

---

## 0. The big finding: MD-1 is mostly RESHAPE + FILL, not greenfield

A large, correct Moadian foundation already exists (shipped P3.0B–P3.6). MD-1's real
work is: (1) confirm-and-fill the 4 blocked crypto steps, (2) reshape the existing
cockpit into the founder's exact wizard, (3) add MODE A/B key-mode UX + the mock
gateway + api-log, (4) the normalizer skeleton, (5) absorb the scattered old
surfaces. Creating parallel tables/pages would collide with what's here.

### Keep / absorb / replace — backend

| Area | As-found | MD-1 verdict |
|---|---|---|
| `moadian_tenant_profiles` table | Has EXACTLY MD-1's columns: `private_key_storage_mode` enum (`none`/`generated_encrypted`/`imported_encrypted`/`external_reference`), `fiscal_memory_id`, `seller_economic_id`, `seller_national_id`, `public_key_pem`, `public_key_fingerprint`, `encrypted_private_key_blob`, approval lifecycle. Migration `b3c4d5e6f7a8`. | **KEEP.** MD-1's "MODE A/B" = the existing storage-mode enum (`generated_encrypted` = MODE A, `imported_encrypted` = MODE B). Add a self-signed-cert column (see Flag 1) + a `moadian_api_log` table + a `certificate` column set for MODE B. NO new profile table. |
| `moadian_submissions` table | mode/status/reference_number/taxid (nullable, real-inquiry-only)/packet_uid/payloads. Migrations `e5f9a2c1d7b3`, `f3a8b2c1d5e7`. | **KEEP.** Reuse for the cockpit's «آزمایش اتصال» + future send. |
| `profile_service.py` | RSA-2048 keygen, Fernet encryption (`MOADIAN_CRED_KEY`-equivalent derived from `secret_key` — flag KMS TODO), import public/private, SHA-256 fingerprint, approval state machine. | **KEEP & extend.** Add self-signed-cert generation at MODE-A keygen; add cert fingerprint (CN/serial/expiry) + <60d expiry warning for MODE B. |
| `converter.py` | `convert_invoice_to_standard_payload()` → `{header, body, payments, extension, _meta}`, Type-1/Pattern-1 only, decimal/whole-rial, `_meta.unsupported_fields`. | **ABSORB into T2.5 normalizer** as the reference `map_invoice` pattern-1 impl; register unsupported patterns as `NotImplemented`. |
| `validator.py` | structured tax-standard validation. | **KEEP.** Wire to the cockpit's «آزمایش اتصال» + send preflight. |
| `client.py` `LegacyV1MoadianClient` | nonce/submit/inquiry HTTP **implemented**; `get_server_information`, `build_auth_jwt`, `sign_payload_jws`, `encrypt_jwe` raise `ProtocolNotConfirmedError`. | **REPLACE the 4 stubs** with real JWS/JWE per RC_TICS v1.6 §5–§7 (see §2), gated behind `MOADIAN_MODE=mock\|live` with a documented mock. |
| Config `MOADIAN_*` (config.py) | legacy_enabled, legacy_base_url, timeouts, fiscal_memory_id fallback, key paths, proxy. Backend `.env.example` has NONE; ops `.env.example` has all. | **KEEP;** add `MOADIAN_MODE`, `MOADIAN_BASE_URL`, `MOADIAN_CRED_KEY` (Fernet); align backend `.env.example`. |
| Admin submission routes (`/admin/moadian/*`) | dry-run/validate/standard-payload/prepare/legacy-submit/inquiry, admin-guarded. | **KEEP;** cockpit calls validate/standard-payload (already entitlement-gated for merchants). |
| Admin profile routes (`/admin/moadian/profiles/*`) | list/get/approve/reject. | **KEEP** — this is the real «اتصال مودیان» review queue. |

### Keep / absorb / replace — frontend

| Surface | As-found | MD-1 verdict |
|---|---|---|
| `/app/moadian` (`_app.app.moadian.tsx`, 1035 lines) | Already a stepper cockpit: karpousheh guide card, key section (gen/import/download-public/mark-registered), fiscal-memory card, seller-economic-id card, submit-for-approval. Route gate `businessApproved`. | **KEEP as THE cockpit (T3).** Reshape into the founder's exact 4-step flow, add the MODE A/B «روش ارسال» toggle, «آزمایش اتصال» step (nonce+server-information+fiscal-information, mock/live), «سوابق ارتباط» log. Add the `moadian_submission` entitlement gate on top of `businessApproved` (locked card otherwise). |
| Settings `MoadianCard` | pure `<Link to="/app/moadian">`. | **ABSORB** as a cockpit link (keep; it's the settings entry point). |
| `send-to-moadian-card.tsx` (invoice) | disabled submit placeholder, validate/preview, JSON payload preview, lifecycle placeholders. | **KEEP disabled** (real submit is MD-2/R1B per the no-fake-submit rule); its "go to /app/moadian" links now point at the reshaped cockpit. |
| `feature-gates.ts` `moadianApproved` | defined but **no route maps to it** (dead gate since DECISION 2 moved the tax-reportable gate to the taxpayer profile). | **DECIDE:** MD-1 wires the cockpit itself to `moadian_submission` (entitlement) + `businessApproved`. Leave `moadianApproved` unmapped or remove; do NOT re-gate invoices on it. |
| `moadian.ts` / `moadian-types.ts` | full API client + types. | **KEEP & extend** for the new mode toggle + آزمایش-اتصال + log endpoints. |

### Retire / rewrite (old-flow copy — the "no-drift" list)

Every one of these describes the OLD «دکمهٔ ارسال غیرفعال / در دست توسعه» flow or
mislabels taxpayer-profile as Moadian; MD-1 rewrites them around the new cockpit
and the honest positioning:
- Guide `content.ts`: `S8-14` (`:1439`), `S1-12` (`:297`), `S10-02` (`:1727`); admin
  `admin-content.ts:68`. (Update `no-drift.test.ts` coverage with them.)
- `taxpayer-profile.tsx:502-519` — the «اتصال مودیان — در حال توسعه» card that
  duplicates and contradicts the real cockpit and doesn't even link to it → replace
  with a real link.
- `ActivationDashboard.tsx:444-463` UPCOMING «ارسال رسمی مودیان» teaser.
- `mock/tax-status.ts` — fake «متصل به سامانه مودیان» counts feeding the dashboard
  strip → replace with the real profile status.
- **Naming reconcile:** `_admin.admin.taxpayer-profiles.index.tsx` + `admin.ts`
  error strings + `admin-sidebar.tsx:76-80` call the TAXPAYER-profile queue
  «مودیان». Decide label ownership vs the true `/admin/moadian-profiles`.

### Routes/redirects retired: none orphaned
No route is deleted. Every `/app/moadian` in-link (settings, send-card, locked-card,
taxpayer-profile) resolves to the same reshaped cockpit. The mislabeled admin
taxpayer-profile route stays (only its Persian label is reconciled).

---

## 2. Crypto flow AS SPECIFIED (RC_TICS.IS_v1.6) — the confirmed parts

These are transcribed from the doc and are NOT ambiguous (they replace the 4 stubs):

**Auth token (JWS, §5):**
- `GET {base}/api/v2/nonce?timeToLive=<10..200, default 30>` → `{nonce, expDate}`.
- Build a **JWS** (compact), NOT a plain JWT:
  - Header: `{ "alg": "RS256", "x5c": [<base64 DER cert>], "sigT": "<yyyy-MM-dd'T'HH:mm:ss'Z'>", "crit": ["sigT"] }`. `sigT` is UTC (Z); a local `+0330` variant is allowed.
  - Payload: `{ "nonce": "<one-use>", "clientId": "<fiscal memory id>" }`.
  - Signature: RSASSA-PKCS1-v1_5 + SHA-256 (RS256). Token is single-use per request.
- Send as `Authorization: Bearer <jws>` on every subsequent call.

**Server info (§6):** `GET /api/v2/server-information` (auth'd) → `{serverTime, publicKeys:[{key(base64), id, algorithm:"RSA", purpose}]}`. Pick the encryption public key by its `id` → that's the JWE `kid` + the 4096-bit RSA-OAEP key.

**Invoice send (§7):**
- Invoice JWS: **same header shape** as the auth JWS (RS256, x5c, sigT, crit=[sigT]); payload = the normalized invoice JSON (utf-8). Sign with the taxpayer's private key.
- JWE over the JWS: header `{ "alg":"RSA-OAEP-256", "enc":"A256GCM", "kid":<server key id> }`; AES-256-GCM content, 96-bit iv, AAD = ASCII(Base64URL(header)); compact 5-part serialization. AES key wrapped with RSA-OAEP-256 (SHA-256+MGF1) against the 4096-bit server key.
- `POST /api/v2/invoice` body `[{ "payload": <JWE compact>, "header": { "requestTraceId": <uuid>, "fiscalId": <memory id> } }]` (max 1000/req; requestTraceId unique) → `{timestamp, result:[{uid, packetType, referenceNumber, data}]}`.

**Inquiry (§8):** by reference-id / uid / time-range → `status ∈ {SUCCESS, FAILED, IN_PROGRESS, NOT_FOUND}`, with a signed `sign` JWS and `taxId` (the 22-char number confirmed-in-کارپوشه) ONLY on SUCCESS. taxid is set ONLY from this real response — never fabricated.

**Lib choice (to justify in the build):** `jwcrypto` (maintained, does JWS *and* JWE
including RSA-OAEP-256/A256GCM in one lib, matching the doc's jose-4j/jose reference
implementations) over piecing together `pyjwt`+`cryptography`. `cryptography>=41` is
already a dep; `jwcrypto` sits on it.

---

## 🚩 FLAG 1 (LOAD-BEARING) — MODE A auth needs a certificate the doc's trust model won't accept self-signed

The auth JWS header **requires `x5c`** = the taxpayer's signing **certificate**
(base64 DER), and RC_TICS §5 rules 3–6 (p.16) say the org verifies that certificate
against its **Trusted Cert store + CRL + OCSP** — i.e. it expects a cert issued by a
recognized **مرکز میانی (intermediate CA)**.

MODE A (the founder's DEFAULT: "we generate the keypair") produces a **raw RSA
keypair with no CA cert.** The task's own interpretation is "generate a self-signed
cert at keygen so x5c is always populated." That makes the JWS *structurally* valid,
**but a self-signed cert cannot pass a Trusted-Cert/CRL/OCSP check** — so MODE A may
not AUTHENTICATE against the real system at all.

There is a plausible reconciliation in the doc: RC_TICS §2 (p.5) says کارپوشه now
accepts uploading a raw **public key** (not only a cert) against the fiscal-memory
id, and mode 1 is explicitly «توسط مؤدی … با کلید مؤدی». **IF** the org verifies the
auth signature against the public key registered in کارپوشه for that `clientId`
(rather than against the x5c chain), then a self-signed x5c is fine and MODE A works.
**This is unverifiable from the docs alone — it is a sandbox question.**

- **Build decision (safe):** implement MODE A with a self-signed cert populating x5c
  (structurally valid, per the task). Mark it clearly as an *interpretation*.
- **Blocker:** whether MODE A actually authenticates is UNKNOWN until tested against
  the کارپوشه sandbox with a real fiscal-memory id. Do not present MODE A to
  merchants as "works" until a sandbox round-trip proves it. The mock gateway can
  and will simulate success, but that proves plumbing, not the trust model.

## 🚩 FLAG 2 (LOAD-BEARING) — the taxid algorithm document (RC_DCPS.SN) is NOT provided

T2 asks for a `taxid` (شماره مالیاتی) generator "per the official algorithm."
RC_IITP §7-1 (p.23) says taxid is **22 chars = 6 (memory id) + 5 (date) + 10
(serial) + 1 (control digit)**, and points the *exact* algorithm — the date
encoding and the control-digit computation — to a **separate document, «سند قالب
شناسه یکتای حافظه مالیاتی و شماره مالیاتی» (RC_DCPS.SN), available at intamedia.ir.**
That document is **not in our possession**, and the codebase has never generated a
taxid (deliberately: it is only ever read back from a real SUCCESS inquiry).

Known real examples (for later test-vector checking): `A1121604C220002F095011`,
`A1112K04D1271489087018`, `A111DW04E8300004349008`. The memory-id prefix and hex-ish
serial are visible, but the 5-char date encoding and the control digit are NOT
derivable from these alone without the algorithm.

- **Blocker:** cannot implement the taxid generator without RC_DCPS.SN. Per golden
  rule (a) I will not guess a government tax-number algorithm. **Need the founder to
  supply RC_DCPS.SN** (or confirm taxid generation is deferred to MD-2, generating it
  server-side only once the algorithm doc is canonical).

---

## Field dictionary (for the T2.5 normalizer, pattern-1 subset)

Full 99-field table is in RC_IITP §6 (pp.17–21). Pattern-1 (نوع اول، الگوی اول،
فروش) reference fields the normalizer maps end-to-end, with placement:
- **header (سرآمد):** `taxid`, `indatim` (unix ms, 13-digit), `inty`(=1), `inp`(=1),
  `ins`(=1 original sale), `tins`(seller economic id), `tob`(buyer person type),
  `bid`(buyer national/legal id), `tinb`(buyer economic id), `tprdis`, `tdis`,
  `tadis`, `tvam`, `todam`, `tbill`, `setm`(1 cash/2 credit/3 mixed), `cap`, `insp`.
- **body (بدنه), per line:** `sstid`(good/service code), `sstt`(desc), `am`(qty),
  `mu`(unit), `fee`(unit price), `prdis`, `dis`, `adis`, `vra`(VAT rate),
  `vam`(VAT amount), `tsstam`(line total).
- **payments (اطلاعات پرداخت):** empty `[]` for pattern-1 cash/credit in the doc's
  worked example.
- Money: whole-rial, quantize by truncation (§ "قاعده کلی" p.21); our canonical unit
  == the org's unit (ریال) → **assert passthrough, never convert.**
- Totals identities the validator must hold (RC_IITP §7-13..7-18): `tbill = Σ line
  totals`; `tvam = Σ vam`; `tadis = tprdis − tdis`; `Xs ≥ C + Cr` for cash/credit;
  `setm=3 (mixed) ⇒ cap & insp mandatory`.

The doc's worked pattern-1 header (§7-1-2 example) is the byte-for-value fixture
the normalizer unit test asserts against.

---

## Deliverable status & recommendation

- **T0 (audit-first): COMPLETE** — canonical PDFs placed; keep/absorb/replace table
  above; retire list above; crypto flow transcribed; two load-bearing blockers
  flagged.
- **T1–T4 (key modes, crypto core, cockpit, normalizer, harness, deploy): BLOCKED
  on Flag 1 (sandbox auth model) and Flag 2 (RC_DCPS.SN taxid algorithm)** for the
  parts that touch real auth/taxid. The mock-mode plumbing, the cockpit reshape, the
  normalizer pattern-1 skeleton, and the MODE A/B key UX can proceed WITHOUT those
  answers; the real crypto round-trip and the taxid generator cannot.
