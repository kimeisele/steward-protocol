"""
PRAHLAD Types - TypedDicts, Protocols, and Dataclasses.

Extracted to reduce service.py below 800 lines.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol, TypedDict

# =============================================================================
# TypedDicts (Military Grade - No Any)
# =============================================================================


class ChaosProbeResult(TypedDict):
    """Type-safe result from chaos_probe_real()."""

    chaos_id: str
    target: str
    scenario: str
    detected: bool
    system_resilient: bool
    exception_raised: Optional[str]
    ledger_events: List[Dict[str, str]]


class ErrorContextData(TypedDict, total=False):
    """Context data for an error event."""

    chaos_scenario: str
    function_name: str
    stack_trace: str
    input_sample: str
    additional_info: str


class ReproductionContextData(TypedDict, total=False):
    """Context for reproducing an error."""

    error_type: str
    trigger_input: str
    expected_behavior: str
    actual_behavior: str


class PhoenixStateData(TypedDict, total=False):
    """State data for Phoenix tests."""

    component_id: str
    state_hash: str
    timestamp: str
    key_values: Dict[str, str]


class CoverageIntelligence(TypedDict, total=False):
    """Coverage intelligence report."""

    timestamp: str
    source: str
    total_testables: int
    total_tests: int
    by_type: Dict[str, int]
    tests_by_type: Dict[str, int]
    naga_coverage: Dict[str, object]
    prahlad_stats: Dict[str, int]
    error: str


class NagaCoverageData(TypedDict, total=False):
    """NAGA-specific coverage data."""

    testables_covered: int
    tests_available: int
    services: List[str]
    error: str


class ShuddhiHealResult(TypedDict, total=False):
    """Result from Shuddhi healing request."""

    healed: bool
    file_path: str
    rule_id: str
    dry_run: bool
    message: str
    changes: List[str]
    error: str


# =============================================================================
# Protocols
# =============================================================================


class LedgerLike(Protocol):
    """Protocol for ledger-like objects."""

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, str]) -> str: ...

    def get_recent_events(self, limit: int = 10) -> List[object]: ...


class ChaosTarget(Protocol):
    """Protocol for components that can be chaos-tested."""

    def handle(self, data: object) -> object: ...


class KernelLike(Protocol):
    """Protocol for kernel-like objects used in discovery."""

    @property
    def service_registry(self) -> object: ...


class RegistryLike(Protocol):
    """Protocol for testable registry."""

    @property
    def testables(self) -> List[object]: ...

    def discover_from_kernel(self, kernel: object) -> Dict[str, int]: ...

    def get_summary(self) -> Dict[str, object]: ...


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class ErrorEvent:
    """An error event to learn from."""

    error_type: str
    message: str
    component_id: str
    context: ErrorContextData
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestCase:
    """A generated test case from an error."""

    target_component: str
    error_type: str
    reproduction_context: ReproductionContextData
    test_code: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    generator_id: str = ""
    signature: Optional[bytes] = None

    def fingerprint(self) -> str:
        """Unique fingerprint for deduplication."""
        content = f"{self.target_component}:{self.error_type}:{self.reproduction_context}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ChaosScenario(str, Enum):
    """Chaos engineering scenarios."""

    NULL_INPUT = "null_input"
    TIMEOUT = "timeout"
    MALFORMED_DATA = "malformed_data"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_FAILURE = "network_failure"


@dataclass
class ProbeFailure:
    """A single failure during chaos probing."""

    scenario: str
    error_type: str
    message: str


@dataclass
class ProbeResult:
    """Result of a chaos probe."""

    target: str
    scenarios_tested: int = 0
    failures: int = 0
    failure_details: List[ProbeFailure] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DharmaScore:
    """Result of a Dharma audit."""

    total_score: float = 100.0
    unsigned_decisions: int = 0
    signature_compliance: float = 100.0
    ledger_intact: bool = True
    agents_without_identity: int = 0
    identity_coverage: float = 100.0
    timestamp: datetime = field(default_factory=datetime.now)
    auditor_id: str = ""
    signature: Optional[bytes] = None


@dataclass
class PhoenixResult:
    """Result of Phoenix guarantee verification."""

    target: str
    state_preserved: bool = True
    passed: bool = True
    state_before: Optional[PhoenixStateData] = None
    state_after: Optional[PhoenixStateData] = None
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # TypedDicts
    "ChaosProbeResult",
    "ErrorContextData",
    "ReproductionContextData",
    "PhoenixStateData",
    "CoverageIntelligence",
    "NagaCoverageData",
    "ShuddhiHealResult",
    # Protocols
    "LedgerLike",
    "ChaosTarget",
    "KernelLike",
    "RegistryLike",
    # Dataclasses
    "ErrorEvent",
    "TestCase",
    "ChaosScenario",
    "ProbeFailure",
    "ProbeResult",
    "DharmaScore",
    "PhoenixResult",
]
