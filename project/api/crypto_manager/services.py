import sqlite3
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, join, Sequence
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.db.models import Organization, Key, Server
from project.api.crypto_manager import exceptions


class CryptoServices:
    def __init__(self):
        self.inn_to_key_cash = None
        self.org_cash = None

    @staticmethod
    async def update_server_settings(host: str, port: int, db: AsyncSession) -> Server:
        try:
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
            await db.flush()
            await db.commit()

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DBException
        else:
            return instance

    async def get_org_list(self, db: AsyncSession) -> Sequence[Optional[Organization]]:
        try:
            result = await db.execute(select(Organization).options(joinedload(Organization.keys)))
            organizations = result.scalars().unique().all()

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DBException
        else:
            return organizations

    async def add_org(self, org_name: str, org_inn: int, db: AsyncSession) -> Organization:
        new_org = Organization(
                        name=org_name,
                        inn=org_inn
                    )
        try:
            db.add(new_org)
            await db.flush()
            await db.commit()

        except sqlite3.IntegrityError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.IntegrityException
        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DBException
        else:
            return new_org

    # async def _update_inn_to_key_cash(self, org_inn: int, new_key_objects: List[Key],
    #                                   inn_to_key_change_list: List[tuple[int, Key]]) -> None:
    #     if self.inn_to_key_cash:
    #         for inn, key in inn_to_key_change_list:
    #             org_cash = self.inn_to_key_cash.get(inn, None)
    #             if org_cash:
    #                 org_cash[0].remove(key)
    #                 org_cash[1] = datetime.now()
    #     self.inn_to_key_cash = {org_inn: [new_key_objects, datetime.now()]}

    async def add_org_keys(self, org_id: int, keys: List[str], db: AsyncSession) -> Organization:
        keys_stmt = (select(Key).where(Key.key.in_(keys)))
        #TODO: if keys not in db
        try:
            key_objects = await db.execute(keys_stmt)
            key_objects = [key for key in key_objects.scalars().all()]

            for key in key_objects:
                key.organization_id = org_id
                db.add(key)

            await db.flush()
            await db.commit()

            org_query = select(Organization).options(selectinload(Organization.keys)).filter(Organization.id == org_id)
            org_result = await db.execute(org_query)
            org = org_result.scalar_one()

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DBException
        else:
            return org

    async def delete_org_keys(self, org_id: int, keys: List[str], db: AsyncSession) -> Organization:
        try:
            org_query = select(Organization).options(selectinload(Organization.keys)).filter(Organization.id == org_id)
            org_result = await db.execute(org_query)
            org = org_result.scalar_one()

            remaining_keys = []
            for key in org.keys:
                if key.key not in keys:
                    remaining_keys.append(key)

            org.keys = remaining_keys
            db.add(org)
            await db.flush()
            await db.commit()

        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DBException
        else:
            return org

    async def get_org_keys(self, org_id: int, db: AsyncSession) -> List[Optional[Key]]:
        try:
            org_query = select(Organization).options(selectinload(Organization.keys)).filter(Organization.id == org_id)
            org_result = await db.execute(org_query)
            org = org_result.scalar_one()

            result = [key for key in org.keys]
        except SQLAlchemyError as e:
            logging.exception(e)
            await db.rollback()
            raise exceptions.DBException
        else:
            return result


services = CryptoServices()