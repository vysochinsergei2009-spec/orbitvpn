from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, urlunparse

from app.api.base import BaseVPNPanel, PanelUser, PanelConfig
from app.api.clients.marzban import MarzbanApiManager
from app.api.types.marzban import MarzbanUserResponse, MarzbanUserStatus


class MarzbanPanel(BaseVPNPanel):
    
    def __init__(self, config: PanelConfig):
        super().__init__(config)
        self.api = MarzbanApiManager(host=config.host)
    
    async def authenticate(self) -> bool:
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
        data = {
            "username": username,
            "expire": expire_timestamp,
            "data_limit": data_limit,
            "data_limit_reset_strategy": "month",
            "ip_limit": 2,
            "proxies": proxies
        }
        
        marzban_user = await self.api.create_user(data, self._access_token)
        
        if not marzban_user:
            raise ValueError(f"Failed to create user {username} in Marzban")
        
        return self._convert_to_panel_user(marzban_user)
    
    async def get_user(self, username: str) -> Optional[PanelUser]:
        marzban_user = await self.api.get_user(username, self._access_token)
        
        if not marzban_user:
            return None
        
        return self._convert_to_panel_user(marzban_user)
    
    async def get_users(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        owner_username: Optional[str] = None,
    ) -> List[PanelUser]:
        marzban_status = None
        if status:
            try:
                marzban_status = MarzbanUserStatus(status)
            except ValueError:
                pass
        
        marzban_users = await self.api.get_users(
            access=self._access_token,
            offset=offset,
            limit=limit,
            status=marzban_status,
            search=search,
            owner_username=owner_username
        )
        
        if not marzban_users:
            return []
        
        return [self._convert_to_panel_user(user) for user in marzban_users]
    
    async def modify_user(
        self, 
        username: str, 
        expire_timestamp: Optional[int] = None,
        data_limit: Optional[int] = None
    ) -> PanelUser:
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
    
    def _convert_to_panel_user(self, marzban_user: MarzbanUserResponse) -> PanelUser:
        subscription_url = marzban_user.subscription_url
        if not subscription_url and marzban_user.links:
            subscription_url = marzban_user.links[0]
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
