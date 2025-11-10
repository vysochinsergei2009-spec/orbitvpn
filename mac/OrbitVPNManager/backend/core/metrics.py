"""Metrics collection system"""
import asyncio
import psutil
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

from manager.core.models import ServiceMetrics
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class MetricsCollector:
    """Collects and stores metrics for services"""

    def __init__(self, retention_hours: int = 24):
        self._retention_hours = retention_hours
        self._metrics_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)  # Keep last 1000 data points
        )
        self._process_cache: Dict[str, psutil.Process] = {}

    def record_metrics(self, service_name: str, metrics: ServiceMetrics):
        """Record metrics for a service."""
        self._metrics_history[service_name].append(metrics)
        self._cleanup_old_metrics(service_name)

    def get_latest_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """Get the most recent metrics for a service."""
        history = self._metrics_history.get(service_name)
        if history:
            return history[-1]
        return None

    def get_metrics_history(
        self,
        service_name: str,
        hours: int = 1
    ) -> List[ServiceMetrics]:
        """Get metrics history for the specified time period."""
        history = self._metrics_history.get(service_name, deque())
        cutoff = datetime.now() - timedelta(hours=hours)

        return [
            m for m in history
            if m.timestamp >= cutoff
        ]

    def get_all_latest_metrics(self) -> Dict[str, ServiceMetrics]:
        """Get latest metrics for all services."""
        return {
            service: history[-1]
            for service, history in self._metrics_history.items()
            if history
        }

    async def collect_process_metrics(
        self,
        service_name: str,
        pid: Optional[int] = None
    ) -> ServiceMetrics:
        """Collect system metrics for a process."""
        metrics = ServiceMetrics()

        if pid is None:
            return metrics

        try:
            # Get or create process object
            if service_name not in self._process_cache or self._process_cache[service_name].pid != pid:
                self._process_cache[service_name] = psutil.Process(pid)

            process = self._process_cache[service_name]

            # Collect metrics
            with process.oneshot():
                metrics.cpu_percent = process.cpu_percent(interval=0.1)
                mem_info = process.memory_info()
                metrics.memory_mb = mem_info.rss / 1024 / 1024
                metrics.memory_percent = process.memory_percent()

                # Calculate uptime
                create_time = datetime.fromtimestamp(process.create_time())
                metrics.uptime_seconds = int((datetime.now() - create_time).total_seconds())

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            LOG.warning(f"Could not collect metrics for {service_name} (PID: {pid}): {e}")

        return metrics

    def _cleanup_old_metrics(self, service_name: str):
        """Remove metrics older than retention period."""
        history = self._metrics_history[service_name]
        cutoff = datetime.now() - timedelta(hours=self._retention_hours)

        # Remove old entries from the left
        while history and history[0].timestamp < cutoff:
            history.popleft()

    def get_aggregated_metrics(
        self,
        service_name: str,
        hours: int = 1
    ) -> Dict[str, float]:
        """Get aggregated metrics (avg, min, max) for a time period."""
        history = self.get_metrics_history(service_name, hours)

        if not history:
            return {}

        cpu_values = [m.cpu_percent for m in history]
        mem_values = [m.memory_mb for m in history]

        return {
            "cpu_avg": sum(cpu_values) / len(cpu_values),
            "cpu_max": max(cpu_values),
            "cpu_min": min(cpu_values),
            "memory_avg": sum(mem_values) / len(mem_values),
            "memory_max": max(mem_values),
            "memory_min": min(mem_values),
            "samples_count": len(history)
        }

    def clear_metrics(self, service_name: Optional[str] = None):
        """Clear metrics history for a service or all services."""
        if service_name:
            if service_name in self._metrics_history:
                self._metrics_history[service_name].clear()
        else:
            self._metrics_history.clear()
            self._process_cache.clear()
