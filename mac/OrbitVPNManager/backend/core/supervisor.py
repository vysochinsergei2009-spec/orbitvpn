"""Service Supervisor - central management component"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from manager.core.service import ManagedService
from manager.core.health import HealthChecker
from manager.core.metrics import MetricsCollector
from manager.core.models import (
    ServiceStatus,
    ServiceInfo,
    HealthStatus,
    Alert,
    AlertLevel
)
from manager.config.manager_config import ManagerConfig
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class ServiceSupervisor:
    """
    Main supervisor that manages all services.

    Responsibilities:
    - Service lifecycle management (start/stop/restart)
    - Automatic restart on failure
    - Health monitoring
    - Metrics collection
    - Alert management
    """

    def __init__(self, config: ManagerConfig):
        self.config = config
        self._services: Dict[str, ManagedService] = {}
        self._health_checker = HealthChecker()
        self._metrics_collector = MetricsCollector(
            retention_hours=config.metrics.retention_days * 24
        )
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._restart_counts: Dict[str, int] = {}
        self._alert_callbacks = []

    def register_service(self, service: ManagedService):
        """Register a service with the supervisor."""
        self._services[service.name] = service

        # Register health check
        self._health_checker.register_check(
            service.name,
            service.health_check
        )

        LOG.info(f"Registered service: {service.name}")

    def unregister_service(self, service_name: str):
        """Unregister a service."""
        if service_name in self._services:
            del self._services[service_name]
            self._health_checker.unregister_check(service_name)
            LOG.info(f"Unregistered service: {service_name}")

    def register_alert_callback(self, callback):
        """Register callback for alerts."""
        self._alert_callbacks.append(callback)
        self._health_checker.register_alert_callback(callback)

    async def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self._services:
            LOG.error(f"Service not found: {service_name}")
            return False

        service = self._services[service_name]

        try:
            LOG.info(f"Starting service: {service_name}")
            success = await service.start()

            if success:
                LOG.info(f"Service started successfully: {service_name}")
                self._restart_counts[service_name] = 0
                return True
            else:
                LOG.error(f"Failed to start service: {service_name}")
                return False

        except Exception as e:
            LOG.error(f"Error starting service {service_name}: {e}")
            return False

    async def stop_service(
        self,
        service_name: str,
        graceful: bool = True,
        timeout: int = 30
    ) -> bool:
        """Stop a specific service."""
        if service_name not in self._services:
            LOG.error(f"Service not found: {service_name}")
            return False

        service = self._services[service_name]

        try:
            LOG.info(f"Stopping service: {service_name} (graceful={graceful})")
            success = await service.stop(graceful=graceful, timeout=timeout)

            if success:
                LOG.info(f"Service stopped successfully: {service_name}")
                return True
            else:
                LOG.error(f"Failed to stop service: {service_name}")
                return False

        except Exception as e:
            LOG.error(f"Error stopping service {service_name}: {e}")
            return False

    async def restart_service(self, service_name: str) -> bool:
        """Restart a specific service."""
        if service_name not in self._services:
            LOG.error(f"Service not found: {service_name}")
            return False

        service = self._services[service_name]

        try:
            LOG.info(f"Restarting service: {service_name}")
            success = await service.restart()

            if success:
                LOG.info(f"Service restarted successfully: {service_name}")
                self._restart_counts[service_name] = \
                    self._restart_counts.get(service_name, 0) + 1
                return True
            else:
                LOG.error(f"Failed to restart service: {service_name}")
                return False

        except Exception as e:
            LOG.error(f"Error restarting service {service_name}: {e}")
            return False

    async def start_all(self) -> Dict[str, bool]:
        """Start all registered services."""
        results = {}

        for service_name in self._services.keys():
            results[service_name] = await self.start_service(service_name)

        return results

    async def stop_all(self, graceful: bool = True) -> Dict[str, bool]:
        """Stop all services."""
        results = {}

        for service_name in self._services.keys():
            results[service_name] = await self.stop_service(
                service_name,
                graceful=graceful
            )

        return results

    async def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """Get information about a specific service."""
        if service_name not in self._services:
            return None

        service = self._services[service_name]
        return await service.get_info()

    async def get_all_services_info(self) -> Dict[str, ServiceInfo]:
        """Get information about all services."""
        info = {}

        for service_name, service in self._services.items():
            info[service_name] = await service.get_info()

        return info

    async def get_system_status(self) -> Dict[str, any]:
        """Get overall system status."""
        services_info = await self.get_all_services_info()
        overall_health = self._health_checker.get_overall_health()

        running_count = sum(
            1 for info in services_info.values()
            if info.status == ServiceStatus.RUNNING
        )

        return {
            "overall_health": overall_health.value,
            "total_services": len(services_info),
            "running_services": running_count,
            "services": {
                name: info.to_dict()
                for name, info in services_info.items()
            },
            "timestamp": datetime.now().isoformat()
        }

    async def start_monitoring(self):
        """Start background monitoring tasks."""
        if self._is_running:
            LOG.warning("Monitoring already running")
            return

        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        LOG.info("Started monitoring")

    async def stop_monitoring(self):
        """Stop background monitoring."""
        if not self._is_running:
            return

        self._is_running = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        LOG.info("Stopped monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._is_running:
            try:
                # Perform health checks
                health_results = await self._health_checker.check_all()

                # Collect metrics
                for service_name, service in self._services.items():
                    try:
                        metrics = await service.get_metrics()
                        self._metrics_collector.record_metrics(
                            service_name,
                            metrics
                        )
                    except Exception as e:
                        LOG.error(f"Failed to collect metrics for {service_name}: {e}")

                # Check for services that need restart
                await self._check_restart_policies(health_results)

                # Wait before next check
                await asyncio.sleep(self.config.metrics.collect_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                LOG.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    async def _check_restart_policies(self, health_results):
        """Check services that need automatic restart."""
        for service_name, health_result in health_results.items():
            if service_name not in self._services:
                continue

            service = self._services[service_name]
            status = await service.get_status()

            # Get restart policy from config
            restart_policy = "always"  # Default
            if service_name == "telegram_bot":
                restart_policy = self.config.telegram_bot.restart_policy

            # Check if service should be restarted
            should_restart = False

            if restart_policy == "always":
                should_restart = (
                    status == ServiceStatus.FAILED or
                    health_result.status == HealthStatus.UNHEALTHY
                )
            elif restart_policy == "on-failure":
                should_restart = status == ServiceStatus.FAILED

            if should_restart:
                restart_count = self._restart_counts.get(service_name, 0)
                max_restarts = 5  # Default

                if service_name == "telegram_bot":
                    max_restarts = self.config.telegram_bot.max_restarts

                if restart_count < max_restarts:
                    LOG.warning(
                        f"Auto-restarting {service_name} "
                        f"(attempt {restart_count + 1}/{max_restarts})"
                    )

                    await asyncio.sleep(
                        self.config.telegram_bot.restart_delay
                    )
                    await self.restart_service(service_name)

                else:
                    LOG.error(
                        f"Service {service_name} exceeded max restart attempts "
                        f"({max_restarts})"
                    )

                    # Send critical alert
                    await self._send_alert(Alert(
                        level=AlertLevel.CRITICAL,
                        service=service_name,
                        message=f"Service failed and exceeded max restart attempts ({max_restarts})",
                        details={
                            "restart_count": restart_count,
                            "max_restarts": max_restarts,
                            "health_status": health_result.status.value
                        }
                    ))

    async def _send_alert(self, alert: Alert):
        """Send alert to all registered callbacks."""
        for callback in self._alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                LOG.error(f"Alert callback failed: {e}")

    def get_metrics_collector(self) -> MetricsCollector:
        """Get metrics collector instance."""
        return self._metrics_collector

    def get_health_checker(self) -> HealthChecker:
        """Get health checker instance."""
        return self._health_checker
