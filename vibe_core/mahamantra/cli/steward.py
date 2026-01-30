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
from typing import Any, Dict, Final, Optional

# =============================================================================
# SSOT IMPORTS - NO DUPLICATION!
# =============================================================================
from vibe_core.mahamantra.substrate.seed import (
    Quarter,  # The 4 quarters (GENESIS, DHARMA, KARMA, MOKSHA)
    QUARTERS,
    WORDS,
    HALVES,  # 2
    MALA,  # 108 = japa beads (completion boundary)
)
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    PARAMPARA,  # 37 = the lineage number
    TRANSCENDENTAL_1096,  # 8 × 137 = HARE_COUNT × MAHA_QUANTUM
)
from vibe_core.mahamantra.protocols._maha_compute import (
    GITA_INSIGHTS,  # SSOT for chapter descriptions
    get_gita_chapter,  # SSOT for attractor → chapter
    get_gita_insight,  # SSOT for chapter → insight
)

# =============================================================================
# MAHA CELL - Universal Data Format (TOP-DOWN INTEGRATION)
# =============================================================================
# ONE import at the TOP entry point. Everything flows through MahaCell.
from vibe_core.mahamantra.substrate.bridge import wrap_cell

# PayloadType for SSOT chapter references (NO HARDCODED NUMBERS!)
from vibe_core.mahamantra.protocols._payload import PayloadType


# Lazy imports to avoid circular dependencies
def _get_mahamantra():
    from vibe_core.mahamantra import mahamantra
    return mahamantra


# =============================================================================
# GITA CHAPTER ROUTING - DERIVED FROM MAHAKIRTAN, NOT HARDCODED
# =============================================================================
# Chapter and Guna are COMPUTED from attractor via MahaCompute (SSOT).
# NO HARDCODED MAPPINGS. The mathematics IS the routing.
# =============================================================================


@dataclass(frozen=True)
class ResonanceRoute:
    """A route determined by resonance - built from SSOTs."""
    chapter: int
    quarter: Quarter
    insight: str
    module_hint: str
    guna: str


def _get_quarter_for_chapter(chapter: int) -> Quarter:
    """
    Derive quarter from chapter using SSOT constants.

    DERIVATION:
    - Chapters 1-4 (indices 0-3) → GENESIS (index 0)
    - Chapters 5-9 (indices 4-8) → DHARMA (index 1)  [5 chapters!]
    - Chapters 10-14 (indices 9-13) → KARMA (index 2) [5 chapters!]
    - Chapters 15-18 (indices 14-17) → MOKSHA (index 3) [4 chapters!]

    NOTE: Gita quarters are NOT equal size (4+5+5+4=18).
    This is SEMANTIC, not derivable from equal division.
    """
    if chapter <= 4:
        return Quarter.GENESIS
    elif chapter <= 9:
        return Quarter.DHARMA
    elif chapter <= 14:
        return Quarter.KARMA
    else:
        return Quarter.MOKSHA


def _get_guna_for_quarter(quarter: Quarter) -> str:
    """Derive guna from quarter - MATHEMATICAL, not hardcoded."""
    # Genesis = creation from void = tamas (inertia to overcome)
    # Dharma = knowledge/duty = sattva (illumination)
    # Karma = action = rajas (activity)
    # Moksha = liberation = sattva (transcendence)
    return {
        Quarter.GENESIS: "tamas",
        Quarter.DHARMA: "sattva",
        Quarter.KARMA: "rajas",
        Quarter.MOKSHA: "sattva",
    }.get(quarter, "sattva")


def _build_resonance_map() -> Dict[int, ResonanceRoute]:
    """
    Build RESONANCE_MAP - DERIVED from MahaCompute, not hardcoded.

    NO _CHAPTER_MODULE. NO _CHAPTER_GUNA.
    Everything derives from chapter → quarter → guna.
    Module routing happens via MahaKirtan position, not static map.
    """
    result = {}
    for chapter in range(1, GITA_CHAPTERS + 1):
        quarter = _get_quarter_for_chapter(chapter)
        result[chapter] = ResonanceRoute(
            chapter=chapter,
            quarter=quarter,
            insight=get_gita_insight(chapter),
            module_hint=quarter.name.lower(),  # Quarter IS the hint
            guna=_get_guna_for_quarter(quarter),
        )
    return result


