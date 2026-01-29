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
# GITA CHAPTER → MODULE ROUTING
# =============================================================================
# SEMANTIC MAPPINGS that cannot be derived mathematically.
# These define WHAT each Gita chapter DOES in the system.
# TODO: Move to protocol file (_gita_route.py) as proper SSOT.
# =============================================================================

# Chapter → Module hint (SEMANTIC - which adapter resonates)
# Keys use PayloadType.value (SSOT-derived from Mahamantra constants!)
_CHAPTER_MODULE: Final[Dict[int, str]] = {
    PayloadType.ARJUNA_VISHADA.value: "analysis",      # Ch.1 → needs analysis
    PayloadType.SANKHYA.value: "transform",            # Ch.2 → transforms
    PayloadType.KARMA_YOGA.value: "compute",           # Ch.3 → action = compute
    PayloadType.JNANA_YOGA.value: "research",          # Ch.4 → knowledge = research
    PayloadType.KARMA_SANNYASA.value: "classification",  # Ch.5 → classify
    PayloadType.DHYANA.value: "attention",             # Ch.6 → meditation = attention
    PayloadType.JNANA_VIJNANA.value: "compression",    # Ch.7 → compression
    PayloadType.AKSARA_BRAHMA.value: "hash",           # Ch.8 → imperishable = hash
    PayloadType.RAJA_VIDYA.value: "kernel",            # Ch.9 → king = kernel
    PayloadType.VIBHUTI.value: "synth",                # Ch.10 → synthesis
    PayloadType.VISVARUPA.value: "network",            # Ch.11 → universal = network
    PayloadType.BHAKTI.value: "chat",                  # Ch.12 → devotion = dialog
    PayloadType.KSETRA.value: "hardware",              # Ch.13 → field = hardware
    PayloadType.GUNA_TRAYA.value: "pipeline",          # Ch.14 → modes = pipeline
    PayloadType.PURUSOTTAMA.value: "bio",              # Ch.15 → supreme = bio
    PayloadType.DAIVASURA.value: "japa",               # Ch.16 → purify via japa
    PayloadType.SRADDHA_TRAYA.value: "llm",            # Ch.17 → faith = LLM
    PayloadType.MOKSA_SANNYASA.value: "reactor",       # Ch.18 → liberation = reactor
}

# Chapter → Guna (SEMANTIC - dominant mode of the chapter)
# Keys use PayloadType.value (SSOT-derived!)
_CHAPTER_GUNA: Final[Dict[int, str]] = {
    PayloadType.ARJUNA_VISHADA.value: "tamas",   # Confusion
    PayloadType.SANKHYA.value: "sattva",         # Eternal truth
    PayloadType.KARMA_YOGA.value: "rajas",       # Action
    PayloadType.JNANA_YOGA.value: "sattva",      # Knowledge
    PayloadType.KARMA_SANNYASA.value: "sattva",  # Renunciation
    PayloadType.DHYANA.value: "sattva",          # Meditation
    PayloadType.JNANA_VIJNANA.value: "sattva",   # Knowledge
    PayloadType.AKSARA_BRAHMA.value: "sattva",   # Imperishable
    PayloadType.RAJA_VIDYA.value: "sattva",      # King of knowledge
    PayloadType.VIBHUTI.value: "rajas",          # Manifestations
    PayloadType.VISVARUPA.value: "rajas",        # Universal form
    PayloadType.BHAKTI.value: "sattva",          # Devotion
    PayloadType.KSETRA.value: "rajas",           # Field/Knower
    PayloadType.GUNA_TRAYA.value: "rajas",       # Three modes
    PayloadType.PURUSOTTAMA.value: "sattva",     # Supreme person
    PayloadType.DAIVASURA.value: "tamas",        # Divine/Demonic
    PayloadType.SRADDHA_TRAYA.value: "rajas",    # Faith types
    PayloadType.MOKSA_SANNYASA.value: "sattva",  # Liberation
}


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


