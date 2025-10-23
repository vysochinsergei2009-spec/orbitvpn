import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

sys.path.insert(0, str(Path(__file__).parent))

from app.utils.redis import init_cache, get_redis, close_cache
from config import REDIS_URL

console = Console()


@click.group()
def cli():
    """OrbitVPN Bot Manager - Manage your Telegram bot"""
    pass


@cli.group()
def cache():
    """Redis cache management"""
    pass


@cache.command()
@click.option('--pattern', '-p', default='*', help='Key pattern to clear (default: all)')
@click.option('--confirm/--no-confirm', default=True, help='Ask for confirmation')
def clear(pattern, confirm):
    """Clear Redis cache keys"""
    asyncio.run(_clear_cache(pattern, confirm))


async def _clear_cache(pattern: str, confirm: bool):
    await init_cache()
    redis = await get_redis()

    keys = await redis.keys(pattern)

    if not keys:
        console.print(f"[yellow]No keys found matching pattern: {pattern}[/yellow]")
        await close_cache()
        return

    table = Table(title=f"Found {len(keys)} keys", box=box.ROUNDED)
    table.add_column("Key", style="cyan")

    for key in keys[:10]:
        table.add_row(key)

    if len(keys) > 10:
        table.add_row(f"[dim]... and {len(keys) - 10} more[/dim]")

    console.print(table)

    if confirm:
        if not click.confirm(f'\nDelete {len(keys)} keys?'):
            console.print("[yellow]Cancelled[/yellow]")
            await close_cache()
            return

    deleted = await redis.delete(*keys)
    console.print(f"[green]✓ Deleted {deleted} keys[/green]")
    await close_cache()


@cache.command()
def telegraph():
    """Clear Telegraph installation guide cache"""
    asyncio.run(_clear_cache('telegraph:install:*', confirm=False))
    console.print("[green]✓ Telegraph cache cleared. New pages will be created on next request.[/green]")


@cache.command()
def users():
    """Clear all user-related cache"""
    asyncio.run(_clear_cache('user:*', confirm=True))


@cache.command()
def stats():
    """Show Redis cache statistics"""
    asyncio.run(_show_stats())


async def _show_stats():
    await init_cache()
    redis = await get_redis()

    info = await redis.info('stats')

    table = Table(title="Redis Cache Statistics", box=box.DOUBLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total keys", str(await redis.dbsize()))
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

    all_keys = await redis.keys('*')
    if all_keys:
        console.print(f"\n[cyan]Key patterns:[/cyan]")
        patterns = {}
        for key in all_keys:
            prefix = key.split(':')[0]
            patterns[prefix] = patterns.get(prefix, 0) + 1

        for prefix, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            console.print(f"  {prefix}:* → {count} keys")

    await close_cache()


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


if __name__ == '__main__':
    console.print(Panel.fit(
        "[bold cyan]OrbitVPN Bot Manager[/bold cyan]\n"
        "Manage your Telegram VPN bot",
        border_style="cyan"
    ))
    cli()
