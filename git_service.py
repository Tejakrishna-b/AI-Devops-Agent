"""
Git service — clone, branch, backup, commit, push using GitPython.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

from git import Repo, GitCommandError


class GitService:
    """Handles all Git operations via GitPython."""

    def __init__(self, token: str = "", owner: str = "", repo_name: str = ""):
        self.token = token
        self.owner = owner
        self.repo_name = repo_name
        self.repo: Repo | None = None
        self.local_path: Path | None = None

    # ------------------------------------------------------------------ clone
    def clone_repository(self, repo_url: str, dest: str = "cloned_repo") -> Path:
        """Clone a remote repository. Injects token for HTTPS auth."""
        self.local_path = Path(dest)
        if self.local_path.exists():
            shutil.rmtree(self.local_path)

        auth_url = repo_url
        if self.token and repo_url.startswith("https://"):
            # https://<token>@github.com/owner/repo.git
            auth_url = repo_url.replace("https://", f"https://{self.token}@")

        self.repo = Repo.clone_from(auth_url, str(self.local_path))
        return self.local_path

    def open_repo(self, path: str) -> None:
        """Open an already-cloned local repository."""
        self.local_path = Path(path)
        self.repo = Repo(path)

    # -------------------------------------------------------------- snapshot
    def create_backup_snapshot(self, tool_name: str, version: str) -> str:
        """Create a backup git tag on the current HEAD and push it."""
        tag_name = f"backup-{tool_name.lower()}-{version}"
        self.repo.git.checkout("main")
        self.repo.remotes.origin.pull()
        self.repo.create_tag(tag_name, message=f"Backup before upgrading {tool_name} {version}")
        try:
            self.repo.remotes.origin.push(tag_name)
        except GitCommandError:
            pass  # push may fail if no remote write access yet
        return tag_name

    # --------------------------------------------------------------- branch
    def create_feature_branch(self, tool_name: str, target_version: str) -> str:
        """Create and checkout a feature branch."""
        branch_name = f"feature/upgrade-{tool_name.lower()}-{target_version}"
        if branch_name in [ref.name for ref in self.repo.branches]:
            self.repo.git.checkout(branch_name)
        else:
            self.repo.git.checkout("-b", branch_name)
        return branch_name

    # ---------------------------------------------------------- commit/push
    def commit_and_push(self, branch_name: str, message: str, files: list[str]) -> bool:
        """Stage listed files, commit, and push."""
        for f in files:
            self.repo.index.add([f])
        self.repo.index.commit(message)
        try:
            self.repo.remotes.origin.push(branch_name)
            return True
        except GitCommandError:
            return False
