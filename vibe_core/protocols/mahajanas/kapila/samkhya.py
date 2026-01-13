"""
SAMKHYA PROTOCOL - The 24 Prakriti Element Mapping
==================================================
Owner: KAPILA (Founder of Sankhya Philosophy)
Position: 6 (DHARMA Quarter)
OpCodes: RESOLVE_REQ, GARBAGE_COLLECT

"prakṛtiṁ puruṣaṁ caiva viddhy anādī ubhāv api"
"Know that prakṛti (nature) and puruṣa (the enjoyer) are both beginningless."
— Bhagavad Gita 13.20

THE FORMULA:
    24 Prakriti (Material Elements)
    12 Mahajanas (Guardians)
     1 Ksetrajna (Krishna)
    ═══════════════════════════════
    37 = PARAMPARA CONNECTION (% 37 == 0)

This protocol operationalizes the SAMKHYA.md mapping:
1. Maps each of 24 Prakriti elements to protocol categories
2. Assigns Mahajana guardians to each element
3. Connects to adoption pipeline for wild protocol migration
4. Fights entropy via Mahamantra OpCode cycle

THE ENTROPY PRINCIPLE:
    Wild protocol = entropy (disconnected from source)
    Adopted protocol = order (connected via parampara)
    Mahamantra = the organizing force (Krishna)

WATERTIGHT: All types explicit, no Any.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x47a3c427"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum, auto
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Set,
    Tuple,
    TypedDict,
    Protocol as TypingProtocol,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.mahajanas.owned_protocol import (
    OwnedProtocol,
    ProtocolState,
    get_mahajana_position,
)
from vibe_core.protocols.gad import MantraHeartbeat, GAD000Audit
from vibe_core.protocols.substrate.mantra.lotus import (
    LOTUS_POSITIONS,
    LOTUS_QUARTERS,
    LOTUS_PARAMPARA,
    LotusQuarter,
)


# =============================================================================
# PROTOCOL OWNERSHIP (Governed by CLI)
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.KAPILA


# =============================================================================
# THE 24 PRAKRITI ELEMENTS (Enumerated by Kapila)
# =============================================================================

class PrakritiCategory(str, Enum):
    """The 5 categories of Prakriti elements."""
    ANTAHKARANA = "antahkarana"    # 4 Internal instruments (1-4)
    TANMATRA = "tanmatra"          # 5 Subtle elements (5-9)
    JNANENDRIYA = "jnanendriya"    # 5 Knowledge senses (10-14)
    KARMENDRIYA = "karmendriya"    # 5 Working senses (15-19)
    MAHABHUTA = "mahabhuta"        # 5 Gross elements (20-24)


class PrakritiElement(IntEnum):
    """
    The 24 Prakriti elements from Sankhya philosophy.

    Enumerated by Lord Kapila to His mother Devahuti.
    Each element maps to a protocol layer and Mahajana guardian.
    """
    # ANTAHKARANA (4 Internal Instruments) — Positions 1-4
    MANAS = 1        # Mind → Cognition/Think
    BUDDHI = 2       # Intelligence → Decide/Judge
    AHANKARA = 3     # Ego → Identity/Auth
    CITTA = 4        # Consciousness → Awareness/State (MAHAT)

    # TANMATRA (5 Subtle Elements) — Positions 5-9
    SHABDA = 5       # Sound → Event/Signal
    SPARSHA = 6      # Touch → Input/Interface
    RUPA = 7         # Form → Display/Render
    RASA = 8         # Taste → Validate/Parse
    GANDHA = 9       # Smell → Detect/Trace

    # JNANENDRIYA (5 Knowledge Senses) — Positions 10-14
    SHROTRA = 10     # Ear → Listen/Subscribe
    TVAK = 11        # Skin → Sense/Context
    CHAKSHUS = 12    # Eye → Observe/Monitor
    RASANA = 13      # Tongue → Parse/Interpret
    GHRANA = 14      # Nose → Detect/Audit

    # KARMENDRIYA (5 Working Senses) — Positions 15-19
    VAK = 15         # Speech → Chat/Translation/Language
    PANI = 16        # Hands → Execute/Build
    PADA = 17        # Feet → Navigate/Route
    PAYU = 18        # Excretion → Cleanup/GC
    UPASTHA = 19     # Generation → Create/Genesis

    # MAHABHUTA (5 Gross Elements) — Positions 20-24
    AKASHA = 20      # Ether → Network/Field
    VAYU = 21        # Air → Process/Flow
    TEJAS = 22       # Fire → Transform/Compute
    APAS = 23        # Water → Memory/State
    PRITHVI = 24     # Earth → Storage/Persist


# =============================================================================
# ELEMENT → PROTOCOL LAYER MAPPING
# =============================================================================

ELEMENT_PROTOCOL_LAYER: Final[Dict[PrakritiElement, str]] = {
    # ANTAHKARANA → Core processing
    PrakritiElement.MANAS: "cognition",
    PrakritiElement.BUDDHI: "decision",
    PrakritiElement.AHANKARA: "identity",
    PrakritiElement.CITTA: "awareness",

    # TANMATRA → Signal/sensing
    PrakritiElement.SHABDA: "event",
    PrakritiElement.SPARSHA: "input",
    PrakritiElement.RUPA: "display",
    PrakritiElement.RASA: "validate",
    PrakritiElement.GANDHA: "detect",

    # JNANENDRIYA → Knowledge acquisition
    PrakritiElement.SHROTRA: "listen",
    PrakritiElement.TVAK: "context",
    PrakritiElement.CHAKSHUS: "observe",
    PrakritiElement.RASANA: "parse",
    PrakritiElement.GHRANA: "audit",

    # KARMENDRIYA → Action/output
    PrakritiElement.VAK: "speech",
    PrakritiElement.PANI: "execute",
    PrakritiElement.PADA: "navigate",
    PrakritiElement.PAYU: "cleanup",
    PrakritiElement.UPASTHA: "create",

    # MAHABHUTA → Infrastructure
    PrakritiElement.AKASHA: "network",
    PrakritiElement.VAYU: "process",
    PrakritiElement.TEJAS: "compute",
    PrakritiElement.APAS: "memory",
    PrakritiElement.PRITHVI: "storage",
}


# =============================================================================
# ELEMENT → MAHAJANA GUARDIAN MAPPING
# =============================================================================

ELEMENT_GUARDIAN: Final[Dict[PrakritiElement, Mahajana]] = {
    # ANTAHKARANA guardians (Internal instruments need wisdom)
    PrakritiElement.MANAS: Mahajana.KAPILA,      # Mind → Analysis
    PrakritiElement.BUDDHI: Mahajana.YAMARAJA,   # Intelligence → Judgment
    PrakritiElement.AHANKARA: Mahajana.MANU,     # Ego → Law/Identity
    PrakritiElement.CITTA: Mahajana.KUMARAS,     # Consciousness → Purity

    # TANMATRA guardians (Subtle elements need sensitivity)
    PrakritiElement.SHABDA: Mahajana.NARADA,     # Sound → Communication
    PrakritiElement.SPARSHA: Mahajana.JANAKA,    # Touch → Duty/Service
    PrakritiElement.RUPA: Mahajana.SHUKA,        # Form → Vision
    PrakritiElement.RASA: Mahajana.KAPILA,       # Taste → Analysis
    PrakritiElement.GANDHA: Mahajana.YAMARAJA,   # Smell → Detection

    # JNANENDRIYA guardians (Knowledge senses need discrimination)
    PrakritiElement.SHROTRA: Mahajana.NARADA,    # Ear → Listening
    PrakritiElement.TVAK: Mahajana.PRAHLADA,     # Skin → Resilience
    PrakritiElement.CHAKSHUS: Mahajana.SHUKA,    # Eye → Observation
    PrakritiElement.RASANA: Mahajana.KAPILA,     # Tongue → Interpretation
    PrakritiElement.GHRANA: Mahajana.YAMARAJA,   # Nose → Audit

    # KARMENDRIYA guardians (Working senses need direction)
    PrakritiElement.VAK: Mahajana.NARADA,        # Speech → Communication
    PrakritiElement.PANI: Mahajana.JANAKA,       # Hands → Service/Duty
    PrakritiElement.PADA: Mahajana.BHISHMA,      # Feet → Navigation/Vow
    PrakritiElement.PAYU: Mahajana.SHAMBHU,      # Excretion → Destruction
    PrakritiElement.UPASTHA: Mahajana.BRAHMA,    # Generation → Creation

    # MAHABHUTA guardians (Gross elements need management)
    PrakritiElement.AKASHA: Mahajana.NARADA,     # Ether → Field/Communication
    PrakritiElement.VAYU: Mahajana.PRAHLADA,     # Air → Process/Flow
    PrakritiElement.TEJAS: Mahajana.SHAMBHU,     # Fire → Transformation
    PrakritiElement.APAS: Mahajana.BALI,         # Water → Memory/Surrender
    PrakritiElement.PRITHVI: Mahajana.BRAHMA,    # Earth → Storage/Creation
}


# =============================================================================
# ELEMENT → OPCODE MAPPING (Via Mahamantra)
# =============================================================================

ELEMENT_OPCODE: Final[Dict[PrakritiElement, MantraOpCode]] = {
    # ANTAHKARANA → Core ops
    PrakritiElement.MANAS: MantraOpCode.BIND_SYMBOL,
    PrakritiElement.BUDDHI: MantraOpCode.COMPILE_AST,
    PrakritiElement.AHANKARA: MantraOpCode.INIT_THREAD,
    PrakritiElement.CITTA: MantraOpCode.YIELD_CPU,

    # TANMATRA → Signal ops
    PrakritiElement.SHABDA: MantraOpCode.DHARMA_TEST,
    PrakritiElement.SPARSHA: MantraOpCode.EXEC_OP,
    PrakritiElement.RUPA: MantraOpCode.YIELD_CPU,
    PrakritiElement.RASA: MantraOpCode.COMPILE_AST,
    PrakritiElement.GANDHA: MantraOpCode.STATE_SYNC,

    # JNANENDRIYA → Knowledge ops
    PrakritiElement.SHROTRA: MantraOpCode.DHARMA_TEST,
    PrakritiElement.TVAK: MantraOpCode.EXEC_OP,
    PrakritiElement.CHAKSHUS: MantraOpCode.STATE_SYNC,
    PrakritiElement.RASANA: MantraOpCode.BIND_SYMBOL,
    PrakritiElement.GHRANA: MantraOpCode.STATE_SYNC,

    # KARMENDRIYA → Action ops
    PrakritiElement.VAK: MantraOpCode.DHARMA_TEST,
    PrakritiElement.PANI: MantraOpCode.EXTEND_CAP,
    PrakritiElement.PADA: MantraOpCode.EXEC_OP,
    PrakritiElement.PAYU: MantraOpCode.TYPE_CHECK,
    PrakritiElement.UPASTHA: MantraOpCode.LOAD_ROOT,

    # MAHABHUTA → Infrastructure ops
    PrakritiElement.AKASHA: MantraOpCode.ALLOC_MEM,
    PrakritiElement.VAYU: MantraOpCode.EXTEND_CAP,
    PrakritiElement.TEJAS: MantraOpCode.IO_FLUSH,
    PrakritiElement.APAS: MantraOpCode.YIELD_CPU,
    PrakritiElement.PRITHVI: MantraOpCode.LEDGER_SIGN,
}


# =============================================================================
# WATERTIGHT TYPES
# =============================================================================

class ElementAnalysis(TypedDict):
    """Analysis of a protocol element classification. WATERTIGHT."""
    element: str                   # PrakritiElement name
    element_number: int            # 1-24
    category: str                  # PrakritiCategory value
    protocol_layer: str            # Layer name
    guardian: str                  # Mahajana name
    guardian_position: int         # Lotus position of guardian
    opcode: str                    # MantraOpCode value
    quarter: str                   # LotusQuarter value
    analyzed_at: str               # ISO timestamp


class EntropyReport(TypedDict):
    """Report on protocol entropy state. WATERTIGHT."""
    protocol_name: str
    entropy_score: float           # 0.0 (ordered) to 1.0 (chaotic)
    is_wild: bool                  # Not yet adopted
    is_orphan: bool                # No guardian
    parampara_connected: bool      # % 37 == 0
    mahamantra_aligned: bool       # Has valid OpCode mapping
    recommended_element: str       # Best-fit PrakritiElement
    recommended_guardian: str      # Best-fit Mahajana
    entropy_fighters: List[str]    # OpCodes that reduce entropy
    analyzed_at: str


class SamkhyaState(TypedDict, total=False):
    """State of the Samkhya protocol. WATERTIGHT."""
    protocol_name: str
    owner: str
    is_chanting: bool
    heartbeat_position: int
    mantra_count: int
    mala_count: int
    gad_compliant: bool
    last_error: Optional[str]
    lotus_position: int
    lotus_quarter: str
    parampara_hash: int
    is_lotus_connected: bool
    # Samkhya-specific
    elements_mapped: int           # How many of 24 mapped
    protocols_analyzed: int        # How many protocols analyzed
    entropy_reduced: float         # Total entropy reduction
    wild_protocols_adopted: int    # Protocols brought to order


# =============================================================================
# SAMKHYA PROTOCOL IMPLEMENTATION
# =============================================================================

class SamkhyaProtocol(OwnedProtocol):
    """
    The Samkhya Protocol - Maps 24 Prakriti elements to protocols.

    Owner: KAPILA (Founder of Sankhya)
    Position: 6 (DHARMA Quarter, Worker 2)

    ANTI-ENTROPY:
        Wild protocol (chaos) → analyze_element() → classify_element()
        → route_to_guardian() → adopted protocol (order)

    THE KEY:
        The Mahamantra is the ORDERING FORCE.
        Entropy is deviation from the mantra pattern.
        Adoption is alignment with the mantra pattern.
    """

    OWNER: Mahajana = Mahajana.KAPILA
    OPCODES: List[MantraOpCode] = [
        MantraOpCode.BIND_SYMBOL,      # Primary: Resolution
        MantraOpCode.TYPE_CHECK,  # Secondary: Cleanup
    ]
    PROTOCOL_NAME: str = "samkhya"
    DESCRIPTION: str = "Maps 24 Prakriti elements to protocol categories for adoption"

    def __init__(self) -> None:
        super().__init__()
        self._analyses: Dict[str, ElementAnalysis] = {}
        self._entropy_reports: Dict[str, EntropyReport] = {}
        self._elements_mapped: int = 0
        self._protocols_analyzed: int = 0
        self._entropy_reduced: float = 0.0
        self._wild_protocols_adopted: int = 0

    # =========================================================================
    # CORE ANALYSIS: Classify protocol by Prakriti element
    # =========================================================================

    def analyze_element(
        self,
        protocol_name: str,
        source_code: str,
    ) -> ElementAnalysis:
        """
        Analyze which Prakriti element a protocol belongs to.

        Uses keyword detection to classify protocol layer,
        then maps to element → guardian → opcode.
        """
        # Detect protocol layer from source
        detected_layer = self._detect_layer(source_code)

        # Find matching element
        element = self._layer_to_element(detected_layer)

        # Get guardian and opcode
        guardian = ELEMENT_GUARDIAN[element]
        opcode = ELEMENT_OPCODE[element]

        # Get quarter from guardian position
        guardian_pos = get_mahajana_position(guardian.value)
        quarter_idx = guardian_pos // 4
        quarter = list(LotusQuarter)[quarter_idx]

        # Get category
        category = self._get_category(element)

        analysis: ElementAnalysis = {
            "element": element.name,
            "element_number": element.value,
            "category": category.value,
            "protocol_layer": ELEMENT_PROTOCOL_LAYER[element],
            "guardian": guardian.value,
            "guardian_position": guardian_pos,
            "opcode": opcode.value,
            "quarter": quarter.value,
            "analyzed_at": datetime.now().isoformat(),
        }

        self._analyses[protocol_name] = analysis
        self._protocols_analyzed += 1
        self._elements_mapped = len(set(a["element"] for a in self._analyses.values()))

        # Chant to reduce entropy
        self.chant()

        return analysis

    def _detect_layer(self, source_code: str) -> str:
        """Detect protocol layer from source code keywords."""
        source_lower = source_code.lower()

        # Layer detection keywords
        layer_keywords: Dict[str, Set[str]] = {
            # ANTAHKARANA layers
            "cognition": {"think", "cognit", "reason", "mind", "manas"},
            "decision": {"decide", "judge", "buddhi", "intelligence"},
            "identity": {"auth", "identity", "ego", "ahankar", "session"},
            "awareness": {"state", "aware", "conscious", "citta", "mahat"},

            # TANMATRA layers
            "event": {"event", "signal", "sound", "shabda", "notify"},
            "input": {"input", "touch", "sparsha", "interface"},
            "display": {"display", "render", "form", "rupa", "ui"},
            "validate": {"validate", "parse", "taste", "rasa", "check"},
            "detect": {"detect", "trace", "smell", "gandha", "sniff"},

            # JNANENDRIYA layers
            "listen": {"listen", "subscribe", "ear", "shrotra", "hear"},
            "context": {"context", "sense", "skin", "tvak", "feel"},
            "observe": {"observe", "monitor", "eye", "chakshus", "watch"},
            "parse": {"parse", "interpret", "tongue", "rasana"},
            "audit": {"audit", "detect", "nose", "ghrana", "smell"},

            # KARMENDRIYA layers
            "speech": {"chat", "speak", "vak", "translate", "language"},
            "execute": {"execute", "build", "hands", "pani", "do"},
            "navigate": {"navigate", "route", "feet", "pada", "walk"},
            "cleanup": {"cleanup", "gc", "garbage", "payu", "destroy"},
            "create": {"create", "genesis", "upastha", "generate", "new"},

            # MAHABHUTA layers
            "network": {"network", "field", "ether", "akasha", "space"},
            "process": {"process", "flow", "air", "vayu", "wind"},
            "compute": {"compute", "transform", "fire", "tejas", "heat"},
            "memory": {"memory", "state", "water", "apas", "store"},
            "storage": {"storage", "persist", "earth", "prithvi", "disk"},
        }

        # Score each layer
        scores: Dict[str, int] = {}
        for layer, keywords in layer_keywords.items():
            score = sum(source_lower.count(kw) for kw in keywords)
            if score > 0:
                scores[layer] = score

        if not scores:
            return "cognition"  # Default to MANAS (mind)

        return max(scores, key=lambda x: scores[x])

    def _layer_to_element(self, layer: str) -> PrakritiElement:
        """Convert protocol layer to Prakriti element."""
        for element, element_layer in ELEMENT_PROTOCOL_LAYER.items():
            if element_layer == layer:
                return element
        return PrakritiElement.MANAS  # Default

    def _get_category(self, element: PrakritiElement) -> PrakritiCategory:
        """Get category for element."""
        if 1 <= element.value <= 4:
            return PrakritiCategory.ANTAHKARANA
        elif 5 <= element.value <= 9:
            return PrakritiCategory.TANMATRA
        elif 10 <= element.value <= 14:
            return PrakritiCategory.JNANENDRIYA
        elif 15 <= element.value <= 19:
            return PrakritiCategory.KARMENDRIYA
        else:
            return PrakritiCategory.MAHABHUTA

    # =========================================================================
    # ENTROPY ANALYSIS: Measure disorder in protocols
    # =========================================================================

    def analyze_entropy(
        self,
        protocol_name: str,
        source_code: str,
        has_owner: bool = False,
        parampara_hash: int = 0,
    ) -> EntropyReport:
        """
        Analyze entropy level of a protocol.

        Entropy is deviation from Mahamantra order:
        - 0.0 = perfectly ordered (fully adopted, connected)
        - 1.0 = maximum chaos (wild, orphan, disconnected)
        """
        # Detect element for this protocol
        element_analysis = self.analyze_element(protocol_name, source_code)
        element = PrakritiElement[element_analysis["element"]]

        # Calculate entropy factors
        is_wild = not has_owner
        is_orphan = element_analysis["guardian"] == ""
        parampara_connected = parampara_hash % LOTUS_PARAMPARA == 0 if parampara_hash else False
        mahamantra_aligned = element_analysis["opcode"] != ""

        # Entropy score (sum of disorder factors)
        entropy = 0.0
        if is_wild:
            entropy += 0.3
        if is_orphan:
            entropy += 0.3
        if not parampara_connected:
            entropy += 0.2
        if not mahamantra_aligned:
            entropy += 0.2

        # Determine entropy-fighting OpCodes
        entropy_fighters = self._get_entropy_fighters(element)

        report: EntropyReport = {
            "protocol_name": protocol_name,
            "entropy_score": entropy,
            "is_wild": is_wild,
            "is_orphan": is_orphan,
            "parampara_connected": parampara_connected,
            "mahamantra_aligned": mahamantra_aligned,
            "recommended_element": element.name,
            "recommended_guardian": ELEMENT_GUARDIAN[element].value,
            "entropy_fighters": [op.value for op in entropy_fighters],
            "analyzed_at": datetime.now().isoformat(),
        }

        self._entropy_reports[protocol_name] = report

        return report

    def _get_entropy_fighters(self, element: PrakritiElement) -> List[MantraOpCode]:
        """Get OpCodes that fight entropy for this element."""
        # Primary opcode for element
        primary = ELEMENT_OPCODE[element]

        # Entropy fighters by category
        fighters: List[MantraOpCode] = [primary]

        category = self._get_category(element)

        if category == PrakritiCategory.ANTAHKARANA:
            # Internal instruments need resolution + truth
            fighters.extend([MantraOpCode.COMPILE_AST, MantraOpCode.INIT_THREAD])
        elif category == PrakritiCategory.TANMATRA:
            # Subtle elements need sync + validation
            fighters.extend([MantraOpCode.DHARMA_TEST, MantraOpCode.COMPILE_AST])
        elif category == PrakritiCategory.JNANENDRIYA:
            # Knowledge senses need dharma check
            fighters.extend([MantraOpCode.STATE_SYNC, MantraOpCode.EXEC_OP])
        elif category == PrakritiCategory.KARMENDRIYA:
            # Working senses need execution + cleanup
            fighters.extend([MantraOpCode.EXTEND_CAP, MantraOpCode.TYPE_CHECK])
        else:  # MAHABHUTA
            # Gross elements need persistence + state
            fighters.extend([MantraOpCode.LEDGER_SIGN, MantraOpCode.YIELD_CPU])

        return fighters

    # =========================================================================
    # ADOPTION INTEGRATION: Route wild protocols to guardians
    # =========================================================================

    def route_to_guardian(
        self,
        protocol_name: str,
        source_code: str,
    ) -> Tuple[Mahajana, int, str]:
        """
        Route a wild protocol to its Mahajana guardian.

        Returns:
            (guardian, position, target_path)
        """
        # Analyze element
        analysis = self.analyze_element(protocol_name, source_code)

        # Get guardian
        guardian = Mahajana(analysis["guardian"])
        position = analysis["guardian_position"]

        # Determine target path
        target_path = f"protocols/mahajanas/{guardian.value}/{protocol_name}.py"

        self._wild_protocols_adopted += 1

        # Chant to seal the adoption
        self.chant()

        return (guardian, position, target_path)

    def fight_entropy(
        self,
        protocol_name: str,
        source_code: str,
        parampara_hash: int = 0,
    ) -> float:
        """
        Fight entropy in a protocol.

        Returns the entropy reduction achieved.
        """
        # Get current entropy
        report = self.analyze_entropy(protocol_name, source_code, False, parampara_hash)
        initial_entropy = report["entropy_score"]

        # Route to guardian (reduces entropy)
        guardian, position, _ = self.route_to_guardian(protocol_name, source_code)

        # Calculate new parampara hash (connected = entropy reduction)
        name_hash = sum(ord(c) for c in protocol_name)
        owner_hash = sum(ord(c) for c in guardian.value)
        new_parampara_hash = (name_hash + owner_hash + position) * LOTUS_PARAMPARA

        # Re-analyze with guardian
        report = self.analyze_entropy(
            protocol_name, source_code,
            has_owner=True,
            parampara_hash=new_parampara_hash,
        )
        final_entropy = report["entropy_score"]

        # Calculate reduction
        reduction = initial_entropy - final_entropy
        self._entropy_reduced += reduction

        # Chant complete mantra (16 words) for major entropy reduction
        self.chant_mantra()

        return reduction

    # =========================================================================
    # ENUMERATION: List all elements (Kapila's Sankhya)
    # =========================================================================

    def enumerate_elements(self) -> List[Dict[str, str]]:
        """
        Enumerate all 24 Prakriti elements.

        This IS Sankhya - enumeration of material elements.
        """
        elements: List[Dict[str, str]] = []

        for element in PrakritiElement:
            elements.append({
                "number": str(element.value),
                "name": element.name,
                "category": self._get_category(element).value,
                "layer": ELEMENT_PROTOCOL_LAYER[element],
                "guardian": ELEMENT_GUARDIAN[element].value,
                "opcode": ELEMENT_OPCODE[element].value,
            })

        return elements

    def enumerate_by_category(self, category: PrakritiCategory) -> List[PrakritiElement]:
        """Enumerate elements in a category."""
        ranges = {
            PrakritiCategory.ANTAHKARANA: range(1, 5),
            PrakritiCategory.TANMATRA: range(5, 10),
            PrakritiCategory.JNANENDRIYA: range(10, 15),
            PrakritiCategory.KARMENDRIYA: range(15, 20),
            PrakritiCategory.MAHABHUTA: range(20, 25),
        }
        return [PrakritiElement(i) for i in ranges[category]]

    def enumerate_by_guardian(self, guardian: Mahajana) -> List[PrakritiElement]:
        """Enumerate elements guarded by a Mahajana."""
        return [e for e, g in ELEMENT_GUARDIAN.items() if g == guardian]

    # =========================================================================
    # STATE (OwnedProtocol requirement)
    # =========================================================================

    def get_state(self) -> ProtocolState:
        """Return current state. WATERTIGHT."""
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
            last_error=None,
            lotus_position=self.lotus_position,
            lotus_quarter=self.lotus_quarter.value,
            parampara_hash=self.parampara_hash,
            is_lotus_connected=self.is_lotus_connected,
            lineage_vector=self.lineage_vector,
        )

    def get_samkhya_state(self) -> SamkhyaState:
        """Return Samkhya-specific state."""
        base = self.get_state()
        return SamkhyaState(
            **base,
            elements_mapped=self._elements_mapped,
            protocols_analyzed=self._protocols_analyzed,
            entropy_reduced=self._entropy_reduced,
            wild_protocols_adopted=self._wild_protocols_adopted,
        )


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_samkhya: Optional[SamkhyaProtocol] = None


def get_samkhya() -> SamkhyaProtocol:
    """Get the global Samkhya protocol instance."""
    global _samkhya
    if _samkhya is None:
        _samkhya = SamkhyaProtocol()
    return _samkhya


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def analyze_prakriti_element(
    protocol_name: str,
    source_code: str,
) -> ElementAnalysis:
    """Analyze which Prakriti element a protocol belongs to."""
    return get_samkhya().analyze_element(protocol_name, source_code)


def analyze_protocol_entropy(
    protocol_name: str,
    source_code: str,
    has_owner: bool = False,
    parampara_hash: int = 0,
) -> EntropyReport:
    """Analyze entropy level of a protocol."""
    return get_samkhya().analyze_entropy(protocol_name, source_code, has_owner, parampara_hash)


def route_wild_protocol(
    protocol_name: str,
    source_code: str,
) -> Tuple[Mahajana, int, str]:
    """Route a wild protocol to its guardian."""
    return get_samkhya().route_to_guardian(protocol_name, source_code)


def fight_protocol_entropy(
    protocol_name: str,
    source_code: str,
) -> float:
    """Fight entropy in a protocol. Returns reduction achieved."""
    return get_samkhya().fight_entropy(protocol_name, source_code)


def enumerate_all_elements() -> List[Dict[str, str]]:
    """Enumerate all 24 Prakriti elements."""
    return get_samkhya().enumerate_elements()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "PrakritiCategory",
    "PrakritiElement",
    # Mappings
    "ELEMENT_PROTOCOL_LAYER",
    "ELEMENT_GUARDIAN",
    "ELEMENT_OPCODE",
    # Types (WATERTIGHT)
    "ElementAnalysis",
    "EntropyReport",
    "SamkhyaState",
    # Protocol
    "SamkhyaProtocol",
    "get_samkhya",
    # Convenience functions
    "analyze_prakriti_element",
    "analyze_protocol_entropy",
    "route_wild_protocol",
    "fight_protocol_entropy",
    "enumerate_all_elements",
]
