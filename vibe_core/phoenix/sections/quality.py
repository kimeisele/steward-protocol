"""Quality Configuration - Lint, Format, CI settings.

This config is IMMORTAL - lives in repo, survives container wipes.
Pre-commit hooks, CI workflows, lint rules - all defined here.

Philosophy:
- Container gets wiped? Config survives.
- New developer joins? Config tells them what to enforce.
- Agent needs to check code? Config defines the rules.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class LintConfig:
    """Linter configuration (ruff)."""

    tool: str = "ruff"
    # Critical rules that MUST pass (CI fails on these)
    critical_rules: List[str] = field(default_factory=lambda: ["E9", "F63", "F7", "F82"])
    # Info rules (shown but don't fail CI)
    info_rules: List[str] = field(default_factory=lambda: ["E", "F", "I", "W"])
    # Paths to check
    paths: List[str] = field(default_factory=lambda: ["vibe_core", "steward", "scripts"])
    # Paths to exclude
    exclude: List[str] = field(
        default_factory=lambda: [
            ".git",
            ".venv",
            "__pycache__",
            "data",
            "archive",
            "node_modules",
        ]
    )
    # Line length limit
    line_length: int = 120

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "critical_rules": self.critical_rules,
            "info_rules": self.info_rules,
            "paths": self.paths,
            "exclude": self.exclude,
            "line_length": self.line_length,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LintConfig":
        return cls(
            tool=data.get("tool", "ruff"),
            critical_rules=data.get("critical_rules", ["E9", "F63", "F7", "F82"]),
            info_rules=data.get("info_rules", ["E", "F", "I", "W"]),
            paths=data.get("paths", ["vibe_core", "steward", "scripts"]),
            exclude=data.get("exclude", []),
            line_length=data.get("line_length", 120),
        )


@dataclass
class FormatConfig:
    """Formatter configuration (ruff format)."""

    tool: str = "ruff"
    # Auto-fix on commit?
    auto_fix: bool = True
    # Paths to format
    paths: List[str] = field(default_factory=lambda: ["vibe_core", "steward", "scripts"])
    # Line length
    line_length: int = 120
    # Quote style
    quote_style: str = "double"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "auto_fix": self.auto_fix,
            "paths": self.paths,
            "line_length": self.line_length,
            "quote_style": self.quote_style,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormatConfig":
        return cls(
            tool=data.get("tool", "ruff"),
            auto_fix=data.get("auto_fix", True),
            paths=data.get("paths", ["vibe_core", "steward", "scripts"]),
            line_length=data.get("line_length", 120),
            quote_style=data.get("quote_style", "double"),
        )


@dataclass
class TestConfig:
    """Test runner configuration."""

    tool: str = "pytest"
    paths: List[str] = field(default_factory=lambda: ["tests"])
    # Markers to run by default
    default_markers: List[str] = field(default_factory=list)
    # Timeout per test (seconds)
    timeout: int = 300
    # Parallel workers (0 = auto)
    workers: int = 0
    # Coverage threshold (0 = disabled)
    coverage_threshold: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "paths": self.paths,
            "default_markers": self.default_markers,
            "timeout": self.timeout,
            "workers": self.workers,
            "coverage_threshold": self.coverage_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestConfig":
        return cls(
            tool=data.get("tool", "pytest"),
            paths=data.get("paths", ["tests"]),
            default_markers=data.get("default_markers", []),
            timeout=data.get("timeout", 300),
            workers=data.get("workers", 0),
            coverage_threshold=data.get("coverage_threshold", 0),
        )


@dataclass
class CIWorkflow:
    """Single CI workflow definition."""

    name: str
    file: str
    triggers: List[str] = field(default_factory=lambda: ["push", "pull_request"])
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "file": self.file,
            "triggers": self.triggers,
            "required": self.required,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CIWorkflow":
        return cls(
            name=data.get("name", ""),
            file=data.get("file", ""),
            triggers=data.get("triggers", ["push", "pull_request"]),
            required=data.get("required", True),
        )


@dataclass
class CIConfig:
    """CI/CD configuration."""

    # Primary workflows
    workflows: List[CIWorkflow] = field(default_factory=list)
    # Protected branches
    protected_branches: List[str] = field(default_factory=lambda: ["main", "master"])
    # Require status checks before merge
    require_status_checks: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflows": [w.to_dict() for w in self.workflows],
            "protected_branches": self.protected_branches,
            "require_status_checks": self.require_status_checks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CIConfig":
        workflows = [CIWorkflow.from_dict(w) for w in data.get("workflows", [])]
        return cls(
            workflows=workflows,
            protected_branches=data.get("protected_branches", ["main", "master"]),
            require_status_checks=data.get("require_status_checks", True),
        )


@dataclass
class QualityConfig:
    """
    Complete quality configuration.

    This is the SINGLE SOURCE OF TRUTH for:
    - Lint rules
    - Format rules
    - Test configuration
    - CI workflows

    Why here and not in .pre-commit-config.yaml?
    - That file dies with container wipe
    - This config lives in repo forever (phoenix = immortal)
    - Agents can read this to understand quality requirements
    - Kernel can enforce these rules
    """

    lint: LintConfig = field(default_factory=LintConfig)
    format: FormatConfig = field(default_factory=FormatConfig)
    test: TestConfig = field(default_factory=TestConfig)
    ci: CIConfig = field(default_factory=CIConfig)

    # Enforcement flags
    enforce_on_commit: bool = True
    enforce_on_push: bool = True
    block_on_failure: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lint": self.lint.to_dict(),
            "format": self.format.to_dict(),
            "test": self.test.to_dict(),
            "ci": self.ci.to_dict(),
            "enforce_on_commit": self.enforce_on_commit,
            "enforce_on_push": self.enforce_on_push,
            "block_on_failure": self.block_on_failure,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityConfig":
        return cls(
            lint=LintConfig.from_dict(data.get("lint", {})),
            format=FormatConfig.from_dict(data.get("format", {})),
            test=TestConfig.from_dict(data.get("test", {})),
            ci=CIConfig.from_dict(data.get("ci", {})),
            enforce_on_commit=data.get("enforce_on_commit", True),
            enforce_on_push=data.get("enforce_on_push", True),
            block_on_failure=data.get("block_on_failure", True),
        )

    def get_ruff_critical_args(self) -> List[str]:
        """Get ruff args for critical-only check (CI mode)."""
        rules = ",".join(self.lint.critical_rules)
        return [f"--select={rules}"] + self.lint.paths

    def get_ruff_full_args(self) -> List[str]:
        """Get ruff args for full check (informational)."""
        rules = ",".join(self.lint.info_rules)
        return [f"--select={rules}", "--statistics"] + self.lint.paths

    def get_pytest_args(self) -> List[str]:
        """Get pytest args from config."""
        args = self.test.paths.copy()
        if self.test.timeout:
            args.extend(["--timeout", str(self.test.timeout)])
        if self.test.workers:
            args.extend(["-n", str(self.test.workers)])
        if self.test.coverage_threshold:
            args.extend(["--cov", "--cov-fail-under", str(self.test.coverage_threshold)])
        return args


# Default quality config with steward-protocol settings
def get_default_quality_config() -> QualityConfig:
    """Get default quality config matching current CI setup."""
    return QualityConfig(
        lint=LintConfig(
            tool="ruff",
            critical_rules=["E9", "F63", "F7", "F82"],
            info_rules=["E", "F", "I", "W"],
            paths=["vibe_core", "steward", "scripts"],
            line_length=120,
        ),
        format=FormatConfig(
            tool="ruff",
            auto_fix=True,
            paths=["vibe_core", "steward", "scripts"],
            line_length=120,
        ),
        test=TestConfig(
            tool="pytest",
            paths=["tests"],
            timeout=300,
        ),
        ci=CIConfig(
            workflows=[
                CIWorkflow(name="Lint & Format", file="steward-ci.yml", required=True),
                CIWorkflow(name="Integration Tests", file="integration-tests.yml", required=True),
            ],
            protected_branches=["main", "master"],
        ),
    )
