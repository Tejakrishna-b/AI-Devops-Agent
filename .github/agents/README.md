# AI DevOps Agent

## Overview
Custom GitHub Copilot agent for automating DevOps workflows including software upgrades, infrastructure provisioning, and CI/CD management.

## How to Use

### In VS Code Copilot Chat
1. Ensure your workspace is open at the project root
2. Open Copilot Chat (Command+Shift+I or Ctrl+Shift+I)
3. Type `@workspace` followed by your request, or the agent will be auto-selected based on your prompt
4. Examples:
   - "Upgrade SonarQube to version 9.9"
   - "Analyze Jira ticket STBBS-649 and implement changes"
   - "Create infrastructure for new environment"

### Via Terminal
You can also run the agent directly:
```bash
python3 src/main.py "your prompt or Jira link"
```

## Configuration
Update `config/config.yaml` with your credentials:
- Jira URL, username, and API token
- GitHub repository information
- SonarQube URL and token

## Agent Capabilities
- ✅ Jira ticket analysis
- ✅ Software upgrade automation (SonarQube, etc.)
- ✅ Terraform infrastructure generation
- ✅ GitHub branch management
- ✅ Automated PR creation
- ✅ Deployment orchestration

## Example Workflows

### Upgrade SonarQube
```
Upgrade SonarQube to version 9.9 and create infrastructure
```

### Process Jira Ticket
```
jira: STBBS-649
```

### Provision Infrastructure
```
Create new staging environment with Terraform
```

## Files
- `ai-devops-agent.agent.md` - Agent definition and configuration
- `../../src/main.py` - Agent implementation
- `../../config/config.yaml` - Configuration file
