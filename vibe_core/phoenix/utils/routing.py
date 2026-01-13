"""Routing Configuration - Hot-swappable routing rules from MATRIX.md."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x0091f02c"  # GenesisByte: parampara % 37 == 0

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class RoutingRule:
    """Single routing rule from MATRIX.md."""

    pattern: str  # Regex pattern
    circuit: str  # Target circuit name
    priority: str = "NORMAL"
    active: bool = True

    def matches(self, input_text: str) -> bool:
        """Check if this rule matches the input."""
        if not self.active:
            return False
        try:
            return bool(re.search(self.pattern, input_text, re.IGNORECASE))
        except re.error:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for config persistence/spawning."""
        return {
            "pattern": self.pattern,
            "circuit": self.circuit,
            "priority": self.priority,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutingRule":
        """Create RoutingRule from dict."""
        return cls(
            pattern=data.get("pattern", ""),
            circuit=data.get("circuit", ""),
            priority=data.get("priority", "NORMAL"),
            active=data.get("active", True),
        )


def parse_matrix_md(content: str) -> List[RoutingRule]:
    """
    Parse MATRIX.md content into routing rules.

    Expected format:
    | Pattern | Circuit | Priority | Status |
    | :--- | :--- | :--- | :--- |
    | `regex` | `CIRCUIT_NAME` | HIGH | ACTIVE |

    Args:
        content: Raw MATRIX.md file content

    Returns:
        List of RoutingRule objects
    """
    rules: List[RoutingRule] = []

    for line in content.splitlines():
        line = line.strip()

        # Only process table rows
        if not line.startswith("|"):
            continue

        # Skip headers and separators
        if "Pattern" in line or "---" in line or ":---" in line:
            continue

        # Parse row
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 2:
            pattern = parts[0].strip("`")
            circuit = parts[1].strip("`")
            priority = parts[2] if len(parts) > 2 else "NORMAL"
            status = parts[3] if len(parts) > 3 else "ACTIVE"

            active = "ACTIVE" in status.upper() or status == ""

            rules.append(
                RoutingRule(
                    pattern=pattern,
                    circuit=circuit,
                    priority=priority,
                    active=active,
                )
            )

    return rules


def load_routing_rules(matrix_path: Path) -> List[RoutingRule]:
    """
    Load routing rules from MATRIX.md file.

    Args:
        matrix_path: Path to MATRIX.md

    Returns:
        List of RoutingRule objects
    """
    if not matrix_path.exists():
        return []

    try:
        content = matrix_path.read_text()
        return parse_matrix_md(content)
    except Exception:
        return []


def save_routing_rules(rules: List[RoutingRule], matrix_path: Path) -> bool:
    """
    Save routing rules back to MATRIX.md.

    Args:
        rules: List of routing rules
        matrix_path: Path to save to

    Returns:
        True if successful
    """
    try:
        lines = [
            "# MATRIX",
            "| Pattern | Circuit | Priority | Status |",
            "| :--- | :--- | :--- | :--- |",
        ]

        for rule in rules:
            status = "ACTIVE" if rule.active else "INACTIVE"
            lines.append(f"| `{rule.pattern}` | `{rule.circuit}` | {rule.priority} | {status} |")

        matrix_path.write_text("\n".join(lines) + "\n")
        return True
    except Exception:
        return False
