"""CLI Interface for OrbitVPN Manager"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.tree import Tree
from rich.text import Text

sys.path.insert(0, str(Path(__file__).parent.parent))

from manager.config.manager_config import load_config
from manager.core.supervisor import ServiceSupervisor
from manager.core.models import ServiceStatus, HealthStatus
from manager.services.telegram_bot import TelegramBotService
from manager.services.marzban import MarzbanMonitorService
from manager.services.redis import RedisMonitorService
from manager.services.postgres import PostgresMonitorService
from manager.utils.logger import setup_logging, get_logger

console = Console()
LOG = get_logger(__name__)


def get_status_color(status: ServiceStatus) -> str:
    """Get color for service status."""
    colors = {
        ServiceStatus.RUNNING: "green",
        ServiceStatus.STOPPED: "red",
        ServiceStatus.STARTING: "yellow",
        ServiceStatus.STOPPING: "yellow",
        ServiceStatus.RESTARTING: "yellow",
        ServiceStatus.FAILED: "red",
        ServiceStatus.UNKNOWN: "dim"
    }
    return colors.get(status, "white")


def get_health_color(health: HealthStatus) -> str:
    """Get color for health status."""
    colors = {
        HealthStatus.HEALTHY: "green",
        HealthStatus.DEGRADED: "yellow",
        HealthStatus.UNHEALTHY: "red",
        HealthStatus.UNKNOWN: "dim"
    }
    return colors.get(health, "white")


async def create_supervisor() -> ServiceSupervisor:
    """Create and initialize supervisor with all services."""
    config = load_config()

    # Setup logging
    setup_logging(
        log_level=config.logging.level,
        log_file=config.project_dir / "logs" / "manager.log"
    )

    supervisor = ServiceSupervisor(config)

    # Register services
    if config.telegram_bot.enabled:
        supervisor.register_service(TelegramBotService(config.telegram_bot))

    if config.marzban_monitor.enabled:
        supervisor.register_service(MarzbanMonitorService(config.marzban_monitor))

    if config.redis.enabled:
        supervisor.register_service(RedisMonitorService(config.redis))

    if config.postgres.enabled:
        supervisor.register_service(PostgresMonitorService(config.postgres))

    return supervisor


@click.group()
@click.pass_context
def cli(ctx):
    """OrbitVPN Service Manager - Control your bot and Marzban infrastructure"""
    ctx.ensure_object(dict)


# ============================================================================
# SERVICE MANAGEMENT COMMANDS
# ============================================================================

@cli.command()
@click.argument('service', required=False)
def start(service: Optional[str]):
    """Start service(s)"""
    asyncio.run(_start(service))


async def _start(service_name: Optional[str]):
    supervisor = await create_supervisor()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        if service_name:
            task = progress.add_task(f"Starting {service_name}...", total=None)
            success = await supervisor.start_service(service_name)

            if success:
                console.print(f"[green]✓[/green] {service_name} started successfully")
            else:
                console.print(f"[red]✗[/red] Failed to start {service_name}")
        else:
            task = progress.add_task("Starting all services...", total=None)
            results = await supervisor.start_all()

            for svc, success in results.items():
                if success:
                    console.print(f"[green]✓[/green] {svc} started")
                else:
                    console.print(f"[red]✗[/red] {svc} failed")


@cli.command()
@click.argument('service', required=False)
@click.option('--force', is_flag=True, help='Force stop without graceful shutdown')
def stop(service: Optional[str], force: bool):
    """Stop service(s)"""
    asyncio.run(_stop(service, not force))


async def _stop(service_name: Optional[str], graceful: bool):
    supervisor = await create_supervisor()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        if service_name:
            task = progress.add_task(f"Stopping {service_name}...", total=None)
            success = await supervisor.stop_service(service_name, graceful=graceful)

            if success:
                console.print(f"[green]✓[/green] {service_name} stopped")
            else:
                console.print(f"[red]✗[/red] Failed to stop {service_name}")
        else:
            task = progress.add_task("Stopping all services...", total=None)
            results = await supervisor.stop_all(graceful=graceful)

            for svc, success in results.items():
                if success:
                    console.print(f"[green]✓[/green] {svc} stopped")
                else:
                    console.print(f"[red]✗[/red] {svc} failed")


@cli.command()
@click.argument('service', required=False)
def restart(service: Optional[str]):
    """Restart service(s)"""
    asyncio.run(_restart(service))


async def _restart(service_name: Optional[str]):
    supervisor = await create_supervisor()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        if service_name:
            task = progress.add_task(f"Restarting {service_name}...", total=None)
            success = await supervisor.restart_service(service_name)

            if success:
                console.print(f"[green]✓[/green] {service_name} restarted")
            else:
                console.print(f"[red]✗[/red] Failed to restart {service_name}")


@cli.command()
def status():
    """Show status of all services"""
    asyncio.run(_status())


async def _status():
    supervisor = await create_supervisor()
    system_status = await supervisor.get_system_status()

    # Create status table
    table = Table(title="Service Status", box=box.ROUNDED, show_header=True)
    table.add_column("Service", style="cyan", width=20)
    table.add_column("Status", width=12)
    table.add_column("Health", width=12)
    table.add_column("CPU %", justify="right", width=10)
    table.add_column("Memory", justify="right", width=12)
    table.add_column("Uptime", justify="right", width=15)

    for service_name, service_info in system_status['services'].items():
        status_color = get_status_color(ServiceStatus(service_info['status']))
        health_color = get_health_color(HealthStatus(service_info['health']['status']))

        metrics = service_info['metrics']
        uptime_str = f"{metrics['uptime_seconds'] // 3600}h {(metrics['uptime_seconds'] % 3600) // 60}m"

        table.add_row(
            service_name,
            f"[{status_color}]{service_info['status']}[/{status_color}]",
            f"[{health_color}]{service_info['health']['status']}[/{health_color}]",
            f"{metrics['cpu_percent']:.1f}",
            f"{metrics['memory_mb']:.1f} MB",
            uptime_str
        )

    console.print(table)

    # Overall system health
    overall_health = system_status['overall_health']
    health_color = get_health_color(HealthStatus(overall_health))

    console.print(f"\n[bold]Overall Health:[/bold] [{health_color}]{overall_health}[/{health_color}]")
    console.print(f"[dim]Running: {system_status['running_services']}/{system_status['total_services']}[/dim]")


# ============================================================================
# HEALTH & MONITORING COMMANDS
# ============================================================================

@cli.command()
def health():
    """Perform health check on all services"""
    asyncio.run(_health())


async def _health():
    supervisor = await create_supervisor()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        task = progress.add_task("Checking health...", total=None)
        health_checker = supervisor.get_health_checker()
        results = await health_checker.check_all()

    # Display results
    table = Table(title="Health Check Results", box=box.ROUNDED)
    table.add_column("Service", style="cyan")
    table.add_column("Status", width=12)
    table.add_column("Message")
    table.add_column("Response Time", justify="right")

    for service_name, result in results.items():
        health_color = get_health_color(result.status)

        table.add_row(
            service_name,
            f"[{health_color}]{result.status.value}[/{health_color}]",
            result.message,
            f"{result.response_time_ms:.2f}ms"
        )

    console.print(table)


@cli.command()
@click.argument('service', required=False)
@click.option('--hours', '-h', default=1, help='Hours of history to show')
def metrics(service: Optional[str], hours: int):
    """Show metrics for service(s)"""
    asyncio.run(_metrics(service, hours))


async def _metrics(service_name: Optional[str], hours: int):
    supervisor = await create_supervisor()
    metrics_collector = supervisor.get_metrics_collector()

    if service_name:
        # Show detailed metrics for one service
        latest = metrics_collector.get_latest_metrics(service_name)
        aggregated = metrics_collector.get_aggregated_metrics(service_name, hours)

        if not latest:
            console.print(f"[yellow]No metrics found for {service_name}[/yellow]")
            return

        panel_content = f"""
