"""
Invariant Checker for Vibe Agency Governance.

The InvariantChecker enforces the "Soul" of the system - hard constraints that
must be satisfied before any tool execution. This is the "Über-Ich" (Superego)
that prevents agents from violating system integrity.

Key concepts:
- Soul: A YAML configuration defining safety rules
- Invariant: A rule that must always hold true
- SoulResult: The result of checking a tool call against the soul

Architecture note:
This is ARCH-029 from Phase 3 (Governance & Soul).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SoulResult:
    """
    Result of checking a tool call against soul invariants.

    Attributes:
        allowed: Whether the tool call is permitted
        reason: Human-readable explanation if blocked (None if allowed)
    """

    allowed: bool
    reason: str | None = None


class InvariantChecker:
    """
    Validates tool calls against soul.yaml safety rules.

    This is the enforcement mechanism for system governance. Every tool call
    should be validated through this checker before execution.

    Design principles:
    1. Fail-safe: If soul.yaml is missing, we allow (for development)
    2. Explicit: Each rule has a clear condition and message
    3. Composable: Rules can be added without code changes
    4. Traceable: Every block includes the reason

    Example soul.yaml:
        safety_rules:
          - id: "protect_git"
            condition: "path_contains"
            pattern: ".git"
            action: "block"
            message: "Touching .git is forbidden."
    """

    def __init__(self, soul_path: str = "config/soul.yaml"):
        """
        Initialize the InvariantChecker.

        Args:
            soul_path: Path to the soul.yaml configuration file
        """
        self.soul_path = Path(soul_path)
        self.rules = self._load_rules()

    def _load_rules(self) -> list[dict]:
        """
        Load safety rules from soul.yaml.

        Returns:
            List of rule dictionaries. Empty list if file doesn't exist.
        """
        if not self.soul_path.exists():
            # Fail-safe: Missing soul.yaml is allowed for development
            # In production, this should probably raise an error
            return []

        with open(self.soul_path) as f:
            data = yaml.safe_load(f)
            return data.get("safety_rules", [])

    def check_tool_call(self, tool_name: str, params: dict[str, Any]) -> SoulResult:
        """
        Validate a tool call against all safety rules.

        This is the main entry point for governance checks. Call this before
        executing any tool.

        Args:
            tool_name: Name of the tool being called (e.g., "write_file")
            params: Tool parameters (e.g., {"path": "/etc/passwd", "content": "..."})

        Returns:
            SoulResult indicating whether the call is allowed and why

        Example:
            >>> checker = InvariantChecker()
            >>> result = checker.check_tool_call("write_file", {"path": ".git/config"})
            >>> print(result.allowed)  # False
            >>> print(result.reason)   # "Touching .git is forbidden..."
        """
        # Check each rule in order
        for rule in self.rules:
            # Only apply rules that have "block" action
            if rule.get("action") != "block":
                continue

            # Check if this rule applies to this tool call
            result = self._check_rule(rule, tool_name, params)
            if not result.allowed:
                return result

        # All rules passed
        return SoulResult(allowed=True)

    def _check_rule(self, rule: dict, tool_name: str, params: dict[str, Any]) -> SoulResult:
        """
        Check a single rule against a tool call.

        Args:
            rule: The rule dictionary from soul.yaml
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            SoulResult indicating whether this rule blocks the call
        """
        condition = rule.get("condition")

        # File path based rules (most common)
        if "path" in params:
            path_str = str(params["path"])

            # Rule: path_contains
            if condition == "path_contains":
                pattern = rule.get("pattern", "")
                if pattern and pattern in path_str:
                    return SoulResult(
                        allowed=False,
                        reason=f"{rule.get('message', 'Path blocked by soul rule')} (Rule: {rule.get('id', 'unknown')})",
                    )

            # Rule: path_matches (exact match)
            elif condition == "path_matches":
                pattern = rule.get("pattern", "")
                if pattern and pattern == path_str:
                    return SoulResult(
                        allowed=False,
                        reason=f"{rule.get('message', 'Path blocked by soul rule')} (Rule: {rule.get('id', 'unknown')})",
                    )

            # Rule: path_outside_root (sandbox confinement)
            elif condition == "path_outside_root":
                if self._is_path_outside_root(path_str):
                    return SoulResult(
                        allowed=False,
                        reason=f"{rule.get('message', 'Path outside root blocked')} (Rule: {rule.get('id', 'unknown')})",
                    )

        # Rule passed (or didn't apply)
        return SoulResult(allowed=True)

    def _is_path_outside_root(self, path_str: str) -> bool:
        """
        Check if a path is outside the project root.

        This implements sandbox confinement - agents should only be able to
        access files within the project directory.

        Args:
            path_str: The path to check

        Returns:
            True if path is outside project root
        """
        try:
            # Get absolute path of the target
            target_path = Path(path_str).resolve()

            # Get project root (assuming we're running from project root)
            # In production, this should be configurable
            root_path = Path.cwd().resolve()

            # Check if target is under root
            # This handles .. and symlinks correctly
            try:
                target_path.relative_to(root_path)
                return False  # Inside root
            except ValueError:
                return True  # Outside root

        except (OSError, RuntimeError):
            # If we can't resolve the path, block it (fail-safe)
            return True

    def reload(self) -> None:
        """
        Reload rules from soul.yaml.

        Useful for development/testing when you want to update rules without
        restarting the system.
        """
        self.rules = self._load_rules()

    @property
    def rule_count(self) -> int:
        """Return the number of loaded rules."""
        return len(self.rules)

    def get_rule_ids(self) -> list[str]:
        """Return list of all rule IDs."""
        return [rule.get("id", "unknown") for rule in self.rules]
