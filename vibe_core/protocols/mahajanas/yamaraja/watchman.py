"""
WATCHMAN PROTOCOL - AST-Based Violation Detection
==================================================

Owner: YAMARAJA (Judgment/Audit)
OpCode: AUDIT_LOG (Detection gate)

"The Watchman guards the temple. When an agent breaks the law,
the Watchman's sword falls swift and merciless. No exceptions."

PATTERN: ShuddhiProtocol HEALS, WatchmanProtocol DETECTS.
Both use AST parsing. Complementary, not overlapping.

EXISTING IMPL: vibe_core/cartridges/system/watchman/cartridge_main.py
This protocol wraps the existing WatchmanCartridge as a thin interface.

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x3039c8a2"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import (
    ClassVar,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    TypedDict,
    runtime_checkable,
)

# Import YamarajaProtocolBase - Watchman is a CAPABILITY, not separate position
from vibe_core.protocols.mahajanas.yamaraja import YamarajaProtocolBase


# =============================================================================
# WATCHMAN = YAMARAJA CAPABILITY (Not separate position!)
# =============================================================================
# Watchman is Position 15 (YAMARAJA) with AUDIT_LOG opcode.
# It doesn't register a new position - it USES YamarajaProtocolBase.


# =============================================================================
# WATERTIGHT TYPES (NO ANY!)
# =============================================================================


class ViolationSeverity(str, Enum):
    """Severity levels for violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ViolationPattern(str, Enum):
    """Types of violation patterns Watchman detects."""
    MOCK_RETURN = "mock_return"
    FAKE_SUCCESS = "fake_success"
    PLACEHOLDER_IMPL = "placeholder_impl"
    UNINITIALIZED_ATTR = "uninitialized_attr"
    UNAUTHORIZED_NETWORK = "unauthorized_network"
    UNVERIFIED_CONNECTION = "unverified_connections"
    ANY_TYPE_USAGE = "any_type_usage"
    MISSING_OWNER = "missing_owner"
    MISSING_CHANTING = "missing_chanting"


class Violation(TypedDict, total=False):
    """
    A detected violation. WATERTIGHT - no Any!
    """
    agent_id: str
    file_path: str
    line_number: int
    pattern: str  # ViolationPattern.value
    severity: str  # ViolationSeverity.value
    code_snippet: str
    reason: str
    rule_id: str
    has_remedy: bool


class PatrolResult(TypedDict, total=False):
    """
    Result of a patrol scan. WATERTIGHT - no Any!
    """
    status: str  # "clean", "VIOLATIONS_DETECTED"
    violations_found: int
    agents_frozen: List[str]
    agents_thawed: List[str]
    violations: List[Violation]


class InspectionResult(TypedDict, total=False):
    """
    Result of deep AST inspection. WATERTIGHT - no Any!
    """
    status: str  # "COMPLIANT", "WARNINGS_DETECTED", "VIOLATIONS_DETECTED"
    total_violations: int
    critical_count: int
    by_severity: Dict[str, int]
    by_agent: Dict[str, int]
    violations: List[Violation]
    healing_tasks_created: int
    violations_recorded: int
    should_fail_build: bool


class HealthResult(TypedDict, total=False):
    """
    Result of system health check. WATERTIGHT - no Any!
    """
    status: str  # "healthy", "degraded", "critical"
    git_hooks_installed: bool
    hooks_valid: bool
    critical_files_present: bool
    recommendations: List[str]


class WatchmanState(TypedDict, total=False):
    """
    Current state of Watchman. WATERTIGHT - no Any!
    """
    protocol_name: str
    owner: str
    is_chanting: bool
    violations_detected: int
    last_patrol: str  # ISO timestamp
    last_inspection: str  # ISO timestamp
    health: str


# =============================================================================
# WATCHMAN PROTOCOL
# =============================================================================


@runtime_checkable
class WatchmanProtocol(Protocol):
    """
    AST-based violation detection protocol.

    Owner: YAMARAJA (Position 15)
    OpCode: AUDIT_LOG

    PATTERN: Watchman DETECTS, Shuddhi HEALS.
    Both use AST. Complementary roles.

    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 15 in the Mahamantra."""
        ...

    # =========================================================================
    # Patrol (Quick Grep-Based Scan)
    # =========================================================================

    def patrol(self) -> PatrolResult:
        """
        Run quick pattern-based scan.
        Fast (~50ms), catches obvious violations.
        """
        ...

    # =========================================================================
    # Deep Inspection (AST-Based)
    # =========================================================================

    def inspect(self, paths: Optional[List[str]] = None) -> InspectionResult:
        """
        Run deep AST-based inspection.
        Slower (~500ms) but thorough.

        Args:
            paths: Paths to inspect (default: all system agents)

        Returns:
            InspectionResult with violations and analysis
        """
        ...

    def inspect_file(self, file_path: Path) -> List[Violation]:
        """
        Inspect a single file for violations.
        Uses AST parsing for accuracy.
        """
        ...

    # =========================================================================
    # Health Check (Infrastructure)
    # =========================================================================

    def check_health(self) -> HealthResult:
        """
        Check system infrastructure health.
        READ-ONLY - never modifies.
        """
        ...

    # =========================================================================
    # Violation Management
    # =========================================================================

    def get_violations(self, severity: Optional[ViolationSeverity] = None) -> List[Violation]:
        """Get recorded violations, optionally filtered by severity."""
        ...

    def record_violation(self, violation: Violation) -> bool:
        """Record a violation to ledger."""
        ...

    # =========================================================================
    # State
    # =========================================================================

    def get_state(self) -> WatchmanState:
        """Get current state. WATERTIGHT."""
        ...


# =============================================================================
# NULL WATCHMAN (For testing)
# =============================================================================


class NullWatchman(YamarajaProtocolBase):
    """
    Null implementation for testing.
    All clear, no violations.
    """

    @classmethod
    def position_index(cls) -> int:
        return 15

    def patrol(self) -> PatrolResult:
        return PatrolResult(
            status="clean",
            violations_found=0,
            agents_frozen=[],
            agents_thawed=[],
            violations=[],
        )

    def inspect(self, paths: Optional[List[str]] = None) -> InspectionResult:
        return InspectionResult(
            status="COMPLIANT",
            total_violations=0,
            critical_count=0,
            by_severity={},
            by_agent={},
            violations=[],
            healing_tasks_created=0,
            violations_recorded=0,
            should_fail_build=False,
        )

    def inspect_file(self, file_path: Path) -> List[Violation]:
        return []

    def check_health(self) -> HealthResult:
        return HealthResult(
            status="healthy",
            git_hooks_installed=True,
            hooks_valid=True,
            critical_files_present=True,
            recommendations=[],
        )

    def get_violations(self, severity: Optional[ViolationSeverity] = None) -> List[Violation]:
        return []

    def record_violation(self, violation: Violation) -> bool:
        return True

    def get_state(self) -> WatchmanState:
        return WatchmanState(
            protocol_name="watchman",
            owner="yamaraja",
            is_chanting=False,
            violations_detected=0,
            last_patrol="",
            last_inspection="",
            health="pristine",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ViolationSeverity",
    "ViolationPattern",
    # Types (WATERTIGHT)
    "Violation",
    "PatrolResult",
    "InspectionResult",
    "HealthResult",
    "WatchmanState",
    # Protocol
    "WatchmanProtocol",
    # Null Implementation
    "NullWatchman",
]
