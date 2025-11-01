"""Health checking system"""
import asyncio
import time
from typing import Dict, List, Callable, Awaitable
from datetime import datetime, timedelta

from manager.core.models import HealthStatus, HealthCheckResult, Alert, AlertLevel
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class HealthChecker:
    """Manages health checks for all services"""

    def __init__(self):
        self._checks: Dict[str, Callable[[], Awaitable[HealthCheckResult]]] = {}
        self._last_results: Dict[str, HealthCheckResult] = {}
        self._alert_callbacks: List[Callable[[Alert], Awaitable[None]]] = []
        self._last_alerts: Dict[str, datetime] = {}

    def register_check(
        self,
        service_name: str,
        check_func: Callable[[], Awaitable[HealthCheckResult]]
    ):
        """Register a health check function for a service."""
        self._checks[service_name] = check_func
        LOG.info(f"Registered health check for {service_name}")

    def unregister_check(self, service_name: str):
        """Unregister a health check."""
        if service_name in self._checks:
            del self._checks[service_name]
            LOG.info(f"Unregistered health check for {service_name}")

    def register_alert_callback(
        self,
        callback: Callable[[Alert], Awaitable[None]]
    ):
        """Register callback for health alerts."""
        self._alert_callbacks.append(callback)

    async def check_service(self, service_name: str) -> HealthCheckResult:
        """Perform health check for a specific service."""
        if service_name not in self._checks:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                message=f"No health check registered for {service_name}"
            )

        start_time = time.time()
        try:
            result = await self._checks[service_name]()
            result.response_time_ms = (time.time() - start_time) * 1000

            # Store result
            old_result = self._last_results.get(service_name)
            self._last_results[service_name] = result

            # Check if status changed and trigger alerts
            if old_result and old_result.status != result.status:
                await self._handle_status_change(service_name, old_result, result)

            return result

        except Exception as e:
            LOG.error(f"Health check failed for {service_name}: {e}")
            result = HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )
            self._last_results[service_name] = result
            return result

    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """Perform health checks on all registered services."""
        results = {}

        tasks = {
            name: self.check_service(name)
            for name in self._checks.keys()
        }

        completed = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for name, result in zip(tasks.keys(), completed):
            if isinstance(result, Exception):
                results[name] = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Error: {str(result)}"
                )
            else:
                results[name] = result

        return results

    async def _handle_status_change(
        self,
        service_name: str,
        old_result: HealthCheckResult,
        new_result: HealthCheckResult
    ):
        """Handle health status changes and trigger alerts."""
        # Determine alert level
        alert_level = self._determine_alert_level(new_result.status)

        # Check if we should send alert (rate limiting)
        if not self._should_send_alert(service_name, alert_level):
            return

        alert = Alert(
            level=alert_level,
            service=service_name,
            message=f"Health status changed: {old_result.status.value} → {new_result.status.value}",
            details={
                "old_status": old_result.status.value,
                "new_status": new_result.status.value,
                "message": new_result.message,
                "details": new_result.details
            }
        )

        # Send to all callbacks
        for callback in self._alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                LOG.error(f"Alert callback failed: {e}")

        # Update last alert time
        self._last_alerts[f"{service_name}_{alert_level.value}"] = datetime.now()

    def _determine_alert_level(self, status: HealthStatus) -> AlertLevel:
        """Determine alert level from health status."""
        if status == HealthStatus.UNHEALTHY:
            return AlertLevel.CRITICAL
        elif status == HealthStatus.DEGRADED:
            return AlertLevel.WARNING
        elif status == HealthStatus.HEALTHY:
            return AlertLevel.INFO
        else:
            return AlertLevel.WARNING

    def _should_send_alert(
        self,
        service_name: str,
        alert_level: AlertLevel,
        min_interval_seconds: int = 300
    ) -> bool:
        """Check if alert should be sent based on rate limiting."""
        key = f"{service_name}_{alert_level.value}"
        last_alert = self._last_alerts.get(key)

        if last_alert is None:
            return True

        elapsed = (datetime.now() - last_alert).total_seconds()
        return elapsed >= min_interval_seconds

    def get_last_result(self, service_name: str) -> HealthCheckResult:
        """Get last health check result for a service."""
        return self._last_results.get(
            service_name,
            HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                message="No health check performed yet"
            )
        )

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health based on all services."""
        if not self._last_results:
            return HealthStatus.UNKNOWN

        statuses = [result.status for result in self._last_results.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
