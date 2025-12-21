"""
VAJRA ARMOR: Immutable DNA Protection Mixin.

"The Diamond Thunderbolt that nothing can shatter."

This module provides the VajraGuarded mixin - a clean way to make
critical attributes immutable after initialization.

Architecture:
    1. Inherit from VajraGuarded
    2. Call protect_attribute("name") for critical fields
    3. Call vajra_seal() at end of __init__
    4. Any attempt to modify sealed attributes raises PermissionError

Usage:
    class MyKernel(VajraGuarded):
        def __init__(self):
            VajraGuarded.__init__(self)

            self._critical_factory = lambda: SomeClass()
            self.protect_attribute("_critical_factory")

            # ... rest of init ...

            self.vajra_seal()  # Lock it down

    # After seal():
    kernel._critical_factory = malicious_factory  # Raises PermissionError!

<!-- @HARNESS
files:
  - path: vibe_core/security.py
    required: true
wiring:
  - pattern: "class VajraGuarded"
    in: vibe_core/security.py
  - pattern: "vajra_seal"
    in: vibe_core/security.py
  - pattern: "VAJRA VIOLATION"
    in: vibe_core/security.py
tests:
  - tests/security/test_putana_poison.py
-->
"""

import logging
from typing import Set

logger = logging.getLogger("VAJRA")


class VajraGuarded:
    """
    Mixin that seals objects against attribute modification.

    Once vajra_seal() is called, protected attributes become immutable.
    Any attempt to modify them raises PermissionError.

    This is the kernel's "DNA protection" - blueprints and factories
    cannot be poisoned after initialization.
    """

    def __init__(self):
        """Initialize Vajra protection (unsealed by default)."""
        # These must be set via object.__setattr__ to avoid recursion
        object.__setattr__(self, "_vajra_sealed", False)
        object.__setattr__(self, "_vajra_protected", set())

    def protect_attribute(self, name: str) -> None:
        """
        Mark an attribute as part of the DNA (immutable after seal).

        Args:
            name: Attribute name to protect (e.g., "_ledger_blueprint")
        """
        self._vajra_protected.add(name)

    def vajra_seal(self) -> None:
        """
        Activate the Vajra seal.

        After this call, any attempt to modify protected attributes
        will raise PermissionError("VAJRA VIOLATION").
        """
        object.__setattr__(self, "_vajra_sealed", True)
        logger.info(
            f"💎 VAJRA SEAL: {self.__class__.__name__} DNA locked. "
            f"Protected: {self._vajra_protected}"
        )

    def vajra_unseal(self) -> None:
        """
        Temporarily unseal for legitimate modifications.

        WARNING: Use sparingly! This should only be used for
        controlled kernel upgrades or testing.
        """
        object.__setattr__(self, "_vajra_sealed", False)
        logger.warning(f"⚠️ VAJRA UNSEAL: {self.__class__.__name__} DNA unlocked!")

    def is_vajra_sealed(self) -> bool:
        """Check if the object is currently sealed."""
        return getattr(self, "_vajra_sealed", False)

    def get_protected_attributes(self) -> Set[str]:
        """Get the set of protected attribute names."""
        return getattr(self, "_vajra_protected", set()).copy()

    def __setattr__(self, name: str, value) -> None:
        """
        Intercept attribute setting to enforce Vajra protection.

        Raises:
            PermissionError: If attempting to modify a sealed, protected attribute.
        """
        # 1. Always allow setting Vajra control attributes
        if name in ("_vajra_sealed", "_vajra_protected"):
            object.__setattr__(self, name, value)
            return

        # 2. Check if seal is active
        if getattr(self, "_vajra_sealed", False):
            # 3. Check if attribute is protected
            protected = getattr(self, "_vajra_protected", set())
            if name in protected:
                logger.error(
                    f"🚫 VAJRA VIOLATION: Attempt to poison '{name}' "
                    f"on {self.__class__.__name__}!"
                )
                raise PermissionError(
                    f"VAJRA VIOLATION: Attempt to rewrite immutable DNA '{name}' "
                    f"on {self.__class__.__name__}. The blueprint is sealed."
                )

        # 4. Allowed - proceed with normal setattr
        object.__setattr__(self, name, value)


class VajraViolation(PermissionError):
    """
    Exception raised when attempting to modify sealed DNA.

    This is a subclass of PermissionError for compatibility,
    but can be caught specifically for Vajra violations.
    """

    pass
