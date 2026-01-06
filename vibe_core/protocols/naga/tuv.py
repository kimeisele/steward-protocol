"""
TÜV Protocol - NAGA Type Audit Intelligence.

"Der TÜV prüft nicht nur OB etwas funktioniert, sondern OB es RICHTIG gebaut ist."

This protocol defines the interface for type system auditing:
- Leakage detection (Any types where shouldn't be)
- Protocol/Implementation alignment verification
- Antidote tracking (pending fixes)
- Churning log (value creation)

NOT documentation - CODE that can be queried and acted upon.

SCALING PATTERN:
- Add new field to dataclass → ONE change, auto-serialized
- from_dict() handles enum/datetime conversion
- Generic FindingRegistry handles storage/filtering (PROTOCOL-FIRST naming)
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Generic, List, Optional, Protocol, Type, TypedDict, TypeVar, runtime_checkable

# =============================================================================
# ENUMS
# =============================================================================


class LeakSeverity(str, Enum):
    """Severity of a type leak."""

    CRITICAL = "critical"  # Runtime safety issue
    HIGH = "high"  # Protocol boundary leak
    MEDIUM = "medium"  # Protocol layer Dict[str, Any]
    LOW = "low"  # Internal/acceptable
    INTENTIONAL = "intentional"  # Decorator *args/**kwargs


class LeakStatus(str, Enum):
    """Status of a registered leak."""

    OPEN = "open"  # Needs antidote
    WORKAROUND = "workaround"  # Acceptable workaround in place
    HEALING = "healing"  # Antidote in progress
    HEALED = "healed"  # Fixed


class LeakPattern(str, Enum):
    """Common leak patterns."""

    ANY_PARAM = "any_param"  # def foo(x: Any)
    ANY_RETURN = "any_return"  # def foo() -> Any
    DICT_STR_ANY = "dict_str_any"  # Dict[str, Any]
    LIST_ANY = "list_any"  # List[Any]
    OPTIONAL_ANY = "optional_any"  # Optional[Any]
    SIGNATURE_MISMATCH = "signature_mismatch"  # Protocol != Implementation
    MISSING_METHOD = "missing_method"  # Protocol method not implemented
    CIRCULAR_DEP = "circular_dep"  # Type in wrong layer


class ProtocolGapSeverity(str, Enum):
    """Severity of a protocol gap."""

    CRITICAL = "critical"  # Namesake missing (StewardProtocol!)
    HIGH = "high"  # Multiple scattered implementations, no protocol
    MEDIUM = "medium"  # Single impl without protocol
    LOW = "low"  # Nice-to-have protocol


class ProtocolGapStatus(str, Enum):
    """Status of a protocol gap."""

    IDENTIFIED = "identified"  # Gap found
    PLANNED = "planned"  # In battle plan
    IN_PROGRESS = "in_progress"  # Being implemented
    CLOSED = "closed"  # Protocol created


# =============================================================================
# TYPEDDICTS (Serialized Forms - NO Any!)
# =============================================================================


class LeakDict(TypedDict, total=False):
    """Serialized form of Leak - for JSON storage."""

    id: str
    location: str
    pattern: str
    severity: str
    status: str
    description: str
    antidote: str
    detected_at: str
    healed_at: str


class ProtocolGapDict(TypedDict, total=False):
    """Serialized form of ProtocolGap - for JSON storage."""

    id: str
    name: str
    severity: str
    status: str
    description: str
    existing_implementations: List[str]
    suggested_location: str
    detected_at: str
    closed_at: str


# =============================================================================
# FINDABLE PROTOCOL (For Generic Registry)
# =============================================================================


class FindableProtocol(Protocol):
    """Protocol for items that can be stored in FindingRegistry."""

    id: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "FindableProtocol":
        """Deserialize from dict."""
        ...


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class Leak:
    """A registered type system leak."""

    id: str  # LEAK-001, LEAK-002, etc.
    location: str  # file:line
    pattern: LeakPattern
    severity: LeakSeverity
    status: LeakStatus
    description: str
    antidote: str  # Proposed fix
    detected_at: datetime = field(default_factory=datetime.now)
    healed_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: LeakDict) -> "Leak":
        """Deserialize from dict - handles enum/datetime conversion."""
        return cls(
            id=data["id"],
            location=data["location"],
            pattern=LeakPattern(data["pattern"]),
            severity=LeakSeverity(data["severity"]),
            status=LeakStatus(data["status"]),
            description=data["description"],
            antidote=data["antidote"],
            detected_at=datetime.fromisoformat(data["detected_at"]) if data.get("detected_at") else datetime.now(),
            healed_at=datetime.fromisoformat(data["healed_at"]) if data.get("healed_at") else None,
        )


@dataclass
class ProtocolGap:
    """A protocol that SHOULD exist but doesn't."""

    id: str  # GAP-001, GAP-002, etc.
    name: str  # StewardProtocol, IdentityProtocol
    severity: ProtocolGapSeverity
    status: ProtocolGapStatus
    description: str
    existing_implementations: List[str]  # Classes that SHOULD use this protocol
    suggested_location: str  # Where protocol should live
    detected_at: datetime = field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: ProtocolGapDict) -> "ProtocolGap":
        """Deserialize from dict - handles enum/datetime conversion."""
        impls = data.get("existing_implementations", [])
        if isinstance(impls, str):
            impls = impls.split(",") if impls else []
        return cls(
            id=data["id"],
            name=data["name"],
            severity=ProtocolGapSeverity(data["severity"]),
            status=ProtocolGapStatus(data["status"]),
            description=data["description"],
            existing_implementations=impls,
            suggested_location=data["suggested_location"],
            detected_at=datetime.fromisoformat(data["detected_at"]) if data.get("detected_at") else datetime.now(),
            closed_at=datetime.fromisoformat(data["closed_at"]) if data.get("closed_at") else None,
        )


