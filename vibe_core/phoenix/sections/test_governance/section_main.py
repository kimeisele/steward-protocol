"""
TEST GOVERNANCE CONFIG SECTION - Who Watches the Watchers

PROBLEM:
- AI writes test
- Code changes
- Test fails
- AI changes test to pass  <-- REGRESSION! Contract broken!
- Nobody notices

SOLUTION:
- Tests are IMMUTABLE CONTRACTS
- Hash of each test stored in lineage at "birth"
- Mutation attempts are BLOCKED (or require human approval)
- Regression = AI must fix CODE, not test!

This config section controls test governance policy.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

# Phoenix section marker
section_id = "test_governance"


@dataclass
class TestGovernanceConfig:
    """
    Configuration for test suite governance.

    This is the "watchman's watchman" - ensures tests can't be
    silently modified to hide regressions.
    """

    # ========================================================================
    # MUTATION POLICY
    # ========================================================================

    mutation_policy: str = "blocked"
    """
    What happens when AI attempts to modify a test file:
    - "blocked": Modification is rejected entirely
    - "human_approval": Requires explicit human approval
    - "warn_only": Log warning but allow (dangerous!)
    """

    # ========================================================================
    # BASELINE ENFORCEMENT
    # ========================================================================

    baseline_enforcement: bool = True
    """
    If True, compare test file hashes against lineage records.
    Tests that have mutated since their "birth" are flagged.
    """

    baseline_path: str = "data/test_baselines.json"
    """Path to store test baseline hashes."""

    # ========================================================================
    # REGRESSION MODE
    # ========================================================================

    regression_mode: str = "fix_code_not_test"
    """
    When a test fails, what should AI do?
    - "fix_code_not_test": AI MUST fix the implementation, not the test
    - "allow_test_updates": AI can update tests (dangerous!)
    """

    # ========================================================================
    # FROZEN PATTERNS
    # ========================================================================

    frozen_tests: List[str] = field(
        default_factory=lambda: [
            "tests/integration/test_system_boot.py",
            "tests/test_unified_loader.py",
            "tests/hardening/**",
        ]
    )
    """
    Glob patterns for tests that can NEVER be modified by AI.
    These are the "constitutional tests" - the foundation.
    """

    human_review_required_patterns: List[str] = field(
        default_factory=lambda: [
            "tests/**",  # All tests require human review by default
        ]
    )
    """
    Glob patterns for tests that require human review for ANY change.
    """

    # ========================================================================
    # AUDIT SETTINGS
    # ========================================================================

    log_all_test_mutations: bool = True
    """Log every attempt to modify a test file."""

    mutation_log_path: str = "data/logs/test_mutations.log"
    """Path for test mutation audit log."""

    alert_on_mutation_attempt: bool = True
    """Raise visible alert when mutation is attempted."""

    # ========================================================================
    # SERIALIZATION (required for SectionLoader)
    # ========================================================================

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestGovernanceConfig":
        """Create from parsed YAML dict."""
        return cls(
            mutation_policy=data.get("mutation_policy", "blocked"),
            baseline_enforcement=data.get("baseline_enforcement", True),
            baseline_path=data.get("baseline_path", "data/test_baselines.json"),
            regression_mode=data.get("regression_mode", "fix_code_not_test"),
            frozen_tests=data.get(
                "frozen_tests",
                [
                    "tests/integration/test_system_boot.py",
                    "tests/test_unified_loader.py",
                    "tests/hardening/**",
                ],
            ),
            human_review_required_patterns=data.get("human_review_required_patterns", ["tests/**"]),
            log_all_test_mutations=data.get("log_all_test_mutations", True),
            mutation_log_path=data.get("mutation_log_path", "data/logs/test_mutations.log"),
            alert_on_mutation_attempt=data.get("alert_on_mutation_attempt", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to YAML-compatible dict."""
        return {
            "mutation_policy": self.mutation_policy,
            "baseline_enforcement": self.baseline_enforcement,
            "baseline_path": self.baseline_path,
            "regression_mode": self.regression_mode,
            "frozen_tests": self.frozen_tests,
            "human_review_required_patterns": self.human_review_required_patterns,
            "log_all_test_mutations": self.log_all_test_mutations,
            "mutation_log_path": self.mutation_log_path,
            "alert_on_mutation_attempt": self.alert_on_mutation_attempt,
        }

    # ========================================================================
    # VALIDATION
    # ========================================================================

    def validate(self) -> List[str]:
        """Validate configuration. Returns list of error messages."""
        errors: List[str] = []

        valid_policies = ["blocked", "human_approval", "warn_only"]
        if self.mutation_policy not in valid_policies:
            errors.append(f"mutation_policy must be one of {valid_policies}")

        valid_modes = ["fix_code_not_test", "allow_test_updates"]
        if self.regression_mode not in valid_modes:
            errors.append(f"regression_mode must be one of {valid_modes}")

        return errors

    def is_frozen(self, test_path: str) -> bool:
        """Check if a test file is frozen (can never be modified)."""
        from fnmatch import fnmatch

        for pattern in self.frozen_tests:
            if fnmatch(test_path, pattern):
                return True
        return False

    def requires_human_review(self, test_path: str) -> bool:
        """Check if a test file requires human review for changes."""
        from fnmatch import fnmatch

        for pattern in self.human_review_required_patterns:
            if fnmatch(test_path, pattern):
                return True
        return False
