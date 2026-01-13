"""Steward Configuration - Agent Protocol settings from vibe_core.steward.yaml.

FRACTAL PATTERN: Mirrors kernel.py, city.py, quality.py

Implements SPECIFICATION.md:
- Layer 1.5: User & Team Context
- Layer 1.6: Cognitive Policy

Source: config/steward.yaml
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xe7a196ce"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModelPreferences:
    """LLM model preferences for different cognitive tasks."""

    reasoning: str = ""  # Deep analysis, complex problem-solving
    efficiency: str = ""  # Fast operations, simple tasks
    creative: str = ""  # Content generation, creative work
    fallback: str = ""  # Backup when preferred unavailable


@dataclass
class EconomicConstraints:
    """Hard limits on resource consumption."""

    max_cost_per_run: float = 1.0  # USD limit per delegation
    max_daily_budget: float = 10.0  # USD limit per 24h
    provider_priority: List[str] = field(default_factory=list)  # Ordered providers


@dataclass
class CognitivePolicy:
    """
    Layer 1.6: Cognitive Policy (SPECIFICATION.md)

    Gives users control over agent cognition:
    - Which models for which tasks
    - Economic constraints
    """

    model_preferences: ModelPreferences = field(default_factory=ModelPreferences)
    economic_constraints: EconomicConstraints = field(default_factory=EconomicConstraints)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitivePolicy":
        mp_data = data.get("model_preferences", {})
        ec_data = data.get("economic_constraints", {})

        return cls(
            model_preferences=ModelPreferences(
                reasoning=mp_data.get("reasoning", ""),
                efficiency=mp_data.get("efficiency", ""),
                creative=mp_data.get("creative", ""),
                fallback=mp_data.get("fallback", ""),
            ),
            economic_constraints=EconomicConstraints(
                max_cost_per_run=ec_data.get("max_cost_per_run", 1.0),
                max_daily_budget=ec_data.get("max_daily_budget", 10.0),
                provider_priority=ec_data.get("provider_priority", []),
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_preferences": {
                "reasoning": self.model_preferences.reasoning,
                "efficiency": self.model_preferences.efficiency,
                "creative": self.model_preferences.creative,
                "fallback": self.model_preferences.fallback,
            },
            "economic_constraints": {
                "max_cost_per_run": self.economic_constraints.max_cost_per_run,
                "max_daily_budget": self.economic_constraints.max_daily_budget,
                "provider_priority": self.economic_constraints.provider_priority,
            },
        }


@dataclass
class UserPreferences:
    """Individual user preferences."""

    role: str = ""
    workflow_style: str = "balanced"  # balanced, test_first, iterative
    verbosity: str = "medium"  # low, medium, high
    communication: str = "friendly"  # concise, friendly, explanatory
    language: str = "en-US"
    timezone: str = ""
    constraints: List[str] = field(default_factory=list)


@dataclass
class TeamContext:
    """Team-wide defaults."""

    development_style: str = "test_driven"
    git_workflow: str = "rebase_over_merge"
    commit_style: str = "conventional_commits"
    min_coverage: float = 0.80
    quality_gates: List[str] = field(default_factory=list)


@dataclass
class UserContext:
    """
    Layer 1.5: User & Team Context (SPECIFICATION.md)

    Precedence: User Preferences > Team Context > Agent Defaults
    """

    default_user: UserPreferences = field(default_factory=UserPreferences)
    users: Dict[str, UserPreferences] = field(default_factory=dict)
    team: TeamContext = field(default_factory=TeamContext)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserContext":
        # Default user
        default_data = data.get("default_user", {})
        default_user = UserPreferences(
            role=default_data.get("role", ""),
            workflow_style=default_data.get("workflow_style", "balanced"),
            verbosity=default_data.get("verbosity", "medium"),
            communication=default_data.get("communication", "friendly"),
            language=default_data.get("language", "en-US"),
            timezone=default_data.get("timezone", ""),
            constraints=default_data.get("constraints", []),
        )

        # Named users
        users = {}
        users_data = data.get("users", {})
        for username, user_data in users_data.items():
            users[username] = UserPreferences(
                role=user_data.get("role", ""),
                workflow_style=user_data.get("workflow_style", "balanced"),
                verbosity=user_data.get("verbosity", "medium"),
                communication=user_data.get("communication", "friendly"),
                language=user_data.get("language", "en-US"),
                timezone=user_data.get("timezone", ""),
                constraints=user_data.get("constraints", []),
            )

        # Team
        team_data = data.get("team", {})
        team = TeamContext(
            development_style=team_data.get("development_style", "test_driven"),
            git_workflow=team_data.get("git_workflow", "rebase_over_merge"),
            commit_style=team_data.get("commit_style", "conventional_commits"),
            min_coverage=team_data.get("min_coverage", 0.80),
            quality_gates=team_data.get("quality_gates", []),
        )

        return cls(default_user=default_user, users=users, team=team)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_user": {
                "role": self.default_user.role,
                "workflow_style": self.default_user.workflow_style,
                "verbosity": self.default_user.verbosity,
                "communication": self.default_user.communication,
                "language": self.default_user.language,
                "timezone": self.default_user.timezone,
                "constraints": self.default_user.constraints,
            },
            "users": {
                username: {
                    "role": prefs.role,
                    "workflow_style": prefs.workflow_style,
                    "verbosity": prefs.verbosity,
                    "communication": prefs.communication,
                    "language": prefs.language,
                    "timezone": prefs.timezone,
                    "constraints": prefs.constraints,
                }
                for username, prefs in self.users.items()
            },
            "team": {
                "development_style": self.team.development_style,
                "git_workflow": self.team.git_workflow,
                "commit_style": self.team.commit_style,
                "min_coverage": self.team.min_coverage,
                "quality_gates": self.team.quality_gates,
            },
        }

    def get_user(self, username: Optional[str] = None) -> UserPreferences:
        """Get user preferences with fallback to default."""
        if username and username in self.users:
            return self.users[username]
        return self.default_user


@dataclass
class BehaviorConfig:
    """
    Agent behavior rules - Genesis Protocol, Anti-Slop, etc.

    These are the constitutional rules for STEWARD behavior.
    """

    genesis_protocol: bool = True  # Verify system integrity before work
    anti_slop_rules: bool = True  # No shortcuts, verify everything
    require_tests: bool = True  # Must run tests before claiming done
    require_commit: bool = True  # Must commit changes
    require_handoff: bool = True  # Must update .session_handoff.json
    enforce_oath: bool = True  # Enforce Constitutional Oath for all agents


@dataclass
class StewardConfig:
    """
    STEWARD Protocol Configuration - Layer 1.5 and 1.6 ONLY.

    Auto-discovered by SectionLoader -> loads from config/steward.yaml

    IMPORTANT: This configures the PROTOCOL, not an agent identity.
    STEWARD is the governance framework itself, not an agent like herald/civic.

    What belongs here:
    - Layer 1.5: User & Team Context (operator preferences)
    - Layer 1.6: Cognitive Policy (model preferences, budgets)
    - Behavior Rules (Genesis Protocol, Anti-Slop)

    What does NOT belong here:
    - Agent identity (agents have steward.json files)
    - System prompt templates (prompts are GENERATED from Protocol data)

    FRACTAL: Same pattern as KernelConfig, CityConfig, QualityConfig
    """

    # Class-level section identifier for auto-discovery
    section_id = "steward"
    source_file = "steward.yaml"

    # Layer 1.5: User & Team Context
    user_context: UserContext = field(default_factory=UserContext)

    # Layer 1.6: Cognitive Policy
    cognitive_policy: CognitivePolicy = field(default_factory=CognitivePolicy)

    # Behavior rules (Genesis Protocol, Anti-Slop)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)

    # Active user (set at runtime via --user flag)
    active_user: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StewardConfig":
        """Create StewardConfig from parsed YAML dict."""
        return cls(
            user_context=UserContext.from_dict(data.get("user_context", {})),
            cognitive_policy=CognitivePolicy.from_dict(data.get("cognitive_policy", {})),
            behavior=BehaviorConfig(
                genesis_protocol=data.get("behavior", {}).get("genesis_protocol", True),
                anti_slop_rules=data.get("behavior", {}).get("anti_slop_rules", True),
                require_tests=data.get("behavior", {}).get("require_tests", True),
                require_commit=data.get("behavior", {}).get("require_commit", True),
                require_handoff=data.get("behavior", {}).get("require_handoff", True),
                enforce_oath=data.get("behavior", {}).get("enforce_oath", True),
            ),
            active_user=data.get("active_user"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize back to YAML-compatible dict."""
        return {
            "user_context": self.user_context.to_dict(),
            "cognitive_policy": self.cognitive_policy.to_dict(),
            "behavior": {
                "genesis_protocol": self.behavior.genesis_protocol,
                "anti_slop_rules": self.behavior.anti_slop_rules,
                "require_tests": self.behavior.require_tests,
                "require_commit": self.behavior.require_commit,
                "require_handoff": self.behavior.require_handoff,
                "enforce_oath": self.behavior.enforce_oath,
            },
        }

    def get_active_user_prefs(self) -> UserPreferences:
        """Get preferences for the active user."""
        return self.user_context.get_user(self.active_user)
