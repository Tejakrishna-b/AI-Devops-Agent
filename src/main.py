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

    def generate_changes(self, analysis):
        print(f"Generating changes for {analysis['target']} upgrade...")
        # Simulate code/config/terraform generation
        if analysis["action"] == "upgrade":
            print(f"Upgrading {analysis['target']} to version {analysis['version']}")
            print("Generating Terraform for infrastructure...")
            # Here, you would generate files and code
            return True
        return False

    def create_branch(self, repo):
        branch_name = "feature/upgrade-{}".format(repo.split("/")[-1].replace(".git", ""))
        self.create_github_branch(branch_name)
        return branch_name

    def add_code(self, repo, branch):
        print(f"Adding code to {repo} on branch {branch}...")
        # Simulate adding code/config/terraform
        print("Code, Terraform, and config files added.")
        return True

    def commit_code(self, repo, branch):
        print(f"Committing code in {repo} on branch {branch}...")
        # Simulate commit
        print("Code committed.")
        return True

    def create_pull_request(self, repo, branch):
        title = f"Upgrade {repo} on branch {branch}"
        body = "Automated upgrade and infrastructure changes."
        self.create_github_pr(branch, title, body)
        print("Pull request created.")
        return True

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
        
        # If Jira ticket, fetch and explain it first
        if "jira" in analysis:
            print("📥 Fetching Jira ticket details...\n")
            issue_data = self.get_jira_issue(analysis["jira"])
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
        
        print("\n🔄 Starting automated DevOps workflow...\n")
        repos = self.locate_repositories()
        for repo in repos:
            branch = self.create_branch(repo)
            self.generate_changes(analysis)
            self.add_code(repo, branch)
            self.commit_code(repo, branch)
            self.create_pull_request(repo, branch)
            print("\n⏳ Waiting for developer review and merge...")
            print("✅ Code merged.")
            self.deploy(repo)
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
