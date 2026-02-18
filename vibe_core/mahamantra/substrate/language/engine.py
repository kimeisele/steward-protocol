"""
MAHA LANGUAGE ENGINE — Lotus-Rooted Orchestrator
=================================================

Single path: Lotus.__call__() → MahaComposition.compose() → EngineResult.

Seed is deterministic (same input → same seed, always).
Output is LIVING (Chamber accumulates — Kshetrajna changes the field).
No fake copies of Antaranga/Venu/Kernel. The real ones live in Lotus/Chamber.
"""

from __future__ import annotations

__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2c80316d"

import logging
from typing import Dict, Optional

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS, PARAMPARA, WORDS,
)
from vibe_core.mahamantra.substrate.language.types import EngineResult

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("MAHA_LANGUAGE")


class MahaLanguageEngine:
    """Lotus-rooted language orchestrator.

    Lotus.__call__() runs the full 9 NavaBhakti pipeline:
        compress → synth → smaranam → verse → cell → kirtan → yajna
    All real infrastructure (Chamber, Antaranga, Venu) lives there.

    This engine is a thin shell:
        1. Call Lotus
        2. Route to section (attractor → Gita section)
        3. Compose via MahaComposition adapter (protocol-based)
        4. Package into EngineResult
    """

    def generate(self, text: str) -> EngineResult:
        """Lotus → MahaComposition.compose() → EngineResult."""
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.mahamantra.substrate.language.phonetics import scan_syllable_rhythm
        from vibe_core.mahamantra.adapters.composition import get_composition
        from vibe_core.mahamantra.substrate.language.section_router import (
            SECTION_SIGNATURES, extract_template, route_to_section,
        )

        # === LOTUS: The real Maha Mantra computation ===
        lotus = get_mahamantra()
        lr = lotus(text)

        vib = lr.get("vibration", {})
        seed = vib.get("seed", 0)
        attractor = vib.get("attractor", 0)
        rhythm = scan_syllable_rhythm(text)

        # Early exit: no phonemic content
        nama = lr.get("nama", {})
        if not nama.get("coords"):
            guna = lr.get("guna", {})
            return EngineResult(
                input_text=text, seed=seed, attractor=0, guardian_name="",
                guardian_function="", intent_category=guna.get("opcode", ""),
                section_name="", section_mode="", verse_ref="",
                resonant_words=(), template_words=(),
                antaranga_active=0, antaranga_prana=0,
                output="[no phonemic content]",
                derivation="input has no encodable phonemes",
                syllable_count=rhythm.syllable_count,
                stress_pattern=rhythm.stress_pattern,
                sequencer_steps=rhythm.sequencer_steps,
            )

        # === SECTION ROUTING (attractor → Gita section) ===
        section_name, verse_num, _ = route_to_section(attractor, seed)
        section_sig = SECTION_SIGNATURES.get(section_name, {})
        section_mode = section_sig.get("mode", "CORE")
        template = extract_template(GITA_CHAPTERS, verse_num)

        # === COMPOSITION: use VM-composed output if available, else fallback ===
        output = lr.get("composed") or get_composition().compose(lr, text)

        # === PACKAGE RESULT from Lotus response ===
        verse = lr.get("verse")
        lotus_ant = lr.get("antaranga", {})
        guna = lr.get("guna", {})
        guardian_name = lr.get("guardian", "")
        diw = lr.get("diw", {})

        res_words = tuple(
            (rw.get("sanskrit", ""), rw.get("meaning", ""), float(rw.get("score", 0)))
            for rw in lr.get("smaranam", ())
        )
        tmpl_words = tuple(
            (tw.get("sanskrit", ""), tw.get("meaning", ""), tw.get("role", ""))
            for tw in template[:WORDS]
        )

        verse_ref = verse["id"] if verse else f"BG.18.{verse_num}"

        derivation = (
            f"seed={seed} → attractor={attractor} "
            f"→ guardian={guardian_name}({lr.get('trinity_function', '')}) "
            f"→ section={section_name}({section_mode}) "
            f"→ verse={verse_ref} "
            f"→ rhythm={rhythm.signature}({rhythm.syllable_count}) "
            f"→ diw=0x{diw.get('raw', 0):05x} "
            f"→ antaranga={lotus_ant.get('active_slots', 0)}slots,"
            f"{lotus_ant.get('total_prana', 0)}prana"
        )

        return EngineResult(
            input_text=text, seed=seed, attractor=attractor,
            guardian_name=guardian_name,
            guardian_function=lr.get("trinity_function", ""),
            intent_category=guna.get("opcode", ""),
            section_name=section_name, section_mode=section_mode,
            verse_ref=verse_ref,
            resonant_words=res_words, template_words=tmpl_words,
            antaranga_active=lotus_ant.get("active_slots", 0),
            antaranga_prana=lotus_ant.get("total_prana", 0),
            output=output, derivation=derivation,
            diw_applied=diw.get("raw", 0),
            syllable_count=rhythm.syllable_count,
            stress_pattern=rhythm.stress_pattern,
            sequencer_steps=rhythm.sequencer_steps,
        )


_ENGINE: Optional[MahaLanguageEngine] = None


def get_engine() -> MahaLanguageEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = MahaLanguageEngine()
    return _ENGINE


def generate(text: str) -> EngineResult:
    """Convenience: generate a response for any input text."""
    return get_engine().generate(text)
