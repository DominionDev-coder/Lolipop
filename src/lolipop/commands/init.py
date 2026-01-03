"""
Lolipop init command

Initialize a project from lolipop.yaml / loli.yaml (.yaml or .yml)
or initialize the current directory as a Lolipop project.
"""

from pathlib import Path
import typer

from lolipop.modules.config_loader import load_lolipop_yaml
from lolipop.handlers.project_init import init_project
from lolipop.handlers.project_tracker import register_project
from lolipop.clients.git_client import GitClient
from lolipop.modules.logger import error, info, success

app = typer.Typer(help="Initialize a Lolipop project")

@app.callback(invoke_without_command=True)
def init(
    file: Path | None = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to lolipop.yaml / loli.yaml (.yaml or .yml)",
    ),
    directory: Path | None = typer.Option(
        None,
        "--directory",
        "-d",
        help="Directory to create the project in",
    ),
):
    try:
        # -------------------------
        # Detect config file
        # -------------------------
        if file:
            cfg_path = file
        else:
            for name in (
                "lolipop.yaml",
                "lolipop.yml",
                "loli.yaml",
                "loli.yml",
            ):
                p = Path(name)
                if p.exists():
                    cfg_path = p
                    break
            else:
                raise FileNotFoundError(
                    "No lolipop.yaml / loli.yaml found in current directory"
                )

        cfg_path = cfg_path.resolve()

        cfg = load_lolipop_yaml(cfg_path)

        if not cfg.name:
            raise RuntimeError("Project name is required")

        # -------------------------
        # Target directory
        # -------------------------
        target_dir = (
            directory.resolve()
            if directory
            else Path.cwd()
        )

        # -------------------------
        # Init project
        # -------------------------
        init_project(cfg, target_dir)

        # Move config into project if needed
        target_cfg = target_dir / cfg_path.name
        if cfg_path != target_cfg:
            target_cfg.write_text(cfg_path.read_text(encoding="utf-8"), encoding="utf-8")
            success(f"Config placed at {target_cfg}")

        # -------------------------
        # Git (scan, don’t force)
        # -------------------------
        if not (target_dir / ".git").exists():
            info("Initializing Git repository...")
            GitClient.init_repo(target_dir)

        # -------------------------
        # Tracking
        # -------------------------
        register_project(target_dir, cfg)

        success(f"Project '{cfg.name}' initialized successfully 🍭")

    except Exception as e:
        error(str(e))
        raise typer.Exit(code=1)
