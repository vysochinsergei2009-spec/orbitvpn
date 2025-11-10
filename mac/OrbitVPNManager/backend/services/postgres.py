"""PostgreSQL Monitor Service"""
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
from manager.config.manager_config import PostgresConfig
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class PostgresMonitorService(ManagedService):
    """Monitors PostgreSQL health and performance"""

    def __init__(self, config: PostgresConfig):
        super().__init__("postgres")
        self.config = config

    async def start(self) -> bool:
        """Start monitoring."""
        self._set_status(ServiceStatus.RUNNING)
        self._set_started()
        LOG.info("PostgreSQL monitor started")
        return True

    async def stop(self, graceful: bool = True, timeout: int = 30) -> bool:
        """Stop monitoring."""
        self._set_stopped()
        LOG.info("PostgreSQL monitor stopped")
        return True

    async def restart(self) -> bool:
        """Restart monitoring."""
        await self.stop()
        await self.start()
        self._increment_restart_count()
        return True

    async def health_check(self) -> HealthCheckResult:
        """Check PostgreSQL health."""
        start_time = time.time()

        try:
            from app.repo.db import get_db
            from sqlalchemy import text

            async for db in get_db():
                # Test connection with simple query
                query_start = time.time()
                result = await db.execute(text("SELECT 1"))
                query_time_ms = (time.time() - query_start) * 1000

                # Get database stats
                stats_query = text("""
                    SELECT
                        pg_database_size(current_database()) as db_size,
                        (SELECT count(*) FROM pg_stat_activity) as active_connections,
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_queries
                """)

                stats_result = await db.execute(stats_query)
                stats = stats_result.fetchone()

                db_size_mb = stats[0] / 1024 / 1024 if stats[0] else 0
                active_connections = stats[1] if stats[1] else 0
                active_queries = stats[2] if stats[2] else 0

                details = {
                    "query_time_ms": round(query_time_ms, 2),
                    "db_size_mb": round(db_size_mb, 2),
                    "active_connections": active_connections,
                    "active_queries": active_queries
                }

                response_time = (time.time() - start_time) * 1000

                # Check for slow queries
                if query_time_ms > self.config.slow_query_threshold:
                    return HealthCheckResult(
                        status=HealthStatus.DEGRADED,
                        message=f"Slow queries detected ({query_time_ms:.2f}ms)",
                        details=details,
                        response_time_ms=response_time
                    )

                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message=f"PostgreSQL healthy ({query_time_ms:.2f}ms)",
                    details=details,
                    response_time_ms=response_time
                )

        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"PostgreSQL connection failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )

    async def get_metrics(self) -> ServiceMetrics:
        """Get PostgreSQL metrics."""
        metrics = ServiceMetrics()

        try:
            from app.repo.db import get_db
            from sqlalchemy import text

            async for db in get_db():
                # Get database size
                size_query = text("SELECT pg_database_size(current_database())")
                size_result = await db.execute(size_query)
                db_size = size_result.scalar()
                metrics.memory_mb = db_size / 1024 / 1024 if db_size else 0

                # Get connection stats
                conn_query = text("""
                    SELECT
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                """)

                conn_result = await db.execute(conn_query)
                conn_stats = conn_result.fetchone()

                # Get table stats
                table_query = text("""
                    SELECT
                        count(*) as total_tables,
                        sum(n_tup_ins) as total_inserts,
                        sum(n_tup_upd) as total_updates,
                        sum(n_tup_del) as total_deletes
                    FROM pg_stat_user_tables
                """)

                table_result = await db.execute(table_query)
                table_stats = table_result.fetchone()

                metrics.custom_metrics = {
                    "total_connections": conn_stats[0] if conn_stats else 0,
                    "active_connections": conn_stats[1] if conn_stats else 0,
                    "idle_connections": conn_stats[2] if conn_stats else 0,
                    "total_tables": table_stats[0] if table_stats else 0,
                    "total_inserts": table_stats[1] if table_stats else 0,
                    "total_updates": table_stats[2] if table_stats else 0,
                    "total_deletes": table_stats[3] if table_stats else 0
                }

                break

        except Exception as e:
            LOG.error(f"Error collecting PostgreSQL metrics: {e}")

        return metrics

    async def get_table_stats(self) -> dict:
        """Get statistics for all tables."""
        try:
            from app.repo.db import get_db
            from sqlalchemy import text

            async for db in get_db():
                query = text("""
                    SELECT
                        schemaname,
                        relname as table_name,
                        n_live_tup as row_count,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) as size
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                """)

                result = await db.execute(query)
                rows = result.fetchall()

                tables = []
                for row in rows:
                    tables.append({
                        "schema": row[0],
                        "table_name": row[1],
                        "row_count": row[2],
                        "inserts": row[3],
                        "updates": row[4],
                        "deletes": row[5],
                        "size": row[6]
                    })

                return {"tables": tables}

        except Exception as e:
            LOG.error(f"Error getting table stats: {e}")
            return {"tables": []}
