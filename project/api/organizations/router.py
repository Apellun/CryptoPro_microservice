from fastapi import APIRouter, Depends
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.db import get_db
from project.api.organizations.schemas import (
    OrganizationRead, OrganizationCreate, OrganizationUpdate,
    OrganizationKeysUpdate
)
from project.api.organizations.services import organizations_services

organizations_router = APIRouter()


@organizations_router.get('/', status_code=200, response_model=List[Optional[OrganizationRead]])
async def get_org_list(db: AsyncSession = Depends(get_db)):
    result = await organizations_services.get_org_list(db=db)
    return result


@organizations_router.get('/{org_inn}', status_code=200, response_model=Optional[OrganizationRead])
async def get_org(org_inn: str, db: AsyncSession = Depends(get_db)):
    result = await organizations_services.get_org(org_inn=org_inn, db=db)
    return result


@organizations_router.post('/', status_code=200, response_model=Optional[OrganizationRead])
async def add_org(organization: OrganizationCreate, db: AsyncSession = Depends(get_db)):
    result = await organizations_services.add_org(org_name=organization.name, org_inn=organization.inn, db=db)
    return result


@organizations_router.put('/{old_inn}', status_code=200, response_model=Optional[OrganizationRead])
async def update_org(old_inn: str, new_org_keys: OrganizationUpdate, db: AsyncSession = Depends(get_db)):
    result = await organizations_services.update_org(old_inn=old_inn, new_org_keys=new_org_keys, db=db)
    return result


@organizations_router.patch('/{org_inn}', status_code=200, response_model=OrganizationRead)
async def update_org_keys(org_inn: str, new_org_keys: OrganizationKeysUpdate, db: AsyncSession = Depends(get_db)):
    result = await organizations_services.update_org_keys(org_inn=org_inn, new_org_keys=new_org_keys, db=db)
    return result


@organizations_router.delete('/{org_inn}', status_code=200)
async def delete_org(org_inn: str, db: AsyncSession = Depends(get_db)):
    await organizations_services.delete_org(org_inn=org_inn, db=db)