"""
OrbitVPN Bot Manager

Unified management interface for OrbitVPN services.
This file provides backward compatibility while delegating to the new manager system.
"""
import sys
from pathlib import Path

# Import the new CLI system
from manager.cli import cli

if __name__ == '__main__':
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    console.print(Panel.fit(
        "[bold cyan]OrbitVPN Service Manager[/bold cyan]\n"
        "Control your Telegram bot and Marzban infrastructure\n\n"
        "[dim]Powered by manager v1.0.0[/dim]",
        border_style="cyan"
    ))

    cli()
