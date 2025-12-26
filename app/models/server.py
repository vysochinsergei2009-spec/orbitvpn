from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ServerTypes(str, Enum):
    MARZBAN = "marzban"
    MARZNESHIN = "marzneshin"


class Server(BaseModel):
    id: str
    name: str
    types: ServerTypes
    data: Dict[str, Any]
    access: Optional[str] = None
