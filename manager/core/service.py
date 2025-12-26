"""Base service abstraction"""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from manager.core.models import (
    ServiceStatus,
    HealthCheckResult,
    ServiceMetrics,
    ServiceInfo
)


class ManagedService(ABC):
    """Base class for all managed services"""

    def __init__(self, name: str):
        self.name = name
        self._status = ServiceStatus.UNKNOWN
        self._pid: Optional[int] = None
        self._started_at: Optional[datetime] = None
        self._last_restart: Optional[datetime] = None
        self._restart_count = 0

    @abstractmethod
    async def start(self) -> bool:
        """Start the service. Returns True if successful."""
        pass

    @abstractmethod
    async def stop(self, graceful: bool = True, timeout: int = 30) -> bool:
        """
        Stop the service.

        Args:
            graceful: If True, attempt graceful shutdown
            timeout: Maximum seconds to wait for graceful shutdown

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def restart(self) -> bool:
        """Restart the service. Returns True if successful."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """Perform health check on the service."""
        pass

    @abstractmethod
    async def get_metrics(self) -> ServiceMetrics:
        """Get current metrics for the service."""
        pass

    async def get_status(self) -> ServiceStatus:
        """Get current service status."""
        return self._status

    async def get_info(self) -> ServiceInfo:
        """Get complete service information."""
        health = await self.health_check()
        metrics = await self.get_metrics()

        return ServiceInfo(
            name=self.name,
            status=self._status,
            health=health,
            metrics=metrics,
            pid=self._pid,
            started_at=self._started_at,
            last_restart=self._last_restart
        )

    def _set_status(self, status: ServiceStatus):
        """Update service status."""
        self._status = status

    def _set_started(self, pid: Optional[int] = None):
        """Mark service as started."""
        self._status = ServiceStatus.RUNNING
        self._pid = pid
        self._started_at = datetime.now()

    def _set_stopped(self):
        """Mark service as stopped."""
        self._status = ServiceStatus.STOPPED
        self._pid = None

    def _increment_restart_count(self):
        """Increment restart counter."""
        self._restart_count += 1
        self._last_restart = datetime.now()
