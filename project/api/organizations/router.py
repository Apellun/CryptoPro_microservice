from fastapi import APIRouter, Depends
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.db import get_db
from project.api.organizations.schemas import OrganizationGet, OrganizationPost
from project.api.organizations.services import organizations_services

organizations_router = APIRouter()


@organizations_router.get('/get_org', status_code=200, response_model=Optional[OrganizationGet])
async def get_org(org_inn: str, db: AsyncSession = Depends(get_db)): #TODO: org not found
    result = await organizations_services.get_org(org_inn=org_inn, db=db)
    return result


@organizations_router.get('/get_org_list', status_code=200, response_model=List[Optional[OrganizationGet]])
async def get_org_list(db: AsyncSession = Depends(get_db)):
    result = await organizations_services.get_org_list(db=db)
    return result


@organizations_router.post('/add_org', status_code=200) #TODO response validation error
async def add_org(organization: OrganizationPost, db: AsyncSession = Depends(get_db)):
    result = await organizations_services.add_org(org_name=organization.name, org_inn=organization.inn, db=db)
    return result