@dataclass
class ProtocolAudit:
    """Result of auditing a protocol against its implementation."""

    protocol_name: str
    service_name: str
    passed: bool
    mismatches: List[str] = field(default_factory=list)
    missing_methods: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChurnEntry:
    """Record of value creation (Gift → Nektar)."""

    date: str
    target: str
    gift: str  # Before state
    nektar: str  # After state
    churn_type: str  # "fix", "refactor", "intelligence"


@dataclass
class ProtocolCoverageReport:
    """Protocol coverage analysis report."""

    timestamp: datetime
    protocols_found: int
    gaps_total: int
    gaps_critical: int
    gaps_high: int
    coverage_percent: float  # protocols_found / (protocols_found + gaps)
    gaps: List[ProtocolGap]


@dataclass
class TÜVReport:
    """Full TÜV audit report."""

    timestamp: datetime
    protocols_checked: int
    protocols_passed: int
    leaks_total: int
    leaks_open: int
    leaks_healed: int
    leaks: List[Leak]
    audits: List[ProtocolAudit]
    churns: List[ChurnEntry]
    # Protocol coverage (NEW)
    coverage: Optional[ProtocolCoverageReport] = None


# =============================================================================
# GENERIC REGISTRY (Protocol-First: FindingRegistry)
# =============================================================================


# TypedDict for serialized findings - JSON storage format
class SerializedFinding(TypedDict, total=False):
    """Generic serialized finding - all fields become strings in JSON."""

    id: str
    # All other fields are string-serialized (enums as values, datetimes as isoformat)


# Type variable bound to FindableProtocol
F = TypeVar("F", bound="FindableProtocol")


class FindingRegistry(Generic[F]):
    """
    Generic registry for audit findings (Leaks, Gaps, etc.).

    PROTOCOL-FIRST: Not TÜV-specific, usable by any NAGA auditor.

    SCALING PATTERN:
    - Add field to dataclass → auto-serialized via asdict()
    - from_dict() handles deserialization
    - filter() works on any field without code changes

    Usage:
        leaks: FindingRegistry[Leak] = FindingRegistry(Leak, "LEAK")
        gaps: FindingRegistry[ProtocolGap] = FindingRegistry(ProtocolGap, "GAP")
    """

    def __init__(self, item_cls: Type[F], id_prefix: str):
        self._item_cls = item_cls
        self._id_prefix = id_prefix
        self._items: Dict[str, F] = {}
        self._next_id = 1

    def register(self, item: F) -> str:
        """Register an item. Auto-assigns ID if empty."""
        item_id = getattr(item, "id", "")
        if not item_id:
            item_id = f"{self._id_prefix}-{self._next_id:03d}"
            object.__setattr__(item, "id", item_id)  # Set on dataclass
            self._next_id += 1
        self._items[item_id] = item
        return item_id

    def get(self, item_id: str) -> Optional[F]:
        """Get item by ID."""
        return self._items.get(item_id)

    def all(self) -> List[F]:
        """Get all items."""
        return list(self._items.values())

    def filter(self, **kwargs: object) -> List[F]:
        """
        Filter items by field values.

        Example: filter(status=LeakStatus.OPEN, severity=LeakSeverity.HIGH)

        Generic filtering - no code changes needed for new fields.
        """
        result = list(self._items.values())
        for field_name, value in kwargs.items():
            if value is not None:
                result = [i for i in result if getattr(i, field_name, None) == value]
        return result

    def count(self, **kwargs: object) -> int:
        """Count items matching filter."""
        return len(self.filter(**kwargs))

    def to_list(self) -> List[SerializedFinding]:
        """Serialize all items for JSON storage. Uses asdict() - auto-scales!"""
        result: List[SerializedFinding] = []
        for item in self._items.values():
            d = asdict(item)
            # Convert enums to values, datetimes to isoformat
            for k, v in list(d.items()):
                if isinstance(v, Enum):
                    d[k] = v.value
                elif isinstance(v, datetime):
                    d[k] = v.isoformat()
            result.append(d)  # type: ignore[arg-type]
        return result

    def load_list(self, data: List[SerializedFinding]) -> None:
        """Load items from list. Uses from_dict() classmethod."""
        self._items.clear()
        for d in data:
            item = self._item_cls.from_dict(d)  # type: ignore[arg-type]
            item_id = getattr(item, "id", "")
            self._items[item_id] = item
        # Update next_id
        if self._items:
            max_id = max(int(k.split("-")[1]) for k in self._items.keys() if "-" in k)
            self._next_id = max_id + 1

    @property
    def next_id(self) -> int:
        """Current next ID."""
        return self._next_id

    @next_id.setter
    def next_id(self, value: int) -> None:
        """Set next ID (for loading from disk)."""
        self._next_id = value


# Backward compat alias
TÜVRegistry = FindingRegistry


# =============================================================================
# PROTOCOL
# =============================================================================


