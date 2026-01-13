"""
Guardrails Configuration - Preflight Checks.

Controls system behavior BEFORE boot/execution.
Different from runtime guards (tool_safety_guard) or test guards (test_guardian).

Guard Hierarchy:
  guardrails/        PREFLIGHT (before boot) <- THIS
  tool_safety_guard  RUNTIME (during tool execution)
  test_guardian      TEST PHASE (during test runs)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x1bd1e7aa"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


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
class UIFilesConfig:
    """Auto-commit configuration for generated UI files."""

    auto_commit: bool = True
    auto_push: bool = False
    commit_message: str = "auto: Update generated UI files"
    patterns: List[str] = field(default_factory=lambda: ["*.md", "!docs/**"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "auto_commit": self.auto_commit,
            "auto_push": self.auto_push,
            "commit_message": self.commit_message,
            "patterns": self.patterns,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UIFilesConfig":
        return cls(
            auto_commit=data.get("auto_commit", True),
            auto_push=data.get("auto_push", False),
            commit_message=data.get("commit_message", "auto: Update generated UI files"),
            patterns=data.get("patterns", ["*.md", "!docs/**"]),
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
    ui_files: UIFilesConfig = field(default_factory=UIFilesConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "git": self.git.to_dict(),
            "tests": self.tests.to_dict(),
            "environment": self.environment.to_dict(),
            "ui_files": self.ui_files.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailsConfig":
        return cls(
            git=GitGuardrails.from_dict(data.get("git", {})),
            tests=TestGuardrails.from_dict(data.get("tests", {})),
            environment=EnvironmentGuardrails.from_dict(data.get("environment", {})),
            ui_files=UIFilesConfig.from_dict(data.get("ui_files", {})),
        )
