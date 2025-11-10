"""Core data models for the manager"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


class HealthStatus(str, Enum):
    """Health status of a service"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceStatus(str, Enum):
    """Service operational status"""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    RESTARTING = "restarting"
    FAILED = "failed"
    UNKNOWN = "unknown"


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ServiceMetrics:
    """Metrics for a service"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    uptime_seconds: int = 0
    restart_count: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
            "memory_percent": self.memory_percent,
            "uptime_seconds": self.uptime_seconds,
            "restart_count": self.restart_count,
            **self.custom_metrics
        }


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)
    response_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
            "response_time_ms": self.response_time_ms
        }


@dataclass
class ServiceInfo:
    """Complete information about a service"""
    name: str
    status: ServiceStatus
    health: HealthCheckResult
    metrics: ServiceMetrics
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    last_restart: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "health": self.health.to_dict(),
            "metrics": self.metrics.to_dict(),
            "pid": self.pid,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_restart": self.last_restart.isoformat() if self.last_restart else None,
        }


@dataclass
class Alert:
    """System alert"""
    level: AlertLevel
    service: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "service": self.service,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged
        }


@dataclass
class MarzbanNodeInfo:
    """Marzban node information"""
    name: str
    address: str
    status: HealthStatus
    users_count: int = 0
    users_active: int = 0
    traffic_up: int = 0  # bytes
    traffic_down: int = 0  # bytes
    last_check: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "address": self.address,
            "status": self.status.value,
            "users_count": self.users_count,
            "users_active": self.users_active,
            "traffic_up": self.traffic_up,
            "traffic_down": self.traffic_down,
            "last_check": self.last_check.isoformat()
        }


@dataclass
class MarzbanInstanceInfo:
    """Marzban instance information"""
    instance_id: str
    name: str
    base_url: str
    status: HealthStatus
    is_active: bool
    priority: int
    nodes: List[MarzbanNodeInfo] = field(default_factory=list)
    total_users: int = 0
    active_users: int = 0
    last_check: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "name": self.name,
            "base_url": self.base_url,
            "status": self.status.value,
            "is_active": self.is_active,
            "priority": self.priority,
            "nodes": [node.to_dict() for node in self.nodes],
            "total_users": self.total_users,
            "active_users": self.active_users,
            "last_check": self.last_check.isoformat()
        }


@dataclass
class UserStats:
    """User statistics"""
    total_users: int = 0
    active_subscriptions: int = 0
    trial_users: int = 0
    new_today: int = 0
    total_configs: int = 0
    revenue_today: float = 0.0
    revenue_month: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_users": self.total_users,
            "active_subscriptions": self.active_subscriptions,
            "trial_users": self.trial_users,
            "new_today": self.new_today,
            "total_configs": self.total_configs,
            "revenue_today": self.revenue_today,
            "revenue_month": self.revenue_month
        }
