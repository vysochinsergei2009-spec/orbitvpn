from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel

class PanelUser(BaseModel):
    """Унифицированная модель пользователя (независимо от панели)"""
    username: str
    expire_timestamp: Optional[int] = None
    data_limit: Optional[int] = None
    used_traffic: int = 0
    is_active: bool = True
    subscription_url: str
    
    class Config:
        arbitrary_types_allowed = True

class PanelConfig(BaseModel):
    """Конфигурация подключения к панели"""
    host: str
    username: str
    password: str
    panel_type: str  # "marzban", "marzneshin", "3x-ui"

class BaseVPNPanel(ABC):
    """Абстрактный базовый класс для всех VPN панелей"""
    
    def __init__(self, config: PanelConfig):
        self.config = config
        self._access_token: Optional[str] = None
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Получить токен доступа"""
        pass
    
    @abstractmethod
    async def create_user(
        self, 
        username: str, 
        expire_timestamp: int,
        data_limit: int,
        proxies: dict
    ) -> PanelUser:
        """Создать пользователя"""
        pass
    
    @abstractmethod
    async def get_user(self, username: str) -> Optional[PanelUser]:
        """Получить пользователя"""
        pass
    
    @abstractmethod
    async def modify_user(
        self, 
        username: str, 
        expire_timestamp: Optional[int] = None,
        data_limit: Optional[int] = None
    ) -> PanelUser:
        """Изменить пользователя"""
        pass
    
    @abstractmethod
    async def delete_user(self, username: str) -> bool:
        """Удалить пользователя"""
        pass
    
    @abstractmethod
    async def get_available_services(self) -> List[dict]:
        """Получить доступные сервисы/inbounds"""
        pass