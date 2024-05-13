import logging
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Server
from project.api.core import exceptions


class ServerDAO:
    async def update_server_settings(self, host: str, port: int, db: AsyncSession) -> Server:
        try:
            result = await db.execute(select(Server))
            instance = result.scalar_one()
            if instance.host != host:
                instance.host = host
            if instance.port != port:
                instance.port = port

        except NoResultFound:
            instance = Server(host=host, port=port)
            db.add(instance)

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))

        await db.flush()
        await db.commit()
        return instance


server_dao = ServerDAO()