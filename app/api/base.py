from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PanelUser(BaseModel):
    username: str
    expire_timestamp: Optional[int] = None
    data_limit: Optional[int] = None
    used_traffic: int = 0
    is_active: bool = True
    subscription_url: str
    
    class Config:
        arbitrary_types_allowed = True

class PanelConfig(BaseModel):
    host: str
    username: str
    password: str
    panel_type: str

class BaseVPNPanel(ABC):
    def __init__(self, config: PanelConfig):
        self.config = config
        self._access_token: Optional[str] = None
    
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    
    @abstractmethod
    async def create_user(
        self, 
        username: str, 
        expire_timestamp: int,
        data_limit: int,
        proxies: Dict[str, Any]
    ) -> PanelUser:
        pass
    
    @abstractmethod
    async def get_user(self, username: str) -> Optional[PanelUser]:
        pass
    
    @abstractmethod
    async def get_users(
        self,
        **filters
    ) -> List[PanelUser]:
        pass
    
    @abstractmethod
    async def modify_user(
        self, 
        username: str, 
        expire_timestamp: Optional[int] = None,
        data_limit: Optional[int] = None
    ) -> PanelUser:
        pass
    
    @abstractmethod
    async def delete_user(self, username: str) -> bool:
        pass
    
    @abstractmethod
    async def activate_user(self, username: str) -> bool:
        pass
    
    @abstractmethod
    async def disable_user(self, username: str) -> bool:
        pass
    
    @abstractmethod
    async def reset_user(self, username: str) -> bool:
        pass
    
    @abstractmethod
    async def revoke_user_subscription(self, username: str) -> bool:
        pass
        
    @abstractmethod
    async def get_available_services(self) -> List[Dict[str, Any]]:
        pass
    

    @abstractmethod
    async def get_admins(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def set_owner(self, username: str, admin_username: str) -> bool:
        pass
    
    @abstractmethod
    async def activate_users(self, admin_username: str) -> bool:
        pass
    
    @abstractmethod
    async def disable_users(self, admin_username: str) -> bool:
        pass
    
    @abstractmethod
    async def get_nodes(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def restart_node(self, node_id: int) -> bool:
        pass
