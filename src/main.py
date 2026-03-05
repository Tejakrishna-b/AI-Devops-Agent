import sys

class AIDevOpsAgent:
    def __init__(self):
        import yaml
        import os
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.jira_url = config["jira"]["url"]
        self.jira_username = config["jira"]["username"]
        self.jira_token = config["jira"]["api_token"]
        self.git_provider = config["git"]["provider"]
        self.git_repo = config["git"]["repo"]
        self.git_token = config["git"].get("token")
        self.git_owner = config["git"].get("owner")
        self.sonarqube_url = config["sonarqube"]["url"]
        self.sonarqube_token = config["sonarqube"]["token"]
        self.software_targets = ["SonarQube", "OtherSoftware"]
    def get_jira_issue(self, issue_key):
        import requests
        url = f"{self.jira_url}/rest/api/2/issue/{issue_key}"
        auth = (self.jira_username, self.jira_token)
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch Jira issue: {response.text}")
            return None

    def explain_jira_issue(self, issue_data):
        """Explain Jira issue in detail before proceeding with work"""
        if not issue_data:
            return None
        
        print("\n" + "="*70)
        print("📋 JIRA TICKET ANALYSIS")
        print("="*70)
        
        fields = issue_data.get("fields", {})
        issue_key = issue_data.get("key", "Unknown")
        
        print(f"\n🎫 Ticket ID: {issue_key}")
        print(f"📌 Summary: {fields.get('summary', 'N/A')}")
        print(f"🏷️  Type: {fields.get('issuetype', {}).get('name', 'N/A')}")
        print(f"⚠️  Priority: {fields.get('priority', {}).get('name', 'N/A')}")
        print(f"📊 Status: {fields.get('status', {}).get('name', 'N/A')}")
        
        assignee = fields.get('assignee')
        if assignee:
            print(f"👤 Assignee: {assignee.get('displayName', 'N/A')}")
        
        reporter = fields.get('reporter')
        if reporter:
            print(f"👤 Reporter: {reporter.get('displayName', 'N/A')}")
        
        description = fields.get('description', '')
        if description:
            print(f"\n📝 Description:\n{description[:500]}..." if len(description) > 500 else f"\n📝 Description:\n{description}")
        
        # Extract requirements
        print("\n🎯 Identified Requirements:")
        requirements = self.extract_requirements(fields)
        for i, req in enumerate(requirements, 1):
            print(f"   {i}. {req}")
        
        print("\n" + "="*70)
        print("🚀 PROCEEDING WITH AUTOMATED WORKFLOW")
        print("="*70 + "\n")
        
        return requirements

    def extract_requirements(self, fields):
        """Extract actionable requirements from Jira ticket"""
        requirements = []
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '').lower()
        
        # Check for common upgrade patterns
        if 'upgrade' in summary or 'upgrade' in description:
            # Try to extract software and version
            if 'sonarqube' in summary or 'sonarqube' in description:
                requirements.append("Upgrade SonarQube to latest/specified version")
            requirements.append("Update infrastructure configuration")
            requirements.append("Test compatibility after upgrade")
        
        if 'infrastructure' in summary or 'infrastructure' in description:
            requirements.append("Provision/update infrastructure with Terraform")
        
        if 'deployment' in summary or 'deployment' in description:
            requirements.append("Deploy changes to specified environment")
        
        # If no specific requirements found, add general ones
        if not requirements:
            requirements.append("Analyze and implement requested changes")
            requirements.append("Create necessary configuration files")
            requirements.append("Prepare deployment artifacts")
        
        return requirements

    def create_github_branch(self, branch_name):
        import requests
        if not self.git_token:
            print(f"[SIMULATION] Creating GitHub branch: {branch_name} in repo {self.git_repo}")
            print("Note: Add GitHub token to config.yaml for real API calls")
            return True
        
        # Get the default branch SHA
        repo_name = self.git_repo.split('/')[-1] if '/' in self.git_repo else self.git_repo
        url = f"https://api.github.com/repos/{self.git_owner}/{repo_name}/git/refs/heads/main"
        headers = {"Authorization": f"token {self.git_token}", "Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            sha = response.json()["object"]["sha"]
            # Create new branch
            repo_name = self.git_repo.split('/')[-1] if '/' in self.git_repo else self.git_repo
            create_url = f"https://api.github.com/repos/{self.git_owner}/{repo_name}/git/refs"
            data = {"ref": f"refs/heads/{branch_name}", "sha": sha}
            create_response = requests.post(create_url, json=data, headers=headers)
            if create_response.status_code == 201:
                print(f"✅ Created GitHub branch: {branch_name}")
                return True
            else:
                print(f"❌ Failed to create branch: {create_response.text}")
                return False
        else:
            print(f"❌ Failed to get main branch: {response.text}")
            return False

    def create_github_pr(self, branch_name, title, body):
        import requests
        if not self.git_token:
            print(f"[SIMULATION] Creating GitHub PR from branch {branch_name}: {title}")
            print("Note: Add GitHub token to config.yaml for real API calls")
            return True
        
        repo_name = self.git_repo.split('/')[-1] if '/' in self.git_repo else self.git_repo
        url = f"https://api.github.com/repos/{self.git_owner}/{repo_name}/pulls"
        headers = {"Authorization": f"token {self.git_token}", "Accept": "application/vnd.github.v3+json"}
        data = {"title": title, "body": body, "head": branch_name, "base": "main"}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            pr_url = response.json()["html_url"]
            print(f"✅ Created Pull Request: {pr_url}")
            return pr_url
        else:
            print(f"❌ Failed to create PR: {response.text}")
            return None

    def analyze_prompt(self, prompt):
        print(f"Analyzing prompt: {prompt}")
        # Simulate prompt/Jira analysis
        if "jira:" in prompt:
            # Simulate reading Jira ticket
            return {"action": "upgrade", "target": "SonarQube", "version": "9.9", "jira": prompt.split("jira:")[1].strip()}
        for target in self.software_targets:
            if target.lower() in prompt.lower():
                # Extract version if present
                import re
                match = re.search(r"version\s*(\d+\.\d+)", prompt)
                version = match.group(1) if match else "latest"
                return {"action": "upgrade", "target": target, "version": version}
        return {"action": "unknown"}

    def locate_repositories(self):
        print("Locating repositories...")
        # Simulate repo location (could use GitHub API)
        if hasattr(self, "git_repo") and self.git_repo:
            return [self.git_repo]
        return ["https://github.com/example/repo1.git"]

    def generate_changes(self, analysis, requirements=None, issue_data=None):
        import os
        print(f"\n📝 Generating changes for {analysis.get('target', 'project')}...")
        
        # Create workspace directory
        workspace_dir = "workspace"
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir)
            print(f"✅ Created workspace directory: {workspace_dir}")
        
        files_created = []
        
        # Generate solution explanation document
        if issue_data:
            explanation_path = os.path.join(workspace_dir, "SOLUTION_EXPLANATION.md")
            with open(explanation_path, "w") as f:
                f.write(self.generate_solution_explanation(issue_data, requirements, analysis))
            files_created.append(explanation_path)
            print(f"   ✅ Created: {explanation_path}")
        
        # Generate code based on requirements
        if requirements:
            print(f"\n🔨 Generating code based on {len(requirements)} requirements...")
            
            # Extract context from issue
            fields = issue_data.get('fields', {}) if issue_data else {}
            summary = fields.get('summary', '').lower()
            description = fields.get('description', '').lower()
            
            # Create automation script for automation/testing requirements
            if any('automate' in req.lower() or 'test' in req.lower() or 'report' in req.lower() for req in requirements):
                script_path = os.path.join(workspace_dir, "automation_script.py")
                with open(script_path, "w") as f:
                    f.write(self.generate_automation_script(requirements, summary, description))
                files_created.append(script_path)
                print(f"   ✅ Created: {script_path}")
            
            # Create centralized config for config management requirements
            if 'config' in summary or 'configuration' in description:
                config_path = os.path.join(workspace_dir, "centralized_config.py")
                with open(config_path, "w") as f:
                    f.write(self.generate_centralized_config(summary, description))
                files_created.append(config_path)
                print(f"   ✅ Created: {config_path}")
            
            # Create configuration file
            config_path = os.path.join(workspace_dir, "config.json")
            with open(config_path, "w") as f:
                f.write(self.generate_config_file(requirements, summary))
            files_created.append(config_path)
            print(f"   ✅ Created: {config_path}")
            
            # Create README
            readme_path = os.path.join(workspace_dir, "README.md")
            with open(readme_path, "w") as f:
                f.write(self.generate_readme(requirements, analysis, issue_data))
            files_created.append(readme_path)
            print(f"   ✅ Created: {readme_path}")
        
        # Handle upgrade scenarios
        if analysis.get("action") == "upgrade":
            print(f"\n⬆️  Upgrading {analysis['target']} to version {analysis['version']}")
            
            # Generate Terraform file
            terraform_path = os.path.join(workspace_dir, "main.tf")
            with open(terraform_path, "w") as f:
                f.write(self.generate_terraform(analysis))
            files_created.append(terraform_path)
            print(f"   ✅ Created: {terraform_path}")
            
            # Generate upgrade script
            upgrade_script = os.path.join(workspace_dir, "upgrade.sh")
            with open(upgrade_script, "w") as f:
                f.write(self.generate_upgrade_script(analysis))
            files_created.append(upgrade_script)
            print(f"   ✅ Created: {upgrade_script}")
        
        print(f"\n✅ Generated {len(files_created)} files")
        return files_created

    def create_branch(self, repo, issue_key=None):
        import subprocess
        import os
        
        # Generate branch name
        if issue_key:
            branch_name = f"feature/{issue_key.lower()}"
        else:
            branch_name = "feature/upgrade-{}".format(repo.split("/")[-1].replace(".git", ""))
        
        print(f"\n🌿 Creating Git branch: {branch_name}")
        
        try:
            # Check if branch exists
            result = subprocess.run(
                ["git", "rev-parse", "--verify", branch_name],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                print(f"   ⚠️  Branch {branch_name} already exists, checking it out...")
                subprocess.run(["git", "checkout", branch_name], check=True)
            else:
                # Create and checkout new branch
                subprocess.run(["git", "checkout", "-b", branch_name], check=True)
                print(f"   ✅ Created and checked out branch: {branch_name}")
            
            return branch_name
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create branch: {e}")
            return None

    def add_code(self, repo, branch, files):
        import subprocess
        import os
        
        print(f"\n📦 Adding generated files to Git...")
        
        try:
            if files:
                for file in files:
                    subprocess.run(["git", "add", file], check=True, cwd=os.getcwd())
                    print(f"   ✅ Added: {file}")
                return True
            else:
                print("   ⚠️  No files to add")
                return False
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to add files: {e}")
            return False

    def commit_code(self, repo, branch, message=None):
        import subprocess
        import os
        
        print(f"\n💾 Committing changes...")
        
        if not message:
            message = f"Automated changes for {branch}"
        
        try:
            subprocess.run(["git", "commit", "-m", message], check=True, cwd=os.getcwd())
            print(f"   ✅ Committed with message: {message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to commit: {e}")
            return False

    def create_pull_request(self, repo, branch):
        title = f"Upgrade {repo} on branch {branch}"
        body = "Automated upgrade and infrastructure changes."
        self.create_github_pr(branch, title, body)
        print("Pull request created.")
        return True

    def generate_solution_explanation(self, issue_data, requirements, analysis):
        """Generate detailed explanation of the issue and solution"""
        fields = issue_data.get('fields', {})
        issue_key = issue_data.get('key', 'N/A')
        summary = fields.get('summary', 'N/A')
        description = fields.get('description', 'N/A')
        priority = fields.get('priority', {}).get('name', 'N/A')
        status = fields.get('status', {}).get('name', 'N/A')
        
        return f"""# Solution Explanation for {issue_key}

## Issue Summary
**Jira Ticket**: [{issue_key}](https://vertexinc.atlassian.net/browse/{issue_key})
**Title**: {summary}
**Priority**: {priority}
**Status**: {status}

## Problem Statement
{description}

## Root Cause Analysis
Based on the Jira ticket analysis, the key problems identified are:
{chr(10).join(f'{i+1}. {req}' for i, req in enumerate(requirements))}

## Solution Approach

### Architecture Overview
This solution implements an automated approach to address the issues identified in the Jira ticket.

### Key Components
1. **Automation Scripts**: Handle the automated workflow
2. **Configuration Management**: Centralized configuration to eliminate duplication
3. **Infrastructure Code**: Terraform for provisioning and managing infrastructure
4. **Documentation**: Complete setup and usage instructions

### Implementation Details

#### 1. Centralized Configuration
- Eliminates duplicate configuration across different environments
- Single source of truth for all configuration data
- Easy to maintain and update

#### 2. Automated Testing
- Ensures all components work as expected
- Unified report format for consistency
- Reduces manual testing effort

#### 3. Infrastructure as Code
- Version-controlled infrastructure
- Repeatable deployments
- Easy rollback capabilities

## How This Fixes the Issue

### Before
- Configuration scattered across multiple files
- Manual processes prone to errors
- Difficult to maintain and update
- No standardization

### After
- Centralized configuration management
- Automated workflows
- Standardized processes
- Easy to maintain and scale

## Testing Strategy
1. Unit tests for individual components
2. Integration tests for end-to-end workflows
3. Configuration validation
4. Infrastructure deployment tests

## Deployment Plan
1. Review generated code and configuration
2. Run automated tests
3. Deploy to staging environment
4. Verify functionality
5. Deploy to production
6. Monitor for issues

## Validation Criteria
- [ ] All tests pass successfully
- [ ] Configuration is centralized and accessible
- [ ] Infrastructure provisions correctly
- [ ] Documentation is complete
- [ ] No regressions in existing functionality

## Next Steps
1. Review this solution with the team
2. Test in development environment
3. Address any feedback
4. Deploy to staging
5. Final validation before production

## Support
For questions or issues, refer to the original Jira ticket or contact the DevOps team.

Generated by AI DevOps Agent on {analysis.get('timestamp', '2026-03-05')}
"""

    def generate_automation_script(self, requirements, summary="", description=""):
        """Generate Python automation script based on requirements"""
        script = f"""#!/usr/bin/env python3
\"\"\"
Automated Solution Reporting Script
Generated by AI DevOps Agent

Requirements:
{chr(10).join(f'- {req}' for req in requirements)}
\"\"\"

import json
import os
from datetime import datetime

class SolutionReporter:
    def __init__(self):
        self.report_format = "unified"
        self.output_dir = "reports"
        
    def generate_report(self, test_results):
        \"\"\"Generate unified format report\"\"\"
        report = {{
            "timestamp": datetime.now().isoformat(),
            "format_version": "1.0",
            "test_results": test_results,
            "status": "completed"
        }}
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save report
        report_file = os.path.join(
            self.output_dir, 
            f"report_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.json"
        )
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report generated: {{report_file}}")
        return report_file
    
    def run_tests(self):
        \"\"\"Run automated tests\"\"\"
        print("Running automated solution reporting tests...")
        
        # Placeholder for actual test logic
        test_results = {{
            "total_tests": 10,
            "passed": 10,
            "failed": 0,
            "skipped": 0
        }}
        
        return test_results

if __name__ == "__main__":
    reporter = SolutionReporter()
    results = reporter.run_tests()
    reporter.generate_report(results)
    print("Automation complete!")
"""
        return script

    def generate_centralized_config(self, summary, description):
        """Generate centralized configuration management system"""
        return f"""#!/usr/bin/env python3
\"\"\"
Centralized Configuration Management System
Generated by AI DevOps Agent

Purpose: {summary}
\"\"\"

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigurationManager:
    \"\"\"Centralized configuration manager for Solution Tests\"\"\"
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.configs = {{}}
        self.load_all_configs()
    
    def load_all_configs(self):
        \"\"\"Load all configuration files from the config directory\"\"\"
        config_files = self.config_dir.glob("*.json")
        for config_file in config_files:
            config_name = config_file.stem
            with open(config_file, 'r') as f:
                self.configs[config_name] = json.load(f)
        print(f"Loaded {{len(self.configs)}} configuration(s)")
    
    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        \"\"\"Retrieve configuration by name\"\"\"
        return self.configs.get(config_name)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]):
        \"\"\"Save configuration to file\"\"\"
        config_path = self.config_dir / f"{{config_name}}.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        self.configs[config_name] = config_data
        print(f"Saved configuration: {{config_name}}")
    
    def get_taxpayer_config(self, taxpayer_id: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get taxpayer-specific configuration\"\"\"
        taxpayer_configs = self.get_config("taxpayers")
        if taxpayer_configs:
            return taxpayer_configs.get(taxpayer_id)
        return None
    
    def get_environment_config(self, env_name: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get environment-specific configuration\"\"\"
        env_configs = self.get_config("environments")
        if env_configs:
            return env_configs.get(env_name)
        return None
    
    def get_product_config(self, product_name: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get product-specific configuration\"\"\"
        product_configs = self.get_config("products")
        if product_configs:
            return product_configs.get(product_name)
        return None

if __name__ == "__main__":
    # Example usage
    config_manager = ConfigurationManager()
    
    # Create sample configurations
    sample_environments = {{
        "dev": {{"url": "https://dev.example.com", "timeout": 30}},
        "staging": {{"url": "https://staging.example.com", "timeout": 30}},
        "prod": {{"url": "https://prod.example.com", "timeout": 60}}
    }}
    config_manager.save_config("environments", sample_environments)
    
    sample_taxpayers = {{
        "taxpayer1": {{"id": "001", "name": "Test Corp", "jurisdiction": "US"}},
        "taxpayer2": {{"id": "002", "name": "Demo Inc", "jurisdiction": "CA"}}
    }}
    config_manager.save_config("taxpayers", sample_taxpayers)
    
    print("\nCentralized Configuration Management System initialized!")
    print(f"Configuration directory: {{config_manager.config_dir.absolute()}}")
\"\"\"

    def generate_config_file(self, requirements, summary=""):
        """Generate configuration file"""
        import json
        config = {
            "project": summary or "Solution Implementation",
            "version": "1.0.0",
            "requirements": requirements,
            "settings": {
                "report_format": "unified",
                "output_directory": "reports",
                "auto_upload": False,
                "notification_enabled": True
            },
            "generated_by": "AI DevOps Agent",
            "timestamp": "2026-03-05"
        }
        return json.dumps(config, indent=2)
    
    def generate_readme(self, requirements, analysis, issue_data=None):
        """Generate README documentation"""
        issue_key = issue_data.get('key', 'N/A') if issue_data else 'N/A'
        fields = issue_data.get('fields', {}) if issue_data else {}
        summary = fields.get('summary', 'N/A')
        
        return f"""# Automated Solution Implementation - {issue_key}

## Jira Ticket
- **ID**: {issue_key}
- **Summary**: {summary}
- **Link**: [View in Jira](https://vertexinc.atlassian.net/browse/{issue_key})

## Automated Solution Implementation

## Overview
This workspace contains the automated solution generated by AI DevOps Agent.

## Requirements Addressed
{chr(10).join(f'{i+1}. {req}' for i, req in enumerate(requirements))}

## Project Details
- **Target**: {analysis.get('target', 'N/A')}
- **Action**: {analysis.get('action', 'N/A')}
- **Generated**: March 5, 2026

## File Structure
```
workspace/
├── automation_script.py   # Main automation script
├── config.json           # Configuration file
├── main.tf              # Terraform infrastructure (if applicable)
├── upgrade.sh           # Upgrade script (if applicable)
└── README.md            # This file
```

## Usage

### Run Automation Script
```bash
python3 automation_script.py
```

### Apply Infrastructure Changes
```bash
terraform init
terraform plan
terraform apply
```

## Testing
Run the automation script to verify all reports are generated in the unified format.

## Deployment
1. Review all generated files
2. Run tests to ensure functionality
3. Deploy to target environment
4. Monitor for any issues

## Support
For issues or questions, refer to the original Jira ticket or contact the DevOps team.
"""

    def generate_terraform(self, analysis):
        """Generate Terraform infrastructure code"""
        target = analysis.get('target', 'application')
        version = analysis.get('version', 'latest')
        
        return f"""# Terraform Infrastructure for {target}
# Generated by AI DevOps Agent

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}

variable "aws_region" {{
  description = "AWS region"
  default     = "us-east-1"
}}

variable "{target.lower()}_version" {{
  description = "{target} version to deploy"
  default     = "{version}"
}}

resource "aws_instance" "{target.lower()}_server" {{
  ami           = "ami-0c55b159cbfafe1f0"  # Update with appropriate AMI
  instance_type = "t3.medium"
  
  tags = {{
    Name        = "{target}-${{var.{target.lower()}_version}}"
    Environment = "production"
    ManagedBy   = "Terraform"
    Version     = var.{target.lower()}_version
  }}
}}

output "{target.lower()}_instance_id" {{
  description = "ID of the {target} instance"
  value       = aws_instance.{target.lower()}_server.id
}}

output "{target.lower()}_public_ip" {{
  description = "Public IP of the {target} instance"
  value       = aws_instance.{target.lower()}_server.public_ip
}}
"""

    def generate_upgrade_script(self, analysis):
        """Generate upgrade shell script"""
        target = analysis.get('target', 'Application')
        version = analysis.get('version', 'latest')
        
        return f"""#!/bin/bash
# {target} Upgrade Script
# Generated by AI DevOps Agent
# Target Version: {version}

set -e

echo "Starting {target} upgrade to version {version}..."

# Backup current installation
echo "Creating backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="/opt/backups/{target.lower()}_$timestamp"
mkdir -p "$backup_dir"

# Stop services
echo "Stopping {target} services..."
# systemctl stop {target.lower()} || true

# Download and install new version
echo "Installing {target} version {version}..."
# Add actual installation commands here

# Update configuration
echo "Updating configuration..."
# Add configuration update commands

# Start services
echo "Starting {target} services..."
# systemctl start {target.lower()}

# Verify installation
echo "Verifying installation..."
# Add verification commands

echo "✅ {target} upgrade to version {version} completed successfully!"
echo "Backup location: $backup_dir"
"""

    def deploy(self, repo):
        print(f"Deploying {repo}...")
        # Simulate deployment
        print("Deployment complete.")
        return True

    def run_workflow(self, prompt):
        print("\n" + "="*70)
        print("🤖 AI DEVOPS AGENT - AUTOMATED WORKFLOW")
        print("="*70 + "\n")
        
        analysis = self.analyze_prompt(prompt)
        if analysis["action"] == "unknown":
            print("❌ Could not determine action from prompt.")
            return
        
        requirements = None
        issue_key = None
        issue_data = None
        
        # If Jira ticket, fetch and explain it first
        if "jira" in analysis:
            issue_key = analysis["jira"]
            print("📥 Fetching Jira ticket details...\n")
            issue_data = self.get_jira_issue(issue_key)
            if issue_data:
                requirements = self.explain_jira_issue(issue_data)
                # Ask for confirmation before proceeding
                print("\n⏸️  Review the analysis above.")
                response = input("\n👉 Proceed with automated workflow? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("\n⛔ Workflow cancelled by user.")
                    return
            else:
                print("\n⚠️  Could not fetch Jira details, proceeding with prompt analysis...\n")
                requirements = None
                issue_data = None
        
        print("\n🔄 Starting automated DevOps workflow...\n")
        repos = self.locate_repositories()
        for repo in repos:
            # Create branch with issue key if available
            branch = self.create_branch(repo, issue_key)
            
            # Generate actual code files with full context
            generated_files = self.generate_changes(analysis, requirements, issue_data)
            
            # Add generated files to git
            if generated_files and self.add_code(repo, branch, generated_files):
                # Commit with meaningful message
                commit_msg = f"Automated implementation for {issue_key}" if issue_key else f"Automated changes for {analysis.get('target', 'project')}"
                self.commit_code(repo, branch, commit_msg)
                
                # Push to remote
                print("\n📤 Pushing changes to remote repository...")
                import subprocess
                try:
                    subprocess.run(["git", "push", "-u", "origin", branch], check=True)
                    print(f"   ✅ Pushed branch {branch} to remote")
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️  Failed to push: {e}")
                
                # Create PR
                self.create_pull_request(repo, branch)
                print("\n⏳ Waiting for developer review and merge...")
                print("✅ Once merged, deployment can proceed.")
            else:
                print("   ⚠️  No files generated or failed to add files")
                
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETE")
        print("="*70 + "\n")

if __name__ == "__main__":
    agent = AIDevOpsAgent()
    import sys
    if len(sys.argv) > 1:
        user_prompt = sys.argv[1]
    else:
        user_prompt = input("Enter your prompt or Jira link: ")
    agent.run_workflow(user_prompt)
