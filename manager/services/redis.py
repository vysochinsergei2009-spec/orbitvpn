"""Redis Monitor Service"""
import time
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manager.core.service import ManagedService
from manager.core.models import (
    ServiceStatus,
    HealthStatus,
    HealthCheckResult,
    ServiceMetrics
)
from manager.config.manager_config import RedisConfig
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class RedisMonitorService(ManagedService):
    """Monitors Redis health and performance"""

    def __init__(self, config: RedisConfig):
        super().__init__("redis")
        self.config = config

    async def start(self) -> bool:
        """Start monitoring."""
        self._set_status(ServiceStatus.RUNNING)
        self._set_started()
        LOG.info("Redis monitor started")
        return True

    async def stop(self, graceful: bool = True, timeout: int = 30) -> bool:
        """Stop monitoring."""
        self._set_stopped()
        LOG.info("Redis monitor stopped")
        return True

    async def restart(self) -> bool:
        """Restart monitoring."""
        await self.stop()
        await self.start()
        self._increment_restart_count()
        return True

    async def health_check(self) -> HealthCheckResult:
        """Check Redis health."""
        start_time = time.time()

        try:
            from app.utils.redis import get_redis

            redis = await get_redis()

            # Measure latency with PING
            ping_start = time.time()
            await redis.ping()
            latency_ms = (time.time() - ping_start) * 1000

            # Get info
            info = await redis.info()

            # Get memory usage
            memory_used_mb = info.get('used_memory', 0) / 1024 / 1024
            memory_max_mb = info.get('maxmemory', 0) / 1024 / 1024

            # Get stats
            total_keys = await redis.dbsize()
            connected_clients = info.get('connected_clients', 0)

            details = {
                "latency_ms": round(latency_ms, 2),
                "memory_used_mb": round(memory_used_mb, 2),
                "memory_max_mb": round(memory_max_mb, 2),
                "total_keys": total_keys,
                "connected_clients": connected_clients,
                "uptime_seconds": info.get('uptime_in_seconds', 0)
            }

            response_time = (time.time() - start_time) * 1000

            # Determine health status
            if latency_ms > self.config.max_latency_ms:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    message=f"High latency: {latency_ms:.2f}ms",
                    details=details,
                    response_time_ms=response_time
                )

            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message=f"Redis healthy (latency: {latency_ms:.2f}ms)",
                details=details,
                response_time_ms=response_time
            )

        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )

    async def get_metrics(self) -> ServiceMetrics:
        """Get Redis metrics."""
        metrics = ServiceMetrics()

        try:
            from app.utils.redis import get_redis

            redis = await get_redis()
            info = await redis.info()

            # Memory metrics
            metrics.memory_mb = info.get('used_memory', 0) / 1024 / 1024
            memory_max = info.get('maxmemory', 0)
            if memory_max > 0:
                metrics.memory_percent = (
                    info.get('used_memory', 0) / memory_max * 100
                )

            # CPU metrics
            metrics.cpu_percent = info.get('used_cpu_sys', 0) + info.get('used_cpu_user', 0)

            # Uptime
            metrics.uptime_seconds = info.get('uptime_in_seconds', 0)

            # Custom metrics
            metrics.custom_metrics = {
                "total_keys": await redis.dbsize(),
                "connected_clients": info.get('connected_clients', 0),
                "total_connections": info.get('total_connections_received', 0),
                "total_commands": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "evicted_keys": info.get('evicted_keys', 0),
                "expired_keys": info.get('expired_keys', 0)
            }

            # Calculate hit rate
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            if hits + misses > 0:
                metrics.custom_metrics["hit_rate_percent"] = round(
                    (hits / (hits + misses)) * 100, 2
                )

        except Exception as e:
            LOG.error(f"Error collecting Redis metrics: {e}")

        return metrics

    async def get_key_patterns(self) -> dict:
        """Get breakdown of keys by pattern."""
        try:
            from app.utils.redis import get_redis

            redis = await get_redis()
            all_keys = await redis.keys('*')

            patterns = {}
            for key in all_keys:
                prefix = key.split(':')[0]
                patterns[prefix] = patterns.get(prefix, 0) + 1

            return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))

        except Exception as e:
            LOG.error(f"Error getting key patterns: {e}")
            return {}
