"""
OPUS-311 Sprint 1: Integrity Check Protocol

The Lazy Loading House of Cards must fall.

Boot-time validation of all lazy loaders.
No more "works at boot, fails 3 hours later".

Usage:
    checker = IntegrityChecker()
    issues = checker.check_all()
    if issues:
        for issue in issues:
            logger.warning(f"🔥 {issue.component}: {issue.error}")
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable


class IssueSeverity(Enum):
    """Severity of integrity issue."""

    CRITICAL = "critical"  # System cannot function
    HIGH = "high"  # Feature broken
    MEDIUM = "medium"  # Degraded functionality
    LOW = "low"  # Cosmetic / warning


@dataclass
class IntegrityIssue:
    """A problem found during integrity check."""

    component: str  # e.g., "cartridge:archivist.audit"
    error: str  # The actual error message
    severity: IssueSeverity = IssueSeverity.HIGH
    exception: Optional[Exception] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.component}: {self.error}"


@dataclass
class IntegrityReport:
    """Result of full integrity check."""

    issues: List[IntegrityIssue] = field(default_factory=list)
    checked_count: int = 0
    passed_count: int = 0
    duration_ms: float = 0.0

    @property
    def failed_count(self) -> int:
        return len(self.issues)

    @property
    def success_rate(self) -> float:
        if self.checked_count == 0:
            return 1.0
        return self.passed_count / self.checked_count

    @property
    def has_critical(self) -> bool:
        return any(i.severity == IssueSeverity.CRITICAL for i in self.issues)

    def summary(self) -> str:
        """Human-readable summary."""
        status = "✅ PASS" if not self.issues else "❌ FAIL"
        return (
            f"{status} | "
            f"Checked: {self.checked_count} | "
            f"Passed: {self.passed_count} | "
            f"Failed: {self.failed_count} | "
            f"Duration: {self.duration_ms:.0f}ms"
        )


@runtime_checkable
class IntegrityCheckProtocol(Protocol):
    """
    OPUS-311: Boot-time integrity validation.

    Validates that all lazy-loaded components can actually load.
    Run this at boot to catch errors early.

    The Arjuna Pattern: If check fails, system can still boot
    with degraded functionality (Null fallbacks).
    """

    def check_all(self) -> IntegrityReport:
        """
        Check all registered components.

        Returns:
            IntegrityReport with all issues found
        """
        ...

    def check_component(self, name: str) -> Optional[IntegrityIssue]:
        """
        Check a specific component.

        Returns:
            IntegrityIssue if failed, None if passed
        """
        ...

    def register_checker(
        self,
        name: str,
        checker: Callable[[], None],
        severity: IssueSeverity = IssueSeverity.HIGH,
    ) -> None:
        """
        Register a component checker.

        The checker should raise an exception if the component fails.
        """
        ...

    def warm_cache(self) -> int:
        """
        Touch all lazy loaders to warm the cache.

        Returns:
            Number of components warmed
        """
        ...


class NullIntegrityChecker:
    """
    Arjuna Pattern: No-op implementation.

    Used when integrity checking is disabled.
    """

    def check_all(self) -> IntegrityReport:
        return IntegrityReport()

    def check_component(self, name: str) -> Optional[IntegrityIssue]:
        return None

    def register_checker(
        self,
        name: str,
        checker: Callable[[], None],
        severity: IssueSeverity = IssueSeverity.HIGH,
    ) -> None:
        pass

    def warm_cache(self) -> int:
        return 0


class IntegrityChecker:
    """
    OPUS-311: Real implementation of IntegrityCheckProtocol.

    Validates lazy loaders at boot time.
    """

    def __init__(self):
        self._checkers: Dict[str, tuple[Callable[[], None], IssueSeverity]] = {}

    def register_checker(
        self,
        name: str,
        checker: Callable[[], None],
        severity: IssueSeverity = IssueSeverity.HIGH,
    ) -> None:
        """Register a component checker."""
        self._checkers[name] = (checker, severity)

    def check_component(self, name: str) -> Optional[IntegrityIssue]:
        """Check a specific component."""
        if name not in self._checkers:
            return IntegrityIssue(
                component=name,
                error="Component not registered",
                severity=IssueSeverity.LOW,
            )

        checker, severity = self._checkers[name]
        try:
            checker()
            return None
        except Exception as e:
            return IntegrityIssue(
                component=name,
                error=str(e),
                severity=severity,
                exception=e,
            )

    def check_all(self) -> IntegrityReport:
        """Check all registered components."""
        import time

        start = time.time()
        issues: List[IntegrityIssue] = []
        passed = 0

        for name in self._checkers:
            issue = self.check_component(name)
            if issue:
                issues.append(issue)
            else:
                passed += 1

        duration = (time.time() - start) * 1000

        return IntegrityReport(
            issues=issues,
            checked_count=len(self._checkers),
            passed_count=passed,
            duration_ms=duration,
        )

    def warm_cache(self) -> int:
        """Touch all lazy loaders."""
        count = 0
        for name, (checker, _) in self._checkers.items():
            try:
                checker()
                count += 1
            except Exception:
                pass  # Ignore errors during warming
        return count

    def register_command_registry(self) -> None:
        """Register CommandRegistry checker."""

        def check():
            from vibe_core.cli.command_registry import CommandRegistry

            registry = CommandRegistry.get_instance()
            registry.scan_all()
            stats = registry.stats()
            if stats["total"] == 0:
                raise RuntimeError("No commands registered")

        self.register_checker("command_registry", check, IssueSeverity.CRITICAL)

    def register_cartridge_tools(self) -> None:
        """Register cartridge tools checker."""

        def check():
            from vibe_core.cartridge_service import CartridgeService

            service = CartridgeService.get_instance()
            # Just check it loads, don't load all tools
            if not service:
                raise RuntimeError("CartridgeService not available")

        self.register_checker("cartridge_service", check, IssueSeverity.HIGH)

    def register_cognitive(self) -> None:
        """Register cognitive layer checker."""

        def check():
            from vibe_core.protocols.cognition import OperatorCognitiveProtocol

            # This just checks the import works
            assert OperatorCognitiveProtocol is not None

        self.register_checker("cognitive_protocol", check, IssueSeverity.HIGH)

    def register_all_defaults(self) -> None:
        """Register all default checkers."""
        self.register_command_registry()
        self.register_cartridge_tools()
        self.register_cognitive()
