"""
Guardrails Configuration - Preflight Checks.

Controls system behavior BEFORE boot/execution.
Different from runtime guards (tool_safety_guard) or test guards (test_guardian).

Guard Hierarchy:
  guardrails/        PREFLIGHT (before boot) <- THIS
  tool_safety_guard  RUNTIME (during tool execution)
  test_guardian      TEST PHASE (during test runs)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class GuardrailMode(str, Enum):
    """How a guardrail behaves when triggered."""

    BLOCK = "block"  # Stop execution, require fix
    WARN = "warn"  # Show warning, continue anyway
    IGNORE = "ignore"  # Skip check entirely


@dataclass
class GitGuardrails:
    """Git-related preflight checks."""

    uncommitted_changes: GuardrailMode = GuardrailMode.WARN
    behind_remote: GuardrailMode = GuardrailMode.IGNORE
    untracked_files: GuardrailMode = GuardrailMode.IGNORE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uncommitted_changes": self.uncommitted_changes.value,
            "behind_remote": self.behind_remote.value,
            "untracked_files": self.untracked_files.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GitGuardrails":
        return cls(
            uncommitted_changes=GuardrailMode(data.get("uncommitted_changes", "warn")),
            behind_remote=GuardrailMode(data.get("behind_remote", "ignore")),
            untracked_files=GuardrailMode(data.get("untracked_files", "ignore")),
        )


@dataclass
class TestGuardrails:
    """Test-related preflight checks."""

    must_pass: GuardrailMode = GuardrailMode.IGNORE
    coverage_minimum: GuardrailMode = GuardrailMode.IGNORE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "must_pass": self.must_pass.value,
            "coverage_minimum": self.coverage_minimum.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestGuardrails":
        return cls(
            must_pass=GuardrailMode(data.get("must_pass", "ignore")),
            coverage_minimum=GuardrailMode(data.get("coverage_minimum", "ignore")),
        )


@dataclass
class EnvironmentGuardrails:
    """Environment-related preflight checks."""

    required_env_vars: GuardrailMode = GuardrailMode.WARN
    python_version: GuardrailMode = GuardrailMode.IGNORE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "required_env_vars": self.required_env_vars.value,
            "python_version": self.python_version.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentGuardrails":
        return cls(
            required_env_vars=GuardrailMode(data.get("required_env_vars", "warn")),
            python_version=GuardrailMode(data.get("python_version", "ignore")),
        )


@dataclass
class GuardrailsConfig:
    """
    Complete guardrails configuration.

    Usage:
        config = get_config()
        if config.guardrails.git.uncommitted_changes == GuardrailMode.BLOCK:
            # Block boot
        elif config.guardrails.git.uncommitted_changes == GuardrailMode.WARN:
            # Show warning, continue
        else:
            # Ignore
    """

    section_id = "guardrails"

    git: GitGuardrails = field(default_factory=GitGuardrails)
    tests: TestGuardrails = field(default_factory=TestGuardrails)
    environment: EnvironmentGuardrails = field(default_factory=EnvironmentGuardrails)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "git": self.git.to_dict(),
            "tests": self.tests.to_dict(),
            "environment": self.environment.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsConfig":
        return cls(
            git=GitGuardrails.from_dict(data.get("git", {})),
            tests=TestGuardrails.from_dict(data.get("tests", {})),
            environment=EnvironmentGuardrails.from_dict(data.get("environment", {})),
        )
