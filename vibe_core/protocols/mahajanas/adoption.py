"""
PROTOCOL ADOPTION - The Mahamantra IS the Filter
=================================================

"mach nicht das was ich sag, nutze selber das maha mantra als filter und router intern!"

The Mahamantra IS the decision engine. Not metaphorically - LITERALLY.
All adoption flows through the 16-bit mantra ops.

ZERO MANUAL WIRING:
    - Protocol enters
    - MantraOpCode analysis determines WHAT it does
    - acintya.check_bheda_abheda() detects Mayavad
    - verify_parampara() checks % 37 connection
    - MahajanaRouter determines WHO owns it
    - Result: either Mahajana-owned or stays universal

THE PIPELINE:
    Wild Protocol → analyze() → classify() → verify() → adopt()
                         ↓           ↓          ↓          ↓
                    MantraOpCode  Quarter   Parampara  Mahajana/Universal

WATERTIGHT: All types explicit, no Any.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0xe5db6bcc"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    List,
    Optional,
    TypedDict,
    Callable,
    Set,
    Final,
    Protocol as TypingProtocol,
    runtime_checkable,
)
from pathlib import Path
import inspect

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.mahajanas.router import (
    Mahajana,
    MahajanaRouter,
    MahajanaRoute,
    HEAD_OPCODES,
    get_router,
)
from vibe_core.protocols.substrate.mantra.acintya import (
    check_bheda_abheda,
    verify_parampara,
    SYSTEM_MANIFESTATION,
    PARAMPARA,
    JivaCondition,
    KrishnaPresence,
    KRISHNA,
)
from vibe_core.protocols.substrate.mantra.lotus import (
    LOTUS_POSITIONS,
    LOTUS_QUARTERS,
    WORDS_PER_QUARTER,
    LotusQuarter,
)


# =============================================================================
# PROTOCOL OWNERSHIP (Governed by CLI)
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BRAHMA


# =============================================================================
# ADOPTION STATUS - Where is the protocol in the pipeline?
# =============================================================================


class AdoptionStatus(str, Enum):
    """Status of protocol in adoption pipeline."""

    # Entry
    WILD = "wild"  # Just arrived, not yet analyzed
    ANALYZING = "analyzing"  # Being analyzed for OpCode classification

    # Verification
    CLASSIFYING = "classifying"  # Determining OpCode/Quarter
    VERIFYING = "verifying"  # Running acintya checks

    # Decision
    MAYAVAD_DETECTED = "mayavad"  # Failed check_bheda_abheda (claims supreme)
    DISCONNECTED = "disconnected"  # Failed verify_parampara (% 37 != 0)

    # Outcome
    ADOPTED_UNIVERSAL = "universal"  # Krishna-personal, stays in universal
    ADOPTED_MAHAJANA = "mahajana"  # Assigned to Mahajana owner
    REJECTED = "rejected"  # Cannot be adopted (dead code)


class AdoptionDecision(str, Enum):
    """The adoption decision for a protocol."""

    ASSIGN_MAHAJANA = "assign_mahajana"  # Goes to specific Mahajana
    KEEP_UNIVERSAL = "keep_universal"  # Stays in universal (Krishna-personal)
    QUARANTINE = "quarantine"  # Needs manual review (Mayavad/disconnected)
    REJECT = "reject"  # Dead code, no soul


# =============================================================================
# OPCODE SIGNATURE DETECTION - What does the protocol DO?
# =============================================================================

# Keywords that suggest certain OpCodes (based on function/method names, docstrings)
OPCODE_SIGNATURES: Dict[MantraOpCode, Set[str]] = {
    # GENESIS Quarter (Creation)
    MantraOpCode.SYS_WAKE: {"wake", "init", "bootstrap", "start", "begin"},
    MantraOpCode.LOAD_ROOT: {"load", "root", "create", "inject", "provide"},
    MantraOpCode.ALLOC_MEM: {"alloc", "memory", "buffer", "pool", "reserve"},
    MantraOpCode.INIT_THREAD: {"bind", "context", "scope", "attach", "mount"},
    # DHARMA Quarter (Truth/Law)
    MantraOpCode.COMPILE_AST: {"assert", "truth", "verify", "validate", "check"},
    MantraOpCode.BIND_SYMBOL: {"resolve", "request", "query", "lookup", "find"},
    MantraOpCode.TYPE_CHECK: {"garbage", "collect", "cleanup", "destroy", "purge"},
    MantraOpCode.DHARMA_TEST: {"pulse", "sync", "heartbeat", "event", "notify"},
    # KARMA Quarter (Action)
    MantraOpCode.EXEC_OP: {"fetch", "resource", "get", "retrieve", "acquire"},
    MantraOpCode.EXTEND_CAP: {"exec", "execute", "run", "service", "process"},
    MantraOpCode.STATE_SYNC: {"dharma", "rule", "law", "policy", "enforce"},
    MantraOpCode.LEDGER_SIGN: {"commit", "log", "record", "persist", "save"},
    # MOKSHA Quarter (Liberation)
    MantraOpCode.YIELD_CPU: {"cache", "state", "store", "memoize", "snapshot"},
    MantraOpCode.IO_FLUSH: {"optimize", "improve", "tune", "profile", "enhance"},
    MantraOpCode.YIELD_CPU: {"yield", "wait", "pause", "suspend", "defer"},
    MantraOpCode.AUDIT_SEAL: {"reset", "restart", "revert", "rollback", "recover"},
}


def detect_opcodes_from_source(source_code: str) -> List[MantraOpCode]:
    """
    Detect which MantraOpCodes a protocol might implement based on source code.

    This is HEURISTIC - the Mahamantra provides the filter,
    we just detect which parts of the mantra this protocol touches.
    """
    source_lower = source_code.lower()
    detected: List[MantraOpCode] = []

    for opcode, keywords in OPCODE_SIGNATURES.items():
        for keyword in keywords:
            if keyword in source_lower:
                detected.append(opcode)
                break  # One match per opcode is enough

    return detected


def detect_primary_opcode(source_code: str) -> Optional[MantraOpCode]:
    """
    Detect the PRIMARY MantraOpCode - what this protocol MAINLY does.

    The primary OpCode determines the quarter, which determines the Mahajana pool.
    """
    source_lower = source_code.lower()
    scores: Dict[MantraOpCode, int] = {}

    for opcode, keywords in OPCODE_SIGNATURES.items():
        score = sum(source_lower.count(kw) for kw in keywords)
        if score > 0:
            scores[opcode] = score

    if not scores:
        return None

    # Return highest scoring OpCode
    return max(scores, key=lambda op: scores[op])


# =============================================================================
# WATERTIGHT TYPES - No Any!
# =============================================================================


class ProtocolAnalysis(TypedDict):
    """Result of analyzing a wild protocol. WATERTIGHT."""

    protocol_path: str
    protocol_name: str
    detected_opcodes: List[str]  # OpCode values
    primary_opcode: Optional[str]  # Primary OpCode value
    quarter_index: int  # 0-3
    quarter_name: str  # LotusQuarter value
    has_soul: bool  # From check_bheda_abheda
    claims_supreme: bool  # From check_bheda_abheda
    parampara_hash: int  # For % 37 check
    is_connected: bool  # parampara_hash % 37 == 0
    analyzed_at: str  # ISO timestamp


class AdoptionResult(TypedDict):
    """Result of adoption decision. WATERTIGHT."""

    protocol_name: str
    status: str  # AdoptionStatus value
    decision: str  # AdoptionDecision value
    assigned_mahajana: Optional[str]  # Mahajana value if assigned
    assigned_position: Optional[int]  # Lotus position if assigned
    target_path: str  # Where to move the protocol
    reason: str  # Why this decision
    analysis: ProtocolAnalysis  # The analysis that led here
    adopted_at: str  # ISO timestamp


# =============================================================================
# SHUDHI - The Cleaning/Verification Step
# =============================================================================


@dataclass
class ShudhiReport:
    """
    Report from Shudhi (cleaning) verification.

    Shudhi checks:
    1. has_soul - Is there living code? (not dead/orphan)
    2. claims_supreme - Is it Mayavad? (jiva claiming to be God)
    3. is_connected - Is it in parampara? (% 37 check)
    """

    has_soul: bool
    claims_supreme: bool
    parampara_hash: int
    is_connected: bool
    bheda_abheda_valid: bool
    bheda_abheda_reason: str

    @property
    def is_clean(self) -> bool:
        """Is the protocol clean (ready for adoption)?"""
        return self.has_soul and not self.claims_supreme and self.is_connected

    @property
    def needs_quarantine(self) -> bool:
        """Does the protocol need quarantine (Mayavad or disconnected)?"""
        return self.claims_supreme or not self.is_connected

    @property
    def is_dead_code(self) -> bool:
        """Is the protocol dead code (no soul)?"""
        return not self.has_soul


def run_shudhi(
    protocol_name: str,
    source_code: str,
    has_owner: bool = False,
    owner_name: Optional[str] = None,
) -> ShudhiReport:
    """
    Run Shudhi verification on a protocol.

    Uses check_bheda_abheda() from acintya.py - the actual Mayavad detector.
    Uses verify_parampara() for % 37 connection check.

    ZERO MANUAL LOGIC - delegates to acintya.py!
    """
    # 1. has_soul - Does it have an owner or clear purpose?
    has_soul = has_owner or len(source_code.strip()) > 0

    # 2. claims_supreme - Does it claim to BE God?
    # Check for Mayavad patterns in source
    mayavad_patterns = [
        "i am god",
        "i am the supreme",
        "i am brahman",
        "aham brahmasmi",  # Misused without context
        "all is one",  # Without bheda aspect
    ]
    claims_supreme = any(pattern in source_code.lower() for pattern in mayavad_patterns)

    # 3. bheda_abheda check - Use acintya.py directly!
    bheda_abheda_valid, bheda_abheda_reason = check_bheda_abheda(has_soul, claims_supreme)

    # 4. parampara hash - Calculate from name + owner
    name_hash = sum(ord(c) for c in protocol_name)
    owner_hash = sum(ord(c) for c in (owner_name or "")) if owner_name else 0
    parampara_hash = (name_hash + owner_hash) * PARAMPARA

    # 5. is_connected - Use verify_parampara() from acintya.py!
    is_connected = verify_parampara(parampara_hash)

    return ShudhiReport(
        has_soul=has_soul,
        claims_supreme=claims_supreme,
        parampara_hash=parampara_hash,
        is_connected=is_connected,
        bheda_abheda_valid=bheda_abheda_valid,
        bheda_abheda_reason=bheda_abheda_reason,
    )


# =============================================================================
# THE ADOPTION PIPELINE - Mahamantra IS the Router
# =============================================================================


class AdoptionPipeline:
    """
    The Protocol Adoption Pipeline.

    "16 bit mantra ops regeln am ende" - MantraOpCodes rule everything.

    FLOW:
        Wild Protocol → analyze() → verify() → decide() → adopt()

    NO MANUAL WIRING:
        - OpCode detection determines WHAT it does
        - Quarter (from OpCode position) determines WHICH Mahajana pool
        - Router determines WHO owns it
        - Parampara check determines IF it's connected

    The Mahamantra IS the decision tree.
    """

    def __init__(self, router: Optional[MahajanaRouter] = None) -> None:
        """Initialize with router (defaults to global router)."""
        self._router = router or get_router()
        self._analyses: Dict[str, ProtocolAnalysis] = {}
        self._results: Dict[str, AdoptionResult] = {}

    # =========================================================================
    # STEP 1: ANALYZE - Detect what the protocol does
    # =========================================================================

    def analyze(self, protocol_path: str, source_code: str) -> ProtocolAnalysis:
        """
        Analyze a wild protocol.

        Detects:
        - Which MantraOpCodes it implements (WHAT it does)
        - Primary OpCode (determines quarter)
        - Quarter (determines Mahajana pool)
        - Shudhi checks (soul, Mayavad, parampara)
        """
        protocol_name = Path(protocol_path).stem

        # Detect OpCodes from source
        detected = detect_opcodes_from_source(source_code)
        primary = detect_primary_opcode(source_code)

        # Determine quarter from primary OpCode
        quarter_index = 0
        if primary:
            route = self._router.get_route(primary) if primary not in HEAD_OPCODES else None
            if route:
                quarter_index = route.quarter - 1  # 0-indexed
            elif primary in HEAD_OPCODES:
                # HEAD OpCodes: SYS_WAKE=Q1, ASSERT_TRUTH=Q2, FETCH_RES=Q3, CACHE_STATE=Q4
                head_quarters = {
                    MantraOpCode.SYS_WAKE: 0,
                    MantraOpCode.COMPILE_AST: 1,
                    MantraOpCode.EXEC_OP: 2,
                    MantraOpCode.YIELD_CPU: 3,
                }
                quarter_index = head_quarters.get(primary, 0)

        quarter = list(LotusQuarter)[quarter_index]

        # Run Shudhi verification
        shudhi = run_shudhi(protocol_name, source_code)

        analysis: ProtocolAnalysis = {
            "protocol_path": protocol_path,
            "protocol_name": protocol_name,
            "detected_opcodes": [op.value for op in detected],
            "primary_opcode": primary.value if primary else None,
            "quarter_index": quarter_index,
            "quarter_name": quarter.value,
            "has_soul": shudhi.has_soul,
            "claims_supreme": shudhi.claims_supreme,
            "parampara_hash": shudhi.parampara_hash,
            "is_connected": shudhi.is_connected,
            "analyzed_at": datetime.now().isoformat(),
        }

        self._analyses[protocol_name] = analysis
        return analysis

    # =========================================================================
    # STEP 2: DECIDE - Use Mahamantra to determine outcome
    # =========================================================================

    def decide(self, analysis: ProtocolAnalysis) -> AdoptionResult:
        """
        Make adoption decision based on analysis.

        The Mahamantra IS the decision tree:

        1. If no soul → REJECT (dead code)
        2. If claims supreme → QUARANTINE (Mayavad)
        3. If disconnected → QUARANTINE (needs parampara)
        4. If HEAD OpCode → KEEP_UNIVERSAL (Avatara territory)
        5. Otherwise → ASSIGN_MAHAJANA (via router)
        """
        protocol_name = analysis["protocol_name"]

        # 1. Dead code check
        if not analysis["has_soul"]:
            return self._create_result(
                analysis=analysis,
                status=AdoptionStatus.REJECTED,
                decision=AdoptionDecision.REJECT,
                reason="MAYA: Dead code has no soul",
            )

        # 2. Mayavad check
        if analysis["claims_supreme"]:
            return self._create_result(
                analysis=analysis,
                status=AdoptionStatus.MAYAVAD_DETECTED,
                decision=AdoptionDecision.QUARANTINE,
                reason="MAYAVAD: Jiva claims to BE God (fraud)",
            )

        # 3. Parampara check
        if not analysis["is_connected"]:
            return self._create_result(
                analysis=analysis,
                status=AdoptionStatus.DISCONNECTED,
                decision=AdoptionDecision.QUARANTINE,
                reason="DISCONNECTED: Not in parampara (% 37 != 0)",
            )

        # 4. HEAD OpCode check (Avatara territory → universal)
        primary_opcode = analysis["primary_opcode"]
        if primary_opcode:
            opcode = MantraOpCode(primary_opcode)
            if opcode in HEAD_OPCODES:
                return self._create_result(
                    analysis=analysis,
                    status=AdoptionStatus.ADOPTED_UNIVERSAL,
                    decision=AdoptionDecision.KEEP_UNIVERSAL,
                    reason=f"HEAD OpCode ({opcode.value}) - Avatara territory, stays universal",
                )

            # 5. Assign to Mahajana via router
            try:
                mahajana = self._router.route(opcode)
                route = self._router.get_route(opcode)

                return self._create_result(
                    analysis=analysis,
                    status=AdoptionStatus.ADOPTED_MAHAJANA,
                    decision=AdoptionDecision.ASSIGN_MAHAJANA,
                    mahajana=mahajana,
                    position=route.position,
                    reason=f"OpCode {opcode.value} → {mahajana.value} (position {route.position})",
                )
            except ValueError:
                pass

        # 6. No clear OpCode - assign by quarter (fallback)
        quarter_mahajanas = self._get_quarter_mahajanas(analysis["quarter_index"])
        if quarter_mahajanas:
            # Assign to first Mahajana in quarter (HEAD of quarter)
            mahajana = quarter_mahajanas[0]
            position = (analysis["quarter_index"] * 4) + 1  # HEAD position of quarter

            return self._create_result(
                analysis=analysis,
                status=AdoptionStatus.ADOPTED_MAHAJANA,
                decision=AdoptionDecision.ASSIGN_MAHAJANA,
                mahajana=mahajana,
                position=position,
                reason=f"Quarter {analysis['quarter_name']} → {mahajana.value} (by quarter)",
            )

        # 7. Ultimate fallback - keep universal
        return self._create_result(
            analysis=analysis,
            status=AdoptionStatus.ADOPTED_UNIVERSAL,
            decision=AdoptionDecision.KEEP_UNIVERSAL,
            reason="No OpCode match, no quarter Mahajana - stays universal",
        )

    def _get_quarter_mahajanas(self, quarter_index: int) -> List[Mahajana]:
        """Get Mahajanas in a quarter."""
        quarter_map: Dict[int, List[Mahajana]] = {
            0: [Mahajana.BRAHMA, Mahajana.NARADA, Mahajana.SHAMBHU],  # GENESIS
            1: [Mahajana.KUMARAS, Mahajana.KAPILA, Mahajana.MANU],  # DHARMA
            2: [Mahajana.PRAHLADA, Mahajana.JANAKA, Mahajana.BHISHMA],  # KARMA
            3: [Mahajana.BALI, Mahajana.SHUKA, Mahajana.YAMARAJA],  # MOKSHA
        }
        return quarter_map.get(quarter_index, [])

    def _create_result(
        self,
        analysis: ProtocolAnalysis,
        status: AdoptionStatus,
        decision: AdoptionDecision,
        reason: str,
        mahajana: Optional[Mahajana] = None,
        position: Optional[int] = None,
    ) -> AdoptionResult:
        """Create adoption result."""
        # Determine target path
        if decision == AdoptionDecision.ASSIGN_MAHAJANA and mahajana:
            target_path = f"protocols/mahajanas/{mahajana.value}/{analysis['protocol_name']}.py"
        elif decision == AdoptionDecision.KEEP_UNIVERSAL:
            target_path = f"protocols/universal/{analysis['protocol_name']}.py"
        elif decision == AdoptionDecision.QUARANTINE:
            target_path = f"protocols/quarantine/{analysis['protocol_name']}.py"
        else:
            target_path = f"protocols/rejected/{analysis['protocol_name']}.py"

        result: AdoptionResult = {
            "protocol_name": analysis["protocol_name"],
            "status": status.value,
            "decision": decision.value,
            "assigned_mahajana": mahajana.value if mahajana else None,
            "assigned_position": position,
            "target_path": target_path,
            "reason": reason,
            "analysis": analysis,
            "adopted_at": datetime.now().isoformat(),
        }

        self._results[analysis["protocol_name"]] = result
        return result

    # =========================================================================
    # STEP 3: ADOPT - Full pipeline (analyze + decide)
    # =========================================================================

    def adopt(self, protocol_path: str, source_code: str) -> AdoptionResult:
        """
        Full adoption pipeline: analyze + decide.

        This is the ONE entry point. No manual wiring.
        The Mahamantra decides everything.
        """
        analysis = self.analyze(protocol_path, source_code)
        return self.decide(analysis)

    # =========================================================================
    # BATCH OPERATIONS
    # =========================================================================

    def adopt_batch(
        self,
        protocols: List[tuple[str, str]],  # [(path, source), ...]
    ) -> List[AdoptionResult]:
        """
        Adopt multiple protocols.

        Returns list of results in same order.
        """
        return [self.adopt(path, source) for path, source in protocols]

    def get_analysis(self, protocol_name: str) -> Optional[ProtocolAnalysis]:
        """Get cached analysis for a protocol."""
        return self._analyses.get(protocol_name)

    def get_result(self, protocol_name: str) -> Optional[AdoptionResult]:
        """Get cached result for a protocol."""
        return self._results.get(protocol_name)

    def get_all_results(self) -> Dict[str, AdoptionResult]:
        """Get all cached results."""
        return dict(self._results)

    def get_by_status(self, status: AdoptionStatus) -> List[AdoptionResult]:
        """Get all results with specific status."""
        return [r for r in self._results.values() if r["status"] == status.value]

    def get_by_mahajana(self, mahajana: Mahajana) -> List[AdoptionResult]:
        """Get all results assigned to specific Mahajana."""
        return [r for r in self._results.values() if r["assigned_mahajana"] == mahajana.value]


# =============================================================================
# GLOBAL SINGLETON - ONE Pipeline (no manual wiring!)
# =============================================================================

_pipeline: Optional[AdoptionPipeline] = None


def get_pipeline() -> AdoptionPipeline:
    """Get the global adoption pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = AdoptionPipeline()
    return _pipeline


