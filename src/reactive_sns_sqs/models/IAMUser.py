from typing import Optional
from pydantic import BaseModel

class IAMUser(BaseModel):
    name: Optional[str]
    access_key: str
    secret_key: str