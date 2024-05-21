from pydantic import BaseModel


class BaseAPIModel(BaseModel):
    class Config:
        from_attributes = True