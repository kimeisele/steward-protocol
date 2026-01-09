"""
BRIDGE PROTOCOL - Setu Bandha (The Connector).

"Build the bridge with stones that float (Truth), not with sand (Any)."

STRICT TYPING ENFORCEMENT:
- Input MUST be 'CommandContext' (Legacy) OR 'CLICapabilityToken' (Naga).
- Anything else raises 'MayavadError'.
- NO 'Any'. NO 'unknown_wanderer'.
"""

from dataclasses import dataclass
from typing import Union

# IMPORT SOURCES (Strict Dependencies)
from vibe_core.protocols.cli_execution import CLICapabilityToken
from vibe_core.protocols.command import CommandContext

# IMPORT TARGET (Universal Truth)
from .types import ProtocolError, SovereignContext, TranscendentalQuality


class MayavadError(ProtocolError):
    """Raised when an object tries to cross the bridge without form (Type)."""

    pass


class SetuBandha:
    """
    The Bridge Builder.
    Hardened. No Any.
    """

    @staticmethod
    def cross_bridge(
        input_obj: Union[CommandContext, CLICapabilityToken],
    ) -> SovereignContext:
        """
        The Checkpoint.

        Strictly typed. If you pass an 'int' or 'dict' here, static analysis fails.
        If you force it at runtime, the 'else' block kills it.
        """
        # 1. THE NAGA PATH (Cryptographic & Strong)
        if isinstance(input_obj, CLICapabilityToken):
            return SetuBandha._from_token(input_obj)

        # 2. THE LEGACY PATH (Structural & Weak)
        elif isinstance(input_obj, CommandContext):
            return SetuBandha._from_legacy(input_obj)

        # 3. THE VOID (Defense against dynamic stupidity)
        else:
            obj_type = type(input_obj).__name__
            raise MayavadError(
                f"Bridge Breach: Object of type '{obj_type}' attempted to cross. "
                "Only 'CommandContext' and 'CLICapabilityToken' are permitted."
            )

    @staticmethod
    def _from_token(token: CLICapabilityToken) -> SovereignContext:
        """
        Transforms Naga Token -> SovereignContext.
        """
        # Extract Identity
        identity = token.subject

        # Extract Signature (Binary Proof)
        # We ensure it's a hex string for the Universal Layer
        sig = token.signature.hex() if isinstance(token.signature, bytes) else str(token.signature)

        # Calculate Tattva (Ontological Level)
        level = TranscendentalQuality.EXISTENCE  # Base Jiva

        # ELEVATION LOGIC (Specific & Hardcoded)
        if token.issuer == "KERNEL":
            # Kernel-signed tokens are trusted administrative acts
            level = TranscendentalQuality.TRUTHFULNESS  # Quality 8

        if token.subject == "Jagannath":
            # Divinity Exception (The Lord)
            level = TranscendentalQuality.SOURCE_OF_INCARNATIONS  # Quality 58

        return SovereignContext(
            identity_id=identity,
            signature=sig,
            tattva_level=level,
        )

    @staticmethod
    def _from_legacy(ctx: CommandContext) -> SovereignContext:
        """
        Transforms Legacy Context -> SovereignContext.
        """
        # CRITICAL: Legacy Contexts have NO cryptographic signature.
        # They are inherently "Dirty" (Saucam Failure).

        identity = ctx.caller or "anonymous_legacy"

        # We mark this explicitly as LOWEST QUALITY.
        # The 'Dharma' protocol will likely reject this for high-value targets.
        return SovereignContext(
            identity_id=identity,
            signature="",  # EMPTY SIGNATURE = UNVERIFIED
            tattva_level=TranscendentalQuality.EXISTENCE,  # Lowest Level (1)
        )
