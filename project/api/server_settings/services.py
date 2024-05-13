from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Server
from project.api.server_settings.dao import server_dao


class ServerServices:
    async def update_server_settings(self, host: str, port: int, db: AsyncSession) -> Server:
        result = await server_dao.update_server_settings(host, port, db)
        return result


server_services = ServerServices()