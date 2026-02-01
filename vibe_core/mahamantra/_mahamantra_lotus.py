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

# These imports are needed for class definition
from vibe_core.mahamantra._lotus import LotusNode, LotusPath
from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol
from vibe_core.mahamantra._types import (
    AkashState,
    ExecuteResult,
    GitaRoute,
    RouteResult,
    VibrationState,
)
from vibe_core.mahamantra.protocols._header import MahaCell, MahaHeader

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
    }

    # Lazy-loaded instances
    _kirtan = None
    _compressor = None
    _gita_index = None
    _gita_index = None
    _gita_by_attractor = None
    _pipeline = None

    def __init__(self) -> None:
        LotusNode.__init__(self, LotusPath())
        GADBase.__init__(self)

    @classmethod
    def _get_kirtan(cls):
        """
        Lazy-load PERSON-Anchored Kirtan (PrabhupadaKirtan).

        "selbst die mahajans fragen dann prabhupad nach seinen gita interpretation"
        Every computation flows through THE PERSON - Prabhupada.

        PrabhupadaKirtan wraps MahaKirtan with:
        - 8 Siksastakam stages (L0-L7) pipeline
        - PERSON-anchored parampara verification (% 37 == 0)
        - Bidirectional CALL ↔ RESPONSE transmission
        """
        if cls._kirtan is None:
            from vibe_core.mahamantra.substrate.mantra.prabhupada_kirtan import PrabhupadaKirtan
            from vibe_core.mahamantra.adapters.compression import MahaCompression
            from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

            cls._kirtan = PrabhupadaKirtan(mod_space=MAHA_QUANTUM)
            cls._compressor = MahaCompression()

        return cls._compressor, cls._kirtan

    def _compute_vibration(self, input_data):
        """Compute vibration state from input (PERSON-anchored)."""
        compressor, kirtan = self._get_kirtan()

        cell = None
        if isinstance(input_data, MahaCell):
            cell = input_data
            seed = cell.header.sravanam
        else:
            command = input_data
            comp_result = compressor.compress(command)
            seed = comp_result.seed

        # PERSON-ANCHORED: flows through Prabhupada
        result = kirtan.compute_with_person(seed)

        from vibe_core.mahamantra.substrate.resonance import MahaResonator
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM

        resonator = MahaResonator(mod_space=MAHA_QUANTUM)
        attractor = resonator.oscillate_once(result.transformed_value)

        return {
            "seed": seed,
            "transformed_value": result.transformed_value,
            "beat": result.beat_number,
            "resonance": result.flute_resonance,
            "vina_resonance": result.vina_resonance,
            "vina_string": result.vina_string,
            "attractor": attractor,
            "parampara_channel": result.parampara_channel,
            "oracle_validated": result.oracle_validated,
            # PERSON-ANCHORED additions
            "person_verified": result.person_verified,
            "is_bona_fide": result.is_bona_fide,
            "siksastakam_stage": result.siksastakam_stage.verse,
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
        """
        import time
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, WORDS

        t = int(time.time())
        pos = t % WORDS  # SSOT: WORDS from seed.py
        guardian = ALL_GUARDIANS[pos]
        
        return {
            "quarter": "karma" if pos > 8 else "dharma", 
            "guardian": guardian,
            "word": "hare" if pos % 2 == 0 else "krishna",
            "opcode": "EXECUTE",
            "position": pos,
            "tick": t
        }

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

        # LAZY mode (default) - services load on first use
        # The _get_kirtan() method already handles lazy loading

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
        from vibe_core.mahamantra.protocols._seed import WORDS, PARAMPARA, MAHA_QUANTUM
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
        compressor, kirtan = self._get_kirtan()

        if seed is None:
            comp_result = compressor.compress(input_text)
            seed = comp_result.seed

        # =====================================================================
        # 3. SMARANAM - PrabhupadaKirtan → PERSON-anchored vibration state
        # =====================================================================
        # PERSON-ANCHORED: Every computation flows through Prabhupada
        # PrabhupadaKirtanResult has all KirtanComputeResult fields + parampara
        kirtan_result = kirtan.compute_with_person(seed)

        # =====================================================================
        # 4. PADA_SEVANAM - MahaModularSynth → attractor (full 16-position coverage)
        # =====================================================================
        # FIX: MahaResonator.oscillate_once() only produces 5 attractors due to
        # quadratic convergence in RAMA operation. MahaModularSynth with "quantum"
        # preset uses feedback to break convergence and reach all 16 positions.
        from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
        synth = MahaModularSynth(default_preset="quantum")
        attractor = synth.transform(kirtan_result.transformed_value)

        # =====================================================================
        # 5. ARCANAM - Parampara verification (% 37 == 0)
        # =====================================================================
        parampara_verified = (seed % PARAMPARA == 0)
        parampara_channel = kirtan_result.parampara_channel
        oracle_validated = kirtan_result.oracle_validated

        # =====================================================================
        # 6. VANDANAM - GitaResonance → verse match
        # =====================================================================
        from vibe_core.mahamantra.adapters.gita_resonance import match_attractor
        from vibe_core.mahamantra.protocols._maha_compute import get_gita_chapter

        verse_result = match_attractor(attractor)
        chapter = get_gita_chapter(attractor)

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
            }

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
            is_head, get_quarter_head,
            get_name_at_position, get_trinity_function,
        )

        # Position from attractor (holographic - embedded in computation)
        position = attractor % WORDS  # 0-15

        if position < 4:
            quarter = "genesis"
        elif position < 8:
            quarter = "dharma"
        elif position < 12:
            quarter = "karma"
        else:
            quarter = "moksha"

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
        from vibe_core.mahamantra.substrate.cell import MahaCellUnified
        
        result_cell = MahaCellUnified.create(
            source=seed,
            target=attractor,
            operation=position,
            dna=input_text,  # DNA = input text
            initial_state=None,  # Generic state (optional)
        )
        
        # =====================================================================
        # 8.5. KIRTAN - Call and Response Loop
        # =====================================================================
        # Cell flows through Chamber via KIRTAN (not single dance)
        # KIRTAN = cycles × WORDS transformations
        # "kirtanīyaḥ sadā hariḥ" - One should always chant
        from vibe_core.mahamantra.substrate.chamber import SankirtanChamber
        chamber = SankirtanChamber()

        # KIRTAN LOOP: 1 cycle = WORDS (16) transformations
        # Each transformation applies DIW (Divine Instruction Word)
        result_cell = chamber.kirtan(result_cell, cycles=1)

        # =====================================================================
        # 9. ATMA_NIVEDANAM - Complete response (all paths converge)
        # =====================================================================
        # Update Akash state (persistent field)
        self._akash["total_beats"] += 1
        self._akash["accumulated_value"] = (self._akash["accumulated_value"] + attractor) % MAHA_QUANTUM
        self._akash["attractor_counts"][attractor] = self._akash["attractor_counts"].get(attractor, 0) + 1

        return {
            # Input
            "input": input_text,

            # Vibration (KIRTANAM + SMARANAM + PADA_SEVANAM)
            "vibration": {
                "seed": seed,
                "transformed_value": kirtan_result.transformed_value,
                "beat": kirtan_result.beat_number,
                "flute_resonance": kirtan_result.flute_resonance,
                "vina_resonance": kirtan_result.vina_resonance,
                "vina_string": kirtan_result.vina_string,
                "attractor": attractor,
            },

            # Parampara (ARCANAM) - PERSON-ANCHORED through Prabhupada
            "parampara": {
                "verified": parampara_verified,
                "channel": parampara_channel,
                "oracle_validated": oracle_validated,
                # PERSON-ANCHORED additions (from PrabhupadaKirtan)
                "person_verified": kirtan_result.person_verified,
                "is_bona_fide": kirtan_result.is_bona_fide,
                "transmission_mode": kirtan_result.transmission_mode,
                "siksastakam_stage": kirtan_result.siksastakam_stage.verse,
                "siksastakam_sanskrit": kirtan_result.siksastakam_stage.sanskrit,
                "siksastakam_operation": kirtan_result.siksastakam_stage.operation,
            },

            # Gita (VANDANAM)
            "chapter": chapter,
            "verse": verse_info,
            "matches": len(verse_result.matches),

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

            # MahaCell (SAKHYAM) - MahaCellUnified with lifecycle
            "cell": {
                "header_size": 72,
                "payload_size": len(input_text.encode('utf-8')),
                "total_size": 72 + len(input_text.encode('utf-8')),
                "valid": True,  # Created via MahaCellUnified.create()
                "parampara_verified": parampara_verified,
                "prana": result_cell.prana,
                "integrity": result_cell.membrane_integrity,
                "is_alive": result_cell.is_alive,
                "cycle": result_cell.age,
            },

            # Akash (persistent state)
            "akash": self._akash,

            # Execution: The Cell transformation IS the execution
            # Chamber.kirtan() already transformed the cell via DIW (3 flutes)
            # No external dispatch - holographic principle
            "execution": {
                "success": result_cell.is_alive,
                "prana": result_cell.prana,
                "integrity": result_cell.membrane_integrity,
                "cycles": result_cell.age,
            },
        }

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
            "kirtan_loaded": self._kirtan is not None,
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
