from typing import Optional, List
from project.api.core.schemas import BaseAPIModel
from project.api.keys.schemas import KeyGet


class OrganizationRead(BaseAPIModel):
    id: int
    inn: str
    name: Optional[str] = None
    keys: List[Optional[KeyGet]]


class OrganizationCreate(BaseAPIModel):
    inn: str
    id: Optional[int] = None
    name: Optional[str] = None


class OrganizationUpdate(BaseAPIModel):
    inn: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None


class OrganizationKeysUpdate(BaseAPIModel):
    keys: List[str]