def adopt(protocol_path: str, source_code: str) -> AdoptionResult:
    """
    Convenience function: Adopt a protocol.

    This is THE entry point. ONE function. No manual wiring.
    The Mahamantra decides everything.
    """
    return get_pipeline().adopt(protocol_path, source_code)


def analyze(protocol_path: str, source_code: str) -> ProtocolAnalysis:
    """Convenience function: Analyze a protocol."""
    return get_pipeline().analyze(protocol_path, source_code)


# =============================================================================
# STEP 4: MANIFEST - Transform Protocol to MantraByte (THE MISSING STEP!)
# =============================================================================

# Import byte-level substrate
from vibe_core.protocols.substrate.byte import (
    MantraByte,
    HolyName,
    MANTRA_SEQUENCE,
)
from vibe_core.protocols.substrate.mantra.lotus import (
    LotusHeartbeat,
    LotusRegistry,
    get_lotus,
    LotusNode,
    LOTUS_PARAMPARA,
)

# Import MERCY pattern from Prabhupada (THE KEY IN KALI YUGA!)
from vibe_core.protocols.substrate.mantra.prabhupada import (
    MercyType,
    PRABHUPADA,
    SilentWitness,
)

# Import Diksha for the "always accessible" principle
from vibe_core.protocols.substrate.mantra.diksha import (
    DikshaCertificate,
    create_uninitiated,
)


