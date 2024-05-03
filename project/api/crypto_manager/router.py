import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.db.db import get_db
from project.api.crypto_manager.schemas import Key, ServerSettings, Organization
from project.api.crypto_manager.services import services
from project.api.crypto_manager import exceptions

crypto_manager_router = APIRouter()


@crypto_manager_router.get('/get_org_list', status_code=200, response_model=List[Optional[Organization]])
async def get_org_list(db: AsyncSession = Depends(get_db)):
    try:
        result = await services.get_org_list(db=db)
        return result
    except exceptions.DBException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@crypto_manager_router.get('/get_org_keys', status_code=200, response_model=List[Optional[Key]])
async def get_org_keys(org_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await services.get_org_keys(org_id=org_id, db=db)
        return result
    except exceptions.DBException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@crypto_manager_router.put('/update_server_settings', status_code=200, response_model=ServerSettings) #TODO: response?
async def update_server_settings(server_settings: ServerSettings, db: AsyncSession = Depends(get_db)):
    try:
        result = await services.update_server_settings(server_settings.host, server_settings.port, db=db)
        return result
    except exceptions.DBException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@crypto_manager_router.post('/add_org', status_code=200)
async def add_org(organization: Organization, db: AsyncSession = Depends(get_db)):
    try:
        result = await services.add_org(org_name=organization.name, org_inn=organization.inn, db=db)
        return result
    except exceptions.IntegrityException as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except exceptions.DBException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@crypto_manager_router.put('/add_org_keys', status_code=200)
async def add_org_keys(org_id: int, keys: Dict[str, List], db: AsyncSession = Depends(get_db)):
    try:
        result = await services.add_org_keys(org_id=org_id, keys=keys["keys"], db=db)
        return result
    except exceptions.DBException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@crypto_manager_router.put('/delete_org_keys', status_code=200)
async def delete_org_keys(org_id: int, keys: Dict[str, List], db: AsyncSession = Depends(get_db)):
    try:
        result = await services.delete_org_keys(org_id=org_id, keys=keys["keys"], db=db)
        return result
    except exceptions.DBException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )