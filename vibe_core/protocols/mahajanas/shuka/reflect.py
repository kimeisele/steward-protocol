"""
REFLECT - System Introspection Protocol
=======================================

OWNER: SHUKA (Shukadeva Goswami)
POSITION: 14 (MOKSHA Quarter)
OPCODE: CACHE_STATE

Shuka sees past, present, and future. Born liberated.
This is system introspection: seeing the system's own state.

SHASTRA BASIS:
    Shukadeva Goswami was born fully realized.
    He could see everything - past, present, future.
    He spoke Srimad Bhagavatam to King Parikshit.

    "The parrot (shuka) repeats exactly what it hears."

    In code:
    - Reflect = See system state
    - Introspect = Examine capabilities
    - Discover = Find available services

REFLECTION TYPES:
    - HEALTH: System health check
    - CAPABILITY: Available capabilities
    - DEPENDENCY: Dependency graph
    - METRICS: Performance metrics

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Protocol, Set, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.shuka import (
    CachedValue,
    ReflectionResult,
)


# =============================================================================
# OWNERSHIP DECLARATION
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.SHUKA
LOTUS_POSITION: Final[int] = 14
LOTUS_QUARTER: Final[str] = "moksha"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.YIELD_CPU,  # CACHE_STATE
]


# =============================================================================
# HEALTH STATUS
# =============================================================================

class HealthStatus(str, Enum):
    """System health status."""
    PRISTINE = "pristine"     # Perfect health
    HEALTHY = "healthy"       # Normal operation
    DEGRADED = "degraded"     # Some issues
    CRITICAL = "critical"     # Major issues
    UNKNOWN = "unknown"       # Cannot determine


# =============================================================================
# REFLECTION TYPES
# =============================================================================

@dataclass(frozen=True)
class HealthCheck:
    """Result of a health check."""
    component: str
    status: HealthStatus
    message: str
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass(frozen=True)
class Capability:
    """A system capability."""
    name: str
    owner: str  # Mahajana name
    available: bool
    description: str


@dataclass(frozen=True)
class Dependency:
    """A dependency between components."""
    source: str
    target: str
    dependency_type: str  # "requires", "uses", "optional"


@dataclass
class SystemMetrics:
    """System performance metrics."""
    uptime_seconds: float = 0.0
    memory_used_bytes: int = 0
    active_tasks: int = 0
    completed_tasks: int = 0
    error_count: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SystemSnapshot:
    """Complete system snapshot."""
    timestamp: str
    health_status: HealthStatus
    health_checks: List[HealthCheck]
    capabilities: List[Capability]
    dependencies: List[Dependency]
    metrics: SystemMetrics


# =============================================================================
# REFLECT PROTOCOL
# =============================================================================

HealthChecker = Callable[[], HealthCheck]


@runtime_checkable
class ReflectProtocol(Protocol):
    """
    The System Introspection Protocol - Shuka's Vision.

    OWNER: Mahajana.SHUKA

    Like Shuka who sees all, this protocol provides
    complete visibility into the system.
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.SHUKA."""
        ...

    # Health
    def register_health_check(self, name: str, checker: HealthChecker) -> bool:
        """Register a health check."""
        ...

    def check_health(self, component: Optional[str] = None) -> List[HealthCheck]:
        """Run health checks."""
        ...

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health."""
        ...

    # Capabilities
    def register_capability(self, capability: Capability) -> bool:
        """Register a capability."""
        ...

    def list_capabilities(self, owner: Optional[str] = None) -> List[Capability]:
        """List capabilities."""
        ...

    def has_capability(self, name: str) -> bool:
        """Check if capability exists."""
        ...

    # Dependencies
    def register_dependency(self, dependency: Dependency) -> bool:
        """Register a dependency."""
        ...

    def get_dependencies(self, component: str) -> List[Dependency]:
        """Get dependencies for a component."""
        ...

    # Snapshot
    def take_snapshot(self) -> SystemSnapshot:
        """Take a complete system snapshot."""
        ...


# =============================================================================
# REFLECTOR IMPLEMENTATION
# =============================================================================