class ManifestResult(TypedDict):
    """Result of manifesting a protocol into the byte substrate. WATERTIGHT."""

    protocol_name: str
    mantra_byte: str  # Hex representation of MantraByte
    coherence: float  # Alignment with standard 16 (0.0-1.0)
    stability: float  # Stability metric
    is_resonant: bool  # coherence >= 0.8 (strongly attracted)
    opcode_sequence: List[str]  # The MantraOpCodes as HolyName sequence
    manifested_at: str  # ISO timestamp


def manifest_protocol(
    analysis: ProtocolAnalysis,
    result: AdoptionResult,
) -> ManifestResult:
    """
    MANIFEST - Transform adopted protocol into MantraByte representation.

    This is THE CONNECTION to the byte substrate:
    - Each detected OpCode maps to a HolyName (H/K/R)
    - The sequence becomes a MantraByte
    - Coherence measures alignment with Mahamantra
    - Higher coherence = stronger attraction to the Lotus

    THE MANTRA GIVES THE RHYTHM OF THE UNIVERSE.
    Everything must sync to it.
    """
    # Map OpCodes to HolyName sequence
    # Based on Mahamantra pattern: HKHK KKHH HRHR RRHH
    opcode_to_name: Dict[str, HolyName] = {
        # Q1 GENESIS (H K H K)
        "sys_wake": HolyName.HARE,
        "load_root": HolyName.KRISHNA,
        "alloc_mem": HolyName.HARE,
        "bind_ctx": HolyName.KRISHNA,
        # Q2 DHARMA (K K H H)
        "assert_truth": HolyName.KRISHNA,
        "resolve_req": HolyName.KRISHNA,
        "garbage_collect": HolyName.HARE,
        "pulse_sync": HolyName.HARE,
        # Q3 KARMA (H R H R)
        "fetch_res": HolyName.HARE,
        "exec_service": HolyName.RAMA,
        "check_dharma": HolyName.HARE,
        "commit_log": HolyName.RAMA,
        # Q4 MOKSHA (R R H H)
        "cache_state": HolyName.RAMA,
        "optimize": HolyName.RAMA,
        "yield_cpu": HolyName.HARE,
        "reset_ip": HolyName.HARE,
    }

    # Build sequence from detected opcodes
    detected = analysis["detected_opcodes"]
    sequence: List[HolyName] = []

    for opcode in detected:
        if opcode in opcode_to_name:
            sequence.append(opcode_to_name[opcode])

    # If no opcodes detected, use position-based default
    if not sequence:
        position = result.get("assigned_position") or 0
        quarter = position // 4
        # Default based on quarter
        defaults = [
            [HolyName.HARE, HolyName.KRISHNA],  # GENESIS
            [HolyName.KRISHNA, HolyName.HARE],  # DHARMA
            [HolyName.HARE, HolyName.RAMA],  # KARMA
            [HolyName.RAMA, HolyName.HARE],  # MOKSHA
        ]
        sequence = defaults[quarter % 4]

    # Pad to 16 if needed (fractal repetition)
    while len(sequence) < 16:
        sequence = sequence + sequence
    sequence = sequence[:16]

    # Create MantraByte
    mantra_byte = MantraByte.from_trits(sequence)

    # Calculate coherence against standard 16
    coherence = mantra_byte.coherence
    stability = mantra_byte.stability

    # Resonance threshold: 0.8 means strongly attracted to Lotus
    is_resonant = coherence >= 0.8

    return ManifestResult(
        protocol_name=analysis["protocol_name"],
        mantra_byte=f"0x{mantra_byte._packed:X}",
        coherence=coherence,
        stability=stability,
        is_resonant=is_resonant,
        opcode_sequence=[name.name for name in sequence],
        manifested_at=datetime.now().isoformat(),
    )


