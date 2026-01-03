"""
Lolipop environment handler

Environment creation and management handler
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict
from lolipop.modules.logger import info

LOLI_ENV_HOME = Path.home() / ".local" / "share" / "lolipop" / "envs"
BASE_ENV_NAME = "lolipop-base"


class EnvironmentError(Exception):
    pass


def env_path(name: str) -> Path:
    # ENV DIRECTORY NAME == ENV NAME (IMPORTANT)
    return LOLI_ENV_HOME / name


def environment_exists(name: str) -> bool:
    return env_path(name).exists()


def create_venv(name: str, python_version: str | None = None) -> Path:
    path = env_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)

    python_cmd = "python3.11"
    if python_version:
        python_cmd = f"python{python_version}"

    try:
        subprocess.run(
            [python_cmd, "-m", "venv", str(path)],
            check=True,
        )
    except Exception as e:
        raise EnvironmentError(f"Failed to create venv '{name}': {e}")

    return path


def resolve_environment(env_cfg: Dict) -> Path:
    """
    env_cfg example:
      name: Lolipop
      lang: python
      version: "3.11"
      type: venv
    """

    name = env_cfg.get("name")
    if not name:
        raise EnvironmentError("Environment name is required")

    if environment_exists(name):
        return env_path(name)

    env_type = env_cfg.get("type", "venv")
    python_version = env_cfg.get("version")

    if env_type != "venv":
        raise EnvironmentError("Only venv environments are supported for now")

    return create_venv(name, python_version)


def create_base_environment() -> Path:
    """
    Ensure the lolipop-base environment exists.
    Returns the path to the base environment.
    """
    if environment_exists(BASE_ENV_NAME):
        return env_path(BASE_ENV_NAME)

    info(f"Creating base environment '{BASE_ENV_NAME}'...")
    # Use current Python interpreter for base env
    return create_venv(BASE_ENV_NAME, python_version=None)