class Reflector:
    """
    Shuka's Reflector - System Introspection.

    OWNER: Mahajana.SHUKA

    Features:
    - Health checking
    - Capability discovery
    - Dependency tracking
    - System snapshots
    """

    def __init__(self) -> None:
        """Initialize reflector."""
        self._health_checks: Dict[str, HealthChecker] = {}
        self._capabilities: Dict[str, Capability] = {}
        self._dependencies: List[Dependency] = []
        self._metrics = SystemMetrics()
        self._start_time = datetime.now()

    @property
    def owner(self) -> Mahajana:
        return Mahajana.SHUKA

    def register_health_check(self, name: str, checker: HealthChecker) -> bool:
        """Register a health check."""
        if name in self._health_checks:
            return False
        self._health_checks[name] = checker
        return True

    def check_health(self, component: Optional[str] = None) -> List[HealthCheck]:
        """Run health checks."""
        results: List[HealthCheck] = []

        if component:
            checker = self._health_checks.get(component)
            if checker:
                try:
                    results.append(checker())
                except Exception as e:
                    results.append(HealthCheck(
                        component=component,
                        status=HealthStatus.UNKNOWN,
                        message=f"Check failed: {e}",
                    ))
        else:
            for name, checker in self._health_checks.items():
                try:
                    results.append(checker())
                except Exception as e:
                    results.append(HealthCheck(
                        component=name,
                        status=HealthStatus.UNKNOWN,
                        message=f"Check failed: {e}",
                    ))

        return results

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health."""
        checks = self.check_health()
        if not checks:
            return HealthStatus.UNKNOWN

        # Worst status wins
        statuses = [c.status for c in checks]
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        if HealthStatus.UNKNOWN in statuses:
            return HealthStatus.HEALTHY  # Unknown is not critical
        if all(s == HealthStatus.PRISTINE for s in statuses):
            return HealthStatus.PRISTINE
        return HealthStatus.HEALTHY

    def register_capability(self, capability: Capability) -> bool:
        """Register a capability."""
        self._capabilities[capability.name] = capability
        return True

    def list_capabilities(self, owner: Optional[str] = None) -> List[Capability]:
        """List capabilities."""
        caps = list(self._capabilities.values())
        if owner:
            caps = [c for c in caps if c.owner == owner]
        return caps

    def has_capability(self, name: str) -> bool:
        """Check if capability exists and is available."""
        cap = self._capabilities.get(name)
        return cap is not None and cap.available

    def register_dependency(self, dependency: Dependency) -> bool:
        """Register a dependency."""
        self._dependencies.append(dependency)
        return True

    def get_dependencies(self, component: str) -> List[Dependency]:
        """Get dependencies for a component."""
        return [d for d in self._dependencies if d.source == component]

    def get_dependents(self, component: str) -> List[Dependency]:
        """Get components that depend on this one."""
        return [d for d in self._dependencies if d.target == component]

    def take_snapshot(self) -> SystemSnapshot:
        """Take a complete system snapshot."""
        self._metrics.uptime_seconds = (datetime.now() - self._start_time).total_seconds()
        self._metrics.last_updated = datetime.now().isoformat()

        return SystemSnapshot(
            timestamp=datetime.now().isoformat(),
            health_status=self.get_overall_health(),
            health_checks=self.check_health(),
            capabilities=list(self._capabilities.values()),
            dependencies=self._dependencies.copy(),
            metrics=SystemMetrics(
                uptime_seconds=self._metrics.uptime_seconds,
                memory_used_bytes=self._metrics.memory_used_bytes,
                active_tasks=self._metrics.active_tasks,
                completed_tasks=self._metrics.completed_tasks,
                error_count=self._metrics.error_count,
                last_updated=self._metrics.last_updated,
            ),
        )

    def update_metrics(
        self,
        memory_used: Optional[int] = None,
        active_tasks: Optional[int] = None,
        completed_tasks: Optional[int] = None,
        error_count: Optional[int] = None,
    ) -> None:
        """Update system metrics."""
        if memory_used is not None:
            self._metrics.memory_used_bytes = memory_used
        if active_tasks is not None:
            self._metrics.active_tasks = active_tasks
        if completed_tasks is not None:
            self._metrics.completed_tasks = completed_tasks
        if error_count is not None:
            self._metrics.error_count = error_count
        self._metrics.last_updated = datetime.now().isoformat()


# =============================================================================
# NULL REFLECTOR
# =============================================================================

class NullReflector:
    """Null reflector - minimal introspection."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.SHUKA

    def register_health_check(self, name: str, checker: HealthChecker) -> bool:
        return True

    def check_health(self, component: Optional[str] = None) -> List[HealthCheck]:
        return [HealthCheck(component="system", status=HealthStatus.PRISTINE, message="NullReflector")]

    def get_overall_health(self) -> HealthStatus:
        return HealthStatus.PRISTINE

    def register_capability(self, capability: Capability) -> bool:
        return True

    def list_capabilities(self, owner: Optional[str] = None) -> List[Capability]:
        return []

    def has_capability(self, name: str) -> bool:
        return True

    def register_dependency(self, dependency: Dependency) -> bool:
        return True

    def get_dependencies(self, component: str) -> List[Dependency]:
        return []

    def take_snapshot(self) -> SystemSnapshot:
        return SystemSnapshot(
            timestamp=datetime.now().isoformat(),
            health_status=HealthStatus.PRISTINE,
            health_checks=[],
            capabilities=[],
            dependencies=[],
            metrics=SystemMetrics(),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OWNER", "LOTUS_POSITION", "LOTUS_QUARTER", "OWNED_OPCODES",
    "HealthStatus", "HealthCheck", "Capability", "Dependency",
    "SystemMetrics", "SystemSnapshot", "HealthChecker",
    "ReflectProtocol", "Reflector", "NullReflector",
]
