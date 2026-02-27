"""
MAHA BUDDHI — The Discriminative Intelligence Instance
=======================================================

Mahat-tattva. The Great Intelligence. Element #7 (SEVEN).

BG 3.42: indriyāṇi parāṇy āhur indriyebhyaḥ paraṁ manaḥ
         manasas tu parā buddhir yo buddheḥ paratas tu saḥ

"The senses are superior to the body, the mind superior to
 the senses, the intelligence superior to the mind — and the
 soul is superior to the intelligence."

Buddhi sits ABOVE Manas (perception) and BELOW the soul (Purusa).
It takes raw computation (Lotus VM) and resonant vocabulary
(MahaComposition), and produces UNDERSTANDING — cognitive frames
that drive action.

This is not a prompt builder. This is not a template filler.
This is the cognitive engine that THINKS.

Usage:
    from vibe_core.mahamantra.substrate.buddhi import get_buddhi

    buddhi = get_buddhi()
    cognition = buddhi.think("distributed consensus patterns")

    # cognition.perspective → "Karma Yoga - Action"
    # cognition.focus → "field"
    # cognition.approach → "DHARMA"
    # cognition.mode → "RAJAS"
    # cognition.function → "VISHNU"
    # cognition.verse_concepts → ({"sanskrit": "dharma", "meaning": "duty"}, ...)
    # cognition.composed → "dharma karma action truth sustain"
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from vibe_core.mahamantra.protocols._buddhi import (
    BuddhiEvaluation,
    BuddhiResult,
)
from vibe_core.mahamantra.substrate.core.seed import SEVEN

logger = logging.getLogger("MAHAMANTRA.BUDDHI")

# Tattva constant — Buddhi is element #7 in Sankhya
BUDDHI_TATTVA = SEVEN

# Discrimination threshold — below this, output is incoherent
_COHERENCE_THRESHOLD = 0.5


class MahaBuddhi:
    """The discriminative intelligence — Mahat-tattva.

    Stateful singleton. Tracks cognitive history.
    Wires Lotus (VM) + MahaComposition (resonance scoring).
    Produces BuddhiResult — pure cognition, zero prompts.
    """

    def __init__(self) -> None:
        self._think_count = 0
        self._eval_count = 0
        self._last_cognition: Optional[BuddhiResult] = None

    @property
    def think_count(self) -> int:
        return self._think_count

    @property
    def last_cognition(self) -> Optional[BuddhiResult]:
        return self._last_cognition

    def think(
        self,
        input_data: str,
        *,
        vm_result: Optional[Dict[str, object]] = None,
    ) -> BuddhiResult:
        """Discriminate: produce cognitive understanding from input.

        1. Run Lotus VM (or accept pre-computed result)
        2. Run MahaComposition for resonant vocabulary
        3. Interpret 27-key result into cognitive frame
        4. Return BuddhiResult
        """
        from vibe_core.mahamantra.adapters.composition import get_composition
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

        lotus = get_mahamantra()
        composition = get_composition()

        # Step 1: VM computation (or reuse pre-computed)
        if vm_result is None:
            vm_result = lotus(input_data)

        # Step 2: Composition — resonant vocabulary
        composed = composition.compose(vm_result, input_data)

        # Step 3: Cognitive interpretation
        guna = vm_result.get("guna", {})
        cell = vm_result.get("cell", {})
        verse = vm_result.get("verse", {})

        result = BuddhiResult(
            perspective=str(vm_result.get("chapter_significance", "")),
            focus=str(vm_result.get("gita_phase", "")),
            approach=str(vm_result.get("quarter", "")),
            mode=str(guna.get("mode", "")),
            function=str(vm_result.get("trinity_function", "")),
            chapter=int(vm_result.get("chapter", 0)),
            verse_concepts=tuple(verse.get("words", ())),
            resonant_words=tuple(vm_result.get("smaranam", ())),
            prana=int(cell.get("prana", 0)),
            integrity=float(cell.get("integrity", 0.0)),
            is_alive=bool(cell.get("is_alive", False)),
            composed=composed,
            vm_result=vm_result,
        )

        self._think_count += 1
        self._last_cognition = result

        logger.info(
            "think #%d: %s | %s | %s | prana=%d",
            self._think_count,
            result.perspective,
            result.mode,
            result.approach,
            result.prana,
        )

        return result

    def evaluate(self, cognition: BuddhiResult, output: str) -> BuddhiEvaluation:
        """Post-action alignment check.

        Runs the VM on the output text, compares cognitive frames
        with the original cognition that guided the action.
        """
        output_cognition = self.think(output)

        observations: list[str] = []
        score = 0.0
        checks = 0

        # Guna alignment — same operational mode?
        checks += 1
        if cognition.mode == output_cognition.mode:
            score += 1.0
        else:
            observations.append(
                f"mode drift: {cognition.mode} -> {output_cognition.mode}"
            )

        # Quarter alignment — same approach?
        checks += 1
        if cognition.approach == output_cognition.approach:
            score += 1.0
        else:
            observations.append(
                f"approach drift: {cognition.approach} -> {output_cognition.approach}"
            )

        # Trinity alignment — same function?
        checks += 1
        if cognition.function == output_cognition.function:
            score += 1.0
        else:
            observations.append(
                f"function drift: {cognition.function} -> {output_cognition.function}"
            )

        # Cell vitality — is output alive?
        checks += 1
        if output_cognition.is_alive:
            score += 1.0
        else:
            observations.append("output cell is dead")

        # Integrity — above threshold?
        checks += 1
        if output_cognition.integrity > 0.3:
            score += 1.0
        else:
            observations.append(
                f"low integrity: {output_cognition.integrity:.2f}"
            )

        alignment = score / checks if checks else 0.0
        self._eval_count += 1

        logger.info(
            "evaluate #%d: alignment=%.2f coherent=%s",
            self._eval_count,
            alignment,
            alignment > _COHERENCE_THRESHOLD,
        )

        return BuddhiEvaluation(
            alignment=alignment,
            coherent=alignment > _COHERENCE_THRESHOLD,
            observations=tuple(observations),
        )


# =============================================================================
# SINGLETON
# =============================================================================

_buddhi_instance: Optional[MahaBuddhi] = None


def get_buddhi() -> MahaBuddhi:
    """Get the singleton MahaBuddhi instance."""
    global _buddhi_instance
    if _buddhi_instance is None:
        _buddhi_instance = MahaBuddhi()
    return _buddhi_instance
