from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, urlunparse
from datetime import datetime

from app.api.base import BaseVPNPanel, PanelUser, PanelConfig
from app.api.clients.marzneshin import MarzneshinApiManager
from app.api.types.marzneshin import MarzneshinUserResponse


class MarzneshinPanel(BaseVPNPanel):
    
    def __init__(self, config: PanelConfig):
        super().__init__(config)
        self.api = MarzneshinApiManager(host=config.host)
        self._service_ids_cache: Optional[List[int]] = None
    
    async def authenticate(self) -> bool:
        token = await self.api.get_token(
            username=self.config.username,
            password=self.config.password
        )
        if token:
            self._access_token = token.access_token
            return True
        return False
    
    async def _get_default_service_ids(self) -> List[int]:
        if self._service_ids_cache is not None:
            return self._service_ids_cache
        
        services = await self.api.get_services(self._access_token)
        if not services:
            return []
        
        self._service_ids_cache = [service.id for service in services]
        return self._service_ids_cache
    
    async def create_user(
        self, 
        username: str, 
        expire_timestamp: int,
        data_limit: int,
        proxies: Dict[str, Any]
    ) -> PanelUser:
        service_ids = await self._get_default_service_ids()
        
        if not service_ids:
            raise ValueError("No services available in Marzneshin panel. Please configure services first.")
        
        data = {
            "username": username,
            "expire_strategy": "fixed_date",
            "expire_date": datetime.fromtimestamp(expire_timestamp).isoformat(),
            "data_limit": data_limit,
            "data_limit_reset_strategy": "month",
            "service_ids": service_ids,
        }
        
        marzneshin_user = await self.api.create_user(data, self._access_token)
        
        if not marzneshin_user:
            raise ValueError(f"Failed to create user {username} in Marzneshin")
        
        return self._convert_to_panel_user(marzneshin_user)
    
    async def get_user(self, username: str) -> Optional[PanelUser]:
        marzneshin_user = await self.api.get_user(username, self._access_token)
        
        if not marzneshin_user:
            return None
        
        return self._convert_to_panel_user(marzneshin_user)
    
    async def get_users(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        expired: Optional[bool] = None,
        limited: Optional[bool] = None,
        search: Optional[str] = None,
        owner_username: Optional[str] = None,
        is_active: Optional[str] = None,
    ) -> List[PanelUser]:
        marzneshin_users = await self.api.get_users(
            access=self._access_token,
            page=page,
            size=size,
            expired=expired,
            limited=limited,
            search=search,
            owner_username=owner_username,
            is_active=is_active
        )
        
        if not marzneshin_users:
            return []
        
        return [self._convert_to_panel_user(user) for user in marzneshin_users]
    
    async def modify_user(
        self, 
        username: str, 
        expire_timestamp: Optional[int] = None,
        data_limit: Optional[int] = None
    ) -> PanelUser:
        data = {}
        
        if expire_timestamp is not None:
            data["expire_strategy"] = "fixed_date"
            data["expire_date"] = datetime.fromtimestamp(expire_timestamp).isoformat()
        
        if data_limit is not None:
            data["data_limit"] = data_limit
        
        marzneshin_user = await self.api.modify_user(username, data, self._access_token)
        
        if not marzneshin_user:
            raise ValueError(f"Failed to modify user {username} in Marzneshin")
        
        return self._convert_to_panel_user(marzneshin_user)
    
    async def delete_user(self, username: str) -> bool:
        return await self.api.remove_user(username, self._access_token)
    
    async def activate_user(self, username: str) -> bool:
        return await self.api.activate_user(username, self._access_token)
    
    async def disable_user(self, username: str) -> bool:
        return await self.api.disabled_user(username, self._access_token)
    
    async def reset_user(self, username: str) -> bool:
        return await self.api.reset_user(username, self._access_token)
    
    async def revoke_user_subscription(self, username: str) -> bool:
        return await self.api.revoke_user(username, self._access_token)
    
    async def get_available_services(self) -> List[Dict[str, Any]]:
        services = await self.api.get_services(self._access_token)
        
        if not services:
            return []
        
        return [
            {
                "id": service.id,
                "name": service.name or f"Service {service.id}",
                "inbound_ids": service.inbound_ids,
                "user_count": len(service.user_ids)
            }
            for service in services
        ]
    
    async def get_admins(self) -> List[Dict[str, Any]]:
        admins = await self.api.get_admins(self._access_token)
        
        if not admins:
            return []
        
        return [
            {
                "username": admin.username,
                "is_sudo": admin.is_sudo,
                "telegram_id": getattr(admin, 'telegram_id', None),
                "discord_webhook": getattr(admin, 'discord_webhook', None)
            }
            for admin in admins
        ]
    
    async def set_owner(self, username: str, admin_username: str) -> bool:
        return await self.api.set_owner(username, admin_username, self._access_token)
    
    async def activate_users(self, admin_username: str) -> bool:
        return await self.api.activate_users(admin_username, self._access_token)
    
    async def disable_users(self, admin_username: str) -> bool:
        return await self.api.disabled_users(admin_username, self._access_token)
    
    async def get_nodes(self) -> List[Dict[str, Any]]:
        nodes = await self.api.get_nodes(self._access_token)
        
        if not nodes:
            return []
        
        return [
            {
                "id": node.id,
                "name": node.name,
                "address": node.address,
                "port": node.port,
                "status": node.status.value if hasattr(node, 'status') else None,
                "xray_version": getattr(node, 'xray_version', None)
            }
            for node in nodes
        ]
    
    async def restart_node(self, node_id: int) -> bool:
        return await self.api.restart_node(self._access_token, node_id)
    
    def _convert_to_panel_user(self, marzneshin_user: MarzneshinUserResponse) -> PanelUser:
        expire_timestamp = None
        if marzneshin_user.expire_date:
            expire_timestamp = int(marzneshin_user.expire_date.timestamp())
        
        subscription_url = marzneshin_user.subscription_url
        if subscription_url:
            parsed = urlparse(subscription_url)
            subscription_url = urlunparse(parsed._replace(fragment="OrbitVPN"))
        
        return PanelUser(
            username=marzneshin_user.username,
            expire_timestamp=expire_timestamp,
            data_limit=marzneshin_user.data_limit,
            used_traffic=marzneshin_user.used_traffic,
            is_active=marzneshin_user.is_active,
            subscription_url=subscription_url or ""
        )