"""
Lolipop run command

Handles running a lolipop project by executing its defined scripts
"""

from pathlib import Path
import typer
import subprocess
import os

from lolipop.modules.config_loader import load_project_config
from lolipop.handlers.environment import resolve_environment, create_base_environment
from lolipop.handlers.script_runner import run_scripts
# from lolipop.handlers.project_tracker import update_last_run
from lolipop.modules.logger import error, info

app = typer.Typer(help="Run a Lolipop project")


@app.callback(invoke_without_command=True)
def run(
    target: str = typer.Argument(".", help="Project directory or file to run")
):
    try:
        target_path = Path(target).resolve()

        # -------------------------
        # Resolve project + config
        # -------------------------
        project_dir = (
            target_path.parent if target_path.is_file() else target_path
        )
        cfg = load_project_config(project_dir)

        # -------------------------
        # Environment
        # -------------------------
        env_cfg = cfg.environment or {}
        env_path = (
            resolve_environment(env_cfg)
            if env_cfg.get("name")
            else create_base_environment()
        )

        lang = env_cfg.get("lang", "python")
        version = env_cfg.get("version")

        if lang != "python":
            raise RuntimeError(f"Unsupported language: {lang}")

        python_cmd = (
            f"python{version}" if version else "python3.11"
        )

        env = os.environ.copy()
        env["PATH"] = f"{env_path / 'bin'}:{env['PATH']}"

        # -------------------------
        # Run file directly
        # -------------------------
        if target_path.is_file():
            info(f"Running {target_path.name} using {python_cmd}")
            subprocess.run(
                [python_cmd, target_path.name],
                cwd=project_dir,
                env=env,
                check=True,
            )
            # update_last_run(cfg.name, "run:file", {"file": target_path.name})
            return

        # -------------------------
        # Run project scripts
        # -------------------------
        scripts = cfg.scripts.get("run")
        if not scripts:
            raise RuntimeError("No 'run' script defined in config")

        run_scripts(
            scripts=scripts,
            project_dir=project_dir,
            env_path=env_path,
        )

        # update_last_run(cfg.name, "run:project")

    except Exception as e:
        error(str(e))
        raise typer.Exit(1)
