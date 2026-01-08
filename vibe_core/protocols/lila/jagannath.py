"""
JAGANNATH PROTOCOL - The Sovereign Observer (Layer 1)

"Jagannatha Swami Nayana Patha Gami Bhavatu Me"
May the Lord of the Universe be visible to me.

CONTEXT:
This protocol defines the 'Eyes' of the system.
It is the Bridge between the Silent Kernel (Nirguna) and the Active World (Saguna).
It manages the 'Immigration' of new entities into the protected Union.

RELATIONSHIPS:
- JAGANNATH (The Viewer): Observability & Health.
- BALARAMA (The Holder): NagaProxy - wraps services to give them strength.
- SUBHADRA (The Yogamaya): The connection between them.
"""

from typing import Protocol, runtime_checkable

from vibe_core.protocols.substrate import SubstrateStatus


@runtime_checkable
class IJagannath(Protocol):
    """
    The Lord of the Universe Interface.
    The Ultimate Watcher and Bridge Builder.
    """

    def open_eyes(self) -> SubstrateStatus:
        """
        Gaze upon the system.
        Unlike a simple 'health check', this asserts the reality of the Union.
        Returns the current spiritual status of the substrate.
        """
        ...

    def start_ratha_yatra(self) -> int:
        """
        The Festival of Chariots (System-wide Scan).
        Triggers the 'Ashvamedha' (Horse Sacrifice) in Ananta.

        This moves through the ServiceRegistry:
        1. Identifies Orphans (Immigrants without Papers).
        2. Signals Ananta to flood them (Naturalization).

        Returns:
            Number of entities blessed (naturalized/proxied).
        """
        ...

    def check_immigration_status(self, entity_id: str) -> bool:
        """
        BORDER CONTROL.
        Checks if an entity has crossed the bridge correctly.

        Args:
            entity_id: The ID of the service/agent.

        Returns:
            True if the entity is held by Balarama (NagaProxy) and Valid.
        """
        ...
