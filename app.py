#!/usr/bin/env python3
"""
AI DevOps Agent - Interactive Web UI
Author: AI DevOps Team
"""

import streamlit as st
import sys
import os
import json
import requests
import yaml
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Page configuration
st.set_page_config(
    page_title="AI DevOps Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #17a2b8;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

class AIDevOpsAgentUI:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from config.yaml"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            self.jira_url = config["jira"]["url"]
            self.jira_username = config["jira"]["username"]
            self.jira_token = config["jira"]["api_token"]
            self.git_owner = config["git"]["owner"]
            self.git_repo = config["git"]["repo"]
            self.github_url = f"https://github.com/{self.git_owner}/{self.git_repo}"
        except Exception as e:
            st.error(f"❌ Failed to load configuration: {str(e)}")
            self.jira_url = None
    
    def fetch_jira_ticket(self, issue_key):
        """Fetch Jira ticket details"""
        try:
            url = f"{self.jira_url}/rest/api/2/issue/{issue_key}"
            auth = (self.jira_username, self.jira_token)
            response = requests.get(url, auth=auth)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"❌ Failed to fetch Jira ticket: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None
    
    def extract_requirements(self, fields):
        """Extract requirements from Jira ticket"""
        requirements = []
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '').lower()
        full_text = f"{summary} {description}"
        
        # Pattern matching for specific requirements
        if any(word in full_text for word in ['upgrade', 'update', 'migrate']):
            if 'java' in full_text:
                requirements.append("🔧 Upgrade Java version")
            if 'sonarqube' in full_text or 'sonar' in full_text:
                requirements.append("🔧 Upgrade SonarQube")
            if 'python' in full_text:
                requirements.append("🔧 Upgrade Python version")
            if 'node' in full_text:
                requirements.append("🔧 Upgrade Node.js version")
        
        if 'automate' in full_text:
            requirements.append("⚙️ Automate manual processes")
        if 'terraform' in full_text or 'infrastructure' in full_text:
            requirements.append("🏗️ Provision infrastructure with Terraform")
        if 'ci/cd' in full_text or 'pipeline' in full_text:
            requirements.append("🔄 Update CI/CD pipelines")
        if 'docker' in full_text or 'container' in full_text:
            requirements.append("🐳 Update Docker configurations")
        
        if not requirements:
            requirements.append(f"📝 {fields.get('summary', 'Implement requested changes')}")
        
        return requirements
    
    def generate_solution_steps(self, issue_data):
        """Generate step-by-step solution based on ticket analysis"""
        fields = issue_data.get('fields', {})
        requirements = self.extract_requirements(fields)
        
        steps = []
        
        # Step 1: Analysis
        steps.append({
            "title": "📋 Ticket Analysis",
            "description": "Analyzing Jira ticket requirements",
            "details": [
                f"Summary: {fields.get('summary', 'N/A')}",
                f"Type: {fields.get('issuetype', {}).get('name', 'N/A')}",
                f"Priority: {fields.get('priority', {}).get('name', 'N/A')}",
                f"Status: {fields.get('status', {}).get('name', 'N/A')}"
            ],
            "status": "completed"
        })
        
        # Step 2: Requirements
        steps.append({
            "title": "🎯 Identified Requirements",
            "description": "Requirements extracted from ticket",
            "details": requirements,
            "status": "completed"
        })
        
        # Step 3: Solution Planning
        solution_plan = []
        for req in requirements:
            if 'java' in req.lower():
                solution_plan.append("Create Java upgrade scripts and configuration files")
                solution_plan.append("Update Maven/Gradle build files")
                solution_plan.append("Update Dockerfile for new Java version")
            elif 'sonarqube' in req.lower():
                solution_plan.append("Generate SonarQube upgrade documentation")
                solution_plan.append("Create Terraform infrastructure code")
                solution_plan.append("Update CI/CD pipeline configurations")
            elif 'terraform' in req.lower() or 'infrastructure' in req.lower():
                solution_plan.append("Generate Terraform modules")
                solution_plan.append("Create infrastructure documentation")
            else:
                solution_plan.append("Generate implementation files")
                solution_plan.append("Create documentation and guides")
        
        steps.append({
            "title": "💡 Solution Plan",
            "description": "Automated solution approach",
            "details": solution_plan,
            "status": "in_progress"
        })
        
        # Step 4: Implementation
        steps.append({
            "title": "⚙️ Implementation",
            "description": "Generate code, configs, and infrastructure",
            "details": [
                "Create feature branch in GitHub",
                "Generate necessary files and scripts",
                "Update configuration files",
                "Create migration guides and documentation"
            ],
            "status": "pending"
        })
        
        # Step 5: GitHub Integration
        steps.append({
            "title": "🔗 GitHub Integration",
            "description": "Commit changes and create pull request",
            "details": [
                "Add all generated files to Git",
                "Commit with descriptive message",
                "Push branch to remote repository",
                "Create pull request for review"
            ],
            "status": "pending"
        })
        
        # Step 6: Review & Deploy
        steps.append({
            "title": "🚀 Review & Deploy",
            "description": "Final steps for deployment",
            "details": [
                "Review generated code and configurations",
                "Test in development environment",
                "Merge pull request after approval",
                "Deploy to production"
            ],
            "status": "pending"
        })
        
        return steps

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI DevOps Agent</h1>', unsafe_allow_html=True)
    st.markdown("### Automated DevOps Workflow Solution Engine")
    st.markdown("---")
    
    # Initialize agent
    agent = AIDevOpsAgentUI()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"**GitHub Repo:**\n{agent.github_url}")
        st.info(f"**Jira Instance:**\n{agent.jira_url}")
        
        st.markdown("---")
        st.header("📚 Quick Links")
        st.markdown(f"[GitHub Repository]({agent.github_url})")
        st.markdown(f"[Workspace Files]({agent.github_url}/tree/main/workspace)")
        st.markdown(f"[Pull Requests]({agent.github_url}/pulls)")
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.write("""
        This agent automates:
        - Software upgrades
        - Infrastructure provisioning
        - CI/CD pipeline updates
        - GitHub PR creation
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎫 Enter Jira Ticket")
        jira_input = st.text_input(
            "Jira Ticket Number",
            placeholder="e.g., STBBS-649, DEV-123",
            help="Enter the Jira ticket ID to analyze"
        )
    
    with col2:
        st.subheader("🚀 Action")
        analyze_button = st.button("Analyze Ticket", type="primary", use_container_width=True)
    
    # Process when button clicked
    if analyze_button and jira_input:
        with st.spinner(f"🔍 Fetching Jira ticket {jira_input}..."):
            issue_data = agent.fetch_jira_ticket(jira_input.strip())
        
        if issue_data:
            fields = issue_data.get('fields', {})
            issue_key = issue_data.get('key', jira_input)
            
            # Display ticket info
            st.success(f"✅ Successfully fetched ticket: **{issue_key}**")
            st.markdown("---")
            
            # Ticket Details
            st.header("📋 Ticket Details")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ticket ID", issue_key)
            with col2:
                st.metric("Priority", fields.get('priority', {}).get('name', 'N/A'))
            with col3:
                st.metric("Status", fields.get('status', {}).get('name', 'N/A'))
            
            st.markdown(f"**Summary:** {fields.get('summary', 'N/A')}")
            st.markdown(f"**Type:** {fields.get('issuetype', {}).get('name', 'N/A')}")
            
            if fields.get('description'):
                with st.expander("📝 View Full Description"):
                    st.write(fields.get('description'))
            
            st.markdown("---")
            
            # Generate and display solution steps
            st.header("🔧 Solution Steps")
            steps = agent.generate_solution_steps(issue_data)
            
            for idx, step in enumerate(steps, 1):
                status_emoji = {
                    "completed": "✅",
                    "in_progress": "🔄",
                    "pending": "⏳"
                }.get(step['status'], "⏳")
                
                with st.expander(f"{status_emoji} **Step {idx}: {step['title']}**", expanded=(idx <= 2)):
                    st.write(f"**{step['description']}**")
                    st.markdown("**Details:**")
                    for detail in step['details']:
                        st.markdown(f"- {detail}")
            
            st.markdown("---")
            
            # Action buttons
            st.header("🚀 Execute Automation")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("▶️ Run Agent", type="primary", use_container_width=True):
                    st.info("🔄 Running automation agent...")
                    st.code(f'python3 src/main.py "jira: {issue_key}"', language="bash")
                    st.warning("💡 To execute, run this command in your terminal")
            
            with col2:
                branch_name = f"feature/{issue_key.lower()}"
                github_link = f"{agent.github_url}/tree/{branch_name}"
                st.link_button("🌿 View Branch", github_link, use_container_width=True)
            
            with col3:
                pr_link = f"{agent.github_url}/pulls"
                st.link_button("📝 View PRs", pr_link, use_container_width=True)
            
            # GitHub workspace link
            st.markdown("---")
            st.info(f"""
            📁 **Workspace Files:** All generated files will be available at:
            
            `{agent.github_url}/tree/main/workspace`
            
            🔗 **Generated Branch:** `{branch_name}`
            """)
    
    elif analyze_button and not jira_input:
        st.warning("⚠️ Please enter a Jira ticket number")
    
    # Quick examples
    if not analyze_button:
        st.markdown("---")
        st.header("💡 Example Tickets")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **Java Upgrade**
            - STBBS-649
            - Upgrades Java version
            - Creates migration guides
            """)
        
        with col2:
            st.info("""
            **Infrastructure**
            - Creates Terraform code
            - Provisions resources
            - Updates CI/CD
            """)
        
        with col3:
            st.info("""
            **SonarQube**
            - Upgrades SonarQube
            - Updates configs
            - Generates docs
            """)

if __name__ == "__main__":
    main()
