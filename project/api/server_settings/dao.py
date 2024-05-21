import logging
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Server
from project.api.core import exceptions
from project.api.server_settings.schemas import ServerSettings


class ServerDAO:
    async def update_server_settings(self, server_settings: ServerSettings, db: AsyncSession) -> Server:
        try:
            result = await db.execute(select(Server))
            instance = result.scalar_one()

            for field, value in server_settings.model_dump(exclude_unset=True).items():
                setattr(instance, field, value)

        except NoResultFound:
            instance = Server(
                host=server_settings.host,
                port=server_settings.port
            )
            db.add(instance)

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))

        await db.commit()
        return instance


server_dao = ServerDAO()