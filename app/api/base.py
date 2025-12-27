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
    """
    Абстрактный базовый класс для всех VPN панелей.
    
    Определяет единый интерфейс для работы с Marzban и Marzneshin.
    Все методы возвращают универсальные типы (PanelUser, dict) вместо 
    специфичных для каждой панели.
    """
    
    def __init__(self, config: PanelConfig):
        self.config = config
        self._access_token: Optional[str] = None
    
    # ========== Аутентификация ==========
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Получение токена доступа к API панели"""
        pass
    
    # ========== Управление пользователями ==========
    
    @abstractmethod
    async def create_user(
        self, 
        username: str, 
        expire_timestamp: int,
        data_limit: int,
        proxies: Dict[str, Any]
    ) -> PanelUser:
        """Создание нового пользователя"""
        pass
    
    @abstractmethod
    async def get_user(self, username: str) -> Optional[PanelUser]:
        """Получение информации о пользователе по username"""
        pass
    
    @abstractmethod
    async def get_users(
        self,
        **filters
    ) -> List[PanelUser]:
        """
        Получение списка пользователей с фильтрацией.
        
        Поддерживаемые фильтры:
        - offset/page: Пагинация
        - limit/size: Количество результатов
        - status/is_active: Статус пользователя
        - search: Поиск по username
        - owner_username: Фильтр по владельцу
        - expired/limited: Специфичные фильтры
        """
        pass
    
    @abstractmethod
    async def modify_user(
        self, 
        username: str, 
        expire_timestamp: Optional[int] = None,
        data_limit: Optional[int] = None
    ) -> PanelUser:
        """Изменение параметров пользователя"""
        pass
    
    @abstractmethod
    async def delete_user(self, username: str) -> bool:
        """Удаление пользователя"""
        pass
    
    @abstractmethod
    async def activate_user(self, username: str) -> bool:
        """Активация пользователя"""
        pass
    
    @abstractmethod
    async def disable_user(self, username: str) -> bool:
        """Отключение пользователя"""
        pass
    
    @abstractmethod
    async def reset_user(self, username: str) -> bool:
        """Сброс использованного трафика пользователя"""
        pass
    
    @abstractmethod
    async def revoke_user_subscription(self, username: str) -> bool:
        """
        Отзыв подписки пользователя.
        Генерирует новый subscription_url для безопасности.
        """
        pass
    
    # ========== Сервисы и конфигурации ==========
    
    @abstractmethod
    async def get_available_services(self) -> List[Dict[str, Any]]:
        """
        Получение доступных сервисов/inbounds.
        
        Возвращает:
            List[Dict]: Список словарей с полями:
                - id: Идентификатор
                - name: Название
                - protocol: Протокол (vless, vmess, и т.д.)
                - port: Порт (опционально)
        """
        pass
    
    # ========== Администраторы ==========
    
    @abstractmethod
    async def get_admins(self) -> List[Dict[str, Any]]:
        """
        Получение списка администраторов панели.
        
        Возвращает:
            List[Dict]: Список словарей с полями:
                - username: Имя пользователя
                - is_sudo: Суперадминистратор
                - telegram_id: ID Telegram (опционально)
                - discord_webhook: Discord webhook (опционально)
        """
        pass
    
    @abstractmethod
    async def set_owner(self, username: str, admin_username: str) -> bool:
        """Установка владельца (администратора) для пользователя"""
        pass
    
    @abstractmethod
    async def activate_users(self, admin_username: str) -> bool:
        """Активация всех пользователей, принадлежащих указанному администратору"""
        pass
    
    @abstractmethod
    async def disable_users(self, admin_username: str) -> bool:
        """Отключение всех пользователей, принадлежащих указанному администратору"""
        pass
    
    # ========== Ноды ==========
    
    @abstractmethod
    async def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Получение списка нод (серверов).
        
        Возвращает:
            List[Dict]: Список словарей с полями:
                - id: Идентификатор
                - name: Название
                - address: Адрес
                - port: Порт
                - status: Статус (connected, disconnected, и т.д.)
                - xray_version: Версия Xray (опционально)
        """
        pass
    
    @abstractmethod
    async def restart_node(self, node_id: int) -> bool:
        """Перезапуск/переподключение ноды"""
        pass
