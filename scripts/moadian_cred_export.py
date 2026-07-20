"""One-shot Moadian credential EXPORT (runs INSIDE the source api container).

Reads the MoadianTenantProfile of the given tenant, decrypts the private-key
blob with THIS environment's KeyEncryptionService (MOADIAN_CRED_KEY /
SECRET_KEY), and writes a single JSON bundle to STDOUT — nothing else may be
printed to stdout; diagnostics go to stderr. The source database is NEVER
written. Pipe stdout straight into moadian_cred_import.py on the target;
never redirect it to a file.

Usage (from digi-tax-ops):
  docker compose cp scripts/moadian_cred_export.py api:/tmp/_mx.py
  docker compose exec -T api python /tmp/_mx.py <src_tenant_id> | <ssh …import…>
  docker compose exec -T api rm -f /tmp/_mx.py
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, "/app")  # helper runs from /tmp inside the container

# The app logs to stdout on import; only the JSON bundle may reach the pipe.
# Keep the real stdout as a private fd and point fd 1 at stderr for everyone else.
_REAL_STDOUT = os.dup(1)
os.dup2(2, 1)


async def main(tenant_id: str) -> int:
    from sqlalchemy import select

    from app.database.session import async_session_maker
    from app.modules.moadian.application.profile_service import _key_enc
    from app.modules.moadian.infrastructure.models import MoadianTenantProfile
    from app.modules.tenants.infrastructure.models import Tenant

    async with async_session_maker() as db:
        profile = (
            await db.execute(
                select(MoadianTenantProfile).where(
                    MoadianTenantProfile.tenant_id == tenant_id
                )
            )
        ).scalar_one_or_none()
        tenant = (
            await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        ).scalar_one_or_none()

    if profile is None or tenant is None:
        print(f"source tenant/profile not found: {tenant_id}", file=sys.stderr)
        return 2
    if not profile.encrypted_private_key_blob:
        print("source profile has no stored private key", file=sys.stderr)
        return 2

    pem_bytes = _key_enc.decrypt(profile.encrypted_private_key_blob)

    bundle = {
        "private_key_pem": pem_bytes.decode("utf-8"),
        "fiscal_memory_id": profile.fiscal_memory_id,
        "status": profile.status,
        "private_key_storage_mode": profile.private_key_storage_mode,
        "public_key_pem": profile.public_key_pem,
        "public_key_fingerprint": profile.public_key_fingerprint,
        "signing_cert_der_b64": profile.signing_cert_der_b64,
        "cert_subject_cn": profile.cert_subject_cn,
        "cert_not_after": (
            profile.cert_not_after.isoformat() if profile.cert_not_after else None
        ),
        "seller_economic_id": profile.seller_economic_id,
        "seller_national_id": profile.seller_national_id,
        "company": {
            "name": tenant.name,
            "person_type": tenant.person_type,
            "national_id": tenant.national_id,
            "economic_id": tenant.economic_id,
        },
    }
    # The ONLY write to the real stdout — the secret-bearing bundle, into the pipe.
    os.write(_REAL_STDOUT, json.dumps(bundle, ensure_ascii=False).encode("utf-8"))
    os.close(_REAL_STDOUT)
    print(
        f"exported profile for tenant {tenant_id} "
        f"(memory_id={profile.fiscal_memory_id}, fp={profile.public_key_fingerprint})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: moadian_cred_export.py <src_tenant_id>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(asyncio.run(main(sys.argv[1])))
