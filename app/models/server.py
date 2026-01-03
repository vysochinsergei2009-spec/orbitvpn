from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ServerTypes(str, Enum):
    MARZBAN = "marzban"
    MARZNESHIN = "marzneshin"


class Server(BaseModel):
    id: str
    name: str
    types: ServerTypes
    data: Dict[str, Any] = Field(default_factory=dict)
    access: Optional[str] = None

    class Config:
        use_enum_values = True