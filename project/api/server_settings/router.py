import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.db import get_db
from project.api.server_settings.schemas import ServerSettings
from project.api.server_settings.services import server_services
from project.api.core import exceptions

server_router = APIRouter()


@server_router.put('/update_server_settings', status_code=200, response_model=ServerSettings)
async def update_server_settings(server_settings: ServerSettings, db: AsyncSession = Depends(get_db)):
    try:
        result = await server_services.update_server_settings(server_settings.host, server_settings.port, db=db)
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