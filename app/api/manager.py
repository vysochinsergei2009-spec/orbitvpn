from typing import Dict, Type
from app.api.base import BaseVPNPanel, PanelConfig
from app.api.panels.marzban import MarzbanPanel
from app.api.panels.marzneshin import MarzneshinPanel


class PanelFactory:
    """
    Фабрика для создания экземпляров VPN панелей (паттерн Factory).
    
    Позволяет легко добавлять новые типы панелей без изменения существующего кода.
    """
    
    # Реестр доступных панелей
    _panels: Dict[str, Type[BaseVPNPanel]] = {
        "marzban": MarzbanPanel,
        "marzneshin": MarzneshinPanel,
        # Будущие панели добавляются здесь:
        # "3x-ui": ThreeXUIPanel,
        # "hiddify": HiddifyPanel,
    }
    
    @classmethod
    def create_panel(cls, config: PanelConfig) -> BaseVPNPanel:
        """
        Создать экземпляр панели по типу.
        
        Args:
            config: Конфигурация панели с указанием panel_type
        
        Returns:
            Экземпляр панели (MarzbanPanel, MarzneshinPanel и т.д.)
        
        Raises:
            ValueError: Если panel_type не зарегистрирован
        
        Example:
            config = PanelConfig(
                host="https://panel.example.com",
                username="admin",
                password="secret",
                panel_type="marzban"
            )
            panel = PanelFactory.create_panel(config)
            await panel.authenticate()
            user = await panel.create_user(...)
        """
        panel_class = cls._panels.get(config.panel_type)
        
        if not panel_class:
            available = ", ".join(cls._panels.keys())
            raise ValueError(
                f"Unsupported panel type: {config.panel_type}. "
                f"Available types: {available}"
            )
        
        return panel_class(config)
    
    @classmethod
    def register_panel(cls, panel_type: str, panel_class: Type[BaseVPNPanel]):
        """
        Зарегистрировать новый тип панели (для плагинов).
        
        Args:
            panel_type: Уникальный идентификатор типа (например "3x-ui")
            panel_class: Класс панели, наследующийся от BaseVPNPanel
        
        Example:
            class CustomPanel(BaseVPNPanel):
                ...
            
            PanelFactory.register_panel("custom", CustomPanel)
        """
        if not issubclass(panel_class, BaseVPNPanel):
            raise TypeError(
                f"Panel class must inherit from BaseVPNPanel, "
                f"got {panel_class.__name__}"
            )
        
        cls._panels[panel_type] = panel_class
    
    @classmethod
    def get_available_panel_types(cls) -> list[str]:
        """
        Получить список доступных типов панелей.
        
        Returns:
            Список строк с типами панелей (например ["marzban", "marzneshin"])
        """
        return list(cls._panels.keys())