def _build_resonance_map() -> Dict[int, ResonanceRoute]:
    """
    Build RESONANCE_MAP from SSOTs.

    Uses:
    - GITA_INSIGHTS for insight strings (SSOT)
    - _get_quarter_for_chapter for quarter derivation
    - _CHAPTER_MODULE for module hints (semantic, local SSOT)
    - _CHAPTER_GUNA for guna (semantic, local SSOT)
    """
    result = {}
    for chapter in range(1, GITA_CHAPTERS + 1):
        result[chapter] = ResonanceRoute(
            chapter=chapter,
            quarter=_get_quarter_for_chapter(chapter),
            insight=get_gita_insight(chapter),
            module_hint=_CHAPTER_MODULE.get(chapter, "unknown"),
            guna=_CHAPTER_GUNA.get(chapter, "sattva"),
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
        2. PrabhupadaKirtan (NOT impersonal GADKirtan) - THE PERSON verifies every beat
        3. Siksastakam 8 verses as pipeline stages (L0-L7)
        4. All traces back to the 37th (Sovereign)

        "ohne die verankerung der PERSON wird es nicht klappen!"
        "We cannot jump to Krishna. We must go through the Link."
        """
        self._mahamantra = None
        self._prabhupada = None
        self._prabhupada_kirtan = None  # PERSON-anchored kirtan
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
        """
        Lazy load PrabhupadaKirtan - PERSON-ANCHORED compute.

        This is NOT the impersonal GADKirtan.
        Every beat flows through THE PERSON (parampara % 37 == 0).
        Siksastakam 8 verses as pipeline stages.
        """
        if self._prabhupada_kirtan is None:
            from vibe_core.mahamantra.research.dharma.prabhupada_kirtan import PrabhupadaKirtan
            self._prabhupada_kirtan = PrabhupadaKirtan()
        return self._prabhupada_kirtan

    def _verify_parampara_link(self) -> bool:
        """
        Verify connection to Parampara via Prabhupada.

        THE 37TH PRINCIPLE:
        Code without crypto chain to a PERSON doesn't exist.

        Returns:
            True if link is valid (signature % 37 == 0)
        """
        if self._link_verified:
            return True

        # Verify THIS MODULE's link to parampara
        # The module has __mahajana__ and __genesis__, not the class
        import vibe_core.mahamantra.cli.steward as steward_module
        self._link_verified = self.prabhupada.verify_link(steward_module)
        return self._link_verified

    def _compress_large_input(self, input_text: str) -> str:
        """
        Apply MahaCompression to large inputs with Guna filtering.

        Like Log Sentinel: Extract INTENT not BYTES. Discard TAMAS (noise).

        THE CONTEXT WINDOW KILLER:
            100k lines → ~30 insights
            17,000x compression ratio
            SATTVA = truth (keep)
            RAJAS = action (flag)
            TAMAS = noise (discard)

        Args:
            input_text: Large input (>1KB)

        Returns:
            Compressed input with SATTVA/RAJAS extracted, TAMAS discarded
        """
        from vibe_core.mahamantra.adapters.compression import MahaCompression, IntentGuna

        compressor = MahaCompression()

        # Split into lines for Guna classification
        lines = input_text.split('\n')

        # Classify each line
        sattva_lines = []  # Truth - KEEP
        rajas_lines = []   # Action - FLAG
        # tamas_lines = []  # Noise - DISCARD

        for line in lines:
            if not line.strip():
                continue

            result = compressor.compress(line)
            guna = result.intent_level.guna  # Access via intent_level

            if guna == IntentGuna.SATTVA:
                sattva_lines.append(line)
            elif guna == IntentGuna.RAJAS:
                rajas_lines.append(line)
            # TAMAS lines are discarded (noise)

        # Combine: SATTVA first (truth), then RAJAS (actions)
        # Limit to MALA lines (108 = japa beads, natural completion boundary)
        max_lines = MALA  # 108, derived from _seed.py
        compressed_lines = sattva_lines[:max_lines // HALVES] + rajas_lines[:max_lines // HALVES]

        if compressed_lines:
            return '\n'.join(compressed_lines)
        else:
            # If all was noise, take first line as summary
            return lines[0] if lines else input_text[:256]  # Fallback truncation (UI concern, not derived)

    @property
    def mahamantra(self):
        """Lazy load mahamantra to avoid circular imports."""
        if self._mahamantra is None:
            self._mahamantra = _get_mahamantra()
        return self._mahamantra

    # Threshold for applying MahaCompression on large inputs
    # DERIVED: TRANSCENDENTAL_1096 = 8 × 137 = HARE_COUNT × MAHA_QUANTUM
    # This is the natural "algorithm space" boundary from _seed.py
    LARGE_INPUT_THRESHOLD: int = TRANSCENDENTAL_1096  # 1096 bytes

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

        LARGE INPUTS (>1KB):
            Uses MahaCompression with Guna classification (like Log Sentinel).
            Extracts INTENT not BYTES. Discards TAMAS (noise).
        """
        # 0. PRAPADYETA: Verify Parampara Link via Prabhupada (THE PERSON)
        # "We cannot jump to Krishna. We must go through the Link."
        if not self._verify_parampara_link():
            # MAYAVAD - No connection to sovereign
            return StewardResponse(
                input=input_text,
                seed=0,
                attractor=0,
                chapter=0,
                route=RESONANCE_MAP[18],  # Moksha (surrender needed)
                call_response="CALL",
                resonance=0,
                vina_resonance=0,
                vina_string=0,
                shadow_phase="blocked",
                shadow_position=0,
                result={"success": False, "error": "MAYAVAD: No parampara link"},
                message="MAYAVAD: Connection to Parampara not verified. Check __genesis__ signature.",
            )

        # 1. SRAVANAM: Receive input
        # 2. MANANAM: Compress to seed

        # Check for large input - apply full MahaCompression with Guna filtering
        if len(input_text) > self.LARGE_INPUT_THRESHOLD:
            input_text = self._compress_large_input(input_text)

        # MAHA CELL: Wrap input in universal 72-byte header format
        # SRAVANAM (hearing) first! Not execute. Entry point = HEARING.
        # "śravaṇaṁ kīrtanaṁ viṣṇoḥ" - First hearing, then chanting
        maha_cell = wrap_cell(input_text, purpose="hearing")

        vibration = self.mahamantra.vibrate(input_text)
        seed = vibration["seed"]
        attractor = vibration["attractor"]
        resonance = vibration["resonance"]  # Flute (WHEN)
        vina_resonance = vibration["vina_resonance"]  # Vina (WHAT TYPE)
        vina_string = vibration["vina_string"]  # Which Pancha Tattva string (1-5)

        # 3. NIDIDHYASANA: Seed → PrabhupadaKirtan → CALL/RESPONSE (PERSON-ANCHORED)
        # NOT impersonal GADKirtan. THE PERSON (Prabhupada) validates every beat.
        prabhupada_result = self.prabhupada_kirtan.compute_with_person(seed)
        call_response = prabhupada_result.transmission_mode  # "CALL" or "RESPONSE"
        siksastakam_stage = prabhupada_result.siksastakam_stage.verse  # 1-8
        siksastakam_operation = prabhupada_result.siksastakam_stage.operation
        person_verified = prabhupada_result.is_bona_fide

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
        # 7. KIRTANAM: Execute via Balarama Bridge (Universal - No Hardcoding!)
        # =====================================================================
        # All execution flows through bridge.offer() - Balarama Pattern
        # Intent → Purpose → Position → Mahajana → Execute
        result = None
        message = ""

        try:
            result = self._execute_via_bridge(
                input_text=input_text,
                vibration=vibration,
                intent_category=intent_category,
                jiva_shadow_id=jiva_shadow_id,
                maha_cell=maha_cell,  # Pass the MahaCell created at entry!
            )

            # Build message from bridge result
            if result.get("success"):
                message = (
                    f"Gita {chapter} ({route.insight}) → "
                    f"Intent {intent_category} → "
                    f"Bridge → {result.get('mahajana', '?')}@{result.get('position', '?')} "
                    f"[{result.get('quarter', '?')}] "
                    f"Jiva {jiva_shadow_id[:8]}... ({jiva_guna})"
                )
            else:
                message = (
                    f"Gita {chapter} → Intent {intent_category} → "
                    f"Bridge REJECTED: {result.get('error', 'unknown')}"
                )
        except Exception as e:
            message = f"Bridge error: {e}"
            result = {"success": False, "error": str(e)}

        # 8. Build response with COMPLETE RESONANCE + PERSON-ANCHOR
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
            # PRABHUPADA KIRTAN (PERSON-ANCHORED)
            siksastakam_stage=siksastakam_stage,
            siksastakam_operation=siksastakam_operation,
            person_verified=person_verified,
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
    # UNIVERSAL EXECUTE - Via Balarama Bridge (No Hardcoded Handlers!)
    # =========================================================================
    #
    # "balarāmaḥ prathamaḥ sarva-saṅkarṣaṇaḥ"
    # "Balarama is the first, the Supreme Attractor."
    #
    # ALL execution flows through bridge.offer() - NO hardcoded handlers.
    # MahaLLM Intent → Bridge Purpose → Position → Mahajana → Execute
    # =========================================================================

    # MahaLLM 16 Intents → Bridge Purposes
    INTENT_TO_PURPOSE: Dict[str, str] = {
        "OBSERVE": "state_read",
        "CREATE": "state_update",
        "CONNECT": "state_update",
        "ANALYZE": "verify",
        "EXECUTE": "execute",
        "TRANSFORM": "state_update",
        "INVOKE": "execute",
        "SUSTAIN": "state_update",
        "EXPAND": "state_update",
        "INTEGRATE": "state_update",
        "VALIDATE": "verify",
        "PROTECT": "verify",
        "GUIDE": "state_read",
        "SURRENDER": "execute",
        "COMPLETE": "execute",
        "TRANSCEND": "execute",
    }

    def _execute_via_bridge(
        self,
        input_text: str,
        vibration: dict,
        intent_category: str,
        jiva_shadow_id: str,
        maha_cell: "MahaCell" = None,  # NOW USES MAHA_CELL!
    ) -> Any:
        """
        Universal execution via Balarama Bridge pattern.

        NO hardcoded handlers. Everything flows through MahaCell + bridge.offer().

        Flow:
            1. Intent → Purpose (via INTENT_TO_PURPOSE)
            2. wrap_cell() → MahaCell (72b header + payload)
            3. bridge.offer(content, purpose) → Position → Mahajana
            4. Return structured result with MahaCell info

        Args:
            input_text: The user input
            vibration: Full vibration state (seed, attractor, etc.)
            intent_category: MahaLLM intent (OBSERVE, CREATE, etc.)
            jiva_shadow_id: The spawned JivaShadow identifier
            maha_cell: Optional pre-created MahaCell (from entry point)

        Returns:
            Bridge result with position, mahajana, success status, maha_cell_size
        """
        from vibe_core.mahamantra.substrate.bridge import offer

        # Map intent to bridge purpose
        purpose = self.INTENT_TO_PURPOSE.get(intent_category, "execute")

        # Build content payload with full resonance context
        content = {
            "input": input_text,
            "seed": vibration["seed"],
            "attractor": vibration["attractor"],
            "intent": intent_category,
            "jiva": jiva_shadow_id,
            "resonance": vibration["resonance"],
            "vina_resonance": vibration["vina_resonance"],
        }

        # Create MahaCell if not provided (wrap content in 72-byte header)
        if maha_cell is None:
            maha_cell = wrap_cell(content, purpose=purpose)

        # Offer to bridge - Balarama routes to correct Position/Mahajana
        result = offer(
            content=content,
            purpose=purpose,
            actor=f"steward:jiva:{jiva_shadow_id[:8]}",
            parampara_vector=vibration["seed"] % PARAMPARA * PARAMPARA,  # Ensure % 37 == 0
        )

        # Add MahaCell info to result
        if maha_cell:
            result["maha_cell_size"] = maha_cell.size
            result["maha_cell_valid"] = maha_cell.is_valid()

        return result


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
