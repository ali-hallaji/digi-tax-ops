"""One-shot Moadian credential IMPORT (runs INSIDE the target api container).

Reads the JSON bundle produced by moadian_cred_export.py from STDIN,
re-encrypts the private key with THIS environment's KeyEncryptionService
(the target MOADIAN_CRED_KEY / SECRET_KEY), and upserts it into the target
tenant's MoadianTenantProfile. Company identity fields are copied onto the
tenant row so the business matches the real company. Nothing secret is ever
printed or written to disk.

Usage (on the target host, from the compose dir):
  docker compose cp moadian_cred_import.py api:/tmp/_mi.py
  <export pipe> | docker compose exec -T api python /tmp/_mi.py <dst_tenant_id>
  docker compose exec -T api rm -f /tmp/_mi.py
"""

import asyncio
import json
import sys

sys.path.insert(0, "/app")  # helper runs from /tmp inside the container
from datetime import datetime


def _register_all_models() -> None:
    """Import every module's ORM models so cross-module FKs (e.g. tenants →
    partner_profiles) resolve at flush time."""
    import importlib
    import pkgutil

    import app.modules

    for mod in pkgutil.iter_modules(app.modules.__path__):
        try:
            importlib.import_module(f"app.modules.{mod.name}.infrastructure.models")
        except ModuleNotFoundError:
            continue


async def main(tenant_id: str) -> int:
    bundle = json.loads(sys.stdin.read())

    _register_all_models()

    from sqlalchemy import select

    from app.database.session import async_session_maker
    from app.modules.moadian.application.profile_service import _key_enc
    from app.modules.moadian.infrastructure.models import MoadianTenantProfile
    from app.modules.tenants.infrastructure.models import Tenant

    pem = bundle.pop("private_key_pem", None)
    if not pem:
        print("bundle carries no private key — aborting", file=sys.stderr)
        return 2
    blob = _key_enc.encrypt(pem.encode("utf-8"))
    # Round-trip proof under the TARGET key before touching the DB.
    if _key_enc.decrypt(blob) != pem.encode("utf-8"):
        print("re-encryption round-trip failed — aborting", file=sys.stderr)
        return 2

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
        if tenant is None:
            print(f"target tenant not found: {tenant_id}", file=sys.stderr)
            return 2
        if profile is None:
            profile = MoadianTenantProfile(tenant_id=tenant_id)
            db.add(profile)

        profile.encrypted_private_key_blob = blob
        profile.private_key_storage_mode = (
            bundle.get("private_key_storage_mode") or "imported_encrypted"
        )
        profile.private_key_uploaded_at = datetime.utcnow()
        profile.fiscal_memory_id = bundle.get("fiscal_memory_id")
        profile.status = bundle.get("status") or profile.status
        profile.public_key_pem = bundle.get("public_key_pem")
        profile.public_key_fingerprint = bundle.get("public_key_fingerprint")
        profile.signing_cert_der_b64 = bundle.get("signing_cert_der_b64")
        profile.cert_subject_cn = bundle.get("cert_subject_cn")
        profile.cert_not_after = (
            datetime.fromisoformat(bundle["cert_not_after"])
            if bundle.get("cert_not_after")
            else None
        )
        profile.seller_economic_id = bundle.get("seller_economic_id")
        profile.seller_national_id = bundle.get("seller_national_id")

        company = bundle.get("company") or {}
        for field in ("name", "person_type", "national_id", "economic_id"):
            value = company.get(field)
            if value:
                setattr(tenant, field, value)

        await db.commit()

    print(
        f"imported Moadian credentials into tenant {tenant_id} "
        f"(memory_id={bundle.get('fiscal_memory_id')}, "
        f"fp={bundle.get('public_key_fingerprint')}, status={bundle.get('status')})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: moadian_cred_import.py <dst_tenant_id>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(asyncio.run(main(sys.argv[1])))
