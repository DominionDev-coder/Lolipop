"""
Git client for Lolipop

Uses GitPython when available and valid.
Falls back to subprocess for resilience.
"""

from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING
import subprocess

if TYPE_CHECKING:
    from git import Repo  # type-only import

try:
    import git
    GITPYTHON_AVAILABLE = True
except ImportError:
    git = None
    GITPYTHON_AVAILABLE = False


class GitError(Exception):
    pass


class GitClient:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir.resolve()
        self.backend = "subprocess"
        self.repo: Optional["Repo"] = None

        if GITPYTHON_AVAILABLE:
            try:
                self.repo = git.Repo(self.project_dir)
                self.backend = "gitpython"
            except Exception:
                self.repo = None

        if not self.is_repo():
            raise GitError(f"{self.project_dir} is not a git repository")

    # -------------------------
    # Low-level subprocess
    # -------------------------
    def run_git(self, *args: str) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(e.stderr.strip() or "Git command failed")

    def is_repo(self) -> bool:
        try:
            self.run_git("rev-parse", "--is-inside-work-tree")
            return True
        except GitError:
            return False

    # -------------------------
    # Repository lifecycle
    # -------------------------
    @staticmethod
    def init_repo(project_dir: Path):
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
        )

    # -------------------------
    # Metadata
    # -------------------------
    def info(self) -> Dict[str, Any]:
        if self.backend == "gitpython" and self.repo is not None:
            return {
                "backend": "gitpython",
                "branch": self.repo.active_branch.name,
                "commit": self.repo.head.commit.hexsha,
                "dirty": self.repo.is_dirty(),
                "remote": self.repo.remotes.origin.url
                if self.repo.remotes
                else None,
            }

        return {
            "backend": "subprocess",
            "branch": self.run_git("rev-parse", "--abbrev-ref", "HEAD"),
            "commit": self.run_git("rev-parse", "HEAD"),
            "dirty": bool(self.run_git("status", "--porcelain")),
            "remote": self.run_git("config", "--get", "remote.origin.url"),
        }

    # -------------------------
    # Common operations
    # -------------------------
    def commit(self, message: str):
        if self.backend == "gitpython" and self.repo is not None:
            self.repo.git.add(A=True)
            self.repo.index.commit(message)
        else:
            self.run_git("add", ".")
            self.run_git("commit", "-m", message)

    def pull(self):
        if self.backend == "gitpython" and self.repo is not None and self.repo.remotes:
            self.repo.remotes.origin.pull()
        else:
            self.run_git("pull")

    def push(self):
        if self.backend == "gitpython" and self.repo is not None and self.repo.remotes:
            self.repo.remotes.origin.push()
        else:
            self.run_git("push")

    def add_remote(self, name: str, url: str):
        if self.backend == "gitpython" and self.repo is not None:
            self.repo.create_remote(name, url)
        else:
            self.run_git("remote", "add", name, url)
