"""
MAHA LANGUAGE ENGINE — Thin Orchestrator
=========================================

8 stages wiring existing Mahamantra components into deterministic
text-to-text pipeline. Each stage delegates to a focused module.
"""

from __future__ import annotations

__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2c80316d"

import logging
from typing import Dict, List, Optional

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS, KSETRAJNA, MAHA_QUANTUM, PANCHA, PARAMPARA,
    QUARTERS, SEVEN, WORDS,
)
from vibe_core.mahamantra.substrate.language.types import EngineResult

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("MAHA_LANGUAGE")


class MahaLanguageEngine:
    """The Anti-Entropy Language Model — Lotus-rooted orchestrator.

    Lotus __call__() provides the shared computation (9 NavaBhakti steps).
    This engine adds UNIQUE language stages not in Lotus:
        - Character wave (keystroke → Antaranga)
        - Semantic tree expansion (guardian → name tree)
        - Fractal derivation tree (seed → mode branches)
        - DIW modulation (venu → antaranga)
        - Phoneme trajectory (sequencer synthesis)
        - Composition (Antaranga wave → syllable grid → English)
    """

    def __init__(self) -> None:
        self._antaranga = None
        self._kernel = None
        self._venu = None

    def _ensure_loaded(self) -> None:
        if self._antaranga is not None:
            return
        from vibe_core.mahamantra.substrate.antaranga import AntarangaRegistry
        from vibe_core.mahamantra.substrate.maha_llm_kernel import MahaLLMKernel
        from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator
        self._antaranga = AntarangaRegistry()
        self._kernel = MahaLLMKernel()
        self._venu = VenuOrchestrator()

    def _lotus_compute(self, text: str):
        """Run Lotus __call__() — the real Maha Mantra computation."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        lotus = MahamantraLotus()
        return lotus(text)

    def _build_character_wave(self, text: str) -> Dict:
        from vibe_core.mahamantra.research.language_runtime.antaranga_bridge import (
            impact_keystroke, modulate_with_diw,
        )
        self._antaranga.clear()
        impacts = 0
        rama_coords: List[int] = []
        for char in text:
            result = impact_keystroke(self._antaranga, char)
            if result is not None:
                impacts += KSETRAJNA
                rama_coords.append(result.rama_coord)
        diw = self._venu.step()
        modulate_with_diw(self._antaranga, diw)
        return {
            "char_impacts": impacts,
            "char_wave_prana": self._antaranga.total_prana(),
            "char_wave_active": self._antaranga.active_count(),
            "rama_coords": tuple(rama_coords),
        }

    def _resonate_from_lotus(self, lr: Dict, template: List[Dict], seed: int) -> Dict:
        """Resonate Lotus smaranam words into own Antaranga for derivation tree."""
        from vibe_core.mahamantra.substrate.antaranga import (
            GENESIS_PRANA_U32, INTEGRITY_FULL,
        )
        from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, COORD_HARMONIC
        from vibe_core.mahamantra.substrate.language.composer import _resolve_coords

        word_slots = []
        for i, rw in enumerate(lr.get("smaranam", ())):
            if i >= WORDS:
                break
            sanskrit = rw.get("sanskrit", "")
            score = float(rw.get("score", 0))
            coords = _resolve_coords(sanskrit, -1)
            coord = coords[0] if coords else -1
            if coord < 0:
                continue
            element = int(COORD_ELEMENT[coord]) if coord < 49 else 0
            harmonic = int(COORD_HARMONIC[coord]) if coord < 49 else 0
            slot_idx = (coord * SEVEN + seed) % 512
            prana = int(score * GENESIS_PRANA_U32)
            integrity = int(score * INTEGRITY_FULL)
            self._antaranga.collide(
                slot_idx, v_source=coord, v_target=harmonic,
                v_operation=element, v_arcanam=seed % MAHA_QUANTUM,
                v_atma=i, v_prana=max(1, prana),
                v_integrity=max(1, min(integrity, INTEGRITY_FULL)), v_cycle=1,
            )
            word_slots.append((slot_idx, self._antaranga.prana_at(slot_idx)))
        for j, tw in enumerate(template):
            if not tw.get("coords"):
                continue
            t_coord = tw["coords"][0] if tw["coords"] else 0
            t_element = int(COORD_ELEMENT[t_coord]) if t_coord < 49 else 0
            slot_idx = (t_coord * SEVEN + seed) % 512
            self._antaranga.collide(
                slot_idx, v_source=t_coord, v_target=0,
                v_operation=t_element, v_arcanam=seed % MAHA_QUANTUM,
                v_atma=WORDS + j, v_prana=GENESIS_PRANA_U32 // QUARTERS,
                v_integrity=INTEGRITY_FULL // QUARTERS, v_cycle=1,
            )
        return {
            "word_slots": word_slots,
            "active_slots": self._antaranga.active_count(),
            "total_prana": self._antaranga.total_prana(),
        }

    def _expand(self, guardian_name: str, seed: int, attractor: int) -> Dict:
        from vibe_core.mahamantra.substrate.seed_to_words import seed_to_words
        from vibe_core.mahamantra.research.shabda_spawning import ShabdaSeed
        expansion = self._kernel.expand(guardian_name, depth=2)
        expanded_names = (
            tuple(n for n in expansion.related_names)
            if hasattr(expansion, "related_names") and expansion.related_names else ()
        )
        seed_result = seed_to_words(seed)
        synth_walk_words = (
            tuple((w.sanskrit, w.meanings[0] if w.meanings else "") for w in seed_result.all_words[:WORDS])
            if seed_result.all_words else ()
        )
        root = ShabdaSeed(
            text=guardian_name,
            vibration_sum=attractor % MAHA_QUANTUM,
            syllable_count=len(guardian_name) // 2 or KSETRAJNA,
        )
        shabda_children = tuple(root.spawn(op, mod=MAHA_QUANTUM) for op in ("H", "K", "R"))
        return {
            "expanded_names": expanded_names,
            "expansion_depth": expansion.tree.depth,
            "expansion_words": tuple(
                (rw.sanskrit, rw.meanings[0] if rw.meanings else "") for rw in expansion.resonant_words
            ) if expansion.resonant_words else (),
            "synth_walk_words": synth_walk_words,
            "shabda_children": shabda_children,
        }

    def _sprout_derivation_tree(self, seed, attractor, guardian_name, shabda_children) -> Dict:
        from vibe_core.mahamantra.protocols._fractal import FractalTree
        from vibe_core.mahamantra.substrate.seed_to_words import seed_to_words
        from vibe_core.mahamantra.substrate.algorithm.maha import maha_step
        position = attractor % WORDS
        tree: FractalTree[Dict] = FractalTree()
        root_payload = {"mode": "ROOT", "seed": seed, "prana": self._antaranga.prana_at((seed * SEVEN) % 512), "words": ()}
        root_node = tree.add_root(position, root_payload)
        mode_ops = (("DHARMA", "H"), ("GENESIS", "K"), ("KARMA", "R"))
        branch_words: Dict[str, list] = {"DHARMA": [], "GENESIS": [], "KARMA": []}
        for sub_pos, (mode_name, op) in enumerate(mode_ops):
            sub_seed = maha_step(seed, op, MAHA_QUANTUM)
            sub_result = seed_to_words(sub_seed)
            sub_words = []
            if sub_result.all_words:
                for w in sub_result.all_words[:PANCHA]:
                    if w.meanings:
                        sub_words.append({"sanskrit": w.sanskrit, "meaning": w.meanings[0], "first_coord": w.first_coord})
            branch_slot = (sub_seed * SEVEN) % 512
            branch_prana = self._antaranga.prana_at(branch_slot)
            branch_payload = {"mode": mode_name, "seed": sub_seed, "prana": branch_prana, "words": tuple(sub_words)}
            branch_node = root_node.add_child(sub_pos, branch_payload)
            branch_words[mode_name] = list(sub_words)
            for leaf_idx, (sub_mode, sub_op) in enumerate(mode_ops):
                leaf_seed = maha_step(sub_seed, sub_op, MAHA_QUANTUM)
                leaf_result = seed_to_words(leaf_seed)
                leaf_words = []
                if leaf_result.all_words:
                    for w in leaf_result.all_words[:2]:
                        if w.meanings:
                            leaf_words.append({"sanskrit": w.sanskrit, "meaning": w.meanings[0], "first_coord": w.first_coord})
                leaf_slot = (leaf_seed * SEVEN) % 512
                leaf_prana = self._antaranga.prana_at(leaf_slot)
                branch_node.add_child(leaf_idx, {"mode": f"{mode_name}.{sub_mode}", "seed": leaf_seed, "prana": leaf_prana, "words": tuple(leaf_words)})
                if leaf_prana > 0:
                    branch_words[mode_name].extend(leaf_words)
        return {"tree": tree, "tree_nodes": tree.count_nodes(), "branch_words": branch_words}

    def _modulate(self) -> int:
        diw = self._venu.step()
        for slot_idx in range(512):
            if self._antaranga.is_alive(slot_idx):
                self._antaranga.apply_diw(slot_idx, diw)
        return diw

    def _trace_phonemes(self, attractor: int) -> str:
        from vibe_core.mahamantra.research.maha_sequencer import MahaSequencer
        seq = MahaSequencer()
        position = (attractor % WORDS) + KSETRAJNA
        return seq.synthesize(position, length=QUARTERS)

    def generate(self, text: str) -> EngineResult:
        """Lotus-rooted pipeline: Lotus.__call__() → unique language stages → EngineResult."""
        self._ensure_loaded()
        from vibe_core.mahamantra.substrate.language.phonetics import scan_syllable_rhythm
        from vibe_core.mahamantra.substrate.language.composer import compose_from_wave
        from vibe_core.mahamantra.substrate.language.section_router import (
            SECTION_SIGNATURES, extract_template, route_to_section,
        )

        # === LOTUS: The real Maha Mantra computation ===
        lr = self._lotus_compute(text)

        vib = lr.get("vibration", {})
        seed = vib.get("seed", 0)
        attractor = vib.get("attractor", 0)
        rhythm = scan_syllable_rhythm(text)

        self._venu.reset()
        self._venu._tick = seed % WORDS

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

        # === UNIQUE LANGUAGE STAGES (not in Lotus) ===

        # Section routing from attractor
        section_name, verse_num, section_idx = route_to_section(attractor, seed)
        section_sig = SECTION_SIGNATURES.get(section_name, {})
        section_mode = section_sig.get("mode", "CORE")
        template = extract_template(GITA_CHAPTERS, verse_num)

        # Character wave: keystroke → own Antaranga
        char_wave = self._build_character_wave(text)

        # Resonate Lotus smaranam into own Antaranga
        ant = self._resonate_from_lotus(lr, template, seed)

        # Guardian semantic tree expansion
        guardian_name = lr.get("guardian", "")
        exp = self._expand(guardian_name, seed, attractor) if guardian_name else {
            "expanded_names": (), "expansion_depth": 0,
            "expansion_words": (), "synth_walk_words": (), "shabda_children": (),
        }

        # Fractal derivation tree
        sprout = self._sprout_derivation_tree(seed, attractor, guardian_name, exp.get("shabda_children", ()))

        # DIW modulation on own Antaranga
        diw = self._modulate()

        # Phoneme trajectory
        trajectory = self._trace_phonemes(attractor)

        # === COMPOSITION: Antaranga wave → syllable grid → English ===
        output = compose_from_wave(lr, text)

        # === BUILD RESULT ===
        verse = lr.get("verse")
        lotus_ant = lr.get("antaranga", {})
        guna = lr.get("guna", {})

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
            f"→ expand={exp['expansion_depth']}d/{len(exp.get('synth_walk_words', ()))}w "
            f"→ diw=0x{diw:05x} "
            f"→ char_wave={char_wave['char_impacts']}i/{char_wave['char_wave_active']}a "
            f"→ sprout={sprout['tree_nodes']}nodes "
            f"→ antaranga={lotus_ant.get('active_slots', 0)}slots,{lotus_ant.get('total_prana', 0)}prana"
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
            expansion_depth=exp["expansion_depth"],
            expanded_names=exp.get("expanded_names", ()),
            synth_walk_words=exp.get("synth_walk_words", ()),
            diw_applied=diw,
            shabda_spawns=len(exp.get("shabda_children", ())),
            phoneme_trajectory=trajectory,
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
