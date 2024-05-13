from pydantic import BaseModel
from typing import Optional, List, Dict


class BaseAPIModel(BaseModel):
    class Config:
        from_attributes = True