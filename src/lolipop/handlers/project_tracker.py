"""
Lolipop Project Tracker

Central registry for all Lolipop projects.

Design goals:
- Global, per-user storage
- Install-method independent (brew / pip / source)
- Git is scanned, never enforced
- No internal implementation details recorded
- Supports CLI, TUI, and VS Code extension
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any

from lolipop.clients.git_client import GitClient, GitError
from lolipop.modules.logger import warn
from lolipop.modules.app_support import get_lolipop_data_dir

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

APP_SUPPORT = get_lolipop_data_dir()
ASSETS_DIR = APP_SUPPORT / ".assets"
TRACKING_DIR = ASSETS_DIR / "tracking"

TRACKING_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]

def _file_hash(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    try:
        return _hash(path.read_text(encoding="utf-8"))
    except Exception:
        return None

# ---------------------------------------------------------------------
# Project identity
# ---------------------------------------------------------------------

def project_id(project_dir: Path, git_remote: Optional[str]) -> str:
    """
    Stable project ID:
    - Prefer git remote (clone-safe)
    - Fallback to absolute path
    """
    if git_remote:
        return _hash(git_remote)
    return _hash(str(project_dir.resolve()))

def tracking_file(project_name: str) -> Path:
    return TRACKING_DIR / f"{project_name}.json"

# ---------------------------------------------------------------------
# Load / Save
# ---------------------------------------------------------------------

def load_project(project_name: str) -> Optional[dict]:
    path = tracking_file(project_name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def save_project(metadata: dict) -> None:
    path = tracking_file(metadata["name"])
    path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def list_projects() -> list[dict]:
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in TRACKING_DIR.glob("*.json")
    ]

# ---------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------

def register_project(
    project_dir: Path,
    cfg: Optional[Any] = None,
    activate: bool = True,
) -> dict:
    """
    Register or update a project.

    - Does not require lolipop.yaml
    - Scans Git if present
    - Preserves historical metadata
    """

    project_dir = project_dir.resolve()
    name = cfg.name if cfg and getattr(cfg, "name", None) else project_dir.name

    existing = load_project(name)

    # -------------------------
    # Git scan (never force)
    # -------------------------

    git_info = {
        "initialized": False,
        "remote": None,
        "branch": None,
        "commit": None,
        "dirty": False,
    }

    try:
        git = GitClient(project_dir)
        info_data = git.info()

        git_info.update(
            initialized=True,
            remote=info_data.get("remote"),
            branch=info_data.get("branch"),
            commit=info_data.get("commit"),
            dirty=info_data.get("dirty", False),
        )
    except GitError:
        pass

    pid = project_id(project_dir, git_info["remote"])

    # -------------------------
    # Config file hashes
    # -------------------------

    config_files = {
        "lolipop.yaml": _file_hash(project_dir / "lolipop.yaml"),
        "loli.yaml": _file_hash(project_dir / "loli.yaml"),
        "pyproject.toml": _file_hash(project_dir / "pyproject.toml"),
        "requirements.txt": _file_hash(project_dir / "requirements.txt"),
    }

    # -------------------------
    # Environment
    # -------------------------

    env_cfg = cfg.environment if cfg and hasattr(cfg, "environment") else {}
    environment = {
        "name": env_cfg.get("name") if isinstance(env_cfg, dict) else None,
        "path": str(env_cfg.get("path")) if isinstance(env_cfg, dict) else None,
        "python_version": None,
    }

    # -------------------------
    # Metadata
    # -------------------------

    metadata = {
        "id": pid,
        "name": name,
        "path": str(project_dir),

        "created_at": (
            existing["created_at"]
            if existing and "created_at" in existing
            else _now()
        ),
        "last_seen": _now(),

        "active": False,
        "opened_in_vscode": existing.get("opened_in_vscode", False)
        if existing else False,

        "environment": environment,
        "git": git_info,
        "config_files": config_files,

        "project_metadata": {
            "version": cfg.data.get("version") if cfg else None,
            "description": cfg.data.get("description") if cfg else None,
            "author": cfg.data.get("author") if cfg else None,
        },

        "dependencies": cfg.data.get("dependencies", []) if cfg else [],

        "features": existing.get("features", {}) if existing else {},
        "templates_used": existing.get("templates_used", []) if existing else [],

        "history": (
            existing.get("history", [])
            if existing
            else []
        ),
    }

    if not existing:
        metadata["history"].append(
            {
                "timestamp": _now(),
                "action": "init",
                "details": {},
            }
        )

    save_project(metadata)

    if activate:
        set_active_project(name)

    return metadata

# ---------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------

def set_active_project(project_name: str):
    """
    Marks exactly one project as active.
    """
    for file in TRACKING_DIR.glob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        data["active"] = data["name"] == project_name
        data["last_seen"] = _now()
        file.write_text(json.dumps(data, indent=2), encoding="utf-8")

def get_active_project() -> Optional[dict]:
    for project in list_projects():
        if project.get("active"):
            return project
    return None

# ---------------------------------------------------------------------
# History / events
# ---------------------------------------------------------------------

def record_event(
    project_name: str,
    action: str,
    details: Optional[dict] = None,
):
    data = load_project(project_name)
    if not data:
        warn(f"Project '{project_name}' not found in tracking")
        return

    data["last_seen"] = _now()
    data.setdefault("history", []).append(
        {
            "timestamp": _now(),
            "action": action,
            "details": details or {},
        }
    )

    save_project(data)

# ---------------------------------------------------------------------
# VS Code integration hooks (passive)
# ---------------------------------------------------------------------

def mark_opened_in_vscode(project_name: str, opened: bool = True):
    data = load_project(project_name)
    if not data:
        return

    data["opened_in_vscode"] = opened
    data["last_seen"] = _now()
    save_project(data)