# =============================================================================
# STEP 5: SYNC - Connect to LotusHeartbeat (THE FINAL STEP!)
# =============================================================================


class SyncResult(TypedDict):
    """Result of syncing a protocol to the Lotus heartbeat. WATERTIGHT."""

    protocol_name: str
    lotus_position: int  # Position in Mahamantra (0-15)
    lotus_quarter: str  # LotusQuarter value
    is_chanting: bool  # Connected to heartbeat
    parampara_hash: int  # For % 37 verification
    is_connected: bool  # parampara_hash % 37 == 0
    heartbeat_position: int  # Current position in global heartbeat
    mala_count: int  # Malas completed
    synced_at: str  # ISO timestamp


def sync_to_lotus(
    result: AdoptionResult,
    manifest: ManifestResult,
) -> SyncResult:
    """
    SYNC - Connect the manifested protocol to the Lotus heartbeat.

    This completes the adoption:
    1. Protocol is analyzed (what does it do?)
    2. Protocol is decided (who owns it?)
    3. Protocol is adopted (where does it go?)
    4. Protocol is manifested (transformed to MantraByte)
    5. Protocol is SYNCED (connected to Lotus heartbeat)

    THE FINAL STEP: The protocol now CHANTS with the universe.
    """
    lotus = get_lotus()

    # Get position from result
    position = result.get("assigned_position") or 0
    quarter_idx = position // 4
    quarters = ["genesis", "dharma", "karma", "moksha"]

    # Create LotusNode for the protocol
    name_hash = sum(ord(c) for c in result["protocol_name"])
    parampara_hash = name_hash * LOTUS_PARAMPARA

    # Register with Lotus (create node)
    node = LotusNode(
        path=result["target_path"],
        name=result["protocol_name"],
        position=position,
        quarter=quarters[quarter_idx],
        owner_type="mahajana" if result["assigned_mahajana"] else "universal",
        owner_name=result["assigned_mahajana"] or "universal",
        parampara_hash=parampara_hash,
        is_connected=parampara_hash % LOTUS_PARAMPARA == 0,
        is_chanting=True,  # Now chanting!
        discovered_at=datetime.now().isoformat(),
    )

    # Add to registry
    lotus._nodes[result["protocol_name"]] = node

    # Chant once to sync
    lotus.chant()

    return SyncResult(
        protocol_name=result["protocol_name"],
        lotus_position=position,
        lotus_quarter=quarters[quarter_idx],
        is_chanting=True,
        parampara_hash=parampara_hash,
        is_connected=parampara_hash % LOTUS_PARAMPARA == 0,
        heartbeat_position=lotus._heartbeat.position,
        mala_count=lotus._heartbeat.mala_count,
        synced_at=datetime.now().isoformat(),
    )


