"""Enums for panel navigation system"""

from enum import Enum


class Pages(str, Enum):
    """Page types in bot navigation"""
    # Main pages
    HOME = "home"
    MENU = "menu"
    
    # Server management
    SERVERS = "servers"
    
    # User management
    USERS = "users"
    ACTIONS = "actions"
    TEMPLATES = "templates"
    STATS = "stats"
    
    # Admin pages
    ADMIN_PANEL = "admin_panel"
    ADMIN_USERS = "admin_users"
    ADMIN_PAYMENTS = "admin_payments"
    ADMIN_SERVERS = "admin_servers"
    ADMIN_BROADCAST = "admin_broadcast"
    ADMIN_STATS = "admin_stats"
    
    # System
    UPDATE = "update"


class Actions(str, Enum):
    """Action types for pages"""
    LIST = "list"
    INFO = "info"
    CREATE = "create"
    MODIFY = "modify"
    SEARCH = "search"
    JSON = "json"
    DELETE = "delete"
    EXECUTE = "execute"
    CANCEL = "cancel"


class YesOrNot(str, Enum):
    """Confirmation states"""
    YES_USAGE = "YES_USAGE"
    YES_NORMAL = "YES_NORMAL"
    YES_CHARGE = "YES_CHARGE"
    YES = "✅ Yes"
    NO = "❌ No"


class SelectAll(str, Enum):
    """Select all/deselect all actions"""
    SELECT = "select"
    DESELECT = "deselect"


class JsonHandler(str, Enum):
    """JSON handler types"""
    USER = "user"


class RandomHandler(str, Enum):
    """Random data generators"""
    USERNAME = "username"
