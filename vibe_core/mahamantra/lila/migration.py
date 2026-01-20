"""
MIGRATION - Legacy Service Protocols (Der Vertrag)
==================================================

"dharma eva hato hanti dharmo rakṣati rakṣitaḥ"
"Dharma, when destroyed, destroys; Dharma, when protected, protects."
— Manu Smriti

KEIN MONKEY PATCHING. KEIN ANY. NUR EXPLIZITE VERTRÄGE.

GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
Mayavad: CLEAR (Migration through explicit protocols, not magic)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x263ac482"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable


# =============================================================================
# BASE LEGACY SERVICE PROTOCOL
# =============================================================================


@runtime_checkable
class LegacyServiceProtocol(Protocol):
    """
    Der Vertrag, den jeder Legacy-Service erfüllen muss.

    KEINE SILENT FAILURES. KEINE ANY TYPES.

    Wenn ein Service dieses Protokoll nicht erfüllt,
    wird die Migration mit TypeError abgelehnt.
    """

    def start(self) -> None:
        """
        Start the service.

        Raises:
            RuntimeError: If service fails to start
        """
        ...

    def stop(self) -> None:
        """
        Stop the service gracefully.

        Raises:
            RuntimeError: If service fails to stop
        """
        ...


# =============================================================================
# SPECIFIC SERVICE PROTOCOLS (Position-Based)
# =============================================================================


@runtime_checkable
class BrahmaServiceProtocol(LegacyServiceProtocol, Protocol):
    """
    Protocol for BrahmaService (Position 1: LOAD_ROOT).

    Brahma erschafft. Explizite Methoden, keine Magie.
    """

    def register_agent(self, kernel: object, agent: object, spawn_process: bool = True) -> None:
        """
        Register an agent with the kernel.

        Args:
            kernel: The kernel instance
            agent: The agent to register
            spawn_process: Whether to spawn in separate process

        Raises:
            ValueError: If agent is invalid
            RuntimeError: If registration fails
        """
        ...

    def check_genesis_status(self) -> dict[str, object]:
        """
        Check the genesis status.

        Returns:
            Status dict with keys:
            - ready: bool
            - errors: list[str]
            - agents_count: int

        Raises:
            RuntimeError: If status check fails
        """
        ...


@runtime_checkable
class LifecycleServiceProtocol(LegacyServiceProtocol, Protocol):
    """
    Protocol for LifecycleService (Position 10: STATE_SYNC).

    Janaka erhält. Duty and maintenance.
    """

    def boot(self, boot_mode: str = "FULL") -> None:
        """
        Boot the system.

        Args:
            boot_mode: One of "FULL", "HEADLESS", "MINIMAL"

        Raises:
            ValueError: If boot_mode invalid
            RuntimeError: If boot fails
        """
        ...

    def shutdown(self) -> None:
        """
        Shutdown the system gracefully.

        Raises:
            RuntimeError: If shutdown fails
        """
        ...

    def maintenance_check(self) -> dict[str, object]:
        """
        Perform periodic maintenance check.

        Returns:
            Status dict with keys:
            - healthy: bool
            - warnings: list[str]
            - errors: list[str]

        Raises:
            RuntimeError: If check fails
        """
        ...


@runtime_checkable
class ManifestationServiceProtocol(LegacyServiceProtocol, Protocol):
    """
    Protocol for ManifestationService (Position 14: LOG_EMIT).

    Shuka sees and narrates. Vision and rendering.
    """

    def render_file(self, content: str, path: str) -> bool:
        """
        Render markdown content to file.

        Args:
            content: The markdown content
            path: Target file path

        Returns:
            True if rendering successful

        Raises:
            ValueError: If content or path invalid
            RuntimeError: If rendering fails
        """
        ...

    def check_manifest_health(self) -> dict[str, object]:
        """
        Check manifestation system health.

        Returns:
            Status dict with keys:
            - schemas_loaded: int
            - cache_size: int
            - errors: list[str]

        Raises:
            RuntimeError: If health check fails
        """
        ...


# =============================================================================
# PROTOCOL VERIFICATION
# =============================================================================


def verify_brahma_protocol(service: object) -> bool:
    """
    Verify if service implements BrahmaServiceProtocol.

    Args:
        service: The service instance to verify

    Returns:
        True if service implements protocol

    Note:
        Uses runtime_checkable Protocol, not isinstance magic
    """
    return isinstance(service, BrahmaServiceProtocol)


def verify_lifecycle_protocol(service: object) -> bool:
    """Verify if service implements LifecycleServiceProtocol."""
    return isinstance(service, LifecycleServiceProtocol)


def verify_manifestation_protocol(service: object) -> bool:
    """Verify if service implements ManifestationServiceProtocol."""
    return isinstance(service, ManifestationServiceProtocol)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "LegacyServiceProtocol",
    "BrahmaServiceProtocol",
    "LifecycleServiceProtocol",
    "ManifestationServiceProtocol",
    "verify_brahma_protocol",
    "verify_lifecycle_protocol",
    "verify_manifestation_protocol",
]
