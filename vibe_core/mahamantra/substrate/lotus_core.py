"""
MAHAMANTRA LOTUS - The Root Class (Lazy Loaded)
===============================================

This file contains the MahamantraLotus class, extracted from __init__.py
for lazy loading via __getattr__.

SIKSASTAKAM: This class is only loaded when explicitly imported.
"""

from __future__ import annotations

__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x7340d7d6"

import logging
import sys
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union

if TYPE_CHECKING:
    from vibe_core.mahamantra.reactor.shadow import ShadowReactorFactory
    from vibe_core.mahamantra.reactor.shadow_protocol import (
        ShadowReactorProtocol,
        ShadowState,
        TickStateInput,
    )

# These imports are needed for class definition
from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol
from vibe_core.mahamantra.protocols._header import MahaCell, MahaHeader, HEADER_SIZE_BYTES, HEADER_DAILY_CYCLES
from vibe_core.mahamantra.seed.types import (
    AkashState,
    ExecuteResult,
    GitaRoute,
    RouteResult,
    VibrationState,
)
from vibe_core.mahamantra.substrate.lotus_types import LotusNode, LotusPath
from vibe_core.mahamantra.protocols._pancha import TattvaDict
from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
from vibe_core.mahamantra.substrate.tattva_registry import get_registry

logger = logging.getLogger("MAHAMANTRA")

_THIS_MODULE = sys.modules[__name__]


# =============================================================================
# PIPELINE CACHE — Precomputed seed-independent lookups for __call__()
# =============================================================================
# Same pattern as LexiconVectorCache: build once, use forever.
# Eliminates ~30 lazy imports and ~15 function calls per __call__() invocation.


class _PipelineCache:
    """Seed-independent data resolved once at first use."""

    __slots__ = (
        # Constants (from _seed.py — the 7 axioms and derivations)
        'WORDS', 'MAHA_QUANTUM', 'PARAMPARA', 'KSETRAJNA', 'MAX_CYCLES',
        # Stateless callables (function references, no owned state)
        'encode_text', 'synth_transform',
        'rank_words', 'match_attractor', 'get_gita_chapter',
        'get_chapter_significance', 'is_fruit',
        'verse_words',
        'diw_unpack',
        'get_shadow_oracle',
        'get_chamber',
        'get_shadow_reactor_factory',
        # Classes (type references, not instances)
        'MahaCellUnified', 'register_cell', 'TickStateInput',
        # Position LUTs (length = WORDS = 16, precomputed tuples)
        'ALL_GUARDIANS', 'MAHAMANTRA_SEQUENCE', 'THE_FLUTE_CYCLE',
        'quarter_names', 'is_head_flags',
        'quarter_head_names', 'holy_names', 'trinity_functions',
        'rama_coords', 'phonemes', 'roles',
        # Phoneme signature LUTs (indexed by rama_coord, length = 49)
        # These are module-level tuples in pancha_walk.py — we hold references.
        'COORD_ELEMENT', 'COORD_VARGA', 'COORD_SUB', 'COORD_HARMONIC',
        'ELEMENT_NAMES', 'IS_SHRUTI',
        # Precomputed DIW components (length = WORDS = 16)
        'diw_components',
    )

    def __init__(self) -> None:
        # --- Constants ---
        # NOTE: Compressor is NOT cached here — MahamantraLotus owns it
        # via _get_compressor() (class-level singleton). No duplication.
        from vibe_core.mahamantra.protocols._seed import (
            MAHA_QUANTUM, PARAMPARA, WORDS,
            KSETRAJNA, QUARTERS,
            get_name_at_position, get_quarter_head, get_trinity_function,
            is_head,
        )
        self.WORDS = WORDS
        self.MAHA_QUANTUM = MAHA_QUANTUM
        self.PARAMPARA = PARAMPARA
        self.KSETRAJNA = KSETRAJNA
        self.MAX_CYCLES = QUARTERS

        # --- Stateless callables (resolved once, no owned state) ---
        from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
        self.encode_text = encode_text

        # MahaModularSynth is stateless (pure function: seed → attractor).
        # No singleton exists elsewhere — safe to own one instance here.
        from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
        self.synth_transform = MahaModularSynth(default_preset="quantum").transform

        from vibe_core.mahamantra.substrate.resonance_ranker import rank_words
        self.rank_words = rank_words

        from vibe_core.mahamantra.adapters.gita_resonance import match_attractor
        self.match_attractor = match_attractor

        from vibe_core.mahamantra.protocols._maha_compute import get_gita_chapter
        self.get_gita_chapter = get_gita_chapter

        from vibe_core.mahamantra.substrate.gita import get_chapter_significance
        self.get_chapter_significance = get_chapter_significance

        from vibe_core.mahamantra.protocols._seed import is_fruit
        self.is_fruit = is_fruit

        from vibe_core.mahamantra.substrate.sanskrit_lookup import verse_words
        self.verse_words = verse_words

        from vibe_core.mahamantra.protocols.diw import unpack as diw_unpack
        self.diw_unpack = diw_unpack

        from vibe_core.mahamantra.reactor.shadow_oracle import get_shadow_oracle
        self.get_shadow_oracle = get_shadow_oracle

        from vibe_core.mahamantra.substrate.chamber import get_chamber
        self.get_chamber = get_chamber

        from vibe_core.mahamantra.reactor.shadow import get_shadow_reactor_factory
        self.get_shadow_reactor_factory = get_shadow_reactor_factory

        # --- Classes (type references, not instances) ---
        from vibe_core.mahamantra.substrate.cell import MahaCellUnified
        self.MahaCellUnified = MahaCellUnified

        from vibe_core.mahamantra.substrate.cell_router import register_cell
        self.register_cell = register_cell

        from vibe_core.mahamantra.reactor.shadow_protocol import TickStateInput
        self.TickStateInput = TickStateInput

        # --- Static LUTs (length = WORDS) ---
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, get_quarter_name
        self.ALL_GUARDIANS = ALL_GUARDIANS

        from vibe_core.mahamantra.substrate.venu_orchestrator import THE_FLUTE_CYCLE
        self.THE_FLUTE_CYCLE = THE_FLUTE_CYCLE

        from vibe_core.mahamantra.substrate.opcode import MAHAMANTRA_SEQUENCE
        self.MAHAMANTRA_SEQUENCE = MAHAMANTRA_SEQUENCE

        # Precompute per-position lookups (16 entries each)
        self.quarter_names = tuple(get_quarter_name(p) for p in range(WORDS))
        self.is_head_flags = tuple(is_head(p) for p in range(WORDS))
        self.quarter_head_names = tuple(
            ALL_GUARDIANS[get_quarter_head(p)] for p in range(WORDS)
        )
        self.holy_names = tuple(get_name_at_position(p) for p in range(WORDS))
        self.trinity_functions = tuple(get_trinity_function(p) for p in range(WORDS))
        self.roles = tuple("avatara" if is_head(p) else "mahajana" for p in range(WORDS))

        # RAMA grid lookups (16 entries)
        from vibe_core.mahamantra.substrate.rama_grid import krishna_route, rama_to_phoneme
        self.rama_coords = tuple(krishna_route(p) for p in range(WORDS))
        self.phonemes = tuple(rama_to_phoneme(krishna_route(p)) for p in range(WORDS))

        # Precompute DIW components (16 entries)
        self.diw_components = tuple(diw_unpack(THE_FLUTE_CYCLE[p]) for p in range(WORDS))

        # --- Phoneme signature tables (references to module-level tuples) ---
        from vibe_core.mahamantra.substrate.pancha_walk import (
            COORD_ELEMENT, COORD_VARGA, COORD_SUB, COORD_HARMONIC,
            ELEMENT_NAMES, IS_SHRUTI,
        )
        self.COORD_ELEMENT = COORD_ELEMENT
        self.COORD_VARGA = COORD_VARGA
        self.COORD_SUB = COORD_SUB
        self.COORD_HARMONIC = COORD_HARMONIC
        self.ELEMENT_NAMES = ELEMENT_NAMES
        self.IS_SHRUTI = IS_SHRUTI


