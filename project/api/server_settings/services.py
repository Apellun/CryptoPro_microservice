from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Server
from project.api.server_settings.dao import server_dao
from project.api.server_settings.schemas import ServerSettings


class ServerServices:
    async def update_server_settings(self, server_settings: ServerSettings, db: AsyncSession) -> Server:
        result = await server_dao.update_server_settings(server_settings, db)
        return result


server_services = ServerServices()