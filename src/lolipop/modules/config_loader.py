"""
Lolipop configuration loader

Handles loading configuration from:
- lolipop.yaml / lolipop.yml
- loli.yaml / loli.yml
- pyproject.toml ([tool.lolipop])
"""

from __future__ import annotations

import tomllib
import yaml
from pathlib import Path
from typing import Any, Dict


class LolipopConfigError(Exception):
    pass


class LolipopConfig:
    def __init__(self, source: str, data: Dict[str, Any], path: Path | None = None):
        self.source = source
        self.data = data
        self.path = path

    # ---- synced ----
    @property
    def name(self) -> str | None:
        return self.data.get("name")

    @property
    def version(self) -> str | None:
        return self.data.get("version")

    @property
    def author(self) -> str | None:
        return self.data.get("author")

    @property
    def dependencies(self) -> list:
        return self.data.get("dependencies", [])

    # ---- lolipop-only ----
    @property
    def environment(self) -> dict:
        return self.data.get("environment", {})

    @property
    def scripts(self) -> dict:
        return self.data.get("scripts", {})

    @property
    def setup(self) -> list:
        return self.data.get("setup", [])

    @property
    def files(self) -> dict:
        return self.data.get("files", {})

    @property
    def command(self) -> dict:
        return self.data.get("command", {})


# --------------------------------------------------
# YAML loader
# --------------------------------------------------

def load_lolipop_yaml(path: Path) -> LolipopConfig:
    if not path.exists():
        raise LolipopConfigError(f"Config file not found: {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        raise LolipopConfigError(f"Failed to load YAML {path}: {e}")

    if not isinstance(data, dict):
        raise LolipopConfigError("Invalid YAML structure (expected mapping)")

    return LolipopConfig(source="yaml", data=data, path=path)


# --------------------------------------------------
# pyproject.toml loader
# --------------------------------------------------

def load_pyproject(path: Path) -> LolipopConfig | None:
    if not path.exists():
        return None

    try:
        with path.open("rb") as f:
            pyproject = tomllib.load(f)
    except Exception:
        return None

    lolipop = pyproject.get("tool", {}).get("lolipop")
    if not isinstance(lolipop, dict):
        return None

    return LolipopConfig(source="pyproject", data=lolipop, path=path)


# --------------------------------------------------
# Resolver
# --------------------------------------------------

def load_project_config(project_dir: Path) -> LolipopConfig:
    for name in ("lolipop.yaml", "lolipop.yml", "loli.yaml", "loli.yml"):
        path = project_dir / name
        if path.exists():
            return load_lolipop_yaml(path)

    py_cfg = load_pyproject(project_dir / "pyproject.toml")
    if py_cfg:
        return py_cfg

    raise LolipopConfigError(
        "No lolipop.yaml/.yml, loli.yaml/.yml, or [tool.lolipop] found"
    )
