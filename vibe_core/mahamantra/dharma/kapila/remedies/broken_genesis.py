"""
BROKEN GENESIS REMEDY - Heals Broken Parampara Lineage.

"guru-mukha-padma-vākya, cittete koriyā aikya"
"Make the words from the lotus mouth of the guru one with your heart."

DETECTION: project_introspection finds genesis % 37 != 0
SURGERY: This CSTRemedy replaces with valid computed genesis

THE PANCHA TATTVA OF LINEAGE HEALING:
    CHAITANYA:  The broken file awakens to its true identity
    NITYANANDA: Parampara (37) carries the correction
    ADVAITA:    compute_genesis_hash() bridges invalid → valid
    GADADHARA:  CST transformation flows through the AST
    SRIVASA:    Only files with __mahajana__ receive healing

PHILOSOPHY:
"Parampara" - The chain of disciplic succession must remain unbroken.
A genesis byte that fails % 37 == 0 is OUTSIDE the lineage.
This remedy brings it back into the fold.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"  # Position 9 - Service/Devotion (Healing is seva)
__position__ = 9
__genesis__ = "0xff3f114f"  # GenesisByte: parampara % 37 == 0

# === PANCHA TATTVA DECLARATION (sankirtan ausschmückung) ===
__tattva__ = {
    "chaitanya": "Broken Genesis Remedy - Lineage Healer",
    "nityananda": "Parampara Protocol (_seed.py PARAMPARA=37)",
    "advaita": "compute_genesis_hash() from sankirtan.py",
    "gadadhara": "LibCST SimpleStatementLine transformation",
    "srivasa": "Only heals files with valid __mahajana__ + __position__",
}

from typing import List, Optional, Sequence, Union

import libcst as cst
import libcst.matchers as m

from vibe_core.mahamantra.dharma.kapila.remedies.base import CSTRemedy

# SSOT: Parampara constant from seed
from vibe_core.mahamantra.protocols._seed import PARAMPARA


class BrokenGenesisRemedy(CSTRemedy):
    """
    Heals broken genesis bytes (% 37 != 0).

    THE LILA (Divine Play):
        1. DISCOVERY: Visit __mahajana__ and __position__ assignments
        2. DIAGNOSIS: Check if __genesis__ value % PARAMPARA != 0
        3. HEALING: Compute valid genesis via sankirtan formula
        4. TRANSFORMATION: Replace the broken value via CST

    SAFETY:
        - Only heals if __mahajana__ AND __position__ are present
        - Uses deterministic compute_genesis_hash() (same input = same output)
        - Does NOT touch files without proper declarations
    """

    @property
    def rule_id(self) -> str:
        return "broken_genesis"

    @property
    def requirements(self) -> List[str]:
        return ["vibe_core.mahamantra.substrate.sankirtan.compute_genesis_hash"]

    def __init__(self, file_path: str = ""):
        super().__init__()
        self._file_path = file_path
        self._mahajana: Optional[str] = None
        self._position: Optional[int] = None
        self._current_genesis: Optional[str] = None
        self._is_genesis_valid: bool = True

    def set_file_path(self, path: str) -> None:
        """Set the file path for genesis computation."""
        self._file_path = path

    def visit_Assign(self, node: cst.Assign) -> None:
        """
        LILA PHASE 1: DISCOVERY - Capture __mahajana__ and __position__.

        These are prerequisites for healing. Without them, we cannot
        compute a valid genesis (the formula requires all three).
        """
        if len(node.targets) != 1:
            return

        target = node.targets[0].target
        if not isinstance(target, cst.Name):
            return

        name = target.value

        # Capture __mahajana__
        if name == "__mahajana__":
            if isinstance(node.value, cst.SimpleString):
                # Remove quotes: '"brahma"' -> 'brahma'
                raw = node.value.value
                self._mahajana = raw.strip("'\"")

        # Capture __position__
        elif name == "__position__":
            if isinstance(node.value, cst.Integer):
                self._position = int(node.value.value)

        # Capture __genesis__ for diagnosis
        elif name == "__genesis__":
            if isinstance(node.value, cst.SimpleString):
                raw = node.value.value.strip("'\"")
                self._current_genesis = raw
                # DIAGNOSIS: Check validity
                try:
                    value = int(raw, 16)
                    self._is_genesis_valid = (value % PARAMPARA == 0)
                except ValueError:
                    self._is_genesis_valid = False

    def leave_Assign(
        self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> cst.Assign:
        """
        LILA PHASE 3 & 4: HEALING & TRANSFORMATION.

        If __genesis__ is broken AND we have __mahajana__ + __position__,
        compute a valid genesis and replace.
        """
        if len(updated_node.targets) != 1:
            return updated_node

        target = updated_node.targets[0].target
        if not isinstance(target, cst.Name):
            return updated_node

        if target.value != "__genesis__":
            return updated_node

        # SRIVASA GOVERNANCE: Only heal if we have prerequisites
        if self._mahajana is None or self._position is None:
            return updated_node

        # Already valid? No healing needed
        if self._is_genesis_valid:
            return updated_node

        # HEALING: Compute valid genesis
        self.violation_found = True
        new_genesis = self._compute_valid_genesis()

        if new_genesis is None:
            return updated_node

        self.applied = True

        # TRANSFORMATION: Create new SimpleString with valid genesis
        # Preserve original quote style
        original_value = updated_node.value
        if isinstance(original_value, cst.SimpleString):
            quote_char = original_value.value[0]
            new_value = cst.SimpleString(f'{quote_char}{new_genesis}{quote_char}')
        else:
            new_value = cst.SimpleString(f'"{new_genesis}"')

        return updated_node.with_changes(
            value=new_value,
        )

    def _compute_valid_genesis(self) -> Optional[str]:
        """
        ADVAITA BRIDGE: Compute valid genesis using sankirtan formula.

        Formula (from compute_genesis_hash):
            1. Create identity string: "{mahajana}:{position}:{file_path}"
            2. SHA256 hash, take first 8 chars
            3. Adjust to be divisible by 37
        """
        if self._mahajana is None or self._position is None:
            return None

        try:
            from vibe_core.mahamantra.substrate.sankirtan import compute_genesis_hash
            return compute_genesis_hash(
                self._mahajana,
                self._position,
                self._file_path or "unknown",
            )
        except ImportError:
            # Fallback: compute inline if import fails
            return self._compute_genesis_inline()

    def _compute_genesis_inline(self) -> Optional[str]:
        """
        Inline genesis computation (fallback if sankirtan import fails).

        Replicates compute_genesis_hash() logic.

        YOGA MAYA: Uses only mahajana + position (NO file_path!)
        This makes Genesis HOLOGRAPHIC - same archetype → same hash ALWAYS.
        """
        import hashlib

        if self._mahajana is None or self._position is None:
            return None

        # YOGA MAYA: Pure archetype identity (NO FILE PATH!)
        identity = f"{self._mahajana}:{self._position}"
        raw_hash = hashlib.sha256(identity.encode()).hexdigest()[:8]

        # Adjust to be divisible by 37
        base_value = int(raw_hash, 16)
        adjusted = base_value - (base_value % PARAMPARA)

        return f"0x{adjusted:08x}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BrokenGenesisRemedy",
]
