"""
Jira service — fetch and parse Jira issues.
"""

import requests
from typing import Optional


class JiraService:
    """Interact with Jira REST API."""

    def __init__(self, url: str, username: str, token: str):
        self.url = url.rstrip("/")
        self.auth = (username, token)

    def get_issue(self, issue_key: str) -> Optional[dict]:
        """Fetch a Jira issue by key."""
        resp = requests.get(
            f"{self.url}/rest/api/2/issue/{issue_key}",
            auth=self.auth,
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()
        return None

    @staticmethod
    def parse_issue(issue_data: dict) -> dict:
        """Extract useful fields from a Jira issue."""
        fields = issue_data.get("fields", {})
        return {
            "key": issue_data.get("key", ""),
            "summary": fields.get("summary", ""),
            "description": fields.get("description", ""),
            "type": fields.get("issuetype", {}).get("name", ""),
            "priority": fields.get("priority", {}).get("name", ""),
            "status": fields.get("status", {}).get("name", ""),
        }
