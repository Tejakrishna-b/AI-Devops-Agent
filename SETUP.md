# Setup Instructions for Real API Integration

## Current Status
✅ Agent configured to use **Vertex Jira** (https://vertexinc.atlassian.net)
✅ Real GitHub API integration implemented
⚠️ Missing API tokens (agent will run in simulation mode without them)

## To Enable Real GitHub Workflows

### 1. Create a GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "AI DevOps Agent"
4. Select scopes:
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (update GitHub Actions workflows)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

### 2. Update config.yaml
Edit `config/config.yaml` and add your credentials:

```yaml
jira:
  url: "https://vertexinc.atlassian.net"
  username: "your-vertex-email@vertexinc.com"
  api_token: "YOUR_JIRA_API_TOKEN"

git:
  provider: "github"
  repo: "Tejakrishna-b/AI-Devops-Agent"
  token: "YOUR_GITHUB_TOKEN_HERE"  # ← Add your GitHub token here
  owner: "Tejakrishna-b"
```

### 3. Get Jira API Token (Vertex)
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name and copy the token
4. Add it to `config.yaml` under `jira.api_token`

## Test Real Integration

After adding tokens, run:
```bash
python3 src/main.py "Upgrade SonarQube from 9 to 10"
```

The agent will now:
- ✅ Create **real** GitHub branches
- ✅ Make **real** commits
- ✅ Create **real** pull requests
- ✅ Read **real** Jira tickets from Vertex

## Security Notes
- ⚠️ Never commit `config.yaml` with real tokens to Git
- Add `config/config.yaml` to `.gitignore` if not already there
- Use environment variables for production deployments
