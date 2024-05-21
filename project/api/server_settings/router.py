from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.db import get_db
from project.api.server_settings.schemas import ServerSettings
from project.api.server_settings.services import server_services

server_router = APIRouter()


@server_router.put('/', status_code=200, response_model=ServerSettings)
async def update_server_settings(server_settings: ServerSettings, db: AsyncSession = Depends(get_db)):
    result = await server_services.update_server_settings(server_settings, db=db)
    return result