"""
Lolipop project command

Manage tracked Lolipop projects
"""

import typer
from lolipop.handlers.project_tracker import (
    list_projects,
    load_project,
    set_active_project,
)
from lolipop.modules.logger import info, success, error

app = typer.Typer(help="Manage Lolipop projects", no_args_is_help=True)


@app.command("list")
def list_cmd():
    """List all tracked projects"""
    projects = list_projects()

    if not projects:
        info("No projects tracked yet.")
        return

    for p in projects:
        marker = "✔" if p.get("active") else " "
        info(f"[{marker}] {p.get('name')} → {p.get('path')}")


@app.command("current")
def current():
    """Show the active project"""
    for p in list_projects():
        if p.get("active"):
            success(f"Active project: {p.get('name')}")
            info(p.get("path"))
            return

    error("No active project set")


@app.command("info")
def info_cmd(name: str):
    """Show detailed project info"""
    data = load_project(name)
    if not data:
        error(f"Project '{name}' not found")
        raise typer.Exit(1)

    info(f"Project: {data.get('name')}")
    info(f"Path: {data.get('path')}")

    env = data.get("environment", {})
    info(f"Environment: {env.get('name')}")

    git = data.get("git", {})
    if git.get("initialized"):
        info(f"Git branch: {git.get('branch')}")
        info(f"Git commit: {git.get('commit')}")
        info(f"Dirty: {git.get('dirty')}")
    else:
        info("Git: not initialized")

    if data.get("opened_in_vscode"):
        info("Opened in VS Code ✔")

    if data.get("opened_in_console"):
        info("Opened in Console ✔")


@app.command("switch")
def switch(name: str):
    """Switch active project"""
    if not load_project(name):
        error(f"Project '{name}' not found")
        raise typer.Exit(1)

    set_active_project(name)
    success(f"Switched active project to '{name}'")
