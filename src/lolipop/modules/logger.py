"""
Lolipop logger module

"""

from rich.console import Console

console = Console()

def info(msg: str):
    console.print(f"[cyan]ℹ {msg}[/cyan]")

def success(msg: str):
    console.print(f"[green]✔ {msg}[/green]")

def warn(msg: str):
    console.print(f"[yellow]⚠ {msg}[/yellow]")

def error(msg: str):
    console.print(f"[red]✖ {msg}[/red]")
