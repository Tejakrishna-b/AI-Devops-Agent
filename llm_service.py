"""
LLM service — OpenAI integration for code generation and validation.
"""

import json
from typing import Optional

import openai

from prompts import upgrade_code_prompt, validate_upgrade_prompt, terraform_fix_prompt


class LLMService:
    """Interact with OpenAI API for upgrade code generation & validation."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def _chat(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------ code upgrade
    def generate_upgraded_code(
        self, tool_name: str, current_version: str, target_version: str, code: str
    ) -> str:
        prompt = upgrade_code_prompt(tool_name, current_version, target_version, code)
        return self._chat(prompt)

    # ------------------------------------------------ validation
    def validate_upgrade(
        self,
        tool_name: str,
        current_version: str,
        target_version: str,
        original: str,
        updated: str,
    ) -> dict:
        prompt = validate_upgrade_prompt(tool_name, current_version, target_version, original, updated)
        raw = self._chat(prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"valid": False, "issues": ["LLM returned non-JSON response"], "raw": raw}

    # ------------------------------------------------ terraform fix
    def fix_terraform_errors(self, error_output: str, code: str) -> str:
        prompt = terraform_fix_prompt(error_output, code)
        return self._chat(prompt)
