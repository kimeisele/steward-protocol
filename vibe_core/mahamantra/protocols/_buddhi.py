"""
BUDDHI Protocol — The Discriminative Intelligence (Mahat-tattva)
================================================================

BG 7.4: bhūmir āpo 'nalo vāyuḥ khaṁ mano buddhir eva ca
         ahaṅkāra itīyaṁ me bhinnā prakṛtir aṣṭadhā

"Earth, water, fire, air, ether, mind, intelligence and false ego —
 all together these eight constitute My separated material energies."

Buddhi = Element #7 (SEVEN) in the Sankhya system.
Above Manas (mind/perception), below Ahankara (ego).

BG 3.42: indriyāṇi parāṇy āhur indriyebhyaḥ paraṁ manaḥ
         manasas tu parā buddhir yo buddheḥ paratas tu saḥ

"The senses are superior to the body, the mind superior to the senses,
 the intelligence superior to the mind — and the soul is superior
 to the intelligence."

Manas perceives. Buddhi DISCRIMINATES. Ahankara identifies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol, Tuple, runtime_checkable


@dataclass(frozen=True)
class BuddhiResult:
    """Cognitive output from Buddhi's discrimination.

    Not prompts. Not templates. UNDERSTANDING.

    Any agent consumes this to know:
    - What perspective to take (chapter → lens)
    - Where to focus (field vs fruit)
    - How to approach (quarter → mode of action)
    - What mode to operate in (guna)
    - What function to serve (trinity)
    - What wisdom applies (verse concepts)
    - What resonates (scored words)
    - How much energy is available (prana/integrity)
    """

    # === Cognitive Frame ===
    perspective: str  # Chapter significance → "Karma Yoga - Action", etc.
    focus: str  # Gita phase → "field" (process) or "fruit" (outcome)
    approach: str  # Quarter → "GENESIS"/"DHARMA"/"KARMA"/"MOKSHA"
    mode: str  # Guna → "SATTVA"/"RAJAS"/"TAMAS"
    function: str  # Trinity → "BRAHMA"/"VISHNU"/"SHIVA"

    # === Verse Intelligence ===
    chapter: int  # Gita chapter (1-18)
    verse_concepts: Tuple[Dict[str, str], ...]  # Sanskrit + meaning from matched verse
    resonant_words: Tuple[Dict[str, object], ...]  # Scored resonance matches

    # === Energy State ===
    prana: int  # Cell energy
    integrity: float  # 0.0-1.0 normalized membrane integrity
    is_alive: bool  # Cell vitality

    # === Composition ===
    composed: str  # MahaComposition resonant output (4-7 words)

    # === Raw (for advanced consumers) ===
    vm_result: Dict[str, object] = field(repr=False)


@dataclass(frozen=True)
class BuddhiEvaluation:
    """Post-action alignment assessment.

    Buddhi evaluates: does the output match the cognitive intent?
    """

    alignment: float  # 0.0-1.0 overall alignment score
    coherent: bool  # Above discrimination threshold?
    observations: Tuple[str, ...]  # What Buddhi noticed


@runtime_checkable
class BuddhiProtocol(Protocol):
    """The discriminative intelligence interface.

    Tattva #7 (SEVEN) in the Sankhya system.
    Manas perceives. Buddhi discriminates. Ahankara identifies.
    """

    def think(
        self,
        input_data: str,
        *,
        vm_result: Optional[Dict[str, object]] = None,
    ) -> BuddhiResult:
        """Discriminate: transform input into cognitive understanding.

        Args:
            input_data: Raw text input.
            vm_result: Pre-computed Lotus VM result (avoids redundant computation).

        Returns:
            BuddhiResult — structured cognition, not prompts.
        """
        ...

    def evaluate(self, cognition: BuddhiResult, output: str) -> BuddhiEvaluation:
        """Post-action alignment check.

        Run the VM on the output, compare cognitive frames
        with the original cognition that guided the action.

        Args:
            cognition: The original cognitive intent.
            output: The produced text to evaluate.

        Returns:
            BuddhiEvaluation — alignment assessment.
        """
        ...

    @property
    def think_count(self) -> int:
        """Total number of cognitive discriminations performed."""
        ...
