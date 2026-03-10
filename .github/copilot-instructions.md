# AI DevOps Agent - Workspace Instructions

This workspace contains an AI-powered DevOps automation agent that handles software upgrades, Jira integration, and infrastructure provisioning.

## Available Custom Agents

### @AI DevOps Agent
Use this agent for DevOps automation tasks including:
- Software upgrades (SonarQube, Java, .NET, Python, Node.js)
- Jira ticket analysis and implementation
- Terraform infrastructure generation
- GitHub branch/PR automation
- CI/CD deployment workflows

## Quick Start

**Run the agent from terminal:**
```bash
python3 src/main.py "Upgrade SonarQube to version 10.2"
python3 src/main.py "jira: STBBS-649"
```

**Use via Copilot Chat:**
```
@AI DevOps Agent Upgrade Java from 11 to 17
@AI DevOps Agent jira: YOUR-TICKET-ID
```

## Configuration

- API credentials: `config/config.yaml`
- Agent definition: `.github/agents/ai-devops-agent.agent.md`
- Project structure: `src/main.py` (main agent logic)

## Development Guidelines

- The agent integrates with Vertex Jira and GitHub APIs
- All automation workflows are logged and tracked
- Generated code follows infrastructure-as-code best practices
- PRs are created automatically with descriptive commit messages

