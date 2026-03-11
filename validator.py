"""
Validator — scan repository for tool version references and validate changes.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VersionMatch:
    file: str
    line_number: int
    line_content: str
    matched_version: str


class Validator:
    """Scan repository code, detect versions, and validate upgrades."""

    # File extensions to scan
    SCAN_EXTENSIONS = {".tf", ".yml", ".yaml", ".json", ".Dockerfile", ".hcl"}
    SCAN_FILENAMES = {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"}

    @staticmethod
    def scan_repository_for_tool(repo_path: str, tool_name: str, version: str) -> list[VersionMatch]:
        """Walk the repository and find files referencing tool_name with version."""
        matches: list[VersionMatch] = []
        # Patterns like: version = "9.9", image = "sonarqube:9.9", chartVersion: 9.9
        patterns = [
            re.compile(rf'version\s*[:=]\s*["\']?{re.escape(version)}["\']?', re.IGNORECASE),
            re.compile(rf'{re.escape(tool_name.lower())}[:/]{re.escape(version)}', re.IGNORECASE),
            re.compile(rf'chartVersion\s*:\s*["\']?{re.escape(version)}["\']?', re.IGNORECASE),
        ]

        for root, _dirs, files in os.walk(repo_path):
            # skip hidden dirs and common non-code dirs
            if any(part.startswith(".") for part in Path(root).parts):
                continue
            for fname in files:
                fpath = Path(root) / fname
                ext = fpath.suffix
                if ext not in Validator.SCAN_EXTENSIONS and fname not in Validator.SCAN_FILENAMES:
                    continue
                try:
                    lines = fpath.read_text(errors="ignore").splitlines()
                except Exception:
                    continue
                for idx, line in enumerate(lines, start=1):
                    for pattern in patterns:
                        if pattern.search(line):
                            matches.append(VersionMatch(
                                file=str(fpath),
                                line_number=idx,
                                line_content=line.strip(),
                                matched_version=version,
                            ))
                            break  # one match per line is enough

        return matches

    @staticmethod
    def replace_version_in_file(file_path: str, old_version: str, new_version: str) -> str:
        """Replace all occurrences of old_version with new_version in a file. Returns updated content."""
        content = Path(file_path).read_text()
        updated = content.replace(old_version, new_version)
        Path(file_path).write_text(updated)
        return updated

    @staticmethod
    def run_security_scan(repo_path: str) -> dict:
        """Run basic security checks on the repository (placeholder for tfsec/checkov)."""
        issues: list[str] = []
        for root, _dirs, files in os.walk(repo_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    content = open(fpath, errors="ignore").read()
                except Exception:
                    continue
                if re.search(r'(password|secret|api_key)\s*=\s*"[^"]+"', content, re.IGNORECASE):
                    issues.append(f"Potential hardcoded secret in {fpath}")
        return {"issues": issues, "passed": len(issues) == 0}