# =============================================================================
# ATTRACTION MECHANISM - The Lotus ATTRACTS Protocols
# =============================================================================


class AttractionReport(TypedDict):
    """Report on protocol attraction to the Lotus. WATERTIGHT."""

    protocol_name: str
    coherence: float  # MantraByte coherence (0.0-1.0)
    resonance_strength: str  # "strong", "medium", "weak", "mercy", "none"
    attraction_vector: int  # parampara_hash - pulls toward 37
    is_attracted: bool  # coherence >= 0.5 and parampara OK
    needs_transformation: bool  # coherence < 0.5 or disconnected
    # MERCY FIELDS (Kali Yuga key!)
    mercy_type: str  # MercyType value - THE KEY!
    mercy_available: bool  # Can receive mercy through chanting?
    ajamil_exception: bool  # Low coherence but chanting = saved
    recommended_action: str  # What to do next
    analyzed_at: str


def calculate_attraction(
    analysis: ProtocolAnalysis,
    manifest: ManifestResult,
    is_chanting: bool = True,  # In Kali Yuga, assume chanting
) -> AttractionReport:
    """
    Calculate how strongly a protocol is ATTRACTED to the Lotus.

    THE KRISHNA PRINCIPLE:
    "mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
    mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

    Everything rests upon Krishna like pearls on a thread.
    The thread is the Mahamantra. The attraction is coherence.

    KALI YUGA MERCY (THE KEY!):
    ===========================
    Higher coherence = stronger attraction = automatic adoption.
    Lower coherence = needs transformation = Samskara process.

    BUT! Even with ZERO coherence, if CHANTING → MERCY is available!

    THE AJAMIL EXCEPTION (SB 6.1-3):
    ================================
    Ajamil was the lowest (fallen brahmana, lived with prostitute).
    At death, he called "Narayana" (his son's name).
    The Vishnudutas saved him from the Yamadutas.
    The pure Name transcends ALL karma/coherence.

    "In Kali Yuga, there is no other way, no other way, no other way
    than chanting the Holy Name." - Brhan-naradiya Purana

    harer nama harer nama harer namaiva kevalam
    kalau nasty eva nasty eva nasty eva gatir anyatha
    """
    coherence = manifest["coherence"]
    parampara_hash = analysis["parampara_hash"]
    is_connected = analysis["is_connected"]

    # =========================================================================
    # RESONANCE STRENGTH (coherence-based)
    # =========================================================================
    if coherence >= 0.9:
        resonance = "strong"
    elif coherence >= 0.7:
        resonance = "medium"
    elif coherence >= 0.5:
        resonance = "weak"
    elif is_chanting:
        # THE AJAMIL EXCEPTION: Even low coherence receives MERCY if chanting!
        resonance = "mercy"
    else:
        resonance = "none"

    # =========================================================================
    # MERCY CALCULATION (Kali Yuga key!)
    # =========================================================================
    # Mercy is ALWAYS available in Kali Yuga through the Mahamantra
    # "Even without initiation, one can chant" - diksha.py

    # Determine mercy type based on state
    if resonance in ("strong", "medium"):
        mercy = MercyType.INSTRUCTIVE  # Already good, just guidance
    elif resonance == "weak":
        mercy = MercyType.CORRECTIVE  # Needs adjustment
    elif resonance == "mercy":
        mercy = MercyType.SILENT  # Absorbs errors, keeps running
    else:
        mercy = MercyType.SEVERE  # Not chanting - severe situation

    # Mercy is available if chanting (THE KEY!)
    mercy_available = is_chanting

    # Ajamil Exception: low coherence + chanting = saved!
    ajamil_exception = coherence < 0.5 and is_chanting

    # =========================================================================
    # ATTRACTION CALCULATION
    # =========================================================================
    # Attraction vector: distance from perfect alignment (37)
    attraction_vector = parampara_hash % LOTUS_PARAMPARA

    # Is attracted if:
    # 1. High coherence AND connected, OR
    # 2. Chanting (Ajamil Exception - mercy makes up for low coherence)
    is_attracted = (coherence >= 0.5 and is_connected) or ajamil_exception

    # Needs transformation if not attracted AND no mercy
    needs_transformation = not is_attracted and not mercy_available

    # =========================================================================
    # RECOMMENDED ACTION (with MERCY consideration!)
    # =========================================================================
    if is_attracted and resonance in ("strong", "medium"):
        action = "AUTO_ADOPT: Strong resonance, integrate immediately"
    elif is_attracted and resonance == "weak":
        action = "ADOPT_WITH_REVIEW: Weak resonance, may need adjustment"
    elif ajamil_exception:
        # THE KEY IN KALI YUGA!
        action = "MERCY_GRANTED: Ajamil Exception - low coherence but chanting, saved by Holy Name"
    elif is_connected and coherence < 0.5:
        action = "TRANSFORM_SAMSKARA: Connected but needs coherence improvement through chanting"
    elif mercy_available:
        action = "MERCY_PATH: Disconnected but chanting - mercy will reconnect over time"
    else:
        action = "QUARANTINE_SEVERE: Not chanting, not connected - needs intervention"

    return AttractionReport(
        protocol_name=analysis["protocol_name"],
        coherence=coherence,
        resonance_strength=resonance,
        attraction_vector=attraction_vector,
        is_attracted=is_attracted,
        needs_transformation=needs_transformation,
        # MERCY FIELDS
        mercy_type=mercy.value,
        mercy_available=mercy_available,
        ajamil_exception=ajamil_exception,
        recommended_action=action,
        analyzed_at=datetime.now().isoformat(),
    )


