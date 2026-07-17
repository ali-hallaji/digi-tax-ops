# Moadian transport correction — SELF-TSP (no-certificate) path

**Status: implemented + PROVEN LIVE (2026-07-17). Not yet pushed.**

## Why

We first shipped the `requestsmanager/api/v2` path: auth via a JWS whose `x5c` the org
validates against a trusted-intermediate-CA store. A direct taxpayer using their own
generated key has only a **self-signed** cert, which the org rejects — proven live:

```
GET .../requestsmanager/api/v2/server-information → 401
{"errors":[{"code":"CERTIFICATE_INVALID_ISSUER",
  "message":"صادرکننده گواهی نامعتبر است یا به مراکز میانی مورد اعتماد متصل نمی‌شود."}]}
```

The **SELF-TSP** path (زیرسامانه جمع‌آوری, «بدون گواهی») authenticates against the taxpayer's
**registered public key** with **no certificate at all** — the correct path for a مؤدی
connecting directly with their own key.

## Sources (every wire-format decision traces to one of these)

- **PDF** `docs/moadian/راهنمای_اتصال_به_زیرسامانه_جمع_آوری_SDK_بدون_گواهی_جاوا_9.pdf`
  (official intamedia Java SDK guide, فروردین ۱۴۰۴, 21pp).
- **PORT** the working Python port `github.com/arjavand/moadian`
  (`api.py` / `request.py` / `normalizer.py` / `signer.py`).
- The with-cert guide (`…_java_7.pdf`, 28pp) is the reference for the future MODE-B/trusted
  path, not this one.

## Protocol (implemented in `app/modules/moadian/application/transport_selftsp.py`)

| item | value | source |
|---|---|---|
| base | `https://tp.tax.gov.ir/req/api` | PDF p.6 |
| direct-taxpayer segment | `…/self-tsp` (trusted cos use `…/tsp`) | PDF p.6 |
| sync URL | `{base}/self-tsp/sync/{PACKET_TYPE}` | port api.py |
| HTTP body | `{"time":1,"packet"|"packets":…,"signature":<b64|null>,"signatureKeyId":null}` | port row_data_creator |
| headers | `requestTraceId` (uuid), `timestamp` (ms), `Authorization: Bearer <token>` (only when needed) | port request.py |
| packet | `{uid,packetType,retry:"false",data,encryptionKeyId:"",symmetricKey:"",iv:"",fiscalId,dataSignature:""}` | PDF p.8 |
| **signature** | `base64( RSA-PKCS1v1.5-SHA256( utf8( normalize(packet,headers) ) ) )` — **NO JWS, NO x5c** | PDF §1-12-2 p.19-20; port signer.py |
| normalize | flatten to sorted dot-keyed paths joined by `#` (empty→`#`, `#`→`##`); `Authorization` contributes the token **without** `Bearer ` | port normalizer.py |

**Flow (connection test):** `GET_SERVER_INFORMATION` (unsigned) → org publicKeys →
`GET_TOKEN {username: memoryId}` (**signed** — the auth proof) → token granted.
Invoice send (`INVOICE.V01`, encrypt+sign, base64 AES-GCM+XOR, RSA-OAEP key-wrap) is MD-2.

**Flag (documented, not guessed):** PDF p.8's low-level transport *example* calls
`GET_TOKEN` with `sign=false`, but the concept-layer `DefaultTaxApiClient` and the working
port both **sign** it, and the auth model requires it. We sign `GET_TOKEN`; the live token
grant is the empirical proof (below).

## Live proof (tenant 0618eb31 / ترازپیشه دیبا, the founder's real registered key)

Two token requests, **same key**, different `username`, resolved the memory-id ambiguity
empirically (per the founder's instruction — prove, don't guess):

```
GET_TOKEN username=A41XRD → HTTP 200, token GRANTED
   JWT: {clientType:"MEMORY", taxpayerId:"14008430838", sub:"A41XRD", iss:"TAX Organization"}
GET_TOKEN username=A3ZA7X → HTTP 401 {"code":"4011","message":"امضای بسته‌ی ارسال شده صحیح نمی‌باشد."}
```

→ **A41XRD** is the id registered to this key (already the stored value — no change made).
Full connection test through the gateway:

```json
{"ok": true, "mode": "live", "encryption_key_id": "6a2bcd88-…",
 "fiscal_status": "ACTIVE", "economic_code": "14008430838", "national_id": "14008430838"}
```

## Config / switching

`MOADIAN_TRANSPORT=selftsp` (new default) | `requestsmanager` (legacy JWS+x5c, kept intact
behind the flag for the future MODE-B/CA-cert path). `MOADIAN_BASE_URL` defaults per
transport (`…/req/api` vs `…/requestsmanager`); trailing `/self-tsp` or `/api/v2` is
normalized off. Mock mode is unchanged (offline; harness stays green).

## Follow-ups

- MD-2 invoice send: map our InvoiceDto → the Moadian invoice packet (header/body/payment
  fields, PDF §1-4 pp.10-16) and wire the encrypter (`transport_selftsp` scaffolding + the
  port's `encrypter.py`).
- Cosmetic: `name_trade` came back as the memory id — verify the `GET_FISCAL_INFORMATION`
  response field names and refine the mapping (does not affect the connection test).
