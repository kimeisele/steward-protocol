# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"
__position__ = 14
__genesis__ = "0x0d97ae20"  # GenesisByte: parampara % 37 == 0

from typing import Any, Protocol, runtime_checkable

from .identity import IdentityProtocol


@runtime_checkable
class StewardConfig(Protocol):
    """
    Protocol for the Steward's Persona Configuration.
    Maps to Phoenix UserPreferences/BehaviorConfig side-by-side.
    """

    @property
    def role(self) -> str: ...

    @property
    def prime_directive(self) -> str: ...

    # Behavior Constraints (BehaviorConfig)
    @property
    def require_tests(self) -> bool: ...

    @property
    def anti_slop_mode(self) -> bool: ...


@runtime_checkable
class StewardProtocol(Protocol):
    """
    GAD-000 37th Principle: The Sovereign Observer.

    The Steward wraps the cryptographic Identity with a Persona (Config)
    and provides the 'Stambha' (Interrupt) capability.
    """

    @property
    def identity(self) -> IdentityProtocol:
        """The cryptographic proof (The Keys)."""
        ...

    @property
    def config(self) -> StewardConfig:
        """The psychological context (The Persona)."""
        ...

    def sign_off(self, operation: str, details: dict[str, Any]) -> bool:
        """
        THE SOVEREIGN INTERRUPT (Stambha).

        Determines if an operation aligns with the Persona's Dharma.
        Returns False if the operation violates the Prime Directive or constraints.

        Args:
            operation: Name of the operation (e.g., 'git_commit')
            details: Context arguments and state (args, kwargs, service, capability)
        """
        ...

    def check_limits(self, operation: str) -> bool:
        """
        FAST PATH for Internal Calls (Garuda Flying).

        Checks only budget/rate limits, NOT full intent validation.
        Used when Garuda is flying (internal NAGA-to-NAGA calls).

        Args:
            operation: Name of the operation

        Returns:
            True if within limits, False if budget/rate exceeded.
        """
        ...
