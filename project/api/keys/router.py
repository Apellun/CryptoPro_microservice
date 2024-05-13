from fastapi import APIRouter, Depends
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.db import get_db
from project.api.keys.schemas import KeyGet, KeysPost
from project.api.keys.services import keys_services

keys_router = APIRouter()


@keys_router.get('/get_org_keys', status_code=200, response_model=List[Optional[KeyGet]])
async def get_org_keys(org_inn: str, db: AsyncSession = Depends(get_db)):
    result = await keys_services.get_org_keys(org_inn=org_inn, db=db)
    return result


@keys_router.put('/update_org_keys', status_code=200)
async def update_org_keys(org_inn: str, keys: KeysPost, db: AsyncSession = Depends(get_db)):
    result = await keys_services.update_org_keys(org_inn=org_inn, keys=keys, db=db)
    return result