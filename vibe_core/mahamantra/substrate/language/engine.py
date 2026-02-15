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
    """The Anti-Entropy Language Model — thin orchestrator."""

    def __init__(self) -> None:
        self._llm = None
        self._attention = None
        self._antaranga = None
        self._compressor = None
        self._kernel = None
        self._venu = None

    def _ensure_loaded(self) -> None:
        if self._llm is not None:
            return
        from vibe_core.mahamantra.adapters.attention import MahaAttention
        from vibe_core.mahamantra.adapters.compression import MahaCompression
        from vibe_core.mahamantra.adapters.llm import MahaLLM
        from vibe_core.mahamantra.substrate.antaranga import AntarangaRegistry
        from vibe_core.mahamantra.substrate.maha_llm_kernel import MahaLLMKernel
        from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator
        self._llm = MahaLLM()
        self._attention = MahaAttention()
        self._antaranga = AntarangaRegistry()
        self._compressor = MahaCompression()
        self._kernel = MahaLLMKernel()
        self._venu = VenuOrchestrator()

    def _encode(self, text: str) -> Dict:
        from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
        cached_result = self._attention.attend(text)
        coords = encode_text(text)
        compression = self._compressor.compress(text)
        intent_route = self._llm.route_text(text)
        return {
            "coords": coords, "seed": compression.seed,
            "intent": intent_route.category_name,
            "intent_id": intent_route.intent_id,
            "attention_hit": cached_result.found,
            "cached_result": cached_result.handler if cached_result.found else None,
        }

    def _route(self, text: str, seed: int, coords: tuple) -> Dict:
        from vibe_core.mahamantra.adapters.synth import create_synth
        from vibe_core.mahamantra.substrate.guardian_router import maha_respond
        from vibe_core.mahamantra.substrate.language.section_router import (
            SECTION_SIGNATURES, extract_template, route_to_section,
        )
        synth = create_synth(preset="quantum")
        attractor = synth.resonate(seed).attractor
        guardian_response = maha_respond(text, top_words=SEVEN, seed=seed)
        guardian_resonance = self._kernel.resonate_as(
            text, guardian_response.guardian.name, top_n=SEVEN,
        )
        section_name, verse_num, section_idx = route_to_section(attractor, seed)
        section_sig = SECTION_SIGNATURES.get(section_name, {})
        section_mode = section_sig.get("mode", "CORE")
        template = extract_template(GITA_CHAPTERS, verse_num)
        return {
            "attractor": attractor, "guardian": guardian_response,
            "guardian_resonance": guardian_resonance,
            "section_name": section_name, "section_mode": section_mode,
            "verse_num": verse_num, "template": template,
        }

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

    def _resonate(self, guardian_response, template: List[Dict], seed: int) -> Dict:
        from vibe_core.mahamantra.substrate.antaranga import (
            GENESIS_PRANA_U32, INTEGRITY_FULL,
        )
        from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, COORD_HARMONIC
        resonant_words = guardian_response.words
        word_slots = []
        for i, rw in enumerate(resonant_words):
            if i >= WORDS:
                break
            coord = rw.word.first_coord
            element = int(COORD_ELEMENT[coord]) if coord >= 0 else 0
            harmonic = int(COORD_HARMONIC[coord]) if coord >= 0 else 0
            slot_idx = (coord * SEVEN + seed) % 512
            prana = int(rw.total_score * GENESIS_PRANA_U32)
            integrity = int(rw.total_score * INTEGRITY_FULL)
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
        """Complete pipeline: text in → EngineResult out. Deterministic."""
        self._ensure_loaded()
        from vibe_core.mahamantra.substrate.language.phonetics import scan_syllable_rhythm
        from vibe_core.mahamantra.substrate.language.composer import compose

        enc = self._encode(text)
        coords = enc["coords"]
        seed = enc["seed"]
        rhythm = scan_syllable_rhythm(text)

        self._venu.reset()
        self._venu._tick = seed % WORDS

        if not coords:
            return EngineResult(
                input_text=text, seed=seed, attractor=0, guardian_name="",
                guardian_function="", intent_category=enc["intent"],
                section_name="", section_mode="", verse_ref="",
                resonant_words=(), template_words=(),
                antaranga_active=0, antaranga_prana=0,
                output="[no phonemic content]",
                derivation="input has no encodable phonemes",
                syllable_count=rhythm.syllable_count,
                stress_pattern=rhythm.stress_pattern,
                sequencer_steps=rhythm.sequencer_steps,
            )

        route = self._route(text, seed, coords)
        char_wave = self._build_character_wave(text)
        ant = self._resonate(route["guardian"], route["template"], seed)
        ant["char_wave"] = char_wave

        g = route["guardian"].guardian
        exp = self._expand(g.name, seed, route["attractor"])
        sprout = self._sprout_derivation_tree(seed, route["attractor"], g.name, exp["shabda_children"])
        diw = self._modulate()
        trajectory = self._trace_phonemes(route["attractor"])

        from vibe_core.mahamantra.substrate.language.state_bridge import extract_state_vector
        state_vec = extract_state_vector(prana_level=ant.get("total_prana", 0))

        output = compose(
            route["guardian"], route["template"], rhythm, text,
            route["section_mode"], ant, expansion_data=exp, seed=seed,
            branch_words=sprout["branch_words"], antaranga=self._antaranga,
            state=state_vec,
        )

        derivation = (
            f"seed={seed} → attractor={route['attractor']} "
            f"→ guardian={g.name}({g.function}) "
            f"→ section={route['section_name']}({route['section_mode']}) "
            f"→ verse=BG.18.{route['verse_num']} "
            f"→ rhythm={rhythm.signature}({rhythm.syllable_count}) "
            f"→ expand={exp['expansion_depth']}d/{len(exp['synth_walk_words'])}w "
            f"→ diw=0x{diw:05x} "
            f"→ char_wave={char_wave['char_impacts']}i/{char_wave['char_wave_active']}a "
            f"→ sprout={sprout['tree_nodes']}nodes "
            f"→ antaranga={ant['active_slots']}slots,{ant['total_prana']}prana"
        )

        res_words = tuple(
            (rw.word.sanskrit, rw.word.meanings[0] if rw.word.meanings else "", rw.total_score)
            for rw in route["guardian"].words
        )
        tmpl_words = tuple(
            (tw.get("sanskrit", ""), tw.get("meaning", ""), tw.get("role", ""))
            for tw in route["template"][:WORDS]
        )

        return EngineResult(
            input_text=text, seed=seed, attractor=route["attractor"],
            guardian_name=g.name, guardian_function=g.function,
            intent_category=enc["intent"],
            section_name=route["section_name"], section_mode=route["section_mode"],
            verse_ref=f"BG.18.{route['verse_num']}",
            resonant_words=res_words, template_words=tmpl_words,
            antaranga_active=ant["active_slots"], antaranga_prana=ant["total_prana"],
            output=output, derivation=derivation,
            attention_cached=False, expansion_depth=exp["expansion_depth"],
            expanded_names=exp["expanded_names"],
            synth_walk_words=exp["synth_walk_words"],
            diw_applied=diw, shabda_spawns=len(exp["shabda_children"]),
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
