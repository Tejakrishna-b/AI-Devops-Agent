"""
DevOpsUpgradeAgent — core orchestrator for the AI DevOps Upgrade Agent.

Coordinates: request parsing → repo clone → backup → branch → scan →
upgrade → terraform validate → security scan → PR creation → report.
"""

import re
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import Config
from git_service import GitService
from terraform_service import TerraformService
from llm_service import LLMService
from jira_service import JiraService
from validator import Validator
from prompts import upgrade_code_prompt

from github import Github


class DevOpsUpgradeAgent:
    """Core system controller — automates DevOps tool upgrades."""

    SUPPORTED_TOOLS = ["SonarQube", "Snyk", "Datadog", "Terraform", "Docker"]

    def __init__(self, config: Config | None = None):
        self.cfg = config or Config()
        self.git_svc = GitService(
            token=self.cfg.git_token,
            owner=self.cfg.git_owner,
            repo_name=self.cfg.git_repo,
        )
        self.tf_svc = TerraformService()
        self.jira_svc = JiraService(self.cfg.jira_url, self.cfg.jira_username, self.cfg.jira_token)
        self.validator = Validator()

        # LLM service is optional — only created when an API key is available
        self.llm: LLMService | None = None
        if self.cfg.openai_api_key:
            self.llm = LLMService(api_key=self.cfg.openai_api_key, model=self.cfg.openai_model)

        # State for the current run
        self.status: dict[str, str] = {}
        self._report: dict = {}

    # ------------------------------------------------------------------ 1
    def parse_request(
        self,
        text: str = "",
        tool_name: str = "",
        current_version: str = "",
        target_version: str = "",
        repository: str = "",
        environment: str = "dev",
    ) -> dict:
        """Parse a free-text or structured upgrade request."""
        if tool_name and current_version and target_version:
            return {
                "tool_name": tool_name,
                "current_version": current_version,
                "target_version": target_version,
                "repository": repository or self.cfg.github_url,
                "environment": environment,
            }

        # Free-text parsing
        m = re.search(
            r"(?:upgrade|update|migrate)\s+([\w./-]+)\s+(?:from\s+(?:version\s+)?)"
            r"([\d.]+)\s+to\s+(?:version\s+)?([\d.]+)",
            text,
            re.IGNORECASE,
        )
        if m:
            return {
                "tool_name": m.group(1),
                "current_version": m.group(2),
                "target_version": m.group(3),
                "repository": repository or self.cfg.github_url,
                "environment": environment,
            }

        raise ValueError(f"Could not parse upgrade request: {text}")

    # ------------------------------------------------------------------ 2
    def clone_repository(self, repo_url: str) -> Path:
        """Clone the target repository locally."""
        self._update_status("Repository Cloned", "in_progress")
        dest = str(self.cfg.workspace_dir / "cloned_repo")
        path = self.git_svc.clone_repository(repo_url, dest)
        self._update_status("Repository Cloned", "completed")
        return path

    # ------------------------------------------------------------------ 3
    def create_backup_snapshot(self, tool_name: str, version: str) -> str:
        """Tag the current HEAD as a backup before making changes."""
        self._update_status("Backup Created", "in_progress")
        tag = self.git_svc.create_backup_snapshot(tool_name, version)
        self._update_status("Backup Created", "completed")
        return tag

    # ------------------------------------------------------------------ 4
    def create_feature_branch(self, tool_name: str, target_version: str) -> str:
        """Create a feature branch for the upgrade."""
        self._update_status("Feature Branch Created", "in_progress")
        branch = self.git_svc.create_feature_branch(tool_name, target_version)
        self._update_status("Feature Branch Created", "completed")
        return branch

    # ------------------------------------------------------------------ 5
    def scan_repository_for_tool(self, repo_path: str, tool_name: str, version: str):
        """Scan repository for version references."""
        return self.validator.scan_repository_for_tool(repo_path, tool_name, version)

    # ------------------------------------------------------------------ 6
    def upgrade_code(self, matches, tool_name: str, current_version: str, target_version: str) -> list[str]:
        """Upgrade version references found by the scanner."""
        self._update_status("Code Updated", "in_progress")
        modified_files: list[str] = []

        for match in matches:
            fpath = match.file
            original = Path(fpath).read_text()

            if self.llm:
                updated = self.llm.generate_upgraded_code(
                    tool_name, current_version, target_version, original
                )
                # Strip markdown code fences if present
                updated = re.sub(r"^```\w*\n?", "", updated)
                updated = re.sub(r"\n?```$", "", updated)
                Path(fpath).write_text(updated)
            else:
                self.validator.replace_version_in_file(fpath, current_version, target_version)

            modified_files.append(fpath)

        self._update_status("Code Updated", "completed")
        return modified_files

    # ------------------------------------------------------------------ 7
    def run_terraform_validation(self, working_dir: str) -> dict:
        """Run terraform fmt, validate, plan."""
        self._update_status("Terraform Validation Running", "in_progress")
        self.tf_svc.working_dir = working_dir
        results = self.tf_svc.run_full_validation()

        all_ok = all(r["success"] for r in results.values())

        # If validation fails and LLM is available, attempt auto-fix once
        if not all_ok and self.llm:
            errors = "\n".join(r.get("stderr", "") for r in results.values() if not r["success"])
            tf_files = list(Path(working_dir).glob("*.tf"))
            for tf_file in tf_files:
                code = tf_file.read_text()
                fixed = self.llm.fix_terraform_errors(errors, code)
                fixed = re.sub(r"^```\w*\n?", "", fixed)
                fixed = re.sub(r"\n?```$", "", fixed)
                tf_file.write_text(fixed)
            results = self.tf_svc.run_full_validation()

        status = "completed" if all(r["success"] for r in results.values()) else "failed"
        self._update_status("Terraform Validation Running", status)
        return results

    # ------------------------------------------------------------------ 8
    def run_security_scan(self, repo_path: str) -> dict:
        return self.validator.run_security_scan(repo_path)

    # ------------------------------------------------------------------ 9
    def create_pull_request(
        self,
        branch_name: str,
        tool_name: str,
        target_version: str,
        modified_files: list[str],
        backup_tag: str,
        validation_status: str,
    ) -> Optional[str]:
        """Create a GitHub pull request via PyGithub."""
        self._update_status("Pull Request Created", "in_progress")
        if not self.cfg.git_token:
            self._update_status("Pull Request Created", "failed")
            return None

        g = Github(self.cfg.git_token)
        repo = g.get_repo(f"{self.cfg.git_owner}/{self.cfg.git_repo}")

        title = f"Upgrade {tool_name} to {target_version}"
        body = (
            f"## Upgrade Summary\n\n"
            f"- **Tool:** {tool_name}\n"
            f"- **Target version:** {target_version}\n"
            f"- **Files modified:** {len(modified_files)}\n"
            f"- **Backup snapshot:** `{backup_tag}`\n"
            f"- **Terraform validation:** {validation_status}\n\n"
            f"### Modified Files\n"
            + "\n".join(f"- `{f}`" for f in modified_files)
            + "\n\n---\n*Created by AI DevOps Upgrade Agent*"
        )

        pr = repo.create_pull(title=title, body=body, head=branch_name, base="main")
        self._update_status("Pull Request Created", "completed")
        self._update_status("Waiting For Human Approval", "pending")
        return pr.html_url

    # ------------------------------------------------------------------ 10
    def generate_upgrade_report(
        self,
        tool_name: str,
        current_version: str,
        target_version: str,
        modified_files: list[str],
        tf_result: dict,
        security_result: dict,
        pr_url: str,
        backup_tag: str,
    ) -> dict:
        """Generate a structured upgrade report."""
        report = {
            "tool_name": tool_name,
            "old_version": current_version,
            "new_version": target_version,
            "files_modified": modified_files,
            "terraform_validation": tf_result,
            "security_scan": security_result,
            "pr_link": pr_url,
            "backup_snapshot_tag": backup_tag,
            "generated_at": datetime.now().isoformat(),
        }
        self._report = report
        return report

    # ------------------------------------------------------------------ run
    def run(
        self,
        tool_name: str,
        current_version: str,
        target_version: str,
        repository: str,
        environment: str = "dev",
        status_callback=None,
    ) -> dict:
        """Execute the full upgrade workflow end-to-end."""
        self._status_callback = status_callback
        request = self.parse_request(
            tool_name=tool_name,
            current_version=current_version,
            target_version=target_version,
            repository=repository,
            environment=environment,
        )

        repo_path = self.clone_repository(request["repository"])
        backup_tag = self.create_backup_snapshot(request["tool_name"], request["current_version"])
        branch = self.create_feature_branch(request["tool_name"], request["target_version"])

        matches = self.scan_repository_for_tool(
            str(repo_path), request["tool_name"], request["current_version"]
        )
        modified = self.upgrade_code(
            matches, request["tool_name"], request["current_version"], request["target_version"]
        )

        # Terraform validation (only if .tf files exist)
        tf_result: dict = {}
        tf_files = list(repo_path.glob("**/*.tf"))
        if tf_files:
            tf_result = self.run_terraform_validation(str(repo_path))

        security = self.run_security_scan(str(repo_path))

        # Second AI validation pass
        if self.llm and modified:
            for fpath in modified:
                original = ""  # already overwritten — best-effort
                updated = Path(fpath).read_text()
                result = self.llm.validate_upgrade(
                    request["tool_name"],
                    request["current_version"],
                    request["target_version"],
                    original,
                    updated,
                )
                if not result.get("valid", True):
                    # If invalid, regenerate
                    new_code = self.llm.generate_upgraded_code(
                        request["tool_name"],
                        request["current_version"],
                        request["target_version"],
                        updated,
                    )
                    new_code = re.sub(r"^```\w*\n?", "", new_code)
                    new_code = re.sub(r"\n?```$", "", new_code)
                    Path(fpath).write_text(new_code)

        # Commit & push
        commit_msg = f"chore: upgrade {request['tool_name']} from {request['current_version']} to {request['target_version']}"
        self.git_svc.commit_and_push(branch, commit_msg, modified)

        # Create PR
        val_status = "passed" if (not tf_result or all(r["success"] for r in tf_result.values())) else "failed"
        pr_url = self.create_pull_request(
            branch, request["tool_name"], request["target_version"],
            modified, backup_tag, val_status,
        )

        return self.generate_upgrade_report(
            request["tool_name"],
            request["current_version"],
            request["target_version"],
            modified,
            tf_result,
            security,
            pr_url or "",
            backup_tag,
        )

    # ------------------------------------------------------------------ helpers
    def _update_status(self, step: str, state: str):
        self.status[step] = state
        if hasattr(self, "_status_callback") and self._status_callback:
            self._status_callback(step, state)
