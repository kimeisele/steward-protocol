"""
ORBIT SUBSTRATE - The Clockwork Logic
=====================================

"jyotir-anīkāni" - The Army of Luminaries.

Implements the OrbitCalculator:
- Calculates Lagna (Phase Offset) from Entity ID.
- Determines if "It is Time" based on Kaksha (Frequency).

"""
from vibe_core.mahamantra.protocols._seed import (QUARTERS)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = QUARTERS
__genesis__ = "0xfb0a3320"  # GenesisByte: parampara % 37 == 0

import hashlib
from vibe_core.mahamantra.protocols._orbit import OrbitProtocol
from vibe_core.mahamantra.protocols._seed import WORDS


class OrbitCalculator(OrbitProtocol):
    """
    Calculates orbital mechanics for entities.
    """

    def get_phase_offset(self, entity_id: str, modulus: int = WORDS) -> int:
        """
        Calculate deterministic phase offset (Lagna).

        Algorithm:
        1. SHA256 hash of entity_id.
        2. Convert first 4 bytes to int.
        3. Modulo by modulus (e.g., 16).

        This ensures the same entity always has the same "slot" in the cycle.
        """
        hash_bytes = hashlib.sha256(entity_id.encode("utf-8")).digest()
        # Use first 4 bytes as integer seed
        seed_int = int.from_bytes(hash_bytes[:QUARTERS], byteorder="big")
        return seed_int % modulus

    def should_dance(self, current_tick: int, entity_id: str, kaksha_modulus: int = WORDS) -> bool:
        """
        Determine if it's time to dance.

        Logic:
           (Current Tick + My Phase Offset) % Modulus == 0

        Example:
           Modulus = 16
           Tick = 0
           My Offset = 8
           (0 + 8) % 16 = 8 != 0 -> No Dance

           Tick = 8
           (8 + 8) % 16 = 16 % 16 = 0 -> DANCE!

        This effectively shifts the entity's "Tick 0" to "Tick 8".
        """
        offset = self.get_phase_offset(entity_id, kaksha_modulus)

        # NOTE: We use (tick - offset) or (tick + offset)?
        # If we want offset 4 to fire at tick 4:
        # (4 - 4) % 16 == 0.
        # But (4 + 4) % 16 == 8 != 0.

        # Let's align with the prompt's logic:
        # "Agent B (Mond) ist bei Tick 4."
        # This means at Tick 4, Agent B should fire.
        # So we want `(tick - offset) % modulus == 0`?
        # Or simply `tick % modulus == offset`.

        # `tick % modulus == offset` is cleaner.
        # If offset is 4, it fires at 4, 20, 36...

        cycle_position = current_tick % kaksha_modulus
        return cycle_position == offset
