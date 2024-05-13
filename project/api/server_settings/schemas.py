from project.api.core.schemas import BaseAPIModel


class ServerSettings(BaseAPIModel):
    host: str
    port: int