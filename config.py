"""
Configuration management for AI DevOps Upgrade Agent.
Loads settings from config/config.yaml and environment variables.
"""

import os
import yaml
from pathlib import Path


class Config:
    """Centralized configuration manager."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")

        with open(config_path, "r") as f:
            raw = yaml.safe_load(f)

        # Jira — environment variables override yaml values
        jira = raw.get("jira", {})
        self.jira_url = os.getenv("JIRA_URL", jira.get("url", ""))
        self.jira_username = os.getenv("JIRA_USERNAME", jira.get("username", ""))
        self.jira_token = os.getenv("JIRA_API_TOKEN", jira.get("api_token", ""))

        # Git / GitHub
        git = raw.get("git", {})
        self.git_provider = git.get("provider", "github")
        self.git_repo = git.get("repo", "")
        self.git_token = os.getenv("GITHUB_TOKEN", git.get("token", ""))
        self.git_owner = git.get("owner", "")

        # SonarQube
        sq = raw.get("sonarqube", {})
        self.sonarqube_url = sq.get("url", "")
        self.sonarqube_token = os.getenv("SONARQUBE_TOKEN", sq.get("token", ""))

        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY", raw.get("openai", {}).get("api_key", ""))
        self.openai_model = raw.get("openai", {}).get("model", "gpt-4")

        # Workspace
        self.workspace_dir = Path(raw.get("workspace_dir", "workspace"))

    @property
    def github_url(self) -> str:
        return f"https://github.com/{self.git_owner}/{self.git_repo}"