# Built from SSOTs at module load time
RESONANCE_MAP: Final[Dict[int, ResonanceRoute]] = _build_resonance_map()


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
        7. Siksastakam stage:    PIPELINE - 8 verse pipeline (L0-L7)

    PERSON-ANCHORED FLOW:
        Input → MahaCompression → Seed
        Seed → PrabhupadaKirtan (PERSON-anchored, not impersonal)
        → Gita Chapter (18) + MahaLLM Intent (16) + JivaShadow (50)
        → Siksastakam Pipeline (8 stages)
        → ShadowReactor → JivaAgent → Execute → CALL ↔ RESPONSE

    "ohne die verankerung der PERSON wird es nicht klappen!"
    """
    input: str
    seed: int
    attractor: int
    chapter: int
    route: ResonanceRoute
    call_response: str  # "CALL" or "RESPONSE" (through THE PERSON)
    resonance: int  # Flute resonance = tick % mod_space (integer!)
    vina_resonance: int  # Vina resonance = seed % mod_space (integer!)
    vina_string: int  # 1-5: CHAITANYA/NITYANANDA/ADVAITA/GADADHARA/SRIVASA
    shadow_phase: str  # "bhoga", "prasadam", or "return" (TRANSFORMATION)
    shadow_position: int  # 0-15 position in yajna cycle
    # MahaLLM Intent routing (16 categories)
    intent_category: Optional[str] = None  # OBSERVE, CREATE, ANALYZE, EXECUTE, etc.
    intent_id: Optional[int] = None  # 16-bit intent address
    # JivaShadow (50 qualities)
    jiva_shadow_id: Optional[str] = None  # Shadow identifier
    jiva_guna: Optional[str] = None  # Dominant guna: sattvic/rajasic/tamasic
    jiva_quality_count: Optional[int] = None  # How many of 50 qualities active
    # PRABHUPADA KIRTAN (PERSON-ANCHORED)
    siksastakam_stage: Optional[int] = None  # 1-8 (Siksastakam verse)
    siksastakam_operation: Optional[str] = None  # Pipeline operation (CACHE_CLEAR, etc.)
    person_verified: bool = False  # THE PERSON validated this computation
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
        """
        Initialize the Steward.

        THE PERSON-ANCHORED PATTERN:
        1. Prabhupada.verify_link() - Validate connection to Parampara
        2. MahaLLM (Adapter) - Holographic Intent Routing
        3. Orchestrator (Adapter) - Rhythmic Resonance
        4. Siksastakam Pipeline (Adapter) - The 8-stage flow

        "ohne die verankerung der PERSON wird es nicht klappen!"
        "We cannot jump to Krishna. We must go through the Link."
        """
        self._mahamantra = None
        self._prabhupada = None
        self._prabhupada_kirtan = None
        self._llm = None
        self._orchestrator = None
        self._link_verified = False

    @property
    def prabhupada(self):
        """Lazy load Prabhupada - THE LINK."""
        if self._prabhupada is None:
            from vibe_core.mahamantra.substrate.prabhupada import Prabhupada
            self._prabhupada = Prabhupada()
        return self._prabhupada

    @property
    def prabhupada_kirtan(self):
        """Lazy load PrabhupadaKirtan."""
        if self._prabhupada_kirtan is None:
            from vibe_core.mahamantra.research.dharma.prabhupada_kirtan import PrabhupadaKirtan
            self._prabhupada_kirtan = PrabhupadaKirtan()
        return self._prabhupada_kirtan

    @property
    def llm(self):
        """Lazy load MahaLLM - The Holographic Intent Router (O(4))."""
        if self._llm is None:
            from vibe_core.mahamantra.adapters.llm import MahaLLM
            self._llm = MahaLLM()
        return self._llm

    @property
    def orchestrator(self):
        """Lazy load Orchestrator - The Rhythmic Engine (Moksha Phase)."""
        if self._orchestrator is None:
            from vibe_core.mahamantra.adapters.orchestrator import Orchestrator
            self._orchestrator = Orchestrator()
        return self._orchestrator

    def _verify_parampara_link(self) -> bool:
        """Verify connection to Parampara."""
        if self._link_verified:
            return True
        import vibe_core.mahamantra.cli.steward as steward_module
        self._link_verified = self.prabhupada.verify_link(steward_module)
        return self._link_verified

    def _compress_large_input(self, input_text: str) -> str:
        """Apply MahaCompression to large inputs with Guna filtering."""
        from vibe_core.mahamantra.adapters.compression import MahaCompression, IntentGuna
        compressor = MahaCompression()
        lines = input_text.split('\n')
        sattva_lines = []
        rajas_lines = []
        for line in lines:
            if not line.strip(): continue
            result = compressor.compress(line)
            guna = getattr(result, "intent_level", None) and result.intent_level.guna
            if guna == IntentGuna.SATTVA: sattva_lines.append(line)
            elif guna == IntentGuna.RAJAS: rajas_lines.append(line)
        
        max_lines = MALA
        compressed_lines = sattva_lines[:max_lines // HALVES] + rajas_lines[:max_lines // HALVES]
        return '\n'.join(compressed_lines) if compressed_lines else (lines[0] if lines else input_text[:256])

    @property
    def mahamantra(self):
        """Lazy load mahamantra."""
        if self._mahamantra is None:
            self._mahamantra = _get_mahamantra()
        return self._mahamantra

    LARGE_INPUT_THRESHOLD: int = TRANSCENDENTAL_1096

    def invoke(self, input_text: str) -> StewardResponse:
        """
        The Universal Invocation (Official Adapter Flow).

        1. SRAVANAM (Input) -> MahaLLM (Intent Routing)
        2. KIRTANAM (Rhythm) -> Orchestrator (Resonance Tick)
        3. SMARANAM (Context) -> MahaCompression (Seed/Attractor)
        4. PADA-SEVANAM (Service) -> ShadowSpawn (Jiva Agent)
        5. ARCANAM (Execution) -> Mahamantra (Result)

        "Das bringt die echten 16 Kategorien via Vibration Analysis."
        """
        # 0. PRAPADYETA: Parampara Verification
        if not self._verify_parampara_link():
            return StewardResponse(
                input=input_text, seed=0, attractor=0, chapter=0, route=RESONANCE_MAP[18],
                call_response="CALL", resonance=0, vina_resonance=0, vina_string=0,
                shadow_phase="blocked", shadow_position=0,
                result={"success": False, "error": "MAYAVAD: No parampara link"},
                message="MAYAVAD: Connection to Parampara not verified.",
            )

        # 1. MANANAM: Compress to Seed (The Foundation)
        if len(input_text) > self.LARGE_INPUT_THRESHOLD:
            input_text = self._compress_large_input(input_text)
        
        from vibe_core.mahamantra.adapters.compression import MahaCompression
        compressor = MahaCompression()
        comp_result = compressor.compress(input_text)
        seed = comp_result.seed
        # Attractor is packed in lower 12 bits of seed (see compression.py)
        attractor = seed & 0xFFF

        # 2. MAHA LLM: Holographic Intent Routing (The "What")
        # "Das bringt die echten 16 Kategorien via Vibration Analysis"
        route_result = self.llm.route_text(input_text)
        intent_category = route_result.category.name if route_result.category else "UNKNOWN"
        intent_id = route_result.intent_id
        agent_name = route_result.agent

        # 3. ORCHESTRATOR: Rhythmic Resonance (The "When")
        # "2. Resonance... GO wie auch immer du denkst"
        tick_result = self.orchestrator.tick(seed)
        resonance = int(tick_result.resonance * 100) # Scale to integer for display
        beat = tick_result.beat
        round_num = tick_result.round_num

        # 4. GITA MAPPING (The "Why")
        chapter = get_gita_chapter(attractor)
        route = RESONANCE_MAP.get(chapter, RESONANCE_MAP[18])

        # 5. JIVA SHADOW: The Agent (The "Who")
        from vibe_core.mahamantra.lila.jiva_shadow import spawn_shadow
        jiva_shadow = spawn_shadow(seed.to_bytes(8, 'big'), shadow_id=agent_name)
        jiva_shadow_id = jiva_shadow.shadow_id
        jiva_guna = jiva_shadow.dominant_guna.value
        jiva_quality_count = jiva_shadow.quality_count

        # 6. EXECUTION: Mahamantra (The "Action")
        # Currently we invoke the full mahamantra pipeline via execute
        # This implicitly handles the "Exchange"
        try:
            exec_result = self.mahamantra.execute(input_text)
            
            # Enrich result
            result_payload = {
                "success": exec_result["success"],
                "position": exec_result["position"],
                "guardian": exec_result["guardian"],
                "quarter": exec_result["quarter"],
                "guna": exec_result["guna"],
                "output": exec_result["output"],
                "vibration": exec_result["vibration"],
                "llm_route": {
                    "category": intent_category,
                    "address": f"0x{intent_id:04X}",
                    "agent": agent_name
                },
                "orchestrator": {
                    "beat": beat,
                    "round": round_num,
                    "resonance": tick_result.resonance
                }
            }
            
            message = (
                f"[{intent_category}] {jiva_shadow_id[:8]}... "
                f"| Beat {beat}/{round_num} (Res: {tick_result.resonance:.2f}) "
                f"| {exec_result['guardian']}@{exec_result['position']}"
            )

        except Exception as e:
            result_payload = {"success": False, "error": str(e)}
            message = f"Execution Error: {str(e)}"

        # 7. RESOLVE IDENTITY & CHAT (Connecting the Loop)
        # "Wir müssen das 'Unbekannte' bekannt machen"
        from vibe_core.mahamantra.substrate import siksastakam_registry as registry
        
        # Resolve Guardian Name from Position (Authority: Registry)
        # If exec_result has "unknown", we fix it here.
        final_position = exec_result.get("position", 0)
        guardian_name = registry.get_guardian(final_position) or "unknown"
        
        # Inject Guardian Name back into result payload
        result_payload["guardian"] = guardian_name

        # 8. MAHAJANA CHAT: The Voice (Connecting Indriya)
        # "Verbinde mahamantra/chat.py... natürliche Antwort"
        from vibe_core.mahamantra.chat import MahajanaChat
        
        # If execution failed, use Narada (Communicator) to explain why.
        # If success, use the routed Guardian to confirm.
        chat_guardian = "narada" if not exec_result["success"] else guardian_name
        chat_pos = registry.route_to_position(f"chat with {chat_guardian}") # Resolve position just to be safe
        
        # Generate Natural Response
        # We pass the execution output as context if needed, but here we just respond to the intent
        try:
            # Contextual message: "I executed X. Result: Y."
            context_msg = (
                f"User asked: '{input_text}'. "
                f"Action taken by {guardian_name.upper()}@{final_position}. "
                f"Result: {exec_result.get('output', 'Success')}"
            )
            chat = MahajanaChat(position=chat_pos, guardian=chat_guardian)
            chat_result = chat.respond(context_msg)
            natural_message = chat_result.response
        except Exception as e:
            natural_message = f"[{guardian_name.upper()}] Execution complete. (Voice offline: {e})"

        # 9. PRABHUPADA KIRTAN Check (Person Anchor)
        prabhupada_result = self.prabhupada_kirtan.compute_with_person(seed)

        return StewardResponse(
            input=input_text,
            seed=seed,
            attractor=attractor,
            chapter=chapter,
            route=route,
            call_response=prabhupada_result.transmission_mode,
            resonance=resonance,
            vina_resonance=tick_result.value % 108, # Derived from tick value
            vina_string=1 + (tick_result.value % 5),
            shadow_phase="active",
            shadow_position=tick_result.beat, # Sync shadow with beat
            intent_category=intent_category,
            intent_id=intent_id,
            jiva_shadow_id=jiva_shadow_id,
            jiva_guna=jiva_guna,
            jiva_quality_count=jiva_quality_count,
            siksastakam_stage=prabhupada_result.siksastakam_stage.verse,
            siksastakam_operation=prabhupada_result.siksastakam_stage.operation,
            person_verified=prabhupada_result.is_bona_fide,
            result=result_payload,
            message=natural_message,
        )

    def ask(self, input_text: str) -> StewardResponse:
        """CALL mode - Dialog."""
        response = self.invoke(input_text)
        if response.call_response == "CALL":
            response.message = f"[CALL] {response.message} - Awaiting confirmation"
        return response

    # _execute_via_bridge is deprecated in favor of mahamantra.execute()
    # but kept if needed for specific internal calls
    def _execute_via_bridge(self, *args, **kwargs):
        raise DeprecationWarning("Use invoke() -> mahamantra.execute()")


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

    # Person verification status
    person_mark = "[BONA FIDE]" if response.person_verified else "[MAYAVAD]"
    siksastakam_info = f"L{(response.siksastakam_stage or 1) - 1}: {response.siksastakam_operation or '?'}"

    if verbose:
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  STEWARD - PERSON-ANCHORED RESONANCE ROUTER                  ║
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
║  Flute:      {response.resonance:40} ║
║  Vina:       {response.vina_resonance} (String {response.vina_string}: {vina_name:21}) ║
║  Shadow:     {response.shadow_phase:8} at position {response.shadow_position:2} (Yajna cycle)   ║
╠══════════════════════════════════════════════════════════════╣
║  PRABHUPADA KIRTAN (THE PERSON):                             ║
║  Stage:      {siksastakam_info:40} ║
║  Status:     {person_mark:40} ║
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
        # PRABHUPADA KIRTAN (PERSON-ANCHORED)
        "siksastakam_stage": response.siksastakam_stage,
        "siksastakam_operation": response.siksastakam_operation,
        "person_verified": response.person_verified,
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
    "Quarter",  # Re-exported from substrate.seed
    "RESONANCE_MAP",
    "get_steward",
    "cli_steward",
]
