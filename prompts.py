"""
LLM prompt templates for the AI DevOps Upgrade Agent.
"""


def upgrade_code_prompt(tool_name: str, current_version: str, target_version: str, code_snippet: str) -> str:
    """Prompt to upgrade a tool version in infrastructure code."""
    return (
        f"Upgrade {tool_name} from version {current_version} to {target_version} "
        f"in the following infrastructure code. Only update the version references "
        f"and maintain correct syntax. Do not change unrelated configuration.\n\n"
        f"```\n{code_snippet}\n```\n\n"
        f"Return only the updated code block, nothing else."
    )


def validate_upgrade_prompt(
    tool_name: str,
    current_version: str,
    target_version: str,
    original_code: str,
    updated_code: str,
) -> str:
    """Prompt for second-pass AI validation of upgraded code."""
    return (
        f"You are a senior DevOps engineer. Validate the following code change that "
        f"upgrades {tool_name} from {current_version} to {target_version}.\n\n"
        f"ORIGINAL CODE:\n```\n{original_code}\n```\n\n"
        f"UPDATED CODE:\n```\n{updated_code}\n```\n\n"
        f"Check for:\n"
        f"1. Syntax correctness\n"
        f"2. Version compatibility\n"
        f"3. Dependency conflicts\n"
        f"4. Security issues\n\n"
        f"Respond with a JSON object: "
        f'{{"valid": true/false, "issues": ["issue1", ...], "suggestion": "..."}}'
    )


def terraform_fix_prompt(error_output: str, code_snippet: str) -> str:
    """Prompt to fix Terraform validation errors."""
    return (
        f"The following Terraform code produced validation errors.\n\n"
        f"CODE:\n```hcl\n{code_snippet}\n```\n\n"
        f"ERRORS:\n```\n{error_output}\n```\n\n"
        f"Fix the code so it passes `terraform validate`. Return only the corrected code."
    )
