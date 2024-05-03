from pydantic import BaseModel
from typing import Optional, List, Dict


class BaseAPIModel(BaseModel):
    class Config:
        from_attributes = True


class Key(BaseAPIModel):
    id: int
    key: str


class Organization(BaseAPIModel):
    id: int
    inn: int
    name: Optional[str]
    keys: Optional[List[Key]] = None


class ServerSettings(BaseAPIModel):
    host: str
    port: int