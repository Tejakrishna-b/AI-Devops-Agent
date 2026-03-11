#!/usr/bin/env python3
"""Validation script — verifies all modules, imports, and spec requirements."""

import sys
sys.path.insert(0, ".")

errors = []
passed = 0


def check(label, condition, detail=""):
    global passed
    if condition:
        print(f"  ✅ {label}")
        passed += 1
    else:
        msg = f"  ❌ {label}" + (f" — {detail}" if detail else "")
        print(msg)
        errors.append(msg)


print("=" * 55)
print("  AI DevOps Upgrade Agent — Validation Suite")
print("=" * 55)

# ── 1. Module Imports ────────────────────────────────
print("\n1. Module Imports")
try:
    from config import Config
    check("config.Config", True)
except Exception as e:
    check("config.Config", False, str(e))

try:
    from prompts import upgrade_code_prompt, validate_upgrade_prompt, terraform_fix_prompt
    check("prompts (3 functions)", True)
except Exception as e:
    check("prompts", False, str(e))

try:
    from git_service import GitService
    check("git_service.GitService", True)
except Exception as e:
    check("git_service.GitService", False, str(e))

try:
    from terraform_service import TerraformService
    check("terraform_service.TerraformService", True)
except Exception as e:
    check("terraform_service.TerraformService", False, str(e))

try:
    from llm_service import LLMService
    check("llm_service.LLMService", True)
except Exception as e:
    check("llm_service.LLMService", False, str(e))

try:
    from jira_service import JiraService
    check("jira_service.JiraService", True)
except Exception as e:
    check("jira_service.JiraService", False, str(e))

try:
    from validator import Validator, VersionMatch
    check("validator.Validator + VersionMatch", True)
except Exception as e:
    check("validator", False, str(e))

try:
    from agent import DevOpsUpgradeAgent
    check("agent.DevOpsUpgradeAgent", True)
except Exception as e:
    check("agent.DevOpsUpgradeAgent", False, str(e))

# ── 2. DevOpsUpgradeAgent Methods ────────────────────
print("\n2. DevOpsUpgradeAgent — Required Methods")
required = [
    "parse_request", "clone_repository", "create_backup_snapshot",
    "create_feature_branch", "scan_repository_for_tool", "upgrade_code",
    "run_terraform_validation", "run_security_scan", "create_pull_request",
    "generate_upgrade_report",
]
for m in required:
    check(f"{m}()", hasattr(DevOpsUpgradeAgent, m))

# ── 3. Config Loading ────────────────────────────────
print("\n3. Config Loading")
try:
    cfg = Config()
    check("Config loads from config.yaml", True)
    check(f"github_url = {cfg.github_url}", bool(cfg.github_url))
    check(f"workspace_dir = {cfg.workspace_dir}", cfg.workspace_dir is not None)
except Exception as e:
    check("Config loading", False, str(e))

# ── 4. parse_request ─────────────────────────────────
print("\n4. parse_request (free-text)")
try:
    agent = DevOpsUpgradeAgent(cfg)
    req = agent.parse_request(text="Upgrade SonarQube from 9.9 to 10.3")
    check("tool_name=SonarQube", req["tool_name"] == "SonarQube")
    check("current_version=9.9", req["current_version"] == "9.9")
    check("target_version=10.3", req["target_version"] == "10.3")
except Exception as e:
    check("parse_request", False, str(e))

# ── 5. Validator scanner ─────────────────────────────
print("\n5. Validator — repository scanner")
try:
    matches = Validator.scan_repository_for_tool("infra", "azurerm", "1.0.0")
    check(f"scan infra/ → {len(matches)} match(es)", True)
except Exception as e:
    check("scan_repository_for_tool", False, str(e))

# ── 6. Prompt templates ──────────────────────────────
print("\n6. Prompt Templates")
p1 = upgrade_code_prompt("SonarQube", "9.9", "10.3", "version = \"9.9\"")
check("upgrade_code_prompt generates text", len(p1) > 50)
p2 = validate_upgrade_prompt("SonarQube", "9.9", "10.3", "old", "new")
check("validate_upgrade_prompt generates text", len(p2) > 50)
p3 = terraform_fix_prompt("Error: missing arg", "resource {}")
check("terraform_fix_prompt generates text", len(p3) > 30)

# ── 7. File Structure ────────────────────────────────
print("\n7. File Structure")
import os
expected_files = [
    "app.py", "agent.py", "prompts.py", "git_service.py",
    "terraform_service.py", "llm_service.py", "jira_service.py",
    "validator.py", "config.py", "requirements.txt", "README.md",
    "config/config.yaml",
]
for f in expected_files:
    check(f, os.path.isfile(f))

# ── 8. Requirements ──────────────────────────────────
print("\n8. requirements.txt contents")
with open("requirements.txt") as f:
    reqs = f.read().lower()
for pkg in ["streamlit", "openai", "gitpython", "pygithub", "requests", "pydantic"]:
    check(f"{pkg} listed", pkg in reqs)

# ── Summary ──────────────────────────────────────────
print("\n" + "=" * 55)
if errors:
    print(f"  RESULT: {passed} passed, {len(errors)} FAILED")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"  ALL {passed} CHECKS PASSED ✅")
    print("=" * 55)
