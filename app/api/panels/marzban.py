from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, urlunparse

from app.api.base import BaseVPNPanel, PanelUser, PanelConfig
from app.api.clients.marzban import MarzbanApiManager
from app.api.types.marzban import MarzbanUserResponse


class MarzbanPanel(BaseVPNPanel):
    """
    Адаптер для Marzban панели.
    Конвертирует Marzban-специфичные типы в универсальные PanelUser.
    """
    
    def __init__(self, config: PanelConfig):
        super().__init__(config)
        self.api = MarzbanApiManager(host=config.host)
    
    async def authenticate(self) -> bool:
        """Аутентификация через Marzban API"""
        token = await self.api.get_token(
            username=self.config.username,
            password=self.config.password
        )
        if token:
            self._access_token = token.access_token
            return True
        return False
    
    async def create_user(
        self, 
        username: str, 
        expire_timestamp: int,
        data_limit: int,
        proxies: Dict[str, Any]
    ) -> PanelUser:
        """Создание пользователя в Marzban"""
        data = {
            "username": username,
            "expire": expire_timestamp,  # Marzban использует "expire"
            "data_limit": data_limit,
            "data_limit_reset_strategy": "month",
            "ip_limit": 2,  # Можно вынести в конфиг
            "proxies": proxies
        }
        
        marzban_user = await self.api.create_user(data, self._access_token)
        
        if not marzban_user:
            raise ValueError(f"Failed to create user {username} in Marzban")
        
        return self._convert_to_panel_user(marzban_user)
    
    async def get_user(self, username: str) -> Optional[PanelUser]:
        """Получение пользователя из Marzban"""
        marzban_user = await self.api.get_user(username, self._access_token)
        
        if not marzban_user:
            return None
        
        return self._convert_to_panel_user(marzban_user)
    
    async def modify_user(
        self, 
        username: str, 
        expire_timestamp: Optional[int] = None,
        data_limit: Optional[int] = None
    ) -> PanelUser:
        """Изменение пользователя в Marzban"""
        data = {}
        
        if expire_timestamp is not None:
            data["expire"] = expire_timestamp
        
        if data_limit is not None:
            data["data_limit"] = data_limit
        
        marzban_user = await self.api.modify_user(username, data, self._access_token)
        
        if not marzban_user:
            raise ValueError(f"Failed to modify user {username} in Marzban")
        
        return self._convert_to_panel_user(marzban_user)
    
    async def delete_user(self, username: str) -> bool:
        """Удаление пользователя из Marzban"""
        return await self.api.remove_user(username, self._access_token)
    
    async def get_available_services(self) -> List[Dict[str, Any]]:
        """Получение списка inbounds из Marzban"""
        inbounds = await self.api.get_inbounds(self._access_token)
        
        if not inbounds:
            return []
        
        return [
            {
                "id": inbound.tag,
                "name": inbound.tag,
                "protocol": inbound.protocol.value,
                "port": inbound.port
            }
            for inbound in inbounds
        ]
    
    def _convert_to_panel_user(self, marzban_user: MarzbanUserResponse) -> PanelUser:
        """
        Конвертация Marzban-специфичной модели в универсальную.
        
        Marzban возвращает MarzbanUserResponse с полями:
        - username
        - expire (int timestamp)
        - data_limit (int bytes)
        - used_traffic (int bytes)
        - status (enum)
        - links (List[str])
        - subscription_url (str)
        """
        # Получаем subscription URL или первую ссылку
        subscription_url = marzban_user.subscription_url
        if not subscription_url and marzban_user.links:
            subscription_url = marzban_user.links[0]
            # Добавляем fragment #OrbitVPN для красоты
            parsed = urlparse(subscription_url)
            subscription_url = urlunparse(parsed._replace(fragment="OrbitVPN"))
        
        return PanelUser(
            username=marzban_user.username,
            expire_timestamp=marzban_user.expire,
            data_limit=marzban_user.data_limit,
            used_traffic=marzban_user.used_traffic or 0,
            is_active=marzban_user.is_active,
            subscription_url=subscription_url or ""
        )
