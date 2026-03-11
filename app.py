#!/usr/bin/env python3
"""
AI DevOps Upgrade Agent — Streamlit Web UI
Author: AI DevOps Team
"""

import streamlit as st
import os
import json
import traceback
from datetime import datetime
from pathlib import Path

from config import Config
from agent import DevOpsUpgradeAgent
from jira_service import JiraService

# Page configuration
st.set_page_config(
    page_title="AI DevOps Upgrade Agent",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Minimal CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stButton button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; border: none; font-weight: 600; border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)


# ── Status panel helper ──────────────────────────────────────────────────
STEPS = [
    "Backup Created",
    "Repository Cloned",
    "Feature Branch Created",
    "Code Updated",
    "Terraform Validation Running",
    "Pull Request Created",
    "Waiting For Human Approval",
]


def render_status_panel(status: dict):
    """Render a live status panel for the upgrade workflow."""
    for step in STEPS:
        state = status.get(step, "pending")
        if state == "completed":
            icon = "✅"
        elif state == "in_progress":
            icon = "🔄"
        elif state == "failed":
            icon = "❌"
        else:
            icon = "⏳"
        st.markdown(f"{icon} &nbsp; **{step}**", unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    cfg = Config()

    # Header
    st.title("⚙️ AI DevOps Upgrade Agent")
    st.caption("Automate DevOps tool upgrades in CI/CD pipelines")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        st.info(f"**GitHub:** {cfg.github_url}")
        st.info(f"**Jira:** {cfg.jira_url}")
        st.markdown("---")
        mode = st.radio("Mode", ["Upgrade Agent", "Jira Ticket"])

    # ── Upgrade Agent Mode ───────────────────────────────────────────────
    if mode == "Upgrade Agent":
        col1, col2 = st.columns(2)
        with col1:
            tool_name = st.selectbox(
                "Tool to Upgrade",
                ["SonarQube", "Snyk", "Datadog", "Terraform", "Docker"],
            )
            current_version = st.text_input("Current Version", placeholder="e.g. 9.9")
            target_version = st.text_input("Target Version", placeholder="e.g. 10.3")

        with col2:
            repo_url = st.text_input(
                "Repository URL",
                value=cfg.github_url,
                placeholder="https://github.com/owner/repo",
            )
            environment = st.selectbox("Environment", ["Dev", "Stage", "Prod"])

        st.markdown("---")

        # Status panel placeholder
        status_container = st.container()

        run_btn = st.button("🚀 Run Upgrade Agent", type="primary", use_container_width=True)

        if run_btn:
            if not current_version or not target_version:
                st.warning("Please enter both current and target versions.")
            else:
                agent = DevOpsUpgradeAgent(cfg)

                # Live status callback
                def on_status(step, state):
                    agent.status[step] = state

                with st.spinner("Running upgrade workflow…"):
                    try:
                        report = agent.run(
                            tool_name=tool_name,
                            current_version=current_version,
                            target_version=target_version,
                            repository=repo_url,
                            environment=environment.lower(),
                            status_callback=on_status,
                        )

                        with status_container:
                            st.subheader("Status Panel")
                            render_status_panel(agent.status)

                        st.markdown("---")
                        st.subheader("Upgrade Report")
                        st.json(report)

                        if report.get("pr_link"):
                            st.success(f"Pull Request created: {report['pr_link']}")

                    except Exception as exc:
                        st.error(f"Workflow failed: {exc}")
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())

    # ── Jira Ticket Mode ─────────────────────────────────────────────────
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            jira_input = st.text_input(
                "Jira Ticket Number",
                placeholder="e.g. STBBS-649",
            )
        with col2:
            st.write("")  # spacer
            st.write("")
            analyze_btn = st.button("🔍 Analyze Ticket", type="primary", use_container_width=True)

        if analyze_btn and jira_input:
            jira_svc = JiraService(cfg.jira_url, cfg.jira_username, cfg.jira_token)
            with st.spinner(f"Fetching {jira_input}…"):
                issue = jira_svc.get_issue(jira_input.strip())

            if issue:
                parsed = JiraService.parse_issue(issue)
                st.success(f"Fetched **{parsed['key']}**")

                c1, c2, c3 = st.columns(3)
                c1.metric("Ticket", parsed["key"])
                c2.metric("Priority", parsed["priority"])
                c3.metric("Status", parsed["status"])

                st.markdown(f"**Summary:** {parsed['summary']}")
                if parsed["description"]:
                    with st.expander("Full Description"):
                        st.write(parsed["description"])

                st.markdown("---")
                st.info(
                    f"Run the agent from terminal:\n\n"
                    f"```bash\npython3 src/main.py \"jira: {parsed['key']}\"\n```"
                )
            else:
                st.error("Could not fetch that Jira ticket.")

        elif analyze_btn:
            st.warning("Please enter a Jira ticket number.")


if __name__ == "__main__":
    main()
