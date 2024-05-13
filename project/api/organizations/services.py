from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Organization
from project.api.core.cache import api_cache
from project.api.organizations.dao import organizations_dao


class OrganizationsServices:
    async def get_org(self, org_inn: str, db: AsyncSession) -> Organization:
        if api_cache.org_cache:
            org_instance_cache = api_cache.org_cache.get(org_inn, None)
            if org_instance_cache and datetime.now() - org_instance_cache[1] < timedelta(minutes=15):
                return org_instance_cache[0]

        result = await organizations_dao.get_org(org_inn, db)
        api_cache.add_to_org_cache(org_inn, result)
        return result

    async def get_org_list(self, db: AsyncSession) -> List[Optional[Organization]]:
        result = await organizations_dao.get_org_list(db)
        for org in result:
            api_cache.add_to_key_cache(org.inn, org.keys)
        return result

    async def add_org(self, org_name: str, org_inn: str, db: AsyncSession) -> Organization:
        result = await organizations_dao.add_org(org_name, org_inn, db)
        api_cache.add_to_org_cache(org_inn, result)
        return result


organizations_services = OrganizationsServices()