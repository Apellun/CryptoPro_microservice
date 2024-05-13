from typing import Optional
from sqlalchemy import select, Sequence
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Organization
from project.api.core import exceptions


class OrganizationsDAO:
    async def refresh_org(self, org: Organization, db: AsyncSession) -> Organization:
        await db.refresh(org)
        await db.commit()
        return org

    async def get_org(self, org_inn: str, db: AsyncSession) -> Organization:
        try:
            result = await db.execute(
                select(Organization)
                .where(Organization.inn == org_inn)
                .options(selectinload(Organization.keys))
            )
            result = result.scalars().first() #TODO: AttributeError: 'NoneType' object has no attribute 'keys'
        except SQLAlchemyError as e:
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return result

    async def get_org_list(self, db: AsyncSession) -> Sequence[Optional[Organization]]:
        try:
            result = await db.execute(select(Organization).options(joinedload(Organization.keys))) #TODO: i can cash it
            organizations = result.scalars().unique().all()

        except SQLAlchemyError as e:
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return organizations

    async def add_org(self, org_name: str, org_inn: str, db: AsyncSession) -> Organization:
        new_org = Organization(
            name=org_name,
            inn=org_inn,
            keys=[]
        )
        try:
            db.add(new_org)
            await db.flush()
            await db.commit()

        except IntegrityError as e:
            await db.rollback()
            if str(e).startswith("(sqlite3.IntegrityError) UNIQUE constraint failed"):
                message = "Организация с таким ИНН или именем уже существует в базе"
            else:
                message = None
            raise exceptions.IntegrityException(
                details=str(e),
                message=message
            )
        except SQLAlchemyError as e:
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return new_org


organizations_dao = OrganizationsDAO()