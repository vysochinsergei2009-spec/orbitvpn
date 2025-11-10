"""Alert Management System"""
import asyncio
from typing import List, Callable, Awaitable
from datetime import datetime, timedelta

from manager.core.models import Alert, AlertLevel
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self, min_interval_seconds: int = 300):
        self.min_interval = min_interval_seconds
        self._handlers: List[Callable[[Alert], Awaitable[None]]] = []
        self._alert_history: List[Alert] = []
        self._last_alert_times: dict = {}

    def register_handler(self, handler: Callable[[Alert], Awaitable[None]]):
        """Register an alert handler."""
        self._handlers.append(handler)
        LOG.info(f"Registered alert handler: {handler.__name__}")

    async def send_alert(self, alert: Alert):
        """Send an alert to all registered handlers."""
        # Check rate limiting
        key = f"{alert.service}_{alert.level.value}"
        last_time = self._last_alert_times.get(key)

        if last_time:
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed < self.min_interval:
                LOG.debug(f"Alert rate limited for {key} (elapsed: {elapsed}s)")
                return

        # Store alert
        self._alert_history.append(alert)
        self._last_alert_times[key] = datetime.now()

        # Send to handlers
        for handler in self._handlers:
            try:
                await handler(alert)
            except Exception as e:
                LOG.error(f"Alert handler {handler.__name__} failed: {e}")

        LOG.info(f"Alert sent: {alert.level.value} - {alert.service} - {alert.message}")

    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self._alert_history
            if alert.timestamp >= cutoff
        ]

    def get_unacknowledged_alerts(self) -> List[Alert]:
        """Get unacknowledged alerts."""
        return [alert for alert in self._alert_history if not alert.acknowledged]

    def acknowledge_alert(self, alert: Alert):
        """Mark alert as acknowledged."""
        alert.acknowledged = True

    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        self._alert_history = [
            alert for alert in self._alert_history
            if alert.timestamp >= cutoff
        ]
