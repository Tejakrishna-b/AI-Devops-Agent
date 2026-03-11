# AI DevOps Upgrade Agent

An AI-powered DevOps automation agent that upgrades tools in CI/CD pipelines by analyzing repository code, updating versions, validating changes, and creating pull requests.

## Features

- **Automated Upgrades** — SonarQube, Snyk, Datadog, Terraform, Docker
- **Repository Scanning** — Detects version references in `.tf`, YAML, Dockerfiles, Helm charts
- **AI Code Generation** — OpenAI-powered code updates with validation pass
- **Terraform Validation** — Runs `terraform fmt`, `validate`, and `plan`
- **GitHub Integration** — Clones repos, creates branches & PRs via PyGithub
- **Backup Snapshots** — Tags current HEAD before any modifications
- **Jira Integration** — Reads tickets and generates implementation plans
- **Streamlit UI** — Web dashboard with tool selection, version inputs, and live status panel

## Project Structure

```
ai-devops-agent/
├── app.py                  # Streamlit web UI
├── agent.py                # DevOpsUpgradeAgent — core orchestrator
├── prompts.py              # LLM prompt templates
├── git_service.py          # Git operations (GitPython)
├── terraform_service.py    # Terraform CLI wrapper
├── llm_service.py          # OpenAI integration
├── jira_service.py         # Jira REST API client
├── validator.py            # Repository scanner & security checks
├── config.py               # Configuration loader
├── config/config.yaml      # Settings (credentials via env vars)
├── requirements.txt        # Python dependencies
├── src/main.py             # CLI entry point
├── infra/main.tf           # Sample Terraform
├── tests/test_workflow.py  # Tests
└── workspace/              # Generated upgrade workspaces
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export GITHUB_TOKEN="your-github-token"
export JIRA_API_TOKEN="your-jira-token"
export JIRA_URL="https://your-instance.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export OPENAI_API_KEY="your-openai-key"         # optional
export SONARQUBE_TOKEN="your-sonarqube-token"    # optional
```

### 3. Run the Web UI

```bash
streamlit run app.py
```

### 4. Or Use the CLI

```bash
python3 src/main.py "Upgrade SonarQube from 9.9 to 10.3"
python3 src/main.py "jira: STBBS-649"
```

## Upgrade Workflow

1. **Parse Request** — Extract tool name, versions, repository
2. **Clone Repository** — Pull the target repo locally
3. **Backup Snapshot** — Tag current HEAD (`backup-sonarqube-9.9`)
4. **Feature Branch** — Create `feature/upgrade-sonarqube-10.3`
5. **Scan Code** — Find version references in `.tf`, YAML, Dockerfiles
6. **Upgrade Code** — Replace versions (AI-assisted if OpenAI key set)
7. **Terraform Validation** — `fmt` → `validate` → `plan`
8. **Security Scan** — Check for hardcoded secrets
9. **AI Validation** — Second LLM pass to verify correctness
10. **Create PR** — Push branch and open pull request on GitHub
11. **Human Approval** — Engineer reviews and merges

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| UI | Streamlit |
| AI | OpenAI API |
| Git | GitPython |
| GitHub | PyGithub |
| IaC Validation | Terraform CLI |
| HTTP | Requests |
| Config | PyYAML, Pydantic |

## Configuration

Edit `config/config.yaml` for non-sensitive settings. All credentials should be provided via environment variables (see above).

