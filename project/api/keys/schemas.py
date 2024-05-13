from typing import List
from project.api.core.schemas import BaseAPIModel


class KeyGet(BaseAPIModel):
    id: int
    thumbprint: str


class KeysPost(BaseAPIModel):
    thumbprints: List[str]