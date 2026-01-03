from typing import Dict, Type
from app.api.base import BaseVPNPanel, PanelConfig
from app.api.panels.marzban import MarzbanPanel
from app.api.panels.marzneshin import MarzneshinPanel


class PanelFactory:
    _panels: Dict[str, Type[BaseVPNPanel]] = {
        "marzban": MarzbanPanel,
        "marzneshin": MarzneshinPanel,
    }
    
    @classmethod
    def create_panel(cls, config: PanelConfig) -> BaseVPNPanel:
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
        if not issubclass(panel_class, BaseVPNPanel):
            raise TypeError(
                f"Panel class must inherit from BaseVPNPanel, "
                f"got {panel_class.__name__}"
            )
        
        cls._panels[panel_type] = panel_class
    
    @classmethod
    def get_available_panel_types(cls) -> list[str]:
        return list(cls._panels.keys())
