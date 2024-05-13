from typing import List
from sqlalchemy import Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from project.api.core.db.db import Base


organization_key_table = Table(
    "organization_key",
    Base.metadata,
    Column("organization_id", ForeignKey("organization.id"), primary_key=True),
    Column("key_id", ForeignKey("key.id", ondelete='CASCADE'), primary_key=True),
)


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    inn: Mapped[str] = mapped_column(String, unique=True)

    keys: Mapped[List["Key"]] = relationship(
        "Key",
        back_populates="organizations",
        lazy="joined",
        secondary=organization_key_table
    )


class Key(Base):
    __tablename__ = "key"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    thumbprint: Mapped[str] = mapped_column(String, unique=True)

    organizations: Mapped[List["Organization"]] = relationship(
        "Organization",
        back_populates="keys",
        secondary=organization_key_table
    )


class Server(Base):
    __tablename__ = "server"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    host: Mapped[str] = mapped_column(String, unique=True)
    port: Mapped[int] = mapped_column(Integer)