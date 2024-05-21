from typing import Optional
from sqlalchemy import select, Sequence
from sqlite3 import IntegrityError as SQLiteIntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from project.api.core.db.models import Organization
from project.api.core import exceptions
from project.api.organizations.schemas import OrganizationUpdate


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
            result = result.scalars().first()
            if not result:
                raise exceptions.EntityNotFoundError(message="Орагнизация с данным ИНН не найдена в базе")
        except SQLAlchemyError as e:
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return result

    async def get_org_list(self, db: AsyncSession) -> Sequence[Optional[Organization]]:
        try:
            result = await db.execute(select(Organization).options(joinedload(Organization.keys)))
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

        except SQLAlchemyError as e:
            await db.rollback()
            if isinstance(e, IntegrityError):
                original_exception = e.orig
                if isinstance(original_exception, SQLiteIntegrityError):
                    exception_str = str(original_exception)
                    if exception_str.startswith("UNIQUE constraint failed"):
                        field = exception_str.split(":")[1].strip()
                        if field == "organization.inn":
                            field = "ИНН"
                        else:
                            field = "именем"
                        raise exceptions.UniqueConstraintError(message=f"Организация с таким {field} уже существует в базе")
            raise exceptions.DatabaseError(details=str(e))
        else:
            return new_org

    async def update_org(self, old_inn: str, new_org_details: OrganizationUpdate, db: AsyncSession) -> Organization:
        try:
            org = await self.get_org(old_inn, db)
            if not org:
                raise exceptions.EntityNotFoundError(message="Орагнизация с данным ИНН не найдена в базе")

            for field, value in new_org_details.model_dump(exclude_unset=True).items():
                setattr(org, field, value)
            await db.commit()

        except SQLAlchemyError as e:
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))
        else:
            return org

    async def delete_org(self, org_inn: str, db: AsyncSession):
        try:
            org = await self.get_org(org_inn, db)
            if org:
                await db.delete(org)
                await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            raise exceptions.DatabaseError(details=str(e))


organizations_dao = OrganizationsDAO()