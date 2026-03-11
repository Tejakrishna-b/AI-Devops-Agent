"""
Terraform service — fmt, validate, plan.
"""

import subprocess
from dataclasses import dataclass


@dataclass
class TerraformResult:
    success: bool
    stdout: str
    stderr: str


class TerraformService:
    """Run Terraform CLI operations on a working directory."""

    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir

    def _run(self, args: list[str]) -> TerraformResult:
        result = subprocess.run(
            ["terraform"] + args,
            cwd=self.working_dir,
            capture_output=True,
            text=True,
        )
        return TerraformResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    def fmt(self) -> TerraformResult:
        return self._run(["fmt", "-recursive"])

    def init(self) -> TerraformResult:
        return self._run(["init", "-input=false"])

    def validate(self) -> TerraformResult:
        return self._run(["validate"])

    def plan(self, out_file: str = "tfplan") -> TerraformResult:
        return self._run(["plan", f"-out={out_file}"])

    def run_full_validation(self) -> dict:
        """Run fmt → init → validate → plan and return aggregate results."""
        results = {}
        for step_name, method in [("fmt", self.fmt), ("init", self.init),
                                   ("validate", self.validate), ("plan", self.plan)]:
            res = method()
            results[step_name] = {"success": res.success, "stdout": res.stdout, "stderr": res.stderr}
            if not res.success and step_name in ("init", "validate"):
                break  # stop early on blocking failures
        return results
