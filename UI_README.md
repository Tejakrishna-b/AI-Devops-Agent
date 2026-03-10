# 🤖 AI DevOps Agent - Interactive Web UI

A beautiful, interactive web interface for the AI DevOps Agent that analyzes Jira tickets and generates step-by-step automation solutions.

## ✨ Features

- 🎫 **Jira Integration** - Fetch and analyze Jira tickets automatically
- 📊 **Step-by-Step Solutions** - Clear, visual breakdown of automation workflow
- 🔗 **GitHub Integration** - Direct links to branches, PRs, and workspace files
- 🎨 **Interactive UI** - Beautiful, user-friendly interface built with Streamlit
- 🚀 **Real-time Analysis** - Instant requirement extraction and solution planning

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the Web UI

```bash
streamlit run app.py
```

The UI will automatically open in your browser at `http://localhost:8501`

### 3. Use the Interface

1. **Enter Jira Ticket Number** (e.g., `STBBS-649`)
2. **Click "Analyze Ticket"**
3. **View Step-by-Step Solution**
4. **Access GitHub Links** for branches and PRs

## 📋 How It Works

### Workflow

```
Enter Jira Ticket → Fetch Ticket Data → Analyze Requirements
                            ↓
                  Generate Solution Steps
                            ↓
        Display: Analysis, Plan, Implementation Steps
                            ↓
              GitHub Links + Workspace Access
```

### What You'll See

1. **📋 Ticket Details**
   - Ticket ID, Priority, Status
   - Summary and Description
   - Type and assignee info

2. **🎯 Identified Requirements**
   - Extracted requirements from ticket
   - Categorized by type (upgrade, infrastructure, etc.)

3. **🔧 Solution Steps** (6 automated steps)
   - Step 1: Ticket Analysis ✅
   - Step 2: Requirements Identification ✅
   - Step 3: Solution Planning 🔄
   - Step 4: Implementation ⏳
   - Step 5: GitHub Integration ⏳
   - Step 6: Review & Deploy ⏳

4. **🚀 Quick Actions**
   - Run automation command
   - View generated branch
   - Access pull requests
   - Navigate to workspace files

## 🎨 UI Features

### Main Dashboard
- Clean, professional interface
- Real-time ticket fetching
- Visual status indicators

### Sidebar
- GitHub repository links
- Jira instance info
- Quick access to:
  - Repository
  - Workspace files
  - Pull requests

### Step-by-Step Display
- Expandable sections for each step
- Clear status indicators (✅ 🔄 ⏳)
- Detailed breakdown of actions

## 🔗 GitHub Integration

The UI provides direct links to:

- **Repository:** https://github.com/YOUR-ORG/YOUR-REPO
- **Workspace Files:** `/workspace` directory with generated files
- **Feature Branches:** Auto-generated branch names
- **Pull Requests:** View and manage PRs

## 💡 Example Usage

### Java Upgrade Example

1. Enter ticket: `STBBS-649`
2. Agent analyzes and identifies: "Upgrade Java 18 to 21"
3. Displays solution steps:
   - Create Java upgrade scripts
   - Update Maven/Gradle configs
   - Update Dockerfile
   - Generate migration guide
4. Provides GitHub links to access generated files

### Infrastructure Provisioning

1. Enter ticket with infrastructure requirements
2. Agent identifies: "Provision AWS infrastructure"
3. Displays solution:
   - Generate Terraform modules
   - Create infrastructure documentation
   - Update CI/CD pipelines
4. Links to workspace with Terraform files

## 🛠️ Configuration

The UI reads configuration from `config/config.yaml`:

```yaml
jira:
  url: "https://yourcompany.atlassian.net"
  username: "your-email@company.com"
  api_token: "YOUR_JIRA_API_TOKEN"

git:
  provider: "github"
  repo: "YOUR-REPO"
  owner: "YOUR-ORG"
  token: "YOUR_GITHUB_TOKEN"
```

## 📸 Screenshots

### Main Dashboard
- Clean input for Jira ticket numbers
- Single-click analysis button
- Real-time status updates

### Ticket Analysis View
- Detailed ticket information cards
- Metrics: Priority, Status, Type
- Full description with expand/collapse

### Solution Steps
- 6 comprehensive automation steps
- Visual status indicators
- Expandable detail sections

### GitHub Links
- Direct navigation to branches
- Quick access to PRs
- Workspace file browser

## 🎯 Supported Tasks

The UI can analyze and plan automation for:

- ☕ **Java Upgrades** - Version migrations with configs
- 🐍 **Python Upgrades** - Virtual env and dependency updates
- 🟢 **Node.js Upgrades** - Package.json and runtime updates
- 🔍 **SonarQube Upgrades** - Analysis platform updates
- 🏗️ **Infrastructure** - Terraform provisioning
- 🔄 **CI/CD Updates** - Pipeline configurations
- 🐳 **Docker Updates** - Container and image updates

## 🔧 Troubleshooting

### UI won't start
```bash
# Reinstall streamlit
pip install --upgrade streamlit
streamlit run app.py
```

### Can't fetch Jira tickets
- Verify `config/config.yaml` has correct credentials
- Check Jira API token is valid
- Ensure network connectivity to Jira instance

### GitHub links not working
- Confirm GitHub repo name in config
- Verify repository exists and is accessible

## 🚀 Advanced Features

### Custom Styling
The UI includes custom CSS for:
- Professional color scheme
- Card-based layouts
- Status indicators
- Responsive design

### Real-time Updates
- Instant ticket fetching
- Progressive step display
- Dynamic GitHub link generation

## 📚 Learn More

- [Streamlit Documentation](https://docs.streamlit.io)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [GitHub API](https://docs.github.com/en/rest)

## 🤝 Contributing

To customize the UI:

1. Edit `app.py` for new features
2. Modify CSS in the `st.markdown()` section
3. Add new step types in `generate_solution_steps()`
4. Extend requirement extraction in `extract_requirements()`

---

**Made with ❤️ by AI DevOps Team**
