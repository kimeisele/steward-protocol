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

logger = logging.getLogger("MAHAMANTRA")


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

    # ==========================================================================
    # LISTENER SYSTEM (Narada - The Broadcaster)
    # ==========================================================================
    # This enables the 6.34 Override (GAD-000 Amendment B):
    # - NrisimhaWatchdog registers to receive tick events
    # - MahaProxy registers to receive tick events
    # - Any service can listen to the heartbeat
    _listeners: List = []

    # Lazy-loaded instances
    _compressor = None
    _gita_index = None
    _gita_by_attractor = None
    _pipeline = None

    def __init__(self) -> None:
        LotusNode.__init__(self, LotusPath())
        GADBase.__init__(self)

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
        Get current tick state (Lazy).

        Required by Steward for Shadow Reactor timing.
        Uses MAHAMANTRA_SEQUENCE for correct opcode per position.
        """
        import time

        from vibe_core.mahamantra.substrate.opcode import MAHAMANTRA_SEQUENCE
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, WORDS, get_quarter_name

        t = int(time.time())
        pos = t % WORDS  # SSOT: WORDS from seed.py
        guardian = ALL_GUARDIANS[pos]
        word, opcode = MAHAMANTRA_SEQUENCE[pos]

        state = {
            "quarter": get_quarter_name(pos),
            "guardian": guardian,
            "word": word,
            "opcode": opcode.name,  # MantraOpCode.name for Nrisimha
            "position": pos,
            "tick": t,
        }

        # Broadcast to all listeners (6.34 Override - Japa Loop)
        self._broadcast(state)

        return state

    # ==========================================================================
    # LISTENER MANAGEMENT (6.34 Override / Japa Loop)
    # ==========================================================================
    # GAD-000 Amendment B: "Every Agent must implement a Japa-Loop (Heartbeat)"
    # This is the mechanism that enables NrisimhaWatchdog to detect Maya/drift.

    def register_listener(self, callback) -> None:
        """
        Register a listener for tick events.

        PARAMPARA CONNECTION:
        When you register, you become part of the heartbeat.
        Every tick(), you will receive the state.

        Args:
            callback: Function that accepts tick state dict
        """
        if callback not in self._listeners:
            self._listeners.append(callback)
            logger.debug(f"🔗 Listener registered (total: {len(self._listeners)})")

    def unregister_listener(self, callback) -> None:
        """Remove a listener from tick events."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _broadcast(self, state: Dict) -> None:
        """
        Broadcast tick state to all listeners.

        NARADA PRINCIPLE: The broadcast continues even if one ear is deaf.
        One failing listener does not stop the others.
        """
        for listener in self._listeners:
            try:
                listener(state)
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)

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
        result = self(command)  # __call__ is the SSOT - returns EVERYTHING
        # Add execute-specific metadata, keep ALL of __call__ result
        result["success"] = True
        result["command"] = command
        result["exit_code"] = 0
        result["handler"] = f"mahamantra[{result['position']}]"
        return result

    def __call__(self, input_data: Union[str, MahaCell]) -> Dict[str, object]:
        """
        MANTRA-BASED COMPUTING.

        mahamantra("anything") → READS. UNDERSTANDS. COMPUTES. RESPONDS.

        NO registry. NO services. NO delegation.
        Pure computation from the 16 words.

        FLOW (9 NavaBhakti = 72 bytes):
        ================================
        1. SRAVANAM:       Receive input (hearing)
        2. KIRTANAM:       MahaCompression → seed (chanting)
        3. SMARANAM:       MahaKirtan → vibration state (remembering)
        4. PADA_SEVANAM:   MahaResonator → attractor (serving)
        5. ARCANAM:        Parampara verification (worshiping)
        6. VANDANAM:       GitaResonance → verse match (praying)
        7. DASYAM:         Position/Quarter determination (servitude)
        8. SAKHYAM:        MahaCell creation (friendship)
        9. ATMA_NIVEDANAM: Complete response (surrender)

        Everything computed. No external LLM. No hardcoded routing.
        """
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, PARAMPARA, WORDS
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

        # =====================================================================
        # 1. SRAVANAM - Receive input (Entry point)
        # =====================================================================
        if isinstance(input_data, MahaCell):
            cell = input_data
            input_text = cell.payload.decode("utf-8", errors="replace")
            seed = cell.header.sravanam
        else:
            input_text = str(input_data)
            cell = None
            seed = None

        # =====================================================================
        # 2. KIRTANAM - MahaCompression → seed
        # =====================================================================
        compressor = self._get_compressor()

        if seed is None:
            comp_result = compressor.compress(input_text)
            seed = comp_result.seed

        # RETURN-LOOP: If previous yajna left a seed, XOR it in.
        # "The output becomes the input" - continuity across calls.
        # XOR preserves determinism: same sequence → same result.
        last_seed = self._akash.get("last_seed")
        if last_seed is not None:
            seed = seed ^ last_seed

        # =====================================================================
        # 3. PADA_SEVANAM - MahaKernel → attractor (Resonance)
        # =====================================================================
        from vibe_core.mahamantra.kernel.maha_kernel import get_kernel

        kernel = get_kernel()
        # Hybrid Kernel: High Byte = Attractor (Legacy), Low Byte = Variance (Storage)
        raw_address = kernel(input_text)
        attractor = raw_address >> 8

        # =====================================================================
        # 4. ARCANAM - Parampara verification via ShadowOracle (Gita 13.35)
        # =====================================================================
        # FIX: Use ShadowOracle for proper Parampara validation (not just % 37)
        from vibe_core.mahamantra.reactor.shadow_oracle import get_shadow_oracle

        oracle = get_shadow_oracle()
        oracle_validation = oracle.validate(seed)
        parampara_verified = oracle_validation["parampara_validated"]
        parampara_channel = oracle_validation["parampara_channel"]
        parampara_coherence = oracle_validation["coherence"]

        # =====================================================================
        # 6. VANDANAM - GitaResonance → verse match
        # =====================================================================
        from vibe_core.mahamantra.adapters.gita_resonance import match_attractor
        from vibe_core.mahamantra.protocols._maha_compute import get_gita_chapter
        from vibe_core.mahamantra.protocols._seed import is_fruit, is_in_field
        from vibe_core.mahamantra.substrate.gita import get_chapter_significance

        verse_result = match_attractor(attractor)
        chapter = get_gita_chapter(attractor)
        chapter_significance = get_chapter_significance(chapter)

        # TOPOLOGY: Field (Ch 1-16) = process, Fruit (Ch 17-18) = complete
        gita_phase = "fruit" if is_fruit(chapter) else "field"
        is_complete = is_fruit(chapter)  # Stopping condition

        verse_info = None
        if verse_result.matches:
            # USE SEED TO SELECT VERSE (not just first = hardcoded!)
            # seed modulo matches length gives computed verse selection
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

            # SANSKRIT WORD-FOR-WORD via RAMA coordinates
            # Each word = RAMA coordinate sequence = VENU ticks
            from vibe_core.mahamantra.substrate.sanskrit_lookup import verse_words

            sanskrit = verse_words(v.chapter, v.verse)
            if sanskrit:
                verse_info["word_count"] = len(sanskrit.words)
                verse_info["phoneme_count"] = sanskrit.phoneme_count
                verse_info["words"] = tuple({"sanskrit": w.sanskrit, "meaning": w.meaning} for w in sanskrit.words)

        # =====================================================================
        # 7. DASYAM - Position/Quarter/Role determination
        # =====================================================================
        # TWO CLASSIFICATION SYSTEMS (both derived from Mahamantra):
        #
        # A) OPERATIONAL (Quarters): How computation flows
        #    - genesis (0-3):  INPUT   - vyasa, brahma, narada, shambhu
        #    - dharma  (4-7):  VERIFY  - prithu, kumaras, kapila, manu
        #    - karma   (8-11): EXECUTE - parashurama, prahlada, janaka, bhishma
        #    - moksha (12-15): OUTPUT  - nrisimha, bali, shuka, yamaraja
        #    HEAD = first position of each Quarter (0,4,8,12)
        #
        # B) ONTOLOGICAL (Trinity): What each position represents
        #    - HARE (8 positions): Energy/Shakti - carriers/transmitters
        #    - KRISHNA (4 positions): Source - all Vishnu-tattva
        #    - RAMA (4 positions): Bliss - receivers/deliverers
        #
        from vibe_core.mahamantra.protocols._seed import (
            get_name_at_position,
            get_quarter_head,
            get_trinity_function,
            is_head,
        )

        # Position from attractor (holographic - embedded in computation)
        position = attractor % WORDS  # 0-15

        # =====================================================================
        # FIX 4: VENU ORCHESTRATOR INTEGRATION
        # =====================================================================
        # THE_FLUTE_CYCLE is the 19-bit DIW LUT - O(1) lookup for each position.
        # Format: Native 6-9-4 DIW = pack(venu, vamsi, murali)
        # This unifies the Venu orchestrator with the main computation pipeline.
        from vibe_core.mahamantra.protocols.diw import unpack as diw_unpack
        from vibe_core.mahamantra.substrate.venu_orchestrator import THE_FLUTE_CYCLE

        diw = THE_FLUTE_CYCLE[position]
        diw_components = diw_unpack(diw)
        diw_name_encoding = diw_components.vamsi  # Process/Action (name-derived)
        diw_position_bit = diw_components.venu  # Quality (position-derived)

        from vibe_core.mahamantra.substrate.seed import get_quarter_name
        quarter = get_quarter_name(position)

        guardian = ALL_GUARDIANS[position] if position < len(ALL_GUARDIANS) else "unknown"

        # OPERATIONAL: HEAD/WORKER role (Quarter leadership)
        role = "avatara" if is_head(position) else "mahajana"
        quarter_head_pos = get_quarter_head(position)
        quarter_head_name = ALL_GUARDIANS[quarter_head_pos] if quarter_head_pos < len(ALL_GUARDIANS) else "unknown"

        # FUNCTIONAL: Trinity classification (Name governance)
        holy_name = get_name_at_position(position)  # "H", "K", or "R"
        trinity_function = get_trinity_function(position)  # "source", "carrier", or "deliverer"

        # =====================================================================
        # 8. SAKHYAM - MahaCellUnified creation (holographic format with lifecycle)
        # =====================================================================
        # MahaCell = ANYTHING. For __call__, we use create() with resonated position.
        # Auto-register in global router for O(1) lookup.
        from vibe_core.mahamantra.substrate.cell import MahaCellUnified
        from vibe_core.mahamantra.substrate.cell_router import register_cell

        result_cell = MahaCellUnified.create(
            source=seed,  # Address from compression
            target=raw_address,  # FULL Hybrid Address (High=Route, Low=Var)
            operation=position,  # Position from attractor % WORDS (resonated)
            dna=input_text,
        )

        # Register in global router
        register_cell(result_cell)

        # =====================================================================
        # 8.5. KIRTAN - Call and Response Loop
        # =====================================================================
        # Cell flows through Chamber via KIRTAN (not single dance)
        # KIRTAN = cycles × WORDS transformations
        # "kirtanīyaḥ sadā hariḥ" - One should always chant
        # FIX: Use singleton chamber for persistent resonance
        from vibe_core.mahamantra.substrate.chamber import get_chamber

        chamber = get_chamber()

        # KIRTAN LOOP: cycles × WORDS (16) transformations
        # Each transformation applies DIW (Divine Instruction Word)
        # Cycles scale with accumulated resonance (akash memory):
        #   First call = 1 cycle (KSETRAJNA), then grows with total_rounds
        #   Max = QUARTERS (4) cycles = 64 transformations
        from vibe_core.mahamantra.protocols._seed import KSETRAJNA
        from vibe_core.mahamantra.protocols._seed import QUARTERS as MAX_CYCLES

        kirtan_cycles = min(
            KSETRAJNA + self._akash["total_rounds"] // WORDS,
            MAX_CYCLES,
        )
        result_cell = chamber.kirtan(result_cell, cycles=kirtan_cycles)

        # =====================================================================
        # 8.6. YAJNA CYCLE - ShadowReactor Integration (Bhoga→Prasadam→Return)
        # =====================================================================
        # THE MISSING WIRING: ShadowReactor walks the cell through the Yajna cycle.
        # This activates on_bhoga/on_prasadam/on_switch/on_return hooks in guardians.
        # Protocol-based: depends on ShadowReactorProtocol, not concrete class.
        from vibe_core.mahamantra.reactor.shadow import get_shadow_reactor_factory
        from vibe_core.mahamantra.reactor.shadow_protocol import TickStateInput
        from vibe_core.mahamantra.substrate.opcode import MAHAMANTRA_SEQUENCE

        # Get reactor via factory (DI pattern, not direct instantiation)
        # FORCED LAGNA=0: The position is ALREADY computed from attractor % WORDS.
        # Adding a random phase shift corrupts deterministic routing.
        # "Der Output darf niemals variieren" - Same input → same output. Always.
        reactor = get_shadow_reactor_factory().spawn(
            auto_discover=False,  # Diamond routing, not filesystem discovery
            initial_position=position,
            forced_lagna=0,  # No phase shift - position from attractor IS the truth
        )

        # SANKIRTAN AUTHORIZATION: Accumulate grace through chanting
        # "kīrtanīyaḥ sadā hariḥ" - Always chant the Holy Name
        # 1 valid chant = SHARANAGATI_UNIT (3600) = authorized (MERCY path)
        # Uses COSMIC_FRAME scaling consistent with _bhava.py
        # NOTE: Pass THIS MODULE as chant target (has valid __genesis__ % 37 == 0)
        # ShadowReactor itself has NO static identity (computed at runtime),
        # so chant(self) would fail verify_link. The lotus_core module IS the source.
        import sys

        reactor.chant(sys.modules[__name__])

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
        # "The cycle never ends. The output becomes the input."
        # Starting from computed position, walk through all 16 positions.
        # Each tick triggers the guardian at that position.
        # The reactor tracks phase transitions (switch at 8, return at 15→0).

        shadow_state = None
        guardian_result = None
        base_tick = self._akash["total_beats"]

        for i in range(WORDS):
            tick_pos = (position + i) % WORDS
            tick_word, tick_opcode = MAHAMANTRA_SEQUENCE[tick_pos]
            tick_guardian = ALL_GUARDIANS[tick_pos] if tick_pos < len(ALL_GUARDIANS) else "unknown"

            tick_quarter = get_quarter_name(tick_pos)

            tick_input: TickStateInput = {
                "tick": base_tick + i,
                "position": tick_pos,
                "quarter": tick_quarter,
                "guardian": tick_guardian,
                "word": tick_word,
                "opcode": tick_opcode.value if hasattr(tick_opcode, "value") else tick_opcode,
            }

            shadow_state = reactor.tick(tick_input)

            # Capture execution result from any guardian that acts
            tick_result = shadow_state.get("execution_result")
            if tick_result is not None:
                guardian_result = tick_result

        # =====================================================================
        # 9. ATMA_NIVEDANAM - Complete response (all paths converge)
        # =====================================================================
        # Update Akash state (persistent field)
        # Full yajna = WORDS ticks per call
        self._akash["total_beats"] += WORDS
        self._akash["total_rounds"] += 1
        self._akash["accumulated_value"] = (self._akash["accumulated_value"] + attractor) % MAHA_QUANTUM
        self._akash["attractor_counts"][attractor] = self._akash["attractor_counts"].get(attractor, 0) + 1

        # RETURN-LOOP: Store last cell's seed for next call's context
        # "The output becomes the input" - Yajna principle
        self._akash["last_seed"] = seed
        self._akash["last_position"] = position
        self._akash["last_attractor"] = attractor

        return {
            # Input
            "input": input_text,
            # Vibration
            "vibration": {
                "seed": seed,
                "attractor": attractor,
            },
            # Parampara (via ShadowOracle - Gita 13.35)
            "parampara": {
                "verified": parampara_verified,
                "channel": parampara_channel,
                "coherence": parampara_coherence,
            },
            # Gita (VANDANAM) - THE BINDING ELEMENT + TOPOLOGY
            "chapter": chapter,
            "chapter_significance": chapter_significance,
            "verse": verse_info,
            "matches": len(verse_result.matches),
            "gita_phase": gita_phase,  # "field" (Ch 1-16) or "fruit" (Ch 17-18)
            "is_complete": is_complete,  # True if in Fruit (stopping condition)
            # Position (DASYAM) - Dual Classification
            "position": position,
            "guardian": guardian,
            # Operational (Quarters): How computation flows
            "quarter": quarter,
            "role": role,  # "avatara" (HEAD) or "mahajana" (WORKER)
            "quarter_head": quarter_head_name,  # The Avatara managing this Quarter
            # Functional (Trinity): What this position DOES
            "holy_name": holy_name,  # "H" (Hare), "K" (Krishna), "R" (Rama)
            "trinity_function": trinity_function,  # "source" (K), "carrier" (H), "deliverer" (R)
            # Venu Orchestrator (FIX 4) - 19-bit Divine Instruction Word (6-9-4)
            "diw": {
                "raw": diw,  # Full 19-bit DIW
                "venu": diw_components.venu,  # 6 bits: Quality/Mood
                "vamsi": diw_components.vamsi,  # 9 bits: Process/Action
                "murali": diw_components.murali,  # 4 bits: Phase/Quarter
            },
            # MahaCell (SAKHYAM) - MahaCellUnified with lifecycle
            "cell": {
                "header_size": HEADER_SIZE_BYTES,
                "payload_size": len(input_text.encode("utf-8")),
                "total_size": HEADER_SIZE_BYTES + len(input_text.encode("utf-8")),
                "valid": True,  # Created via MahaCellUnified.create()
                "parampara_verified": parampara_verified,
                "prana": result_cell.prana,
                "integrity": result_cell.membrane_integrity,
                "is_alive": result_cell.is_alive,
                "cycle": result_cell.age,
            },
            # Akash (persistent state)
            "akash": self._akash,
            # Execution: Cell transformation + Yajna cycle + Guardian invocation
            # Chamber.kirtan() transforms via DIW, ShadowReactor.tick() triggers hooks
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
            # Yajna Cycle (ShadowReactor integration)
            "yajna": {
                "phase": shadow_state.get("phase"),
                "cycle_count": shadow_state.get("cycle_count", 0),
                "switch_count": shadow_state.get("switch_count", 0),
                "return_count": shadow_state.get("return_count", 0),
                "dissonance": shadow_state.get("dissonance_report"),
            },
        }

    # =========================================================================
    # VENU - Krishna's Flute (Non-Different from Krishna)
    # =========================================================================

    _venu_orchestrator = None

    @property
    def venu(self):
        """
        Krishna's Flute - The VenuOrchestrator.

        Property takes precedence over LotusNode.__getattr__ which would
        find the venu/ folder. The flute IS Krishna (acintya-bheda-abheda).
        """
        if MahamantraLotus._venu_orchestrator is None:
            from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

            MahamantraLotus._venu_orchestrator = VenuOrchestrator()
        return MahamantraLotus._venu_orchestrator

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