[cyan]Latest Metrics:[/cyan]
  CPU: {latest.cpu_percent:.1f}%
  Memory: {latest.memory_mb:.1f} MB ({latest.memory_percent:.1f}%)
  Uptime: {latest.uptime_seconds // 3600}h {(latest.uptime_seconds % 3600) // 60}m

[cyan]Last {hours}h Aggregated:[/cyan]
  CPU Avg: {aggregated.get('cpu_avg', 0):.1f}% (Max: {aggregated.get('cpu_max', 0):.1f}%)
  Memory Avg: {aggregated.get('memory_avg', 0):.1f} MB (Max: {aggregated.get('memory_max', 0):.1f} MB)
  Samples: {aggregated.get('samples_count', 0)}
"""

        # Add custom metrics if available
        if latest.custom_metrics:
            panel_content += "\n[cyan]Custom Metrics:[/cyan]\n"
            for key, value in latest.custom_metrics.items():
                panel_content += f"  {key}: {value}\n"

        console.print(Panel(panel_content.strip(), title=f"Metrics: {service_name}", border_style="blue"))

    else:
        # Show metrics for all services
        all_metrics = metrics_collector.get_all_latest_metrics()

        table = Table(title="Service Metrics", box=box.ROUNDED)
        table.add_column("Service", style="cyan")
        table.add_column("CPU %", justify="right")
        table.add_column("Memory", justify="right")
        table.add_column("Uptime", justify="right")

        for svc_name, svc_metrics in all_metrics.items():
            uptime_str = f"{svc_metrics.uptime_seconds // 3600}h {(svc_metrics.uptime_seconds % 3600) // 60}m"

            table.add_row(
                svc_name,
                f"{svc_metrics.cpu_percent:.1f}%",
                f"{svc_metrics.memory_mb:.1f} MB",
                uptime_str
            )

        console.print(table)


# ============================================================================
# MARZBAN COMMANDS
# ============================================================================

@cli.group()
def marzban():
    """Marzban instance management"""
    pass


@marzban.command('list')
def marzban_list():
    """List all Marzban instances and nodes"""
    asyncio.run(_marzban_list())


async def _marzban_list():
    supervisor = await create_supervisor()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching Marzban instances...", total=None)

        # Get Marzban service
        marzban_service = None
        for service in supervisor._services.values():
            if isinstance(service, MarzbanMonitorService):
                marzban_service = service
                break

        if not marzban_service:
            console.print("[red]Marzban monitor service not found[/red]")
            return

        instances = await marzban_service.get_instances_info()

    # Create tree visualization
    tree = Tree("[bold cyan]Marzban Infrastructure[/bold cyan]")

    for instance in instances:
        health_color = get_health_color(instance.status)
        instance_label = (
            f"[{health_color}]{instance.name}[/{health_color}] "
            f"({instance.instance_id}) - "
            f"Users: {instance.total_users} / Active: {instance.active_users}"
        )

        instance_node = tree.add(instance_label)

        # Add nodes
        for node in instance.nodes:
            node_health_color = get_health_color(node.status)
            node_label = (
                f"[{node_health_color}]{node.name}[/{node_health_color}] - "
                f"{node.address} - Users: {node.users_count}"
            )
            instance_node.add(node_label)

    console.print(tree)

    # Summary table
    table = Table(title="Summary", box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    total_instances = len(instances)
    active_instances = len([i for i in instances if i.is_active])
    total_users = sum(i.total_users for i in instances)
    active_users = sum(i.active_users for i in instances)
    total_nodes = sum(len(i.nodes) for i in instances)

    table.add_row("Total Instances", str(total_instances))
    table.add_row("Active Instances", str(active_instances))
    table.add_row("Total Users", str(total_users))
    table.add_row("Active Users", str(active_users))
    table.add_row("Total Nodes", str(total_nodes))

    console.print(table)


@marzban.command('check')
@click.argument('instance_id')
def marzban_check(instance_id: str):
    """Check specific Marzban instance"""
    asyncio.run(_marzban_check(instance_id))


async def _marzban_check(instance_id: str):
    supervisor = await create_supervisor()

    marzban_service = None
    for service in supervisor._services.values():
        if isinstance(service, MarzbanMonitorService):
            marzban_service = service
            break

    if not marzban_service:
        console.print("[red]Marzban monitor service not found[/red]")
        return

    instance = await marzban_service.get_instance_details(instance_id)

    if not instance:
        console.print(f"[red]Instance {instance_id} not found[/red]")
        return

    # Display instance details
    health_color = get_health_color(instance.status)

    panel_content = f"""
[cyan]Instance ID:[/cyan] {instance.instance_id}
[cyan]Name:[/cyan] {instance.name}
[cyan]URL:[/cyan] {instance.base_url}
[cyan]Status:[/cyan] [{health_color}]{instance.status.value}[/{health_color}]
[cyan]Active:[/cyan] {instance.is_active}
[cyan]Priority:[/cyan] {instance.priority}
[cyan]Total Users:[/cyan] {instance.total_users}
[cyan]Active Users:[/cyan] {instance.active_users}
[cyan]Nodes:[/cyan] {len(instance.nodes)}
"""

    console.print(Panel(panel_content.strip(), title=f"Instance: {instance.name}", border_style="blue"))

    # Nodes table
    if instance.nodes:
        table = Table(title="Nodes", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Address")
        table.add_column("Status")
        table.add_column("Users", justify="right")
        table.add_column("Active", justify="right")

        for node in instance.nodes:
            node_health_color = get_health_color(node.status)

            table.add_row(
                node.name,
                node.address,
                f"[{node_health_color}]{node.status.value}[/{node_health_color}]",
                str(node.users_count),
                str(node.users_active)
            )

        console.print(table)


# ============================================================================
# CACHE COMMANDS
# ============================================================================

@cli.group()
def cache():
    """Redis cache management"""
    pass


@cache.command('clear')
@click.option('--pattern', '-p', default='*', help='Key pattern to clear')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def cache_clear(pattern: str, yes: bool):
    """Clear Redis cache keys"""
    asyncio.run(_cache_clear(pattern, yes))


async def _cache_clear(pattern: str, yes: bool):
    from app.utils.redis import init_cache, get_redis, close_cache

    await init_cache()
    redis = await get_redis()

    keys = await redis.keys(pattern)

    if not keys:
        console.print(f"[yellow]No keys found matching: {pattern}[/yellow]")
        await close_cache()
        return

    console.print(f"[cyan]Found {len(keys)} keys matching '{pattern}'[/cyan]")

    if not yes:
        if not click.confirm(f'Delete {len(keys)} keys?'):
            console.print("[yellow]Cancelled[/yellow]")
            await close_cache()
            return

    deleted = await redis.delete(*keys)
    console.print(f"[green]✓ Deleted {deleted} keys[/green]")
    await close_cache()


@cache.command('stats')
def cache_stats():
    """Show Redis cache statistics"""
    asyncio.run(_cache_stats())


async def _cache_stats():
    from app.utils.redis import init_cache, get_redis, close_cache

    await init_cache()
    redis = await get_redis()

    info = await redis.info('stats')
    memory_info = await redis.info('memory')

    table = Table(title="Redis Statistics", box=box.DOUBLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total keys", str(await redis.dbsize()))
    table.add_row("Memory used", f"{memory_info.get('used_memory_human', 'N/A')}")
    table.add_row("Connected clients", str(info.get('connected_clients', 0)))
    table.add_row("Total connections", str(info.get('total_connections_received', 'N/A')))
    table.add_row("Total commands", str(info.get('total_commands_processed', 'N/A')))
    table.add_row("Keyspace hits", str(info.get('keyspace_hits', 'N/A')))
    table.add_row("Keyspace misses", str(info.get('keyspace_misses', 'N/A')))

    hit_rate = 0
    if info.get('keyspace_hits') and info.get('keyspace_misses'):
        total = info['keyspace_hits'] + info['keyspace_misses']
        if total > 0:
            hit_rate = (info['keyspace_hits'] / total) * 100
    table.add_row("Hit rate", f"{hit_rate:.2f}%")

    console.print(table)
    await close_cache()


# ============================================================================
# INFO COMMAND
# ============================================================================

@cli.command()
def info():
    """Show bot configuration info"""
    from config import BOT_TOKEN, DATABASE_NAME, REDIS_URL, PLANS

    panel_content = f"""
[cyan]Database:[/cyan] {DATABASE_NAME}
[cyan]Redis:[/cyan] {REDIS_URL}
[cyan]Bot Token:[/cyan] {BOT_TOKEN[:20]}...

[cyan]Subscription Plans:[/cyan]
"""

    for plan_key, plan in PLANS.items():
        panel_content += f"  • {plan_key}: {plan['days']} days - {plan['price']} RUB\n"

    console.print(Panel(panel_content.strip(), title="OrbitVPN Bot Info", border_style="blue"))


# ============================================================================
# WEB DASHBOARD COMMAND
# ============================================================================

@cli.command()
@click.option('--host', default=None, help='Host to bind (default: from config)')
@click.option('--port', default=None, type=int, help='Port to bind (default: from config)')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def dashboard(host: Optional[str], port: Optional[int], reload: bool):
    """Start web dashboard"""
    import uvicorn
    from manager.web.app import create_app

    config = load_config()

    host = host or config.web_dashboard.host
    port = port or config.web_dashboard.port

    console.print(Panel.fit(
        f"[bold cyan]Web Dashboard[/bold cyan]\n"
        f"Starting on [green]http://{host}:{port}[/green]\n\n"
        f"Press Ctrl+C to stop",
        border_style="cyan"
    ))

    app = create_app()

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == '__main__':
    console.print(Panel.fit(
        "[bold cyan]OrbitVPN Service Manager[/bold cyan]\n"
        "Control your Telegram bot and Marzban infrastructure",
        border_style="cyan"
    ))
    cli()
