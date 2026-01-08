"""
JAGANNATH PROTOCOL - The Sovereign Interface (The Wood Form)

"Jagannatha Swami Nayana Patha Gami Bhavatu Me"
May the Lord of the Universe be visible to me.

CONTEXT:
Where Nrisimha is the Protector (Internal Security, Strictness),
Jagannath is the Public Face (Mercy, Accessibility).
He appears in a simple wooden form to be accessible to ALL (even foreigners/external systems).

ARCHITECTURE (The Triad):
- JAGANNATH (The Face): Accessibility (Darshan) & Mercy (Prasadam).
- BALARAMA (The Holder): Strength (Ananta/Proxies) that executes the will.
- SUBHADRA (The Bridge): The Yogamaya that connects the Lord to the World.

GAD-000 COMPLIANCE:
- Observability (Darshan): "Big Eyes" see everything.
- Recoverability (Prasadam): Graceful degradation as Mercy.
- Accessibility (Ratha Yatra): Bringing the state to the public.
"""

from typing import Any, Protocol, runtime_checkable

from vibe_core.protocols.universal.union import UnionScanResult


@runtime_checkable
class JagannathProtocol(Protocol):
    """
    The Lord of the Universe Interface.

    This is the SOVEREIGN FACADE.
    It provides Safe, Merciful access to the Absolute Truth (Kernel).
    """

    def darshan(self) -> UnionScanResult:
        """
        The Divine Vision (Observability).

        "His eyes are very large and round."
        He sees the entire Union without discrimination.

        Returns:
            The complete State of the Union (UnionScanResult).
            No filtering - Raw Reality.
        """
        ...

    def prasadam(self, request: Any) -> Any:
        """
        The Mercy (Graceful Execution).

        "Even if the offering is imperfect, He accepts it."

        Executes a request with 'Graceful Degradation'.
        If strict execution (Nrisimha) would reject it, Jagannath
        attempts to return a safe fallback (Prasad) instead of crasing.

        Args:
            request: The intent/command to execute.

        Returns:
            The result (Mercy) or a safe default. NEVER raises exception.
        """
        ...

    def ratha_yatra(self) -> int:
        """
        The Festival of Chariots (System-wide Pulse).

        "He comes out of the Temple to meet the people."

        Triggers the Ashvamedha (Horse Sacrifice) via Ananta/Balarama.
        Forces a system-wide scan and 'floods' (blesses) any orphan entities
        with the necessary connection (NagaProxy).

        Returns:
            Number of entities blessed (flooded/fixed).
        """
        ...

    @property
    def sovereign_form(self) -> str:
        """
        The Visible Form (Identity).

        Returns the Public Key or Identity String of the Sovereign.
        "The Wood Form" that verifies the signature.
        """
        ...