@runtime_checkable
class TÜVProtocol(Protocol):
    """
    TÜV Audit Intelligence Protocol.

    The NAGA type system auditor - not documentation, CODE.
    """

    # =========================================================================
    # Leak Registry
    # =========================================================================

    def register_leak(self, leak: Leak) -> str:
        """Register a new leak. Returns leak ID."""
        ...

    def get_leak(self, leak_id: str) -> Optional[Leak]:
        """Get leak by ID."""
        ...

    def get_leaks(
        self,
        status: Optional[LeakStatus] = None,
        severity: Optional[LeakSeverity] = None,
        pattern: Optional[LeakPattern] = None,
    ) -> List[Leak]:
        """Query leaks with optional filters."""
        ...

    def heal_leak(self, leak_id: str, commit_hash: str = "") -> bool:
        """Mark a leak as healed."""
        ...

    # =========================================================================
    # Scanning
    # =========================================================================

    def scan_file(self, filepath: str) -> List[Leak]:
        """Scan a file for type leaks."""
        ...

    def scan_module(self, module_path: str) -> List[Leak]:
        """Scan a module for type leaks."""
        ...

    def audit_protocol(self, protocol_name: str, service_name: str) -> ProtocolAudit:
        """Audit a protocol against its implementation."""
        ...

    # =========================================================================
    # Protocol Coverage (REPRODUCIBLE INTELLIGENCE)
    # =========================================================================

    def scan_protocol_coverage(self, base_path: str = "vibe_core") -> ProtocolCoverageReport:
        """
        Scan codebase for protocol gaps.

        This is REPRODUCIBLE intelligence gathering:
        - Finds all Protocol classes
        - Finds all implementations (services, etc.)
        - Identifies implementations WITHOUT protocols
        - Detects scattered implementations (same pattern, no unified protocol)
        """
        ...

    def register_gap(self, gap: ProtocolGap) -> str:
        """Register a protocol gap. Returns gap ID."""
        ...

    def get_gap(self, gap_id: str) -> Optional[ProtocolGap]:
        """Get gap by ID."""
        ...

    def get_gaps(
        self,
        status: Optional[ProtocolGapStatus] = None,
        severity: Optional[ProtocolGapSeverity] = None,
    ) -> List[ProtocolGap]:
        """Query gaps with optional filters."""
        ...

    def close_gap(self, gap_id: str, protocol_location: str = "") -> bool:
        """Mark a gap as closed (protocol created)."""
        ...

    # =========================================================================
    # Reporting
    # =========================================================================

    def get_report(self) -> TÜVReport:
        """Get full TÜV report."""
        ...

    def record_churn(self, entry: ChurnEntry) -> None:
        """Record a churning (value creation)."""
        ...

    # =========================================================================
    # Summary
    # =========================================================================

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts."""
        ...


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================


class NullTÜV:
    """No-op TÜV when audit intelligence is unavailable."""

    def register_leak(self, leak: Leak) -> str:
        return ""

    def get_leak(self, leak_id: str) -> Optional[Leak]:
        return None

    def get_leaks(
        self,
        status: Optional[LeakStatus] = None,
        severity: Optional[LeakSeverity] = None,
        pattern: Optional[LeakPattern] = None,
    ) -> List[Leak]:
        return []

    def heal_leak(self, leak_id: str, commit_hash: str = "") -> bool:
        return False

    def scan_file(self, filepath: str) -> List[Leak]:
        return []

    def scan_module(self, module_path: str) -> List[Leak]:
        return []

    def audit_protocol(self, protocol_name: str, service_name: str) -> ProtocolAudit:
        return ProtocolAudit(
            protocol_name=protocol_name,
            service_name=service_name,
            passed=False,
            mismatches=["TÜV not available"],
        )

    # Protocol coverage (no-op)
    def scan_protocol_coverage(self, base_path: str = "vibe_core") -> ProtocolCoverageReport:
        return ProtocolCoverageReport(
            timestamp=datetime.now(),
            protocols_found=0,
            gaps_total=0,
            gaps_critical=0,
            gaps_high=0,
            coverage_percent=0.0,
            gaps=[],
        )

    def register_gap(self, gap: ProtocolGap) -> str:
        return ""

    def get_gap(self, gap_id: str) -> Optional[ProtocolGap]:
        return None

    def get_gaps(
        self,
        status: Optional[ProtocolGapStatus] = None,
        severity: Optional[ProtocolGapSeverity] = None,
    ) -> List[ProtocolGap]:
        return []

    def close_gap(self, gap_id: str, protocol_location: str = "") -> bool:
        return False

    def get_report(self) -> TÜVReport:
        return TÜVReport(
            timestamp=datetime.now(),
            protocols_checked=0,
            protocols_passed=0,
            leaks_total=0,
            leaks_open=0,
            leaks_healed=0,
            leaks=[],
            audits=[],
            churns=[],
        )

    def record_churn(self, entry: ChurnEntry) -> None:
        pass

    def get_summary(self) -> Dict[str, int]:
        return {"protocols": 0, "leaks_open": 0, "leaks_healed": 0}
