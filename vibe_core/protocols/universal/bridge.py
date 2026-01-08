"""
BRIDGE PROTOCOL - Setu Bandha (The Connector).

"Build the bridge to Lanka (Universal Layer) so the army can cross."

This module bridges the gap between:
1. Legacy Command System (CommandContext) - The Old World.
2. Naga CLI Logic (CLICapabilityToken) - The Cryptographic Defense.
3. Universal Kernel (SovereignContext) - The Divine Goal.

SetuBandha transforms worldly credentials into Sovereign Contexts.
"""

from typing import Any, Union

from vibe_core.protocols.cli_execution import CLICapabilityToken
from vibe_core.protocols.command import CommandContext

from .types import SovereignContext, TranscendentalQuality


class SetuBandha:
    """
    The Bridge Builder.
    Converts diverse inputs into SovereignContext.
    """

    @staticmethod
    def cross_bridge(input_obj: Union[CommandContext, CLICapabilityToken, Any]) -> SovereignContext:
        """
        Takes a legacy or naga object and returns a SovereignContext.
        """

        # 1. Handle Naga Token (Cryptographic)
        if isinstance(input_obj, CLICapabilityToken):
            return SetuBandha._from_token(input_obj)

        # 2. Handle Legacy Context (Mayavad)
        if isinstance(input_obj, CommandContext):
            return SetuBandha._from_legacy(input_obj)

        # 3. Handle Unknown (Neti Neti)
        return SovereignContext(
            identity_id="unknown_wanderer",
            signature="",
            tattva_level=TranscendentalQuality.EXISTENCE,  # Lowest Jiva
        )

    @staticmethod
    def _from_token(token: CLICapabilityToken) -> SovereignContext:
        """
        Transforms Naga Token -> SovereignContext.
        """
        # Mapping Identity
        identity = token.subject

        # Mapping Signature (Bytes -> Hex)
        sig = token.signature.hex() if isinstance(token.signature, bytes) else str(token.signature)

        # Mapping Tattva (Qualities)
        # Naga tokens have 'capabilities'.
        # We derive Tattva Level from Issuer and Subject.

        level = TranscendentalQuality.EXISTENCE  # Default Jiva

        if token.issuer == "KERNEL":
            # Kernel-issued tokens are trusted permissions.
            # Does NOT make you God, but gives you authority.
            # We map this to 50 (Perfect Jiva).
            level = TranscendentalQuality.TRUTHFULNESS  # Just a placeholder high Jiva level

        if token.subject == "Jagannath":
            # The Lord gets his status restored.
            level = TranscendentalQuality.SOURCE_OF_INCARNATIONS  # 58+

        return SovereignContext(identity_id=identity, signature=sig, tattva_level=level)

    @staticmethod
    def _from_legacy(ctx: CommandContext) -> SovereignContext:
        """
        Transforms CommandContext -> SovereignContext.
        """
        # Warning: CommandContext has NO signature. It is 'Dirty'.
        # We allow it passage but mark it as Lowest Tattva.

        identity = ctx.caller
        if not identity:
            identity = "anonymous_legacy"

        # Check Metadata for Pretenders (Asuras)
        # If someone writes "I am God" in metadata, ignore it.

        return SovereignContext(
            identity_id=identity,
            signature="",  # No signature = Dirty Context (Saucam Fail in future)
            tattva_level=TranscendentalQuality.EXISTENCE,
        )
