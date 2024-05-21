from numpy import setdiff1d
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Key
from project.api.core.cache import api_cache
from project.api.keys.dao import keys_dao
from project.api.organizations.dao import organizations_dao
from project.api.organizations.schemas import KeyGet


class KeysServices:
    async def get_org_keys(self, org_inn: str, db: AsyncSession) -> List[Optional[Key]]:
        cached_keys = api_cache.get_cached_keys(org_inn)
        if cached_keys:
            return cached_keys

        keys = await keys_dao.get_org_keys(org_inn, db)
        api_cache.add_to_key_cache(org_inn, keys)
        return keys

    async def update_org_keys(self, org_inn: str, keys: KeyGet, db: AsyncSession):
        thumbprints = keys.thumbprints
        org = await organizations_dao.get_org(org_inn, db)
        org_keys = org.keys

        existing_org_thumbprints = [key.thumbprint for key in org_keys]
        existing_keys = await keys_dao.get_keys(db)
        existing_keys_thumbprints = [key.thumbprint for key in existing_keys]

        thumbprints_to_add_to_db = setdiff1d(thumbprints, existing_keys_thumbprints)
        thumbprints_to_add_to_org = setdiff1d(thumbprints, existing_org_thumbprints)
        thumbprints_to_delete = setdiff1d(existing_org_thumbprints, thumbprints)

        if len(thumbprints_to_add_to_db) > 0:
            await keys_dao.add_keys(thumbprints_to_add_to_db, db)
        if len(thumbprints_to_add_to_org) > 0:
            await keys_dao.add_org_keys(org.id, thumbprints_to_add_to_org, db)
        if len(thumbprints_to_delete) > 0:
            await keys_dao.delete_keys(thumbprints_to_delete, db)

        keys = await keys_dao.get_org_keys(org_inn, db)
        api_cache.add_to_key_cache(org_inn, keys)
        return keys


keys_services = KeysServices()