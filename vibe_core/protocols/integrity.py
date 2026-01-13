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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x8748110e"  # GenesisByte: parampara % 37 == 0

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


# =============================================================================
# VISHNU KERNEL INTEGRITY (Security Ring 0)
# =============================================================================

# The Immutable Core - Changes here require "Main Branch" consensus.
SECURITY_RING_0 = [
    # Core Orchestration
    "vibe_core/kernel_impl.py",
    "vibe_core/kernel_ops.py",
    "vibe_core/ledger.py",
    # Plugin System
    "vibe_core/plugin_protocol.py",
    "vibe_core/plugin_loader.py",
    # Security (Sword, Shield, Gate)
    "vibe_core/narasimha.py",
    "vibe_core/capability_registry.py",
    "vibe_core/bridge.py",
    "vibe_core/security.py",
    # Protocol Foundation
    "vibe_core/protocols/substrate.py",
    "vibe_core/protocols/integrity.py",
    "CONSTITUTION.md",
    # Infrastructure - Workflows
    ".github/workflows/attest.yml",
    ".github/workflows/container-build.yml",
    ".github/workflows/deploy.yml",
    ".github/workflows/factory.yml",
    ".github/workflows/heartbeat.yml",
    ".github/workflows/integration-tests.yml",
    ".github/workflows/scheduled-agents.yml",
    ".github/workflows/scribe-docs.yml",
    ".github/workflows/steward-ci.yml",
    ".github/workflows/system-cycle.yml",
    # Infrastructure - Config
    ".pre-commit-config.yaml",
    ".gitignore",
    # Governance (The Watchers)
    "scripts/governance/vishnu_guard.py",
    "scripts/governance/kernel_hashes.json",
]

from typing import List, Protocol, runtime_checkable

from vibe_core.security import VajraGuarded


@runtime_checkable
class KernelIntegrityProtocol(Protocol):
    """
    Protocol for maintaining the Structural Integrity of the Kernel.

    "Vishnu 0 Protection" - The Kernel protects itself.
    """

    def verify_ring_0(self) -> bool:
        """Verify that all Ring 0 files match their canonical hashes."""
        ...

    def get_protected_files(self) -> List[str]:
        """Return the list of files in Security Ring 0."""
        ...

    def restore_kernel(self) -> List[str]:
        """Force-restore the Kernel to its canonical state."""
        ...


class VishnuIntegrityGuardian(VajraGuarded):
    """
    Implementation of KernelIntegrityProtocol.

    "The Nuclear Option" - Restores truth from origin/main.
    Protected by VajraGuarded to prevent list poisoning.
    """

    def __init__(self):
        VajraGuarded.__init__(self)
        self._security_ring_0 = SECURITY_RING_0
        self.protect_attribute("_security_ring_0")
        self.vajra_seal()

    def verify_ring_0(self) -> bool:
        """
        Check if any Ring 0 file differs from its Immutable Hash.

        New Architecture (GAD-000 Watertight):
        - Instead of checking git diff origin/main (which relies on network/git),
        - We check the SHA256 of the file content against vibe_core.governance.keys.VAJRA_KEYS.
        - This ensures integrity even in dirty/detached states.
        """
        import hashlib
        from pathlib import Path

        from vibe_core.governance.keys import VAJRA_KEYS

        all_intact = True

        # We check files defined in the Registry, not just the list
        for file_path, expected_hash in VAJRA_KEYS.items():
            try:
                p = Path(file_path)
                if not p.exists():
                    # Missing file is a corruption
                    pass  # TODO: Log missing
                    all_intact = False
                    continue

                with open(p, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()

                if file_hash != expected_hash:
                    # HASH MISMATCH
                    all_intact = False
                    # We could log here, but this method just returns bool

            except Exception:
                all_intact = False

        return all_intact

    def get_protected_files(self) -> List[str]:
        from vibe_core.governance.keys import VAJRA_KEYS

        return list(VAJRA_KEYS.keys())

    def restore_kernel(self) -> List[str]:
        """NUCLEAR RESET: Overwrites local changes with origin/main version."""
        import subprocess

        restored = []
        try:
            subprocess.run(["git", "fetch", "origin", "main", "--depth=1"], check=False, capture_output=True)
            for file in self._security_ring_0:
                diff_check = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", file], check=False)
                if diff_check.returncode != 0:
                    subprocess.run(["git", "checkout", "origin/main", "--", file], check=True)
                    subprocess.run(["git", "add", file], check=True)
                    restored.append(file)
            return restored
        except Exception as e:
            raise RuntimeError(f"VISHNU FAILURE: Could not restore kernel integrity: {e}")