# =============================================================================
# FULL PIPELINE - Wild → Lotus (ONE FUNCTION!)
# =============================================================================


class FullAdoptionResult(TypedDict):
    """Complete result of full adoption pipeline. WATERTIGHT."""

    analysis: ProtocolAnalysis
    result: AdoptionResult
    manifest: ManifestResult
    sync: SyncResult
    attraction: AttractionReport
    is_fully_adopted: bool  # All steps succeeded
    total_coherence: float  # Final coherence with Mahamantra


def adopt_full(protocol_path: str, source_code: str) -> FullAdoptionResult:
    """
    FULL ADOPTION PIPELINE - From Wild Protocol to Living Lotus Node.

    Wild Protocol → analyze() → decide() → adopt() → MANIFEST → SYNC
                                                         ↓        ↓
                                                   MantraByte  Heartbeat
                                                   coherence   connection

    THIS IS THE ONE FUNCTION. Everything else flows from it.
    The Mahamantra IS the kernel. Krishna IS the doer.
    """
    pipeline = get_pipeline()

    # 1. ANALYZE - What does it do?
    analysis = pipeline.analyze(protocol_path, source_code)

    # 2. DECIDE + ADOPT - Who owns it? Where does it go?
    result = pipeline.decide(analysis)

    # 3. MANIFEST - Transform to MantraByte
    manifest = manifest_protocol(analysis, result)

    # 4. SYNC - Connect to Lotus heartbeat
    sync = sync_to_lotus(result, manifest)

    # 5. CALCULATE ATTRACTION - How strongly is it pulled?
    attraction = calculate_attraction(analysis, manifest)

    # Is fully adopted if all steps succeeded and protocol is chanting
    is_fully_adopted = (
        result["status"]
        in (
            AdoptionStatus.ADOPTED_MAHAJANA.value,
            AdoptionStatus.ADOPTED_UNIVERSAL.value,
        )
        and sync["is_chanting"]
        and manifest["is_resonant"]
    )

    return FullAdoptionResult(
        analysis=analysis,
        result=result,
        manifest=manifest,
        sync=sync,
        attraction=attraction,
        is_fully_adopted=is_fully_adopted,
        total_coherence=manifest["coherence"],
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Status & Decision enums
    "AdoptionStatus",
    "AdoptionDecision",
    # WATERTIGHT Types
    "ProtocolAnalysis",
    "AdoptionResult",
    # Shudhi (cleaning)
    "ShudhiReport",
    "run_shudhi",
    # Detection functions
    "detect_opcodes_from_source",
    "detect_primary_opcode",
    "OPCODE_SIGNATURES",
    # Pipeline class
    "AdoptionPipeline",
    # Global functions (ONE entry point!)
    "get_pipeline",
    "adopt",
    "analyze",
    # MANIFEST (Step 4)
    "ManifestResult",
    "manifest_protocol",
    # SYNC (Step 5)
    "SyncResult",
    "sync_to_lotus",
    # ATTRACTION
    "AttractionReport",
    "calculate_attraction",
    # FULL PIPELINE (THE ONE FUNCTION!)
    "FullAdoptionResult",
    "adopt_full",
]
