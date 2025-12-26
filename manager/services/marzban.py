"""Marzban Monitor Service"""
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add project path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manager.core.service import ManagedService
from manager.core.models федерации (
    ServiceStatus,
    HealthStatus,
    HealthCheckResult,
    ServiceMetrics,
    MarzbanInstanceInfo,
    MarzbanNodeInfo
)
from manager.config.manager_config import MarzbanMonitorConfig
from manager.utils.logger import get_logger
# Import the refactored client
from app.repo.marzban_client import MarzbanClient, MarzbanInstance

LOG = get_logger(__name__)


class MarzbanMonitorService(ManagedService):
    """Monitors the single Marzban instance defined in the environment."""

    def __init__(self, config: MarzbanMonitorConfig):
        super().__init__("marzban_monitor")
        self.config = config
        self._instances_cache: List[MarzbanInstanceInfo] = []
        self._last_update: Optional[datetime] = None

    async def start(self) -> bool:
        """Start monitoring (doesn't need actual process)."""
        self._set_status(ServiceStatus.RUNNING)
        self._set_started()
        LOG.info("Marzban monitor started")
        return True

    async def stop(self, graceful: bool = True, timeout: int = 30) -> bool:
        """Stop monitoring."""
        self._set_stopped()
        LOG.info("Marzban monitor stopped")
        return True

    async def restart(self) -> bool:
        """Restart monitoring."""
        await self.stop()
        await self.start()
        self._increment_restart_count()
        return True

    async def health_check(self) -> HealthCheckResult:
        """Check health of the Marzban instance."""
        start_time = time.time()
        client = MarzbanClient()
        instance = client._instance # Get the single instance
        api = client._get_or_create_api(instance)
        
        try:
            # A lightweight check, e.g., getting system stats or a non-existent user
            await api.get_users(limit=1) 
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Marzban instance is healthy",
                details={instance.id: "healthy"},
                response_time_ms=response_time
            )
        except Exception as e:
            LOG.warning(f"Marzban health check failed: {e}")
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Marzban instance is unhealthy: {e}",
                details={instance.id: f"error: {str(e)}"},
                response_time_ms=response_time
            )

    async def get_metrics(self) -> ServiceMetrics:
        """Get Marzban monitoring metrics."""
        metrics = ServiceMetrics()
        try:
            instances = await self.get_instances_info()
            if not instances:
                return metrics

            instance = instances[0]
            healthy_nodes = sum(1 for n in instance.nodes if n.status == HealthStatus.HEALTHY)

            metrics.custom_metrics = {
                "total_instances": 1,
                "active_instances": 1 if instance.is_active else 0,
                "total_users": instance.total_users,
                "active_users": instance.active_users,
                "total_nodes": len(instance.nodes),
                "healthy_nodes": healthy_nodes,
            }
        except Exception as e:
            LOG.error(f"Error collecting Marzban metrics: {e}")
        return metrics

    async def get_instances_info(self) -> List[MarzbanInstanceInfo]:
        """Get detailed information about the Marzban instance."""
        if self._last_update and self._instances_cache:
            elapsed = (datetime.now() - self._last_update).total_seconds()
            if elapsed < self.config.check_interval:
                return self._instances_cache

        try:
            client = MarzbanClient()
            instance = client._instance
            api = client._get_or_create_api(instance)

            instance_info = MarzbanInstanceInfo(
                instance_id=instance.id,
                name=instance.name,
                base_url=instance.base_url,
                status=HealthStatus.UNKNOWN,
                is_active=instance.is_active,
                priority=instance.priority,
                nodes=[],
                total_users=0,
                active_users=0
            )

            try:
                # Get nodes information
                nodes_data = await api.get_nodes()
                for node_data in nodes_data:
                    node_info = MarzbanNodeInfo(
                        name=node_data.name or 'Unknown',
                        address=node_data.address or '',
                        status=HealthStatus.HEALTHY if node_data.status == 'connected' else HealthStatus.UNHEALTHY,
                        users_count=node_data.users_count or 0,
                        # Assuming users_active is not directly available in this model
                        users_active=0,
                    )
                    instance_info.nodes.append(node_info)

                # Get users count
                users_data = await api.get_users(limit=10000)
                instance_info.total_users = len(users_data.users)
                instance_info.active_users = sum(1 for u in users_data.users if u.status == 'active')

                instance_info.status = HealthStatus.HEALTHY
            except Exception as e:
                LOG.error(f"Error getting info for instance {instance.id}: {e}")
                instance_info.status = HealthStatus.UNHEALTHY

            instance_info.last_check = datetime.now()
            
            # Update cache
            self._instances_cache = [instance_info]
            self._last_update = datetime.now()
            
            return self._instances_cache

        except Exception as e:
            LOG.error(f"Error getting instances info: {e}")
            return []

    async def get_instance_details(self, instance_id: str) -> Optional[MarzbanInstanceInfo]:
        """Get detailed information about a specific instance."""
        instances = await self.get_instances_info()
        if instances and instances[0].instance_id == instance_id:
            return instances[0]
        return None
