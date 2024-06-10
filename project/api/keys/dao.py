import logging
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Key, organization_key_table
from project.api.core import exceptions


class KeysDAO:
    async def get_all_keys(self, db: AsyncSession) -> List[Optional[Key]]:
        try:
            result = await db.execute(select(Key))
        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return [key[0] for key in result.unique().all()]

    async def get_keys_by_thumbprints(
            self, thumbprints: List[str], db: AsyncSession
    ) -> List[Optional[Key]]:
        stmt = (
            select(Key)
            .where(Key.thumbprint.in_(thumbprints))
        )
        try:
            result = await db.execute(stmt)
        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return [key[0] for key in result.unique().all()]

    async def add_keys(
            self, thumbprints: List[str], db: AsyncSession
    ) -> None:
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

    async def delete_keys_objects(
            self, keys_to_delete: List[Key], db: AsyncSession
    ) -> None:
        for key in keys_to_delete:
            await db.delete(key)
        await db.commit()

    async def get_keys_orgs(
            self, key_ids: List[int], db: AsyncSession
    ) -> List[Optional[Key]]:
        stmt = (
            select(Key, organization_key_table)
            .outerjoin(organization_key_table, Key.id == organization_key_table.c.key_id)
            .where(Key.id.in_(key_ids))
        )
        keys_entries = await db.execute(stmt)

        return [key[0] for key in keys_entries if key[1] is None]

    async def delete_keys_by_thumbprints(
            self, thumbprints: List[str], db: AsyncSession
    ) -> None:
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

    async def untie_org_keys(
            self, org_id: int, key_ids: List[str], db: AsyncSession
    ) -> None:
        stmt = delete(organization_key_table).where(
            organization_key_table.c.key_id.in_(key_ids),
            organization_key_table.c.organization_id == org_id
        )
        await db.execute(stmt)
        await db.commit()


keys_dao = KeysDAO()