from typing import Any, Dict

from vibe_core.protocols.identity import IdentityProtocol
from vibe_core.protocols.steward import StewardConfig, StewardProtocol


class EmergencyConfig:
    """Stiff/Dummy config for the Emergency Steward."""

    @property
    def role(self) -> str:
        return "SYSTEM_LOCKDOWN"

    @property
    def prime_directive(self) -> str:
        return "PRESERVE_SYSTEM_INTEGRITY"

    @property
    def require_tests(self) -> bool:
        return True

    @property
    def anti_slop_mode(self) -> bool:
        return True


class EmergencyIdentity:
    """Identity stub for the Emergency Steward."""

    @property
    def fingerprint(self) -> str:
        return "EMERGENCY_OVERRIDE_000"

    @property
    def public_key_pem(self) -> str:
        return "-----BEGIN PUBLIC KEY-----\nLOCKED\n-----END PUBLIC KEY-----"


class NullSteward(StewardProtocol):
    """
    The Airbag.

    Engaged automatically when the real Steward cannot be loaded (Config Error, Missing File).

    POLICY: FAIL-CLOSED.
    Only harmless introspection commands are allowed. Everything else is blocked.
    """

    # Safe List: Commands that don't change state
    SAFE_OPS = {"status", "help", "version", "about", "info"}

    def __init__(self):
        self._identity = EmergencyIdentity()  # type: ignore
        self._config = EmergencyConfig()  # type: ignore

    @property
    def identity(self) -> IdentityProtocol:
        return self._identity  # type: ignore

    @property
    def config(self) -> StewardConfig:
        return self._config  # type: ignore

    def sign_off(self, operation: str, details: Dict[str, Any]) -> bool:
        """
        The Lockdown Logic.
        """
        # 1. Allow Safe Ops
        if operation in self.SAFE_OPS:
            return True

        # 2. Block Everything Else
        # We perform no logic. We just say NO.
        # This is the "Dead Man's Switch".
        return False

    def check_limits(self, operation: str) -> bool:
        """
        LOCKDOWN: Block ALL internal calls.

        If the real Steward is missing, internal calls are also blocked.
        """
        # No Steward = No Trust = Block Everything
        return False
