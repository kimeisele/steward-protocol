"""Quality Configuration - Lint, Format, CI settings.

This config is IMMORTAL - lives in repo, survives container wipes.
Pre-commit hooks, CI workflows, lint rules - all defined here.

Philosophy:
- Container gets wiped? Config survives.
- New developer joins? Config tells them what to enforce.
- Agent needs to check code? Config defines the rules.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0x62c372a0"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TestCategory(str, Enum):
    """Test categories for filtering."""

    UNIT = "unit"  # Fast, isolated tests
    INTEGRATION = "integration"  # Tests with dependencies
    E2E = "e2e"  # End-to-end tests
    SMOKE = "smoke"  # Quick sanity checks
    SLOW = "slow"  # Known slow tests


@dataclass
class TestProfile:
    """
    A testing profile - defines HOW to run tests.

    Profiles allow:
    - fast: Quick feedback during development (unit tests only, parallel)
    - full: Complete test suite (all tests, with coverage)
    - ci: CI-optimized (parallel, fail-fast, timeout enforcement)
    - smoke: Quick sanity check (tagged smoke tests only)
    """

    name: str
    description: str = ""
    # Which categories to include (empty = all)
    include_categories: List[str] = field(default_factory=list)
    # Which categories to exclude
    exclude_categories: List[str] = field(default_factory=list)
    # Markers to select (pytest -m)
    markers: List[str] = field(default_factory=list)
    # Markers to exclude
    exclude_markers: List[str] = field(default_factory=list)
    # Parallel workers (0 = auto, 1 = sequential)
    workers: int = 0
    # Stop on first failure
    fail_fast: bool = False
    # Timeout per test (0 = no timeout)
    timeout: int = 0
    # Coverage enabled
    coverage: bool = False
    # Coverage threshold (0 = no minimum)
    coverage_threshold: int = 0
    # Verbose output
    verbose: bool = False
    # Show test durations
    show_durations: int = 0  # 0 = disabled, N = show N slowest
    # Extra pytest args
    extra_args: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "include_categories": self.include_categories,
            "exclude_categories": self.exclude_categories,
            "markers": self.markers,
            "exclude_markers": self.exclude_markers,
            "workers": self.workers,
            "fail_fast": self.fail_fast,
            "timeout": self.timeout,
            "coverage": self.coverage,
            "coverage_threshold": self.coverage_threshold,
            "verbose": self.verbose,
            "show_durations": self.show_durations,
            "extra_args": self.extra_args,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestProfile":
        return cls(
            name=data.get("name", "default"),
            description=data.get("description", ""),
            include_categories=data.get("include_categories", []),
            exclude_categories=data.get("exclude_categories", []),
            markers=data.get("markers", []),
            exclude_markers=data.get("exclude_markers", []),
            workers=data.get("workers", 0),
            fail_fast=data.get("fail_fast", False),
            timeout=data.get("timeout", 0),
            coverage=data.get("coverage", False),
            coverage_threshold=data.get("coverage_threshold", 0),
            verbose=data.get("verbose", False),
            show_durations=data.get("show_durations", 0),
            extra_args=data.get("extra_args", []),
        )

    def get_pytest_args(self, paths: Optional[List[str]] = None) -> List[str]:
        """Generate pytest args for this profile."""
        args = []

        # Markers
        if self.markers:
            marker_expr = " or ".join(self.markers)
            if self.exclude_markers:
                marker_expr = f"({marker_expr}) and not ({' or '.join(self.exclude_markers)})"
            args.extend(["-m", marker_expr])
        elif self.exclude_markers:
            args.extend(["-m", f"not ({' or '.join(self.exclude_markers)})"])

        # Workers
        if self.workers != 1:  # 1 = sequential, skip -n
            args.extend(["-n", str(self.workers) if self.workers > 0 else "auto"])

        # Fail fast
        if self.fail_fast:
            args.append("-x")

        # Timeout
        if self.timeout:
            args.extend(["--timeout", str(self.timeout)])

        # Coverage
        if self.coverage:
            args.append("--cov")
            if self.coverage_threshold:
                args.extend(["--cov-fail-under", str(self.coverage_threshold)])

        # Verbose
        if self.verbose:
            args.append("-v")

        # Durations
        if self.show_durations:
            args.extend(["--durations", str(self.show_durations)])

        # Extra args
        args.extend(self.extra_args)

        # Paths
        if paths:
            args.extend(paths)

        return args


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
class AgentFixtureConfig:
    """Configuration for a test agent type."""

    id_prefix: str
    oath_sworn: Optional[bool] = True
    capabilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_prefix": self.id_prefix,
            "oath_sworn": self.oath_sworn,
            "capabilities": self.capabilities,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentFixtureConfig":
        return cls(
            id_prefix=data.get("id_prefix", "test-agent"),
            oath_sworn=data.get("oath_sworn", True),
            capabilities=data.get("capabilities", []),
        )


@dataclass
class KernelPresetConfig:
    """Configuration for a kernel preset."""

    description: str = ""
    plugins: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"description": self.description, "plugins": self.plugins}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KernelPresetConfig":
        return cls(
            description=data.get("description", ""),
            plugins=data.get("plugins", []),
        )


@dataclass
class FixturesConfig:
    """
    Test fixtures configuration - Phoenix Config style.

    This configures the standardized test objects:
    - Kernel settings (ledger path, plugin loading)
    - Agent presets (compliant, no_oath, false_oath)
    - Kernel presets (minimal, permissive, governance, recording)

    conftest.py reads from HERE - no hardcoded values!
    """

    # Kernel defaults
    kernel_ledger_path: str = ":memory:"
    kernel_load_plugins: bool = False

    # Agent presets
    agents: Dict[str, AgentFixtureConfig] = field(default_factory=dict)

    # Kernel presets
    kernel_presets: Dict[str, KernelPresetConfig] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize defaults if not provided."""
        if not self.agents:
            self.agents = self._get_default_agents()
        if not self.kernel_presets:
            self.kernel_presets = self._get_default_presets()

    def _get_default_agents(self) -> Dict[str, AgentFixtureConfig]:
        return {
            "compliant": AgentFixtureConfig(
                id_prefix="test-compliant",
                oath_sworn=True,
                capabilities=["governance", "task_execution"],
            ),
            "no_oath": AgentFixtureConfig(
                id_prefix="test-no-oath",
                oath_sworn=None,  # Attribute missing
                capabilities=[],
            ),
            "false_oath": AgentFixtureConfig(
                id_prefix="test-false-oath",
                oath_sworn=False,
                capabilities=[],
            ),
        }

    def _get_default_presets(self) -> Dict[str, KernelPresetConfig]:
        return {
            "minimal": KernelPresetConfig(
                description="Bare kernel, no plugins, memory ledger",
                plugins=[],
            ),
            "permissive": KernelPresetConfig(
                description="All operations allowed, no governance",
                plugins=["test_mode"],
            ),
            "governance": KernelPresetConfig(
                description="Full governance stack enabled",
                plugins=["steward_protocol", "vedic_governance"],
            ),
            "recording": KernelPresetConfig(
                description="Records all hook calls for assertions",
                plugins=["test_orchestration"],
            ),
        }

    def get_agent_config(self, agent_type: str) -> AgentFixtureConfig:
        """Get agent config by type (compliant, no_oath, false_oath)."""
        return self.agents.get(agent_type, self.agents.get("compliant"))

    def get_kernel_preset(self, preset_name: str) -> KernelPresetConfig:
        """Get kernel preset by name."""
        return self.kernel_presets.get(preset_name, self.kernel_presets.get("minimal"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kernel": {
                "ledger_path": self.kernel_ledger_path,
                "load_plugins": self.kernel_load_plugins,
            },
            "agents": {k: v.to_dict() for k, v in self.agents.items()},
            "kernel_presets": {k: v.to_dict() for k, v in self.kernel_presets.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FixturesConfig":
        kernel_data = data.get("kernel", {})
        agents_data = data.get("agents", {})
        presets_data = data.get("kernel_presets", {})

        return cls(
            kernel_ledger_path=kernel_data.get("ledger_path", ":memory:"),
            kernel_load_plugins=kernel_data.get("load_plugins", False),
            agents={k: AgentFixtureConfig.from_dict(v) for k, v in agents_data.items()},
            kernel_presets={k: KernelPresetConfig.from_dict(v) for k, v in presets_data.items()},
        )


@dataclass
class TestConfig:
    """
    Test runner configuration with profiles.

    Profiles allow different testing modes:
    - fast: Quick feedback (parallel, no slow tests, fail-fast)
    - full: Complete suite (all tests, coverage, show slowest)
    - ci: CI-optimized (parallel, timeout enforcement, fail-fast)
    - smoke: Quick sanity check (smoke-tagged tests only)

    Kernel can call: config.quality.test.get_profile("fast").get_pytest_args()
    """

    tool: str = "pytest"
    paths: List[str] = field(default_factory=lambda: ["tests"])
    # Default profile to use
    default_profile: str = "fast"
    # Available profiles
    profiles: Dict[str, TestProfile] = field(default_factory=dict)
    # Global timeout (can be overridden by profile)
    timeout: int = 300
    # Global workers (can be overridden by profile)
    workers: int = 0
    # Coverage threshold (can be overridden by profile)
    coverage_threshold: int = 0
    # Fixtures configuration (Phoenix Config style)
    fixtures: FixturesConfig = field(default_factory=FixturesConfig)

    def __post_init__(self):
        """Initialize default profiles if none provided."""
        if not self.profiles:
            self.profiles = self._get_default_profiles()

    def _get_default_profiles(self) -> Dict[str, TestProfile]:
        """Generate sensible default profiles."""
        return {
            "fast": TestProfile(
                name="fast",
                description="Quick feedback during development",
                exclude_markers=["slow", "integration", "e2e"],
                workers=0,  # auto
                fail_fast=True,
                timeout=30,
                verbose=False,
                show_durations=5,
            ),
            "full": TestProfile(
                name="full",
                description="Complete test suite with coverage",
                workers=0,  # auto
                fail_fast=False,
                timeout=self.timeout,
                coverage=True,
                coverage_threshold=self.coverage_threshold,
                verbose=True,
                show_durations=10,
            ),
            "ci": TestProfile(
                name="ci",
                description="CI-optimized (strict, parallel, fail-fast)",
                workers=0,  # auto
                fail_fast=True,
                timeout=self.timeout,
                verbose=False,
                show_durations=10,
                extra_args=["--tb=short"],
            ),
            "smoke": TestProfile(
                name="smoke",
                description="Quick sanity check",
                markers=["smoke"],
                workers=0,
                fail_fast=True,
                timeout=10,
                verbose=False,
            ),
            "unit": TestProfile(
                name="unit",
                description="Unit tests only (fast, isolated)",
                markers=["unit"],
                exclude_markers=["integration", "e2e", "slow"],
                workers=0,
                fail_fast=False,
                timeout=30,
                show_durations=5,
            ),
            "integration": TestProfile(
                name="integration",
                description="Integration tests only",
                markers=["integration"],
                workers=1,  # sequential for stability
                fail_fast=False,
                timeout=120,
                verbose=True,
            ),
        }

    def get_profile(self, name: Optional[str] = None) -> TestProfile:
        """Get a test profile by name, or default if not specified."""
        profile_name = name or self.default_profile
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        # Fallback to default profile or first available
        if self.default_profile in self.profiles:
            return self.profiles[self.default_profile]
        if self.profiles:
            return next(iter(self.profiles.values()))
        # Ultimate fallback - create basic profile
        return TestProfile(name="default", timeout=self.timeout, workers=self.workers)

    def list_profiles(self) -> List[str]:
        """List available profile names."""
        return list(self.profiles.keys())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "paths": self.paths,
            "default_profile": self.default_profile,
            "profiles": {k: v.to_dict() for k, v in self.profiles.items()},
            "timeout": self.timeout,
            "workers": self.workers,
            "coverage_threshold": self.coverage_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestConfig":
        profiles_data = data.get("profiles", {})
        profiles = {k: TestProfile.from_dict(v) for k, v in profiles_data.items()}
        config = cls(
            tool=data.get("tool", "pytest"),
            paths=data.get("paths", ["tests"]),
            default_profile=data.get("default_profile", "fast"),
            profiles=profiles,
            timeout=data.get("timeout", 300),
            workers=data.get("workers", 0),
            coverage_threshold=data.get("coverage_threshold", 0),
            fixtures=FixturesConfig.from_dict(data.get("fixtures", {})),
        )
        # Ensure default profiles exist if none provided
        if not config.profiles:
            config.profiles = config._get_default_profiles()
        return config

    def get_pytest_args(self, profile: Optional[str] = None) -> List[str]:
        """Get pytest args for a profile (convenience method)."""
        return self.get_profile(profile).get_pytest_args(self.paths)


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

    Auto-discovered by SectionLoader → loads from config/quality.yaml

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

    # Class-level section identifier for auto-discovery
    section_id = "quality"

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

    def get_pytest_args(self, profile: Optional[str] = None) -> List[str]:
        """Get pytest args for a specific profile (or default)."""
        return self.test.get_pytest_args(profile)

    def get_test_profile(self, name: Optional[str] = None) -> TestProfile:
        """Get a test profile by name."""
        return self.test.get_profile(name)

    def list_test_profiles(self) -> List[str]:
        """List available test profiles."""
        return self.test.list_profiles()


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
