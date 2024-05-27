from project.api.core.schemas import BaseAPIModel


class KeyGet(BaseAPIModel):
    id: int
    thumbprint: str