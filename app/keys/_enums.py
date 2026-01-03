from enum import Enum


class Pages(str, Enum):
    HOME = "home"
    MENU = "menu"
    
    SERVERS = "servers"
    
    USERS = "users"
    ACTIONS = "actions"
    TEMPLATES = "templates"
    STATS = "stats"
    
    ADMIN_PANEL = "admin_panel"
    ADMIN_USERS = "admin_users"
    ADMIN_PAYMENTS = "admin_payments"
    ADMIN_SERVERS = "admin_servers"
    ADMIN_BROADCAST = "admin_broadcast"
    ADMIN_STATS = "admin_stats"
    
    UPDATE = "update"


class Actions(str, Enum):
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
    YES_USAGE = "YES_USAGE"
    YES_NORMAL = "YES_NORMAL"
    YES_CHARGE = "YES_CHARGE"
    YES = "✅ Yes"
    NO = "❌ No"


class SelectAll(str, Enum):
    SELECT = "select"
    DESELECT = "deselect"


class JsonHandler(str, Enum):
    USER = "user"


class RandomHandler(str, Enum):
    USERNAME = "username"
