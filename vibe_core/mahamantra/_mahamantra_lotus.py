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

    def __call__(self, input_text: str) -> ExecuteResult:
        """
        THE ONE ENTRY POINT - SSOT.

        mahamantra("anything") → understands, routes, EXECUTES, responds.

        FLOW (Theologically Correct & RESONANCE BASED):
        ===============================================
        1. PRABHUPADA: Transmit input (blessing)
        2. RESONANCE:  MahaCompression extracts seed/intent/position via MahaKirtan
        3. DISCOVERY:  Resolve Mahajana Service class directly (no string matching!)
        4. POLYMORPHISM: Dispatch based on capability (Cognitive vs Executable)
           - process_intent() -> for Kapila/Cognitive types
           - execute()        -> for Prithu/Worker types
           - Default          -> Error

        FOLDER IS TRUTH: Identity derived from filesystem structure.
        """
        import asyncio
        import importlib
        from vibe_core.mahamantra.substrate.prabhupada import get_prabhupada
        from vibe_core.mahamantra.adapters.compression import MahaCompression
        from vibe_core.mahamantra.substrate.siksastakam_registry import get_entry, get_guardian

        # 1. PRABHUPADA (The Link)
        prabhupada = get_prabhupada()
        transmitted = prabhupada.transmit(input_text)

        # 2. RESONANCE (The Algorithm)
        # Uses MahaLLM + MahaKirtan + MahaResonator internally
        compressor = MahaCompression()
        comp_result = compressor.compress(transmitted)

        seed = comp_result.seed
        position = comp_result.position
        guna = comp_result.intent_level.guna.value

        # 3. DISCOVERY (The Registry Lookup - O(1))
        # We use the registry ONLY to find the class path, NOT for execution logic
        entry = get_entry(position)
        
        service_instance = None
        error_msg = None
        output = ""
        success = False
        exit_code = 1

        if entry:
            try:
                # Lazy load the actual service module
                module = importlib.import_module(entry.module_path)
                # Try to get the Service class (e.g. KapilaService)
                service_cls = getattr(module, entry.service_class, None)
                if not service_cls:
                    # Fallback to Null class if Service not found (e.g. NullKapila)
                    service_cls = getattr(module, entry.null_class, None)
                
                if service_cls:
                    service_instance = service_cls()
            except ImportError:
                error_msg = f"Could not load module {entry.module_path}"
        else:
            error_msg = f"No registry entry for position {position}"

        # 4. POLYMORPHISM (The Execution)
        if service_instance:
            try:
                # A) COGNITIVE INTERFACE (Kapila style)
                if hasattr(service_instance, "process_intent"):
                    # Create minimal valid context
                    # import CognitiveContext only if needed to avoid circular imports? 
                    # For now pass None or mock if strictly typed. 
                    # Assuming optional context or tolerant implementation.
                    
                    # Async handling
                    if asyncio.iscoroutinefunction(service_instance.process_intent):
                        # We are likely in sync context here, so we need a runner
                        # or we rely on the service to handle sync calls if designed well
                        # For now, let's assume we can run it:
                        try:
                            # Simple sync wrapper for async call
                            cognition = asyncio.run(service_instance.process_intent(transmitted, None))
                            output = str(cognition)
                            success = True
                            exit_code = 0
                        except RuntimeError:
                            # Loop already running? 
                            output = "Async execution failed (loop running)"
                            success = False
                    else:
                        output = str(service_instance.process_intent(transmitted, None))
                        success = True
                        exit_code = 0

                # B) EXECUTABLE INTERFACE (Prithu style)
                elif hasattr(service_instance, "execute"):
                    # Standard execute pattern
                    # Some take (command, args), some take (command)
                    # We try to inspect or be robust
                    try:
                        res = service_instance.execute(transmitted, [])
                        if isinstance(res, dict):
                            output = res.get("output", str(res))
                            success = res.get("success", True)
                            exit_code = res.get("exit_code", 0)
                        else:
                            output = str(res)
                            success = True
                            exit_code = 0
                    except TypeError:
                         # Maybe it expects just command?
                        res = service_instance.execute(transmitted)
                        output = str(res)
                        success = True
                        exit_code = 0
                
                # C) ANALYTIC INTERFACE (Null/Stub style)
                elif hasattr(service_instance, "analyze"):
                    res = service_instance.analyze(transmitted)
                    output = str(res)
                    success = True
                    exit_code = 0

                else:
                    error_msg = f"Service {service_instance.__class__.__name__} has no known interface (process_intent/execute/analyze)"
            
            except Exception as e:
                error_msg = f"Execution failed: {str(e)}"
                success = False

        # Derive quarter for result
        if position < 4: quarter = "genesis"
        elif position < 8: quarter = "dharma"
        elif position < 12: quarter = "karma"
        else: quarter = "moksha"

        # 5. RETURN
        return {
            "success": success,
            "exit_code": exit_code,
            "position": position,
            "guardian": entry.guardian if entry else get_guardian(position),
            "quarter": quarter,
            "guna": guna,
            "requires_confirmation": guna == "tamas",
            "output": output,
            "error": error_msg,
            "vibration": {
                "seed": seed,
                "intent_level": guna,
                "compression_ratio": comp_result.compression_ratio,
                "service": service_instance.__class__.__name__ if service_instance else "None"
            },
            "akash": self._akash,
            "maha_cell": None,
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
