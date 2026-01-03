"""
Project initialization handler

Handles initializing a project from a lolipop.yaml / loli.yaml configuration file.
"""

from pathlib import Path

from lolipop.modules.config_loader import LolipopConfig
from lolipop.handlers.environment import (
    resolve_environment,
    create_base_environment,
)
from lolipop.handlers.script_runner import run_scripts
from lolipop.modules.logger import info, success


def init_project(cfg: LolipopConfig, project_dir: Path) -> None:
    project_dir = project_dir.resolve()

    # Allow current or empty directory
    if project_dir.exists() and any(project_dir.iterdir()):
        info(f"Using existing directory: {project_dir}")
    else:
        project_dir.mkdir(parents=True, exist_ok=True)

    project_name = cfg.name or project_dir.name
    info(f"Initializing project: {project_name}")

    # -------------------------
    # Environment
    # -------------------------
    env_cfg = cfg.environment
    if env_cfg:
        env_path = resolve_environment(env_cfg)
        info(f"Using environment: {env_path.name}")
    else:
        env_path = create_base_environment()
        info(f"No environment specified, using base environment")

    # -------------------------
    # Files
    # -------------------------
    for rel_path, content in cfg.files.items():
        file_path = project_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(str(content), encoding="utf-8")
        info(f"Created file: {file_path}")

    # -------------------------
    # Setup
    # -------------------------
    if cfg.setup:
        run_scripts(
            scripts=cfg.setup,
            project_dir=project_dir,
            env_path=env_path,
        )

    success(f"Project '{project_name}' initialized successfully")
