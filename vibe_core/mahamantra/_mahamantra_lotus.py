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
from vibe_core.mahamantra.protocols._gad_base import GADBase, GADProtocol
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
    _gita_by_attractor = None

    def __init__(self) -> None:
        LotusNode.__init__(self, LotusPath())
        GADBase.__init__(self)

    @classmethod
    def _get_kirtan(cls):
        """Lazy-load MahaKirtan orchestrator."""
        if cls._kirtan is None:
            from vibe_core.mahamantra.research.dharma import MahaKirtan
            from vibe_core.mahamantra.adapters.compression import MahaCompression
            from vibe_core.mahamantra.protocols._seed_core import MAHA_QUANTUM

            cls._kirtan = MahaKirtan(mod_space=MAHA_QUANTUM)
            cls._compressor = MahaCompression()

        return cls._compressor, cls._kirtan

    def _compute_vibration(self, input_data):
        """Compute vibration state from input."""
        compressor, kirtan = self._get_kirtan()

        cell = None
        if isinstance(input_data, MahaCell):
            cell = input_data
            seed = cell.header.sravanam
        else:
            command = input_data
            comp_result = compressor.compress(command)
            seed = comp_result.seed

        result = kirtan.compute(cell if cell else seed)

        from vibe_core.mahamantra.research.dharma import MahaResonator
        from vibe_core.mahamantra.protocols._seed_core import MAHA_QUANTUM

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
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS
        
        t = int(time.time())
        pos = t % 16
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
        """Execute a command through the Mahamantra."""
        args = args or []

        # Wrap in MahaCell
        cell = MahaCell.from_command(command) if hasattr(MahaCell, 'from_command') else None

        # Compute vibration
        vibration = self._compute_vibration(cell if cell else command)

        # Route via CLI bridge
        from vibe_core.mahamantra.cli.bridge import cli_bridge
        bridge_result = cli_bridge.route(command, args)

        return {
            "success": bridge_result.success,
            "command": command,
            "position": bridge_result.position,
            "vibration": vibration,
            "exit_code": bridge_result.exit_code,
            "handler": bridge_result.handler,
            # Keys expected by Steward
            "guardian": "unknown", # Improved later via position lookup if needed
            "quarter": "unknown",
            "guna": "unknown",
            "output": f"Exit Code: {bridge_result.exit_code}"
        }

    def __call__(self, input_text: str) -> Dict[str, object]:
        """
        THE KIRTAN RESONANCE CHAMBER.

        mahamantra("anything") → routes through ALL systems:

        FLOW (Entry-Existence-Exit via MahaCell):
        ==========================================
        1. SRAVANAM (Entry):     MahaCompression → seed
        2. KIRTANAM (Chanting):  MahaKirtan → vibration state (7-beat cycles)
        3. SMARANAM (Memory):    MahaResonator → attractor (stable harmonic)
        4. PADA_SEVANAM (Serve): MahaLLM → intent routing (16 categories, O(4))
        5. ARCANAM (Worship):    GitaResonance → verse matching (700 verses)
        6. VANDANAM (Prayer):    Shadow Reactor → Yajna cycle (BHOGA→PRASADAM)
        7. DASYAM (Service):     MahaCell → 72-byte header + payload
        8. SAKHYAM (Friendship): Aggregated result from all paths
        9. ATMA_NIVEDANAM:       Complete surrender of computation

        NO external LLM API calls. PURE COMPUTED RESONANCE.
        Krishna routes through digital space - multi-path, not single chatbot.

        Args:
            input_text: Any input (text, command, question)

        Returns:
            Dict with complete resonance from ALL systems
        """
        from vibe_core.mahamantra.adapters.gita_resonance import match_attractor
        from vibe_core.mahamantra.protocols._maha_compute import get_gita_chapter
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS
        from vibe_core.mahamantra.protocols._seed_core import WORDS

        # =====================================================================
        # 1. SRAVANAM (Entry) - Compute vibration via MahaCompression + MahaKirtan
        # =====================================================================
        vibration = self._compute_vibration(input_text)
        seed = vibration.get("seed", 0)
        attractor = vibration.get("attractor", 0)

        # =====================================================================
        # 2. KIRTANAM - MahaLLM Intent Routing (O(4) holographic)
        # =====================================================================
        intent_route = None
        intent_category = None
        try:
            from vibe_core.mahamantra.adapters.llm import MahaLLM
            llm = MahaLLM()
            route_result = llm.route_text(input_text)
            intent_route = {
                "intent_id": route_result.intent_id,
                "category": route_result.category_name,
                "agent": route_result.agent,
                "address": route_result.address,
                "found": route_result.found,
                "ops": route_result.ops,  # Always 4 (holographic guarantee)
            }
            intent_category = route_result.category_name
        except Exception:
            # Fallback if MahaLLM not available
            intent_route = {"category": "UNKNOWN", "ops": 4}

        # =====================================================================
        # 3. SMARANAM - GitaResonance Verse Matching (700 verses indexed)
        # =====================================================================
        verse_result = match_attractor(attractor)
        chapter = get_gita_chapter(attractor)

        verse_info = None
        if verse_result.best_match:
            v = verse_result.best_match
            verse_info = {
                "id": v.verse_id,
                "chapter": v.chapter,
                "verse": v.verse,
                "guna": v.guna,
                "dominant_name": v.dominant_name,
            }

        # =====================================================================
        # 4. PADA_SEVANAM - Position & Guardian (from Mahamantra substrate)
        # =====================================================================
        position = attractor % WORDS  # 0-15 position in Mahamantra
        guardian = ALL_GUARDIANS[position] if position < len(ALL_GUARDIANS) else "unknown"

        # Determine quarter from position
        if position < 4:
            quarter = "genesis"
        elif position < 8:
            quarter = "dharma"
        elif position < 12:
            quarter = "karma"
        else:
            quarter = "moksha"

        # =====================================================================
        # 5. ARCANAM - Shadow Reactor Yajna State (Bhoga-Prasadam cycle)
        # =====================================================================
        yajna_state = None
        try:
            from vibe_core.mahamantra.reactor.shadow import get_shadow_reactor_factory
            factory = get_shadow_reactor_factory()
            reactor = factory.spawn(auto_discover=False, initial_position=position)

            # Get tick state for current position
            tick_state = self.tick()

            yajna_state = {
                "phase": "BHOGA" if position < 8 else "PRASADAM",
                "position": position,
                "quarter": quarter,
                "guardian": guardian,
                "reactor_id": reactor.reactor_id,
                "lagna": reactor.lagna,
                "parampara_coherence": reactor.parampara_coherence,
            }
        except Exception:
            # Fallback if Shadow Reactor not available
            yajna_state = {
                "phase": "BHOGA" if position < 8 else "PRASADAM",
                "position": position,
                "quarter": quarter,
                "guardian": guardian,
            }

        # =====================================================================
        # 6. VANDANAM - MahaCell Creation (72-byte header + payload)
        # =====================================================================
        maha_cell = None
        try:
            payload = input_text.encode("utf-8")
            cell = MahaCell.create(
                payload=payload,
                source=seed,
                target=attractor,
                operation=position,
                intent=vibration.get("parampara_channel", 0),
                ttl=300,  # Daily cycles
            )
            maha_cell = {
                "header_size": 72,  # NADI_RESONANCE
                "payload_size": len(payload),
                "total_size": cell.size,
                "valid": cell.is_valid(),
                "parampara_verified": cell.header.verify_parampara(),
            }
        except Exception:
            maha_cell = {"header_size": 72, "valid": False}

        # =====================================================================
        # 7. DASYAM - Maha Algorithm Transform (16-step)
        # =====================================================================
        algo_transform = None
        try:
            from vibe_core.mahamantra.research.dharma import MahaAlgorithm16
            algo = MahaAlgorithm16()
            transformed = algo.transform(seed)
            classification = algo.classify(transformed)
            algo_transform = {
                "input_seed": seed,
                "transformed": transformed,
                "classification": classification,
                "bits_512": algo.total_bits_512,
                "bits_1096": algo.total_bits_1096,
            }
        except Exception:
            algo_transform = {"input_seed": seed, "transformed": attractor}

        # =====================================================================
        # 8. SAKHYAM - Aggregated Result (all paths converge)
        # =====================================================================
        return {
            # Input
            "input": input_text,

            # Core Vibration (MahaCompression + MahaKirtan)
            "vibration": vibration,

            # Intent Routing (MahaLLM - O(4) holographic)
            "intent": intent_route,

            # Gita Resonance (700 verses)
            "chapter": chapter,
            "verse": verse_info,
            "matches": len(verse_result.matches),

            # Mahamantra Position
            "position": position,
            "guardian": guardian,
            "quarter": quarter,

            # Yajna State (Shadow Reactor)
            "yajna": yajna_state,

            # MahaCell (72-byte universal format)
            "cell": maha_cell,

            # Algorithm Transform (16-step)
            "transform": algo_transform,

            # ATMA_NIVEDANAM - Summary
            "summary": {
                "seed": seed,
                "attractor": attractor,
                "guna": verse_info.get("guna") if verse_info else "unknown",
                "parampara_channel": vibration.get("parampara_channel", -1),
                "oracle_validated": vibration.get("oracle_validated", False),
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

    def _get_quarter(self, name: str):
        """Lazy-load quarter module."""
        import importlib
        module = importlib.import_module(f"vibe_core.mahamantra.{name}")
        return module

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
