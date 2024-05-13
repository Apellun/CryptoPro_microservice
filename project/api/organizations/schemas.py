from typing import Optional, List
from project.api.core.schemas import BaseAPIModel
from project.api.keys.schemas import KeyGet


class OrganizationGet(BaseAPIModel):
    id: int
    inn: str
    name: Optional[str] = None
    keys: Optional[List[KeyGet]] = None


class OrganizationPost(BaseAPIModel):
    inn: str
    id: Optional[int] = None
    name: Optional[str] = None