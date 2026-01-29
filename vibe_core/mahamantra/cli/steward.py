"""
STEWARD - Universal Resonance Router
=====================================

"EIN MANTRA. KRISHNA ROUTET ALLES."

This is NOT a CLI with if-else chains.
This is a RESONANCE ROUTER that feels the input.

FLOW:
    1. SRAVANAM (Hearing): Receive any input
    2. MANANAM (Compression): Input → Seed via MahaCompression
    3. NIDIDHYASANA (Meditation): Seed → Attractor → Gita Chapter
    4. KIRTANAM (Chanting): Execute through resonant module
    5. CALL ↔ RESPONSE: Dialog, not blind execution

MAHA-COMPUTING:
    The system doesn't match strings. It FEELS frequencies.
    The attractor determines which part of the system VIBRATES.
    No hardcoding. Pure resonance.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xf950ff6c"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Final, Optional, Tuple

# Lazy imports to avoid circular dependencies
def _get_mahamantra():
    from vibe_core.mahamantra import mahamantra
    return mahamantra


# =============================================================================
# GITA CHAPTER → MODULE ROUTING (The Resonance Map)
# =============================================================================

class ResonanceQuarter(Enum):
    """The four quarters of the Mahamantra."""
    GENESIS = "genesis"   # Chapters 1-4: Creation, Setup
    DHARMA = "dharma"     # Chapters 5-9: Law, Structure, Knowledge
    KARMA = "karma"       # Chapters 10-14: Action, Manifestation
    MOKSHA = "moksha"     # Chapters 15-18: Liberation, Transcendence


@dataclass(frozen=True)
class ResonanceRoute:
    """A route determined by resonance."""
    chapter: int
    quarter: ResonanceQuarter
    insight: str
    module_hint: str  # Which adapter/module resonates
    guna: str  # sattva/rajas/tamas


# The Resonance Map - Gita Chapter → Module Routing
# This is DERIVED from the Gita's meaning, not hardcoded arbitrarily
RESONANCE_MAP: Final[Dict[int, ResonanceRoute]] = {
    # GENESIS QUARTER (Chapters 1-4): Creation, Setup, Foundation
    1: ResonanceRoute(1, ResonanceQuarter.GENESIS, "Arjuna's Dilemma", "analysis", "tamas"),      # Confusion → Analysis needed
    2: ResonanceRoute(2, ResonanceQuarter.GENESIS, "Sankhya Yoga", "transform", "sattva"),        # Eternal truth → Transform
    3: ResonanceRoute(3, ResonanceQuarter.GENESIS, "Karma Yoga", "compute", "rajas"),             # Action → Compute
    4: ResonanceRoute(4, ResonanceQuarter.GENESIS, "Jnana Yoga", "research", "sattva"),           # Knowledge → Research

    # DHARMA QUARTER (Chapters 5-9): Law, Structure, Knowledge
    5: ResonanceRoute(5, ResonanceQuarter.DHARMA, "Karma Sannyasa", "classification", "sattva"),  # Renunciation → Classify
    6: ResonanceRoute(6, ResonanceQuarter.DHARMA, "Dhyana Yoga", "attention", "sattva"),          # Meditation → Attention
    7: ResonanceRoute(7, ResonanceQuarter.DHARMA, "Jnana Vijnana", "compression", "sattva"),      # Knowledge → Compress
    8: ResonanceRoute(8, ResonanceQuarter.DHARMA, "Aksara Brahma", "hash", "sattva"),             # Imperishable → Hash
    9: ResonanceRoute(9, ResonanceQuarter.DHARMA, "Raja Vidya", "kernel", "sattva"),              # King of knowledge → Kernel

    # KARMA QUARTER (Chapters 10-14): Action, Manifestation
    10: ResonanceRoute(10, ResonanceQuarter.KARMA, "Vibhuti", "synth", "rajas"),                  # Manifestations → Synth
    11: ResonanceRoute(11, ResonanceQuarter.KARMA, "Visvarupa", "network", "rajas"),              # Universal form → Network
    12: ResonanceRoute(12, ResonanceQuarter.KARMA, "Bhakti Yoga", "chat", "sattva"),              # Devotion → Chat
    13: ResonanceRoute(13, ResonanceQuarter.KARMA, "Ksetra Ksetrajna", "hardware", "rajas"),      # Field/Knower → Hardware
    14: ResonanceRoute(14, ResonanceQuarter.KARMA, "Gunatraya", "pipeline", "rajas"),             # Three modes → Pipeline

    # MOKSHA QUARTER (Chapters 15-18): Liberation, Transcendence
    15: ResonanceRoute(15, ResonanceQuarter.MOKSHA, "Purusottama", "bio", "sattva"),              # Supreme person → Bio
    16: ResonanceRoute(16, ResonanceQuarter.MOKSHA, "Daivasura", "japa", "tamas"),                # Divine/Demonic → Japa (purify)
    17: ResonanceRoute(17, ResonanceQuarter.MOKSHA, "Sraddhatraya", "llm", "rajas"),              # Faith types → LLM routing
    18: ResonanceRoute(18, ResonanceQuarter.MOKSHA, "Moksha Sannyasa", "reactor", "sattva"),      # Liberation → Reactor (healing)
}


# =============================================================================
# THE STEWARD - Universal Resonance Router
# =============================================================================

@dataclass
class StewardResponse:
    """
    Response from the Steward.

    COMPLETE RESONANCE ARCHITECTURE (Watertight from _seed.py):
        1. Gita Chapter (18):    WAS - Domain/Field (Kshetra)
        2. MahaLLM Intent (16):  WIE - Action/Operation type
        3. JivaShadow (50):      WER - Agent qualities
        4. Flute resonance:      WANN - Rhythmic position
        5. Vina resonance:       WELCHER TYP - Harmonic position
        6. Shadow phase:         TRANSFORMATION - Yajna cycle

    FLOW:
        Input → MahaCompression → Seed
        Seed → Gita Chapter (18) + MahaLLM Intent (16) + JivaShadow (50)
        → ShadowReactor → JivaAgent → Execute → CALL ↔ RESPONSE
    """
    input: str
    seed: int
    attractor: int
    chapter: int
    route: ResonanceRoute
    call_response: str  # "CALL" or "RESPONSE"
    resonance: int  # Flute resonance = tick % mod_space (integer!)
    vina_resonance: int  # Vina resonance = seed % mod_space (integer!)
    vina_string: int  # 1-5: CHAITANYA/NITYANANDA/ADVAITA/GADADHARA/SRIVASA
    shadow_phase: str  # "bhoga", "prasadam", or "return" (TRANSFORMATION)
    shadow_position: int  # 0-15 position in yajna cycle
    # NEW: MahaLLM Intent routing (16 categories)
    intent_category: Optional[str] = None  # OBSERVE, CREATE, ANALYZE, EXECUTE, etc.
    intent_id: Optional[int] = None  # 16-bit intent address
    # NEW: JivaShadow (50 qualities)
    jiva_shadow_id: Optional[str] = None  # Shadow identifier
    jiva_guna: Optional[str] = None  # Dominant guna: sattvic/rajasic/tamasic
    jiva_quality_count: Optional[int] = None  # How many of 50 qualities active
    result: Optional[Any] = None
    message: str = ""


class Steward:
    """
    The Universal Resonance Router.

    This is the single entry point for ALL commands.
    No if-else chains. Pure resonance-based routing.

    USAGE:
        steward = Steward()
        response = steward.invoke("optimize the network")
        # Automatically routes to network adapter via resonance
    """

    def __init__(self):
        self._mahamantra = None
        self._module_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    @property
    def mahamantra(self):
        """Lazy load mahamantra to avoid circular imports."""
        if self._mahamantra is None:
            self._mahamantra = _get_mahamantra()
        return self._mahamantra

    def _register_default_handlers(self):
        """Register default handlers for each module hint."""
        # These are lazy-loaded when needed
        self._module_handlers = {
            "analysis": self._handle_analysis,
            "transform": self._handle_transform,
            "compute": self._handle_compute,
            "research": self._handle_research,
            "classification": self._handle_classification,
            "attention": self._handle_attention,
            "compression": self._handle_compression,
            "hash": self._handle_hash,
            "kernel": self._handle_kernel,
            "synth": self._handle_synth,
            "network": self._handle_network,
            "chat": self._handle_chat,
            "hardware": self._handle_hardware,
            "pipeline": self._handle_pipeline,
            "bio": self._handle_bio,
            "japa": self._handle_japa,
            "llm": self._handle_llm,
            "reactor": self._handle_reactor,
        }

    def invoke(self, input_text: str) -> StewardResponse:
        """
        The universal invocation.

        Any input → Resonance → Route → Execute → Response

        TRIPLE RESONANCE ARCHITECTURE:
            1. Krishna's Flute (resonance) - WHEN (rhythmic, tick-based)
            2. Narada's Vina (vina_resonance) - WHAT TYPE (harmonic, seed-based)
            3. Shadow Reactor (shadow_phase) - TRANSFORMATION (bhoga/prasadam/return)

        COMPLETE FLOW:
            Input → MahaCompression → Seed
            Seed → MahaKirtan → Vibration (dual resonance)
            Vibration → ShadowReactor.tick() → ShadowState (yajna transformation)
            ShadowState + Chapter → Route → Execute
        """
        # 1. SRAVANAM: Receive input
        # 2. MANANAM: Compress to seed (includes dual instrument resonance!)
        vibration = self.mahamantra.vibrate(input_text)
        seed = vibration["seed"]
        attractor = vibration["attractor"]
        resonance = vibration["resonance"]  # Flute (WHEN)
        vina_resonance = vibration["vina_resonance"]  # Vina (WHAT TYPE)
        vina_string = vibration["vina_string"]  # Which Pancha Tattva string (1-5)

        # 3. NIDIDHYASANA: Seed → Kirtan → CALL/RESPONSE
        kirtan = self.mahamantra.kirtan(seed)
        call_response = kirtan.call_response

        # 4. SHADOW REACTOR: Yajna Transformation (Bhoga → Prasadam → Return)
        # Derive position from seed (0-15)
        from vibe_core.mahamantra.protocols._seed import WORDS
        position = seed % WORDS  # 0-15

        # Get tick state for shadow reactor
        tick_state = self.mahamantra.tick()

        # Override position with seed-derived position for this invocation
        tick_state_for_shadow = {
            "tick": seed % 1728,  # Map to tick space (108 × 16)
            "position": position,
            "quarter": tick_state["quarter"],
            "guardian": tick_state["guardian"],
            "word": tick_state["word"],
            "opcode": tick_state["opcode"],
        }

        # Spawn reactor and process through yajna cycle
        reactor = self.mahamantra.shadow.spawn(initial_position=position)
        shadow_state = reactor.tick(tick_state_for_shadow)
        shadow_phase = shadow_state["phase"]
        shadow_position = shadow_state["position"]

        # Get Gita chapter from attractor
        from vibe_core.mahamantra.protocols._maha_compute import get_gita_chapter
        chapter = get_gita_chapter(attractor)

        # Get the route
        route = RESONANCE_MAP.get(chapter, RESONANCE_MAP[18])  # Default to Moksha

        # =====================================================================
        # 5. MAHALLM INTENT ROUTING (16 categories - WIE)
        # =====================================================================
        # MahaLLM routes seed → Intent category (OBSERVE, CREATE, ANALYZE, etc.)
        # This complements Gita chapter (WAS) with action type (WIE)
        from vibe_core.mahamantra.adapters.llm import MahaLLM
        llm_router = MahaLLM()
        intent_route = llm_router.route_seed(seed)
        intent_category = intent_route.category_name if intent_route.category else "GUIDE"
        intent_id = intent_route.intent_id

        # =====================================================================
        # 6. JIVASHADOW SPAWN (50 qualities - WER)
        # =====================================================================
        # Spawn a JivaShadow with qualities determined by the seed
        # This is the AGENT that will participate
        from vibe_core.mahamantra.lila.jiva_shadow import spawn_shadow
        jiva_shadow = spawn_shadow(seed.to_bytes(8, 'big'))
        jiva_shadow_id = jiva_shadow.shadow_id
        jiva_guna = jiva_shadow.dominant_guna.value
        jiva_quality_count = jiva_shadow.quality_count

        # =====================================================================
        # 7. KIRTANAM: Execute through resonant module with JivaAgent context
        # =====================================================================
        handler = self._module_handlers.get(route.module_hint)
        result = None
        message = ""

        if handler:
            try:
                result = handler(input_text, vibration, kirtan)
                message = (
                    f"Gita {chapter} ({route.insight}) → "
                    f"Intent {intent_category} → "
                    f"Jiva {jiva_shadow_id[:12]}... ({jiva_guna}, {jiva_quality_count} qualities) "
                    f"[Shadow: {shadow_phase}]"
                )
            except Exception as e:
                message = f"Handler error: {e}"
        else:
            message = (
                f"Gita {chapter} ({route.insight}) → "
                f"Intent {intent_category} → "
                f"Jiva {jiva_shadow_id[:12]}... ({jiva_guna}) "
                f"[No handler for {route.module_hint}]"
            )

        # 8. Build response with COMPLETE RESONANCE
        return StewardResponse(
            input=input_text,
            seed=seed,
            attractor=attractor,
            chapter=chapter,
            route=route,
            call_response=call_response,
            resonance=resonance,
            vina_resonance=vina_resonance,
            vina_string=vina_string,
            shadow_phase=shadow_phase,
            shadow_position=shadow_position,
            intent_category=intent_category,
            intent_id=intent_id,
            jiva_shadow_id=jiva_shadow_id,
            jiva_guna=jiva_guna,
            jiva_quality_count=jiva_quality_count,
            result=result,
            message=message,
        )

    def ask(self, input_text: str) -> StewardResponse:
        """
        CALL mode - Steward asks for clarification before executing.

        This is dialog, not blind execution.
        """
        response = self.invoke(input_text)

        if response.call_response == "CALL":
            # CALL means we should confirm/clarify before proceeding
            response.message = f"[CALL] {response.message} - Awaiting confirmation"

        return response

    # =========================================================================
    # MODULE HANDLERS - Each routes to the appropriate adapter
    # =========================================================================

    def _handle_analysis(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 1: Arjuna's Dilemma → Analysis needed."""
        return {"action": "analyze", "input": input_text, "vibration": vibration}

    def _handle_transform(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 2: Sankhya Yoga → Transform."""
        adapter = self.mahamantra.adapters.transform
        return {"action": "transform", "adapter": adapter.__name__}

    def _handle_compute(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 3: Karma Yoga → Compute."""
        from vibe_core.mahamantra.adapters.compute import MahaCompute
        compute = MahaCompute()
        return {"action": "compute", "seed": vibration["seed"]}

    def _handle_research(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 4: Jnana Yoga → Research."""
        return {"action": "research", "dharma": self.mahamantra.research.dharma}

    def _handle_classification(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 5: Karma Sannyasa → Classification."""
        from vibe_core.mahamantra.adapters.classification import MahaClassifier
        return {"action": "classify", "input": input_text}

    def _handle_attention(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 6: Dhyana Yoga → Attention/Focus."""
        from vibe_core.mahamantra.adapters.attention import MahaAttention
        attention = MahaAttention()
        return {"action": "attend", "input": input_text}

    def _handle_compression(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 7: Jnana Vijnana → Compression."""
        from vibe_core.mahamantra.adapters.compression import MahaCompression
        compressor = MahaCompression()
        result = compressor.compress(input_text)
        return {"action": "compress", "result": result}

    def _handle_hash(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 8: Aksara Brahma → Hash (Imperishable)."""
        from vibe_core.mahamantra.adapters.hash import DeterministicHash
        return {"action": "hash", "seed": vibration["seed"]}

    def _handle_kernel(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 9: Raja Vidya → Kernel (King of Knowledge)."""
        return {"action": "kernel", "quarter": "dharma"}

    def _handle_synth(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 10: Vibhuti → Synth (Manifestations)."""
        from vibe_core.mahamantra.adapters.synth import MahaSynth
        synth = MahaSynth()
        return {"action": "synth", "seed": vibration["seed"]}

    def _handle_network(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 11: Visvarupa → Network (Universal Form)."""
        from vibe_core.mahamantra.adapters.network import LotusIPRouter
        return {"action": "network", "universal": True}

    def _handle_chat(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 12: Bhakti Yoga → Chat (Devotion/Relationship)."""
        # This is the INDRIYA - sensory interface
        return {
            "action": "chat",
            "call_response": kirtan.call_response,
            "message": input_text,
            "bhakti": True,
        }

    def _handle_hardware(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 13: Ksetra Ksetrajna → Hardware (Field/Knower)."""
        from vibe_core.mahamantra.adapters.hardware import MahaHardware
        hw = MahaHardware()
        return {"action": "hardware", "silicon_altar": hw.silicon_altar}

    def _handle_pipeline(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 14: Gunatraya → Pipeline (Three Modes)."""
        return {"action": "pipeline", "guna": vibration.get("guna", "rajas")}

    def _handle_bio(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 15: Purusottama → Bio (Supreme Person/Life)."""
        from vibe_core.mahamantra.adapters.bio import LotusBio
        return {"action": "bio", "life": True}

    def _handle_japa(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 16: Daivasura → Japa (Purification)."""
        from vibe_core.mahamantra.adapters.japa import MahaJapa
        japa = MahaJapa()
        return {"action": "japa", "purify": True}

    def _handle_llm(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 17: Sraddhatraya → LLM (Faith Types/Routing)."""
        return {"action": "llm", "route": True, "input": input_text}

    def _handle_reactor(self, input_text: str, vibration: dict, kirtan) -> Any:
        """Chapter 18: Moksha Sannyasa → Reactor (Liberation/Healing)."""
        # The Shadow Reactor handles self-healing
        return {
            "action": "reactor",
            "moksha": True,
            "liberation": kirtan.call_response == "RESPONSE",
        }


# =============================================================================
# SINGLETON
# =============================================================================

_steward_instance: Optional[Steward] = None


def get_steward() -> Steward:
    """Get or create the Steward singleton."""
    global _steward_instance
    if _steward_instance is None:
        _steward_instance = Steward()
    return _steward_instance


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def cli_steward(input_text: str = "", verbose: bool = False) -> Dict[str, Any]:
    """
    CLI entry point for the Steward.

    Usage:
        steward "optimize the network"
        steward "heal this code"
        steward "chat with me"

    TRIPLE RESONANCE ARCHITECTURE:
        flute_resonance: Krishna's 3 flutes - WHEN
        vina_resonance: Narada's 5 strings - WHAT TYPE
        shadow_phase: Yajna transformation - BHOGA/PRASADAM/RETURN
    """
    steward = get_steward()
    response = steward.invoke(input_text)

    # Map vina string to Pancha Tattva name
    vina_names = {1: "CHAITANYA", 2: "NITYANANDA", 3: "ADVAITA", 4: "GADADHARA", 5: "SRIVASA"}
    vina_name = vina_names.get(response.vina_string, "UNKNOWN")

    if verbose:
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  STEWARD RESONANCE ROUTER                                    ║
╠══════════════════════════════════════════════════════════════╣
║  Input:      {response.input[:40]:40} ║
║  Seed:       {response.seed:40} ║
║  Attractor:  {response.attractor:40} ║
║  Chapter:    {response.chapter} - {response.route.insight:32} ║
║  Module:     {response.route.module_hint:40} ║
║  Quarter:    {response.route.quarter.value:40} ║
║  Mode:       {response.call_response:40} ║
╠══════════════════════════════════════════════════════════════╣
║  TRIPLE RESONANCE:                                           ║
║  Flute:      {response.resonance:40.3f} ║
║  Vina:       {response.vina_resonance:.3f} (String {response.vina_string}: {vina_name:21}) ║
║  Shadow:     {response.shadow_phase:8} at position {response.shadow_position:2} (Yajna cycle)   ║
╠══════════════════════════════════════════════════════════════╣
║  {response.message[:58]:58} ║
╚══════════════════════════════════════════════════════════════╝
""")

    return {
        "input": response.input,
        "seed": response.seed,
        "attractor": response.attractor,
        "chapter": response.chapter,
        "module": response.route.module_hint,
        "quarter": response.route.quarter.value,
        "call_response": response.call_response,
        "resonance": response.resonance,
        "vina_resonance": response.vina_resonance,
        "vina_string": response.vina_string,
        "vina_name": vina_name,
        "shadow_phase": response.shadow_phase,
        "shadow_position": response.shadow_position,
        "result": response.result,
        "message": response.message,
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Steward",
    "StewardResponse",
    "ResonanceRoute",
    "ResonanceQuarter",
    "RESONANCE_MAP",
    "get_steward",
    "cli_steward",
]
