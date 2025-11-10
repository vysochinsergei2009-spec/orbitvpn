"""Marzban Monitor Service"""
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add project path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manager.core.service import ManagedService
from manager.core.models import (
    ServiceStatus,
    HealthStatus,
    HealthCheckResult,
    ServiceMetrics,
    MarzbanInstanceInfo,
    MarzbanNodeInfo
)
from manager.config.manager_config import MarzbanMonitorConfig
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class MarzbanMonitorService(ManagedService):
    """Monitors Marzban instances and nodes"""

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
        """Check health of all Marzban instances."""
        start_time = time.time()

        try:
            # Import here to avoid circular imports
            from app.repo.db import get_db
            from app.repo.models import MarzbanInstance
            from sqlalchemy import select

            healthy_count = 0
            total_count = 0
            details = {}

            async for db in get_db():
                # Get all active instances
                result = await db.execute(
                    select(MarzbanInstance).where(MarzbanInstance.is_active == True)
                )
                instances = result.scalars().all()

                total_count = len(instances)

                # Check each instance
                for instance in instances:
                    try:
                        # Try to get token (basic connectivity check)
                        from app.repo.marzban_client import MarzbanClient
                        client = MarzbanClient()

                        token = await client._get_token(instance.id)
                        if token:
                            healthy_count += 1
                            details[instance.id] = "healthy"
                        else:
                            details[instance.id] = "no_token"

                    except Exception as e:
                        details[instance.id] = f"error: {str(e)}"

                break  # Only need one DB session

            response_time = (time.time() - start_time) * 1000

            if healthy_count == 0:
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"No healthy Marzban instances (0/{total_count})",
                    details=details,
                    response_time_ms=response_time
                )
            elif healthy_count < total_count:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    message=f"Some Marzban instances unhealthy ({healthy_count}/{total_count})",
                    details=details,
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message=f"All Marzban instances healthy ({healthy_count}/{total_count})",
                    details=details,
                    response_time_ms=response_time
                )

        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )

    async def get_metrics(self) -> ServiceMetrics:
        """Get Marzban monitoring metrics."""
        metrics = ServiceMetrics()

        try:
            # Get instance statistics
            instances = await self.get_instances_info()

            total_users = sum(inst.total_users for inst in instances)
            active_users = sum(inst.active_users for inst in instances)
            total_nodes = sum(len(inst.nodes) for inst in instances)
            healthy_nodes = sum(
                len([n for n in inst.nodes if n.status == HealthStatus.HEALTHY])
                for inst in instances
            )

            metrics.custom_metrics = {
                "total_instances": len(instances),
                "active_instances": len([i for i in instances if i.is_active]),
                "total_users": total_users,
                "active_users": active_users,
                "total_nodes": total_nodes,
                "healthy_nodes": healthy_nodes
            }

        except Exception as e:
            LOG.error(f"Error collecting Marzban metrics: {e}")

        return metrics

    async def get_instances_info(self) -> List[MarzbanInstanceInfo]:
        """Get detailed information about all Marzban instances."""
        # Check cache
        if self._last_update and self._instances_cache:
            elapsed = (datetime.now() - self._last_update).total_seconds()
            if elapsed < self.config.check_interval:
                return self._instances_cache

        try:
            from app.repo.db import get_db
            from app.repo.models import MarzbanInstance
            from app.repo.marzban_client import MarzbanClient
            from sqlalchemy import select

            instances_info = []
            client = MarzbanClient()

            async for db in get_db():
                result = await db.execute(select(MarzbanInstance))
                instances = result.scalars().all()

                for instance in instances:
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
                        nodes = await client.get_nodes(instance.id)

                        for node in nodes:
                            node_info = MarzbanNodeInfo(
                                name=node.get('name', 'Unknown'),
                                address=node.get('address', ''),
                                status=HealthStatus.HEALTHY if node.get('status') == 'connected' else HealthStatus.UNHEALTHY,
                                users_count=node.get('users_count', 0),
                                users_active=node.get('users_active', 0)
                            )
                            instance_info.nodes.append(node_info)

                        # Get users count
                        users = await client.get_users(instance.id)
                        instance_info.total_users = len(users) if users else 0

                        instance_info.status = HealthStatus.HEALTHY

                    except Exception as e:
                        LOG.error(f"Error getting info for instance {instance.id}: {e}")
                        instance_info.status = HealthStatus.UNHEALTHY

                    instance_info.last_check = datetime.now()
                    instances_info.append(instance_info)

                break

            # Update cache
            self._instances_cache = instances_info
            self._last_update = datetime.now()

            return instances_info

        except Exception as e:
            LOG.error(f"Error getting instances info: {e}")
            return []

    async def get_instance_details(self, instance_id: str) -> Optional[MarzbanInstanceInfo]:
        """Get detailed information about a specific instance."""
        instances = await self.get_instances_info()
        for instance in instances:
            if instance.instance_id == instance_id:
                return instance
        return None
