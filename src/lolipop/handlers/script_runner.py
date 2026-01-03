"""
Script runner for lolipop

Handles running scripts defined in the project configuration
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable


class ScriptExecutionError(Exception):
    pass


def run_scripts(
    scripts: Iterable[str],
    project_dir: Path,
    env_path: Path,
) -> None:
    if not scripts:
        return

    env = os.environ.copy()

    bin_dir = env_path / "bin"
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env["VIRTUAL_ENV"] = str(env_path)

    for cmd in scripts:
        try:
            subprocess.run(
                cmd,
                shell=True,
                cwd=project_dir,
                env=env,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ScriptExecutionError(f"Command failed: {cmd}") from e
