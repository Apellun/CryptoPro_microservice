from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from project.api.db.db import Base


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    inn: Mapped[str] = mapped_column(Integer, unique=True)

    keys: Mapped[List["Key"]] = relationship("Key", back_populates="organization")


class Key(Base):
    __tablename__ = "key"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String, unique=True)
    organization_id: Mapped["Organization"] = mapped_column(ForeignKey("organization.id"), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="keys")


class Server(Base):
    __tablename__ = "server"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    host: Mapped[str] = mapped_column(String, unique=True)
    port: Mapped[int] = mapped_column(Integer)