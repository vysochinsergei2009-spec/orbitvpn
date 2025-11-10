"""
OrbitVPN Service Manager

Comprehensive management system for OrbitVPN Telegram bot and Marzban VPN infrastructure.
Provides both CLI and Web interfaces for monitoring, controlling, and managing all services.
"""

__version__ = "1.0.0"
__author__ = "OrbitVPN Team"

from manager.core.supervisor import ServiceSupervisor
from manager.config.manager_config import ManagerConfig

__all__ = ["ServiceSupervisor", "ManagerConfig"]
