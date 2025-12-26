"""Manager Configuration Module"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import yaml


@dataclass
class ServiceConfig:
    """Configuration for a managed service"""
    enabled: bool = True
    restart_policy: str = "always"  # always, on-failure, never
    max_restarts: int = 5
    restart_delay: int = 10  # seconds
    health_check_interval: int = 30
    health_check_timeout: int = 10
    health_check_retries: int = 3


@dataclass
class TelegramBotConfig(ServiceConfig):
    """Telegram Bot specific configuration"""
    process_name: str = "orbitvpn_bot"
    tmux_session: str = "orbitvpn_bot"
    log_file: str = "bot.log"


@dataclass
class MarzbanMonitorConfig(ServiceConfig):
    """Marzban monitoring configuration"""
    check_interval: int = 60
    auto_detect_instances: bool = True
    load_balance_check: bool = True


@dataclass
class RedisConfig(ServiceConfig):
    """Redis monitoring configuration"""
    max_latency_ms: int = 100
    check_memory: bool = True


@dataclass
class PostgresConfig(ServiceConfig):
    """PostgreSQL monitoring configuration"""
    check_connections: bool = True
    slow_query_threshold: int = 1000  # ms


@dataclass
class WebDashboardConfig:
    """Web Dashboard configuration"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8080
    auth_enabled: bool = True
    secret_key: str = ""
    admin_users: Dict[str, str] = field(default_factory=dict)  # username: hashed_password
    session_timeout: int = 3600  # seconds


@dataclass
class AlertConfig:
    """Alert configuration"""
    telegram_enabled: bool = True
    admin_chat_ids: List[int] = field(default_factory=list)
    alert_levels: List[str] = field(default_factory=lambda: ["critical", "error"])
    min_interval: int = 300  # Minimum seconds between same alert


@dataclass
class MetricsConfig:
    """Metrics configuration"""
    prometheus_export: bool = False
    prometheus_port: int = 9090
    retention_days: int = 7
    collect_interval: int = 10  # seconds


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"  # json or text
    max_size_mb: int = 100
    backup_count: int = 5
    log_dir: str = "logs"


@dataclass
class ManagerConfig:
    """Main Manager Configuration"""
    telegram_bot: TelegramBotConfig = field(default_factory=TelegramBotConfig)
    marzban_monitor: MarzbanMonitorConfig = field(default_factory=MarzbanMonitorConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    postgres: PostgresConfig = field(default_factory=PostgresConfig)
    web_dashboard: WebDashboardConfig = field(default_factory=WebDashboardConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Paths
    project_dir: Path = field(default_factory=lambda: Path("/root/orbitvpn"))
    venv_path: Path = field(default_factory=lambda: Path("/root/orbitvpn/venv"))

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ManagerConfig":
        """Load configuration from YAML file"""
        if not os.path.exists(yaml_path):
            return cls()

        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        config = cls()

        # Parse services
        services = data.get('services', {})
        if 'telegram_bot' in services:
            config.telegram_bot = TelegramBotConfig(**services['telegram_bot'])
        if 'marzban_monitor' in services:
            config.marzban_monitor = MarzbanMonitorConfig(**services['marzban_monitor'])
        if 'redis' in services:
            config.redis = RedisConfig(**services['redis'])
        if 'postgres' in services:
            config.postgres = PostgresConfig(**services['postgres'])

        # Parse monitoring
        monitoring = data.get('monitoring', {})
        if 'web_dashboard' in monitoring:
            config.web_dashboard = WebDashboardConfig(**monitoring['web_dashboard'])
        if 'alerts' in monitoring:
            config.alerts = AlertConfig(**monitoring['alerts'])
        if 'metrics' in monitoring:
            config.metrics = MetricsConfig(**monitoring['metrics'])

        # Parse logging
        if 'logging' in data:
            config.logging = LoggingConfig(**data['logging'])

        return config

    def to_yaml(self, yaml_path: str):
        """Save configuration to YAML file"""
        data = {
            'services': {
                'telegram_bot': {
                    'enabled': self.telegram_bot.enabled,
                    'restart_policy': self.telegram_bot.restart_policy,
                    'max_restarts': self.telegram_bot.max_restarts,
                    'restart_delay': self.telegram_bot.restart_delay,
                    'health_check_interval': self.telegram_bot.health_check_interval,
                },
                'marzban_monitor': {
                    'enabled': self.marzban_monitor.enabled,
                    'check_interval': self.marzban_monitor.check_interval,
                    'auto_detect_instances': self.marzban_monitor.auto_detect_instances,
                },
                'redis': {
                    'enabled': self.redis.enabled,
                    'health_check_interval': self.redis.health_check_interval,
                    'max_latency_ms': self.redis.max_latency_ms,
                },
                'postgres': {
                    'enabled': self.postgres.enabled,
                    'health_check_interval': self.postgres.health_check_interval,
                },
            },
            'monitoring': {
                'web_dashboard': {
                    'enabled': self.web_dashboard.enabled,
                    'host': self.web_dashboard.host,
                    'port': self.web_dashboard.port,
                    'auth_enabled': self.web_dashboard.auth_enabled,
                },
                'alerts': {
                    'telegram_enabled': self.alerts.telegram_enabled,
                    'admin_chat_ids': self.alerts.admin_chat_ids,
                    'alert_levels': self.alerts.alert_levels,
                },
                'metrics': {
                    'prometheus_export': self.metrics.prometheus_export,
                    'retention_days': self.metrics.retention_days,
                },
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'max_size_mb': self.logging.max_size_mb,
            }
        }

        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_config(config_path: Optional[str] = None) -> ManagerConfig:
    """Load manager configuration"""
    if config_path is None:
        config_path = "/root/orbitvpn/manager/config/services.yaml"

    if os.path.exists(config_path):
        return ManagerConfig.from_yaml(config_path)

    # Create default config
    config = ManagerConfig()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    config.to_yaml(config_path)
    return config
