from typing import Any, Dict

from vibe_core.protocols.identity import IdentityProtocol
from vibe_core.protocols.steward import StewardConfig, StewardProtocol


class DigitalSteward(StewardProtocol):
    """
    Active implementation of the Steward Protocol.

    The 'Digital Steward' is the enforcement agent that bridges
    Cryptographic Identity (Keys) with Human Intent (Config/Persona).

    It executes the 'Sign Off' logic to block operations that violate
    the Persona's constraints (Stambha).
    """

    def __init__(self, identity: IdentityProtocol, config: StewardConfig):
        self._identity = identity
        self._config = config

    @property
    def identity(self) -> IdentityProtocol:
        return self._identity

    @property
    def config(self) -> StewardConfig:
        return self._config

    def sign_off(self, operation: str, details: Dict[str, Any]) -> bool:
        """
        Active logic for Sovereign Interrupt.

        Evaluates:
        1. Behavior Rules (Anti-Slop, Require Tests)
        2. Prime Directive Alignment (Simple check for now)
        """
        # 0. The Prime Directive Check (Placeholder/Future expansion)
        # In a real agent, this would call an LLM. Here, we enforce static rules.

        # 1. Anti-Slop Mode
        # Config structure from Phoenix is nested: config.behavior.anti_slop_rules
        if self.config.behavior.anti_slop_rules:
            # Enforce that 'details' must be populated
            if not details:
                return False

        # 2. Test Requirements
        # If behavior.require_tests is True
        if self.config.behavior.require_tests and "deploy" in operation.lower():
            # Check context for test results (simulated)
            if not details.get("tests_passed", False):
                # Allow if explicitly overriden? No, Stambha is absolute.
                return False

        return True
