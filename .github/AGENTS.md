# Custom Agents for AI-DevOps-Agent

This workspace provides specialized AI agents for DevOps automation tasks.

## Available Agents

### @AI DevOps Agent

**Purpose:** Automates end-to-end DevOps workflows including software upgrades, infrastructure provisioning, and deployment automation.

**Use Cases:**
- Upgrade software (SonarQube, Java, .NET, Node.js, Python)
- Read and implement Jira tickets automatically
- Generate Terraform infrastructure code
- Create GitHub branches and pull requests
- Automate CI/CD deployments

**Example Prompts:**
```
@AI DevOps Agent Upgrade SonarQube to version 10.2
@AI DevOps Agent jira: STBBS-649
@AI DevOps Agent Provision development environment with Terraform
@AI DevOps Agent Upgrade Java from 11 to 17
```

**Configuration:** The agent uses credentials from `config/config.yaml` for Jira and GitHub API integration.

---

## How to Use

1. Open Copilot Chat in VS Code
2. Type `@` to see available agents
3. Select `@AI DevOps Agent` from the list
4. Provide your request (upgrade task, Jira ticket URL, or infrastructure requirement)

The agent will analyze requirements, generate code, create branches, and submit pull requests automatically.
