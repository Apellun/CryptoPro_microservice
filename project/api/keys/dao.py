import logging
from typing import List
from sqlalchemy import select, insert, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Key, organization_key_table, Organization
from project.api.core import exceptions


class KeysDAO:
    async def get_keys(self, db: AsyncSession):
        try:
            result = await db.execute(select(Key))
        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return [key[0] for key in result.unique().all()]

    async def get_org_keys(self, org_inn: str, db: AsyncSession):
        try:
            result = await db.execute(
                select(Key)
                .join(Key.organizations)
                .where(Organization.inn == org_inn)
            )
        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return [key[0] for key in result.unique().all()]

    async def add_keys(self, thumbprints: List[str], db: AsyncSession) -> None:
        try:
            new_keys = []
            for thumbprint in thumbprints:
                new_keys.append(
                    Key(
                        thumbprint=thumbprint
                    )
                )
            db.add_all(new_keys)
            await db.commit()

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))

    async def delete_keys(self, thumbprints: List[str], db: AsyncSession) -> None:
        try:
            await db.execute(
                delete(Key)
                .where(Key.thumbprint.in_(thumbprints))
            )
            await db.commit()

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))

    async def add_org_keys(self, org_id: int, thumbprints: List[str], db: AsyncSession):
        try:
            keys = await db.execute(select(Key).where(Key.thumbprint.in_(thumbprints)))
            keys = keys.unique().all()

            new_org_keys = []
            for key in keys:
                org_key = {
                    "organization_id": org_id,
                    "key_id": key[0].id
                }
                new_org_keys.append(org_key)

            await db.execute(insert(organization_key_table).values(new_org_keys))
            await db.commit()

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))


keys_dao = KeysDAO()