_PIPELINE: Optional[_PipelineCache] = None


def _get_pipeline() -> _PipelineCache:
    """Get or create the PipelineCache singleton."""
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = _PipelineCache()
    return _PIPELINE


class MahamantraLotus(LotusNode, GADBase, GADProtocol):
    """
    The Root of the Lotus.

    This is the only node that knows HOW to execute and resonate.
    Now with AKASH CACHE (136 = FIELD) - Always vibrating!
    """

    # Class-level Akash state (the 136 FIELD - persistent across instances)
    _akash: AkashState = {
        "resonance_level": 0,
        "accumulated_value": 0,
        "total_beats": 0,
        "total_rounds": 0,
        "attractor_counts": {},
        "last_seed": None,
        "last_position": None,
        "last_attractor": None,
    }

    # TattvaGate — which gate is currently active during __call__
    _active_gate: Optional[TattvaGate] = None

    # Gate hooks — callbacks fired at gate boundaries
    # Key: TattvaGate, Value: list of callables(gate, context_dict)
    _gate_hooks: Dict[TattvaGate, List] = {}

    # Lazy-loaded instances
    _compressor = None
    _gita_index = None
    _gita_by_attractor = None
    _pipeline = None
    _singularity_instance = None
    _kernel_instance = None

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold truth of MahamantraLotus — the Root."""
        gate = self._active_gate
        return {
            "chaitanya": "MahamantraLotus — Root of all computation (16 words, 9 NavaBhakti, 5 TattvaGates)",
            "nityananda": "PipelineCache (LUT), MahaCompression (seed), VenuOrchestrator (flute), Singularity (kernel)",
            "advaita": "__call__(input) → PARSE→VALIDATE→EXECUTE→RESULT→SYNC → deterministic response",
            "gadadhara": f"active_gate={gate.name if gate else 'IDLE'}, rounds={self._akash['total_rounds']}, beats={self._akash['total_beats']}",
            "srivasa": "Parampara verification, ShadowOracle, Yajna cycle, Antaranga chamber",
        }

    @property
    def active_gate(self) -> Optional[TattvaGate]:
        """Which TattvaGate is currently active. None if idle."""
        return self._active_gate

    def on_gate(self, gate: TattvaGate, callback) -> None:
        """
        Register a callback to fire when a TattvaGate is entered.

        callback(gate: TattvaGate, ctx: dict) -> None
            gate: which gate was entered
            ctx: mutable dict with pipeline state at that point
        """
        if gate not in self._gate_hooks:
            self._gate_hooks[gate] = []
        self._gate_hooks[gate].append(callback)

    def _fire_gate(self, gate: TattvaGate, ctx: Dict[str, object]) -> None:
        """Set active gate and fire registered hooks."""
        self._active_gate = gate
        for hook in self._gate_hooks.get(gate, ()):
            try:
                hook(gate, ctx)
            except Exception as exc:
                logger.warning("Gate hook error at %s: %s", gate.name, exc)

    def __init__(self) -> None:
        LotusNode.__init__(self, LotusPath())
        GADBase.__init__(self)
        get_registry().register("mahamantra_lotus", self)

    @classmethod
    def _get_compressor(cls):
        """Lazy-load MahaCompression."""
        if cls._compressor is None:
            from vibe_core.mahamantra.adapters.compression import MahaCompression

            cls._compressor = MahaCompression()
        return cls._compressor

    def _compute_vibration(self, input_data):
        """Compute vibration state from input."""
        from vibe_core.mahamantra.kernel.maha_kernel import get_kernel
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, PARAMPARA

        compressor = self._get_compressor()
        kernel = get_kernel()

        # Kernel handles str or MahaCell and returns 16-bit address
        attractor = kernel(input_data)

        # Seed is needed for return dict, extract it manually
        if isinstance(input_data, MahaCell):
            seed = input_data.header.sravanam
        else:
            comp_result = compressor.compress(str(input_data))
            seed = comp_result.seed

        return {
            "seed": seed,
            "attractor": attractor,
            "resonance": seed % MAHA_QUANTUM,
            "parampara_verified": seed % PARAMPARA == 0,
        }

    def vibrate(self, input_data: Union[str, MahaCell]) -> VibrationState:
        """
        Public API for vibration.

        Delegates to _compute_vibration (internal logic).
        """
        return self._compute_vibration(input_data)

    def tick(self) -> Dict[str, Union[str, int]]:
        """
        Advance one position in the 16-word mantra.

        Delegates to Singularity.tick() which:
        - Advances Kala (time)
        - Plays the flute (VenuOrchestrator.step() → DIW)
        - Broadcasts TickState to all listeners via Singularity._broadcast()

        One tick. One DIW. One broadcast. Krishna plays His flute.
        """
        return self._get_singularity().tick()

    # ==========================================================================
    # LISTENER MANAGEMENT — delegates to Singularity (one list, one broadcast)
    # ==========================================================================
    # GAD-000 Amendment B: "Every Agent must implement a Japa-Loop (Heartbeat)"
    # All listeners live in Singularity._listeners. Lotus delegates.

    def register_listener(self, callback) -> None:
        """
        Register a listener for tick events.

        Delegates to Singularity.register_listener() — one listener list
        for the entire system. No dual-broadcast.

        Args:
            callback: Function that accepts tick state dict
        """
        self._get_singularity().register_listener(callback)
        logger.debug(f"🔗 Listener registered via Singularity")

    def unregister_listener(self, callback) -> None:
        """Remove a listener from tick events."""
        listeners = self._get_singularity()._listeners
        if callback in listeners:
            listeners.remove(callback)

    def _broadcast(self, state: Dict) -> None:
        """
        Broadcast tick state to all listeners.

        Delegates to Singularity._broadcast() — one broadcast channel.
        Used by LotusBridge to inject VenuService-driven ticks.
        """
        self._get_singularity()._broadcast(state)

    _bootstrapped: bool = False

    def bootstrap(self, *, silent: bool = False, lazy: bool = True) -> None:
        """
        Initialize the Mahamantra system.

        Args:
            silent: Suppress logging
            lazy: If True, defer heavy service loading until first use
        """
        if self._bootstrapped:
            return

        _log = logging.getLogger("MAHAMANTRA")

        if not lazy:
            # EAGER mode (old behavior) - load everything now
            try:
                from vibe_core.services import maha_compute_service

                if not silent:
                    _log.info("MahaComputeService activated")
            except ImportError as e:
                if not silent:
                    _log.debug(f"MahaComputeService not available: {e}")

            try:
                from vibe_core.mahamantra.adapters.llm import MahaLLM

                kapila = self.dharma.kapila.get_kapila_service()
                kapila.register_cognitive(MahaLLM())
                if not silent:
                    _log.info("Kapila cognition wired with MahaLLM")
            except Exception as e:
                if not silent:
                    _log.debug(f"Kapila cognition wiring failed: {e}")

        self._bootstrapped = True
        if not silent:
            _log.info("Mahamantra bootstrap complete (lazy mode)" if lazy else "Mahamantra bootstrap complete")

    def execute(self, command: str, args: Optional[List[str]] = None) -> ExecuteResult:
        """Execute a command through the Mahamantra. SSOT: delegates to __call__."""
        try:
            result = self(command)  # __call__ is the SSOT - returns EVERYTHING
        except Exception as exc:
            # TRUTH: Surface errors, don't swallow them
            logger.error("Mahamantra execute failed: %s", exc)
            return {
                "success": False,
                "command": command,
                "exit_code": 1,
                "error": str(exc),
                "handler": "mahamantra[error]",
            }
        # Success is DERIVED from cell state, not hardcoded
        cell_alive = result.get("cell", {}).get("is_alive", False)
        result["success"] = cell_alive
        result["command"] = command
        result["exit_code"] = 0 if cell_alive else 1
        result["handler"] = f"mahamantra[{result['position']}]"
        return result

    def __call__(self, input_data: Union[str, MahaCell]) -> Dict[str, object]:
        """
        MANTRA-BASED COMPUTING.

        mahamantra("anything") → READS. UNDERSTANDS. COMPUTES. RESPONDS.

        NO registry. NO services. NO delegation.
        Pure computation from the 16 words.

        TATTVA GATE PIPELINE (5 Gates × NavaBhakti Steps):
        ===================================================
        GATE 0 — CHAITANYA (PARSE/Identity):
            1. SRAVANAM       — Receive input (hearing)
            1.5 NAMA          — Phonetic identity (RAMA coords)
            2. KIRTANAM       — MahaCompression → seed (chanting)

        GATE 1 — NITYANANDA (VALIDATE/Substrate):
            3. PADA_SEVANAM   — Attractor from seed (serving)
            4. ARCANAM        — Parampara verification (worshiping)

        GATE 2 — ADVAITA (EXECUTE/Bridge):
            5. SMARANAM       — Word resonance (remembering)
            6. VANDANAM       — GitaResonance → verse match (praying)

        GATE 3 — GADADHARA (RESULT/Energy):
            7. DASYAM         — Position/Quarter determination (servitude)
            7.5 SHABDA        — RAMA Grid phoneme signature

        GATE 4 — SRIVASA (SYNC/Governance):
            8. SAKHYAM        — MahaCell creation (friendship)
            8.5-8.7 KIRTAN    — Chamber + Yajna cycle
            9. ATMA_NIVEDANAM — Complete response (surrender)

        Everything computed. No external LLM. No hardcoded routing.
        """
        # All seed-independent references resolved once via PipelineCache.
        # Compressor owned by MahamantraLotus (class-level singleton).
        P = _get_pipeline()
        WORDS = P.WORDS
        MAHA_QUANTUM = P.MAHA_QUANTUM

        # =====================================================================
        # GATE 0: CHAITANYA — PARSE / Identity
        # "Who/What is this?" — Receive, identify, compress.
        # =====================================================================
        self._fire_gate(TattvaGate.PARSE, {"input_data": input_data})

        # 1. SRAVANAM - Receive input (Entry point)
        if isinstance(input_data, MahaCell):
            cell = input_data
            input_text = cell.payload.decode("utf-8", errors="replace")
            seed = cell.header.sravanam
        else:
            input_text = str(input_data)
            cell = None
            seed = None

        # =====================================================================
        # 1.5. NAMA - Phonetic Identity (RAMA coordinate sequence)
        # =====================================================================
        input_coords = tuple(P.encode_text(input_text))

        # =====================================================================
        # 2. KIRTANAM - MahaCompression → seed
        # =====================================================================
        if seed is None:
            comp_result = self._get_compressor().compress(input_text)
            seed = comp_result.seed

        # SEED IS PURE: Same input → same seed. Always.

        # =====================================================================
        # GATE 1: NITYANANDA — VALIDATE / Substrate
        # "What does this rest upon?" — Derive attractor, verify parampara.
        # =====================================================================
        self._fire_gate(TattvaGate.VALIDATE, {"input_text": input_text, "seed": seed, "input_coords": input_coords})

        # 3. PADA_SEVANAM - Attractor from Seed (Serial, not Parallel)
        # Pipeline: text → compress → seed → synth → attractor (SERIAL)
        attractor = P.synth_transform(seed)
        variance = seed & 0xFF
        raw_address = (attractor << 8) | variance  # 16-bit Hybrid Address

        # =====================================================================
        # 4. ARCANAM - Parampara verification via ShadowOracle (Gita 13.35)
        # =====================================================================
        oracle = P.get_shadow_oracle()
        oracle_validation = oracle.validate(seed)
        parampara_verified = oracle_validation["parampara_validated"]
        parampara_channel = oracle_validation["parampara_channel"]
        parampara_coherence = oracle_validation["coherence"]

        # =====================================================================
        # GATE 2: ADVAITA — EXECUTE / Bridge
        # "How does this connect?" — Resonance + verse matching.
        # =====================================================================
        self._fire_gate(TattvaGate.EXECUTE, {"seed": seed, "attractor": attractor, "parampara_verified": parampara_verified})

        # 5. SMARANAM - Word Resonance (Remembering)
        resonant_words = P.rank_words(
            input_coords=input_coords,
            input_attractor=attractor,
            top_n=7,
        ) if input_coords else []

        # =====================================================================
        # 6. VANDANAM - GitaResonance → verse match
        # =====================================================================
        verse_result = P.match_attractor(attractor)
        chapter = P.get_gita_chapter(attractor)
        chapter_significance = P.get_chapter_significance(chapter)

        # TOPOLOGY: Field (Ch 1-16) = process, Fruit (Ch 17-18) = complete
        gita_phase = "fruit" if P.is_fruit(chapter) else "field"
        is_complete = P.is_fruit(chapter)  # Stopping condition

        verse_info = None
        if verse_result.matches:
            verse_index = seed % len(verse_result.matches)
            v = verse_result.matches[verse_index]
            verse_info = {
                "id": v.verse_id,
                "chapter": v.chapter,
                "verse": v.verse,
                "guna": v.guna,
                "dominant_name": v.dominant_name,
                "significance": chapter_significance,
            }

            sanskrit = P.verse_words(v.chapter, v.verse)
            if sanskrit:
                verse_info["word_count"] = len(sanskrit.words)
                verse_info["phoneme_count"] = sanskrit.phoneme_count
                verse_info["words"] = tuple({"sanskrit": w.sanskrit, "meaning": w.meaning} for w in sanskrit.words)

        # =====================================================================
        # GATE 3: GADADHARA — RESULT / Energy
        # "How does energy flow?" — Position, phoneme, routing.
        # =====================================================================
        self._fire_gate(TattvaGate.RESULT, {"attractor": attractor, "resonant_words": resonant_words, "verse_result": verse_result})

        # 7. DASYAM - Position/Quarter/Role determination
        # Position from attractor (holographic - embedded in computation)
        position = attractor % WORDS  # 0-15

        # All position-dependent lookups are precomputed LUTs in PipelineCache
        diw = P.THE_FLUTE_CYCLE[position]
        diw_comp = P.diw_components[position]
        quarter = P.quarter_names[position]
        guardian = P.ALL_GUARDIANS[position]
        role = P.roles[position]
        quarter_head_name = P.quarter_head_names[position]
        holy_name = P.holy_names[position]
        trinity_function = P.trinity_functions[position]

        # =====================================================================
        # 7.5. SHABDA - RAMA Grid Phoneme + 4D Coordinate Signature
        # =====================================================================
        # Precomputed: position → rama_coord → phoneme (all in PipelineCache)
        rama_coord = P.rama_coords[position]
        phoneme = P.phonemes[position]
        phoneme_element = P.COORD_ELEMENT[rama_coord]
        phoneme_varga = P.COORD_VARGA[rama_coord]
        phoneme_sub = P.COORD_SUB[rama_coord]
        phoneme_harmonic = P.COORD_HARMONIC[rama_coord]
        phoneme_shruti = P.IS_SHRUTI[rama_coord]

        # =====================================================================
        # GATE 4: SRIVASA — SYNC / Governance
        # "Who governs this?" — Cell creation, chamber, yajna, response.
        # =====================================================================
        self._fire_gate(TattvaGate.SYNC, {"position": position, "guardian": guardian, "seed": seed, "attractor": attractor})

        # 8. SAKHYAM - MahaCellUnified creation (holographic format with lifecycle)
        result_cell = P.MahaCellUnified.create(
            source=seed,
            target=raw_address,
            operation=position,
            dna=input_text,
        )

        P.register_cell(result_cell)

        # =====================================================================
        # 8.5. KIRTAN - Call and Response Loop
        # =====================================================================
        chamber = P.get_chamber()

        # 8.4b. ANTARANGA - Resonant words flow into Inner Chamber
        antaranga_collisions = 0
        if resonant_words:
            antaranga_collisions = chamber.resonate_words(resonant_words, attractor)

        # KIRTAN LOOP: cycles × WORDS (16) transformations
        kirtan_cycles = min(
            P.KSETRAJNA + self._akash["total_rounds"] // WORDS,
            P.MAX_CYCLES,
        )
        result_cell = chamber.kirtan(result_cell, cycles=kirtan_cycles)

        # =====================================================================
        # 8.6. SPELL_KIRTAN - Input Melody over Heartbeat
        # =====================================================================
        if input_coords:
            result_cell = chamber.spell_kirtan(result_cell, input_coords)

        # =====================================================================
        # 8.7. YAJNA CYCLE - ShadowReactor Integration (Bhoga→Prasadam→Return)
        # =====================================================================
        reactor = P.get_shadow_reactor_factory().spawn(
            auto_discover=False,
            initial_position=position,
            forced_lagna=0,
        )

        # SANKIRTAN AUTHORIZATION
        reactor.chant(_THIS_MODULE)

        # Inject MahaCell into reactor for payload flow
        reactor.set_maha_cell(
            MahaCell(
                header=MahaHeader.create(
                    source=seed,
                    target=raw_address,
                    operation=position,
                    link=0,
                    intent=0,
                    ttl=HEADER_DAILY_CYCLES,
                    state=0,
                ),
                payload=input_text.encode("utf-8"),
            )
        )

        # =================================================================
        # FULL YAJNA CYCLE: WORDS ticks (Bhoga→Switch→Prasadam→Return)
        # =================================================================
        shadow_state = None
        guardian_result = None
        base_tick = self._akash["total_beats"]

        for i in range(WORDS):
            tick_pos = (position + i) % WORDS
            tick_word, tick_opcode = P.MAHAMANTRA_SEQUENCE[tick_pos]
            tick_guardian = P.ALL_GUARDIANS[tick_pos]
            tick_quarter = P.quarter_names[tick_pos]

            tick_input: P.TickStateInput = {
                "tick": base_tick + i,
                "position": tick_pos,
                "quarter": tick_quarter,
                "guardian": tick_guardian,
                "word": tick_word,
                "opcode": tick_opcode.value,
            }

            shadow_state = reactor.tick(tick_input)

            tick_result = shadow_state.get("execution_result")
            if tick_result is not None:
                guardian_result = tick_result

        # =====================================================================
        # 9. ATMA_NIVEDANAM - Complete response (all paths converge)
        # =====================================================================
        self._akash["total_beats"] += WORDS
        self._akash["total_rounds"] += 1
        self._akash["accumulated_value"] = (self._akash["accumulated_value"] + attractor) % MAHA_QUANTUM
        self._akash["attractor_counts"][attractor] = self._akash["attractor_counts"].get(attractor, 0) + 1

        self._akash["last_seed"] = seed
        self._akash["last_position"] = position
        self._akash["last_attractor"] = attractor

        # Pipeline complete — reset gate
        self._active_gate = None

        return {
            "input": input_text,
            "tattva_gate": "SRIVASA",  # last gate = SYNC (all 5 gates passed)
            "vibration": {
                "seed": seed,
                "attractor": attractor,
                "rama_index": rama_coord,
                "phoneme": phoneme,
                "signature": {
                    "element": P.ELEMENT_NAMES[phoneme_element],
                    "varga": phoneme_varga,
                    "sub": phoneme_sub,
                    "harmonic": phoneme_harmonic,
                    "shruti": phoneme_shruti,
                    "frequency": phoneme_harmonic * 3 + phoneme_element * 15,
                },
            },
            "parampara": {
                "verified": parampara_verified,
                "channel": parampara_channel,
                "coherence": parampara_coherence,
            },
            "chapter": chapter,
            "chapter_significance": chapter_significance,
            "verse": verse_info,
            "matches": len(verse_result.matches),
            "gita_phase": gita_phase,
            "is_complete": is_complete,
            "position": position,
            "guardian": guardian,
            "quarter": quarter,
            "role": role,
            "quarter_head": quarter_head_name,
            "holy_name": holy_name,
            "trinity_function": trinity_function,
            "diw": {
                "raw": diw,
                "venu": diw_comp.venu,
                "vamsi": diw_comp.vamsi,
                "murali": diw_comp.murali,
            },
            "cell": {
                "header_size": HEADER_SIZE_BYTES,
                "payload_size": len(input_text.encode("utf-8")),
                "total_size": HEADER_SIZE_BYTES + len(input_text.encode("utf-8")),
                "valid": True,
                "parampara_verified": parampara_verified,
                "prana": result_cell.prana,
                "integrity": result_cell.membrane_integrity,
                "is_alive": result_cell.is_alive,
                "cycle": result_cell.age,
            },
            "nama": {
                "coords": input_coords,
                "phoneme_count": len(input_coords),
            },
            "smaranam": tuple(
                {
                    "sanskrit": rw.word.sanskrit,
                    "meaning": rw.word.first_meaning,
                    "score": rw.total_score,
                }
                for rw in resonant_words
            ),
            "antaranga": {
                "active_slots": chamber.antaranga.active_count(),
                "total_prana": chamber.antaranga.total_prana(),
                "collisions": antaranga_collisions,
                "size_bytes": chamber.antaranga.size_bytes,
            },
            "akash": self._akash,
            "execution": {
                "success": result_cell.is_alive,
                "prana": result_cell.prana,
                "integrity": result_cell.membrane_integrity,
                "kirtan_cycles": kirtan_cycles,
                "transformations": kirtan_cycles * WORDS,
                "yajna_ticks": WORDS,
                "cycles": result_cell.age,
                "guardian_acted": guardian_result is not None,
                "guardian_result": guardian_result,
            },
            "yajna": {
                "phase": shadow_state.get("phase"),
                "cycle_count": shadow_state.get("cycle_count", 0),
                "switch_count": shadow_state.get("switch_count", 0),
                "return_count": shadow_state.get("return_count", 0),
                "dissonance": shadow_state.get("dissonance_report"),
            },
            "gate_trace": (
                TattvaGate.PARSE.name,
                TattvaGate.VALIDATE.name,
                TattvaGate.EXECUTE.name,
                TattvaGate.RESULT.name,
                TattvaGate.SYNC.name,
            ),
        }

    # =========================================================================
    # VENU - Krishna's Flute (Non-Different from Krishna)
    # =========================================================================

    _venu_orchestrator = None

    @property
    def venu(self):
        """
        Venu-madhurya (Quality 63) — Krishna's Wonderful Flute.

        Property takes precedence over LotusNode.__getattr__ which would
        find the venu/ folder. The flute IS Krishna (acintya-bheda-abheda).
        """
        if MahamantraLotus._venu_orchestrator is None:
            from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

            MahamantraLotus._venu_orchestrator = VenuOrchestrator()
        return MahamantraLotus._venu_orchestrator

    # =========================================================================
    # SINGULARITY — The Inner Mahamantra (Prema-madhurya: Relations)
    # =========================================================================

    def _get_singularity(self):
        """Lazy-load the Singularity (Mahamantra inner engine)."""
        if MahamantraLotus._singularity_instance is None:
            from vibe_core.mahamantra.kernel.singularity import Mahamantra

            MahamantraLotus._singularity_instance = Mahamantra()
        return MahamantraLotus._singularity_instance

    # =========================================================================
    # PREMA-MADHURYA (Quality 62) — Positions & Relations
    # Guardian names as properties — delegates to Singularity.
    # Properties take precedence over LotusNode.__getattr__.
    # =========================================================================

    @property
    def brahma(self):
        """Position 1 - BRAHMA (Creation)."""
        return self._get_singularity().brahma

    @property
    def narada(self):
        """Position 2 - NARADA (Devotion)."""
        return self._get_singularity().narada

    @property
    def shambhu(self):
        """Position 3 - SHAMBHU (Transformation)."""
        return self._get_singularity().shambhu

    @property
    def kumaras(self):
        """Position 5 - KUMARAS (Purification)."""
        return self._get_singularity().kumaras

    @property
    def kapila(self):
        """Position 6 - KAPILA (Analysis)."""
        return self._get_singularity().kapila

    @property
    def manu(self):
        """Position 7 - MANU (Law)."""
        return self._get_singularity().manu

    @property
    def prahlada(self):
        """Position 9 - PRAHLADA (Resilience)."""
        return self._get_singularity().prahlada

    @property
    def janaka(self):
        """Position 10 - JANAKA (Duty)."""
        return self._get_singularity().janaka

    @property
    def bhishma(self):
        """Position 11 - BHISHMA (Vow)."""
        return self._get_singularity().bhishma

    @property
    def bali(self):
        """Position 13 - BALI (Surrender)."""
        return self._get_singularity().bali

    @property
    def shuka(self):
        """Position 14 - SHUKA (Vision)."""
        return self._get_singularity().shuka

    @property
    def yamaraja(self):
        """Position 15 - YAMARAJA (Judgment)."""
        return self._get_singularity().yamaraja

    @property
    def prithu(self):
        """Position 4 - PRITHU (HEAD - Dharma)."""
        return self._get_singularity().prithu

    @property
    def vyasa(self):
        """Position 0 - VYASA (HEAD - Genesis)."""
        return self._get_singularity().vyasa

    @property
    def parashurama(self):
        """Position 8 - PARASHURAMA (HEAD - Karma)."""
        return self._get_singularity().parashurama

    @property
    def nrisimha(self):
        """Position 12 - NRISIMHA (HEAD - Moksha)."""
        return self._get_singularity().nrisimha

    # =========================================================================
    # RUPA-MADHURYA (Quality 64 = FIXPOINT) — Algorithm / Form
    # =========================================================================

    @property
    def kernel(self):
        """
        Rupa-madhurya (Quality 64) — The Beautiful Form.

        Returns the callable MahaKernel (not the kernel/ folder).
        64 is a fixed point: f(64) = 64. The form needs no transformation.
        """
        if MahamantraLotus._kernel_instance is None:
            from vibe_core.mahamantra.kernel.maha_kernel import get_kernel

            MahamantraLotus._kernel_instance = get_kernel()
        return MahamantraLotus._kernel_instance

    # =========================================================================
    # CONVERGENCE — mod/proto routers (Singularity delegation)
    # =========================================================================

    @property
    def mod(self):
        """ModuleRouter — routes to all 16 Mahajana modules."""
        return self._get_singularity().mod

    @property
    def proto(self):
        """ProtocolRouter — routes to all 16 protocol bases."""
        return self._get_singularity().protocols

    @property
    def steward(self):
        """Lazy access to the Steward resonance router (LEGACY - use __call__ instead)."""
        from vibe_core.mahamantra.cli.steward import get_steward

        return get_steward()

    @property
    def shadow(self):
        """Lazy access to Shadow Reactor Factory."""
        from vibe_core.mahamantra.reactor.shadow import get_shadow_reactor_factory

        return get_shadow_reactor_factory()

    # === Quarter Properties (Lazy) ===

    @property
    def genesis(self):
        """Access Genesis quarter."""
        return self._get_quarter("genesis")

    @property
    def dharma(self):
        """Access Dharma quarter."""
        return self._get_quarter("dharma")

    @property
    def karma(self):
        """Access Karma quarter."""
        return self._get_quarter("karma")

    @property
    def moksha(self):
        """Access Moksha quarter."""
        return self._get_quarter("moksha")

    @property
    def pipeline(self):
        """Access MahamantraPipeline adapter (Lazy Singleton)."""
        if self._pipeline is None:
            from vibe_core.mahamantra.adapters.pipeline import MahamantraPipeline

            self._pipeline = MahamantraPipeline()
        return self._pipeline

    def _get_quarter(self, name: str):
        """Lazy-load quarter module."""
        import importlib

        module = importlib.import_module(f"vibe_core.mahamantra.{name}")
        module = importlib.import_module(f"vibe_core.mahamantra.{name}")
        return module

    # === Adapters (Lazy) ===

    @property
    def transform(self):
        """Access MahaTransform adapter."""
        if not hasattr(self, "_transform_adapter"):
            from vibe_core.mahamantra.adapters.transform import MahaTransform

            self._transform_adapter = MahaTransform()
        return self._transform_adapter

    @property
    def hash(self):
        """Access MahaHash adapter."""
        if not hasattr(self, "_hash_adapter"):
            from vibe_core.mahamantra.adapters.hash import MahaHash

            self._hash_adapter = MahaHash()
        return self._hash_adapter

    @property
    def orchestrator(self):
        """Access Orchestrator adapter."""
        if not hasattr(self, "_orchestrator_adapter"):
            from vibe_core.mahamantra.adapters.orchestrator import Orchestrator

            self._orchestrator_adapter = Orchestrator()
        return self._orchestrator_adapter

    @property
    def gita(self):
        """Access Gita Resonance adapter."""
        import vibe_core.mahamantra.adapters.gita_resonance as gita

        return gita

    def router(self, *args, **kwargs):
        """Create a generic Router."""
        from vibe_core.mahamantra.adapters.routing import Router

        return Router(*args, **kwargs)

    # === IPv6-LIKE ROUTING (O(1) Cell Registry) ===

    @property
    def cells(self):
        """
        Access the CellRouter (O(1) Cell Registry).

        MAHAMANTRA = IPv6 ROUTER:
            16 words = 128 bits = IPv6 address space
            Every cell gets auto-generated address from content.
            O(1) lookup via LotusTree structure.

        USAGE:
            cell = mahamantra.cell_from_content("any content")
            found = mahamantra.cells[cell.header.sravanam]

        "sarvasya cāhaṁ hṛdi sanniviṣṭo" - I am seated in everyone's heart.
        """
        from vibe_core.mahamantra.substrate.cell_router import get_router

        return get_router()

    def cell_from_content(self, content: str, *, register: bool = True):
        """
        Create a MahaCell from ANY content. Address computed automatically.

        MAHACELL = ANYTHING:
            - Pass any string content
            - Address is computed via MahaCompression (Kolmogorov-inspired)
            - Cell is auto-registered in CellRouter for O(1) lookup
            - Returns fully-formed MahaCellUnified

        USAGE:
            cell = mahamantra.cell_from_content("my content")
            found = mahamantra.cells[cell.header.sravanam]  # Same cell

        Args:
            content: Any string content
            register: Auto-register in CellRouter (default True)

        Returns:
            MahaCellUnified with computed address
        """
        from vibe_core.mahamantra.substrate.cell import MahaCellUnified

        return MahaCellUnified.from_content(content, register=register)

    def network(self):
        """
        Create an O(1) IPv4 Router (Longest Prefix Match).

        LOTUS TREE FOR IP ROUTING:
            IPv4 = 32 bits = 8 levels × 4 bits
            O(8) = O(1) constant time LPM

        USAGE:
            router = mahamantra.network()
            router.insert_cidr("192.168.0.0/16", "gateway_a")
            next_hop = router.lookup("192.168.1.100")

        Returns:
            New LotusIPRouter instance
        """
        from vibe_core.mahamantra.adapters.network import create_ip_router

        return create_ip_router()

    def compression(self):
        """
        Create a MahaCompression engine (Intent Extraction).

        NOT DATA COMPRESSION - INTENT EXTRACTION:
            K(x) = shortest program that GENERATES x

        USAGE:
            compressor = mahamantra.compression()
            result = compressor.compress("text")
            print(result.seed)  # Address
            print(result.position)  # 0-15

        Returns:
            New MahaCompression instance
        """
        from vibe_core.mahamantra.adapters.compression import MahaCompression

        return MahaCompression()

    def scan(self) -> Dict[str, object]:
        """
        Scan system state (Governance/Audit).
        Delegate to GAD discovery + internal state.
        """
        return {
            "status": "active",
            "audit": self.get_state(),
            "gad": self.discover(),
        }

    def __getitem__(self, index: int):
        """
        Index into MAHAMANTRA_POSITIONS.

        Enables: mahamantra[2] → MantraPosition at index 2
        """
        from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS

        return MAHAMANTRA_POSITIONS[index]

    def __len__(self) -> int:
        """Return number of positions (16 = WORDS)."""
        from vibe_core.mahamantra.protocols._seed import WORDS

        return WORDS

    def __iter__(self) -> Iterator:
        """Iterate over all positions."""
        from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS

        return iter(MAHAMANTRA_POSITIONS)

    # === GAD Protocol ===

    def guardian(self) -> str:
        return "brahma"

    def position(self) -> int:
        return 1

    def test_saucam(self) -> bool:
        return True

    def discover(self) -> Dict[str, object]:
        """Discover capabilities."""
        return {
            "name": "MahamantraLotus",
            "position": 1,
            "guardian": "brahma",
            "capabilities": ["execute", "bootstrap", "kirtan"],
        }

    def get_state(self) -> Dict[str, object]:
        """Get current state."""
        return {
            "akash": self._akash,
            "compressor_loaded": self._compressor is not None,
        }


# Singleton
_mahamantra_instance: Optional[MahamantraLotus] = None


def get_mahamantra() -> MahamantraLotus:
    """Get the singleton MahamantraLotus instance."""
    global _mahamantra_instance
    if _mahamantra_instance is None:
        _mahamantra_instance = MahamantraLotus()
    return _mahamantra_instance


# Alias for easier access (Universal Router needs this name)
mahamantra = get_mahamantra()
lotus = mahamantra


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahamantraLotus",
    "get_mahamantra",
    "mahamantra",
]
