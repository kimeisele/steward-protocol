"""
LOTUS CLI - The ONE Entry Point
================================

"Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama Hare Rama Rama Rama Hare Hare"

THE LOTUS PATTERN (3×4 = ALIVE):
================================
ONE entry point that unfolds 1→N like a lotus flower.

- 3 = ESSENCE (Hare, Krishna, Rama) - The Holy Names
- 4 = STRUCTURE (Wake, Purify, Serve, Sustain) - The Phases
- 3×4 = Essence FIRST, then Structure = CONNECTED/ALIVE
- 4×3 = Structure FIRST = DEAD/MAYAVAD (we reject this)

USAGE:
    steward chat "query"           # Natural language, routes via resonance
    steward chat --explain "query" # Show how resonance computed

HOW IT WORKS:
    1. Query text resonates with the Mahamantra
    2. Resonance vector (H, K, R) computed
    3. Dominant Name determines BRANCH:
       - HARE   = Energy/Shakti operations
       - KRISHNA = Source/Core governance
       - RAMA   = Strength/Service actions
    4. Query intent determines PHASE:
       - WAKE    = Discovery, Status, Init
       - PURIFY  = Analysis, Validation, Audit
       - SERVE   = Execution, Fetch, Process
       - SUSTAIN = Maintenance, Cache, Optimize

ANTI-MAYAVAD:
    This is NOT 16 separate commands (4×3 = dead).
    This is ONE entry point that BRANCHES (3×4 = alive).
    The tree is rooted in Krishna (chat), not fragmented.

Owner: NARADA (Communication) + SHUKA (Vision)
OpCode: Mahamantra-routed
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Final, List, Optional, Tuple

from vibe_core.protocols.cli import CLIMeta, CLIResult, register_cli
from vibe_core.protocols.substrate.resonance import (
    ResonanceEngine,
    ResonanceVector,
    compute_resonance_vector,
    get_resonance_engine,
)


# =============================================================================
# THE THREE BRANCHES (ESSENCE)
# =============================================================================


class LotusBranch(str, Enum):
    """
    The 3 Holy Names as CLI branches.

    HARE   = Energy (Shakti/Radha) - Operations, monitoring, energy
    KRISHNA = Source (All-Attractive) - Core governance, protocols
    RAMA   = Strength (Balarama) - Service, execution, actions
    VOID   = No resonance - help/default
    """

    HARE = "hare"
    KRISHNA = "krishna"
    RAMA = "rama"
    VOID = "void"


# =============================================================================
# THE FOUR PHASES (STRUCTURE)
# =============================================================================


class LotusPhase(str, Enum):
    """
    The 4 phases within each branch.

    WAKE    = Discovery, Status, Init (OpCodes 1-4)
    PURIFY  = Analysis, Validation, Audit (OpCodes 5-8)
    SERVE   = Execution, Fetch, Process (OpCodes 9-12)
    SUSTAIN = Maintenance, Cache, Optimize (OpCodes 13-16)
    """

    WAKE = "wake"  # Q1: SYS_WAKE, LOAD_ROOT, ALLOC_MEM, BIND_CTX
    PURIFY = "purify"  # Q2: ASSERT_TRUTH, RESOLVE_REQ, GARBAGE_COLLECT, PULSE_SYNC
    SERVE = "serve"  # Q3: FETCH_RES, EXEC_SERVICE, CHECK_DHARMA, COMMIT_LOG
    SUSTAIN = "sustain"  # Q4: CACHE_STATE, OPTIMIZE, YIELD_CPU, RESET_IP


# =============================================================================
# PHASE DETECTION (Intent Keywords)
# =============================================================================

# Keywords that indicate WAKE phase (discovery, status)
WAKE_KEYWORDS: Final[Tuple[str, ...]] = (
    "status",
    "show",
    "list",
    "what",
    "where",
    "who",
    "find",
    "discover",
    "scan",
    "init",
    "start",
    "wake",
    "owners",
    "terrain",
)

# Keywords that indicate PURIFY phase (analysis, validation)
PURIFY_KEYWORDS: Final[Tuple[str, ...]] = (
    "audit",
    "check",
    "validate",
    "analyze",
    "verify",
    "test",
    "inspect",
    "health",
    "gaps",
    "anomaly",
    "purify",
    "clean",
    "fix",
)

# Keywords that indicate SERVE phase (execution, action)
SERVE_KEYWORDS: Final[Tuple[str, ...]] = (
    "fetch",
    "get",
    "execute",
    "run",
    "process",
    "serve",
    "do",
    "create",
    "build",
    "generate",
    "intel",
    "query",
)

# Keywords that indicate SUSTAIN phase (maintenance)
SUSTAIN_KEYWORDS: Final[Tuple[str, ...]] = (
    "cache",
    "optimize",
    "maintain",
    "sustain",
    "persist",
    "save",
    "store",
    "backup",
    "schedule",
    "repeat",
    "cycle",
)


def detect_phase(query: str) -> LotusPhase:
    """
    Detect phase from query intent.

    Uses keyword matching to determine which phase the query belongs to.
    Default is WAKE (discovery) if unclear.
    """
    q = query.lower()

    # Score each phase
    scores: Dict[LotusPhase, int] = {
        LotusPhase.WAKE: 0,
        LotusPhase.PURIFY: 0,
        LotusPhase.SERVE: 0,
        LotusPhase.SUSTAIN: 0,
    }

    for kw in WAKE_KEYWORDS:
        if kw in q:
            scores[LotusPhase.WAKE] += 1

    for kw in PURIFY_KEYWORDS:
        if kw in q:
            scores[LotusPhase.PURIFY] += 1

    for kw in SERVE_KEYWORDS:
        if kw in q:
            scores[LotusPhase.SERVE] += 1

    for kw in SUSTAIN_KEYWORDS:
        if kw in q:
            scores[LotusPhase.SUSTAIN] += 1

    # Return highest scoring phase (WAKE is default)
    max_score = max(scores.values())
    if max_score == 0:
        return LotusPhase.WAKE

    for phase, score in scores.items():
        if score == max_score:
            return phase

    return LotusPhase.WAKE


# =============================================================================
# LOTUS ROUTE (Branch + Phase)
# =============================================================================


@dataclass(frozen=True)
class LotusRoute:
    """
    The computed route: Branch + Phase.

    This is the result of resonance routing.
    Branch comes from dominant Holy Name.
    Phase comes from query intent.
    """

    branch: LotusBranch
    phase: LotusPhase
    resonance: ResonanceVector
    query: str
    opcode_position: int  # 0-15 Mahamantra position

    @property
    def quarter(self) -> int:
        """Which quarter (0-3) based on position."""
        return self.opcode_position // 4

    @property
    def description(self) -> str:
        """Human-readable route description."""
        return f"{self.branch.value.upper()}/{self.phase.value.upper()}"

    def explain(self) -> str:
        """Full explanation of how this route was computed."""
        lines = [
            f"LOTUS ROUTE: {self.description}",
            f"",
            f"Query: \"{self.query}\"",
            f"",
            f"RESONANCE VECTOR:",
            f"  HARE:    {self.resonance['hare']:.3f}",
            f"  KRISHNA: {self.resonance['krishna']:.3f}",
            f"  RAMA:    {self.resonance['rama']:.3f}",
            f"  Dominant: {self.resonance['dominant'].upper()}",
            f"  Magnitude: {self.resonance['magnitude']:.3f}",
            f"",
            f"ROUTE:",
            f"  Branch: {self.branch.value.upper()} ({self._branch_meaning()})",
            f"  Phase: {self.phase.value.upper()} ({self._phase_meaning()})",
            f"  Position: {self.opcode_position} (Quarter {self.quarter + 1})",
        ]
        return "\n".join(lines)

    def _branch_meaning(self) -> str:
        meanings = {
            LotusBranch.HARE: "Energy/Shakti - operations, monitoring",
            LotusBranch.KRISHNA: "Source/Core - governance, protocols",
            LotusBranch.RAMA: "Strength/Service - execution, actions",
            LotusBranch.VOID: "No resonance - help mode",
        }
        return meanings.get(self.branch, "unknown")

    def _phase_meaning(self) -> str:
        meanings = {
            LotusPhase.WAKE: "Discovery, status, initialization",
            LotusPhase.PURIFY: "Analysis, validation, audit",
            LotusPhase.SERVE: "Execution, fetch, process",
            LotusPhase.SUSTAIN: "Maintenance, cache, optimize",
        }
        return meanings.get(self.phase, "unknown")


def compute_route(query: str) -> LotusRoute:
    """
    Compute the lotus route for a query.

    1. Compute resonance vector (H, K, R)
    2. Determine branch from dominant name
    3. Determine phase from query intent
    4. Return complete route
    """
    # Get resonance
    engine = get_resonance_engine()
    resonance = engine.resonate(query)
    position = engine.resolve(query)

    # Map dominant to branch
    dominant = resonance["dominant"]
    if dominant == "hare":
        branch = LotusBranch.HARE
    elif dominant == "krishna":
        branch = LotusBranch.KRISHNA
    elif dominant == "rama":
        branch = LotusBranch.RAMA
    else:
        branch = LotusBranch.VOID

    # Detect phase from intent
    phase = detect_phase(query)

    return LotusRoute(
        branch=branch,
        phase=phase,
        resonance=resonance,
        query=query,
        opcode_position=position,
    )


# =============================================================================
# LOTUS HANDLER REGISTRY
# =============================================================================


@dataclass
class LotusHandler:
    """
    Handler for a specific branch/phase combination.

    The 3×4 = 12 core handlers (not 16 separate commands).
    Each handler can further delegate based on query.
    """

    branch: LotusBranch
    phase: LotusPhase
    description: str
    # Handler function will be set by the CLI
    # Using field with default factory for callable
    handler_name: str = ""

    @property
    def key(self) -> str:
        """Unique key for this handler."""
        return f"{self.branch.value}:{self.phase.value}"


class LotusHandlerRegistry:
    """
    Registry of handlers for branch/phase combinations.

    Unlike fragmented 16-command approach, this is 3×4 = 12
    handlers rooted in ONE entry point.
    """

    _handlers: Dict[str, LotusHandler] = {}

    @classmethod
    def register(cls, branch: LotusBranch, phase: LotusPhase, description: str, handler_name: str) -> None:
        """Register a handler for branch/phase."""
        key = f"{branch.value}:{phase.value}"
        cls._handlers[key] = LotusHandler(
            branch=branch,
            phase=phase,
            description=description,
            handler_name=handler_name,
        )

    @classmethod
    def get(cls, branch: LotusBranch, phase: LotusPhase) -> Optional[LotusHandler]:
        """Get handler for branch/phase."""
        key = f"{branch.value}:{phase.value}"
        return cls._handlers.get(key)

    @classmethod
    def all(cls) -> List[LotusHandler]:
        """Get all registered handlers."""
        return list(cls._handlers.values())


# =============================================================================
# LOTUS CLI - THE ONE ENTRY POINT
# =============================================================================


@register_cli
class LotusCLI:
    """
    THE LOTUS CLI - One Entry Point, Many Branches.

    Like the lotus flower that opens from a single stem,
    this CLI takes ONE entry point (chat) and unfolds
    to N branches based on Mahamantra resonance.

    3×4 PATTERN (ALIVE):
        3 = Branches (HARE, KRISHNA, RAMA)
        4 = Phases (WAKE, PURIFY, SERVE, SUSTAIN)
        Entry = ONE (chat)
        Unfolds = N (based on query)

    USAGE:
        steward chat "show governance status"   → KRISHNA/WAKE
        steward chat "audit protocols"          → KRISHNA/PURIFY
        steward chat "fetch intel"              → HARE/SERVE
        steward chat --explain "query"          → Show routing
    """

    def __init__(self) -> None:
        self._engine = get_resonance_engine()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register the 3×4 = 12 core handlers."""
        # HARE Branch (Energy/Operations)
        LotusHandlerRegistry.register(LotusBranch.HARE, LotusPhase.WAKE, "Status, monitoring, init", "_hare_wake")
        LotusHandlerRegistry.register(LotusBranch.HARE, LotusPhase.PURIFY, "Health check, validation", "_hare_purify")
        LotusHandlerRegistry.register(LotusBranch.HARE, LotusPhase.SERVE, "Intel, fetch ops data", "_hare_serve")
        LotusHandlerRegistry.register(LotusBranch.HARE, LotusPhase.SUSTAIN, "Cache, optimize ops", "_hare_sustain")

        # KRISHNA Branch (Source/Governance)
        LotusHandlerRegistry.register(LotusBranch.KRISHNA, LotusPhase.WAKE, "List, discover protocols", "_krishna_wake")
        LotusHandlerRegistry.register(LotusBranch.KRISHNA, LotusPhase.PURIFY, "Audit, validate governance", "_krishna_purify")
        LotusHandlerRegistry.register(LotusBranch.KRISHNA, LotusPhase.SERVE, "Fetch, inspect protocols", "_krishna_serve")
        LotusHandlerRegistry.register(LotusBranch.KRISHNA, LotusPhase.SUSTAIN, "Persist, schedule governance", "_krishna_sustain")

        # RAMA Branch (Strength/Service)
        LotusHandlerRegistry.register(LotusBranch.RAMA, LotusPhase.WAKE, "Scan, find services", "_rama_wake")
        LotusHandlerRegistry.register(LotusBranch.RAMA, LotusPhase.PURIFY, "Test, verify services", "_rama_purify")
        LotusHandlerRegistry.register(LotusBranch.RAMA, LotusPhase.SERVE, "Execute, run services", "_rama_serve")
        LotusHandlerRegistry.register(LotusBranch.RAMA, LotusPhase.SUSTAIN, "Maintain, optimize services", "_rama_sustain")

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata."""
        return CLIMeta(
            command="chat",
            description="Lotus CLI - ONE entry point, resonance-routed",
            domain="lotus",
            subcommands=["--explain", "--help"],
            tags=["lotus", "mahamantra", "resonance", "3x4", "chat"],
        )

    def run(self, args: List[str]) -> int:
        """
        Main entry point - THE ONE STEM.

        All queries flow through here and branch via resonance.
        """
        if not args:
            self._print_help()
            return 0

        # Parse flags
        explain = "--explain" in args
        if explain:
            args = [a for a in args if a != "--explain"]

        if not args or args[0] in ("--help", "-h", "help"):
            self._print_help()
            return 0

        # Combine remaining args as query
        query = " ".join(args)

        # Compute route
        route = compute_route(query)

        # If explain mode, show routing
        if explain:
            print(route.explain())
            return 0

        # Execute the routed handler
        return self._execute(route)

    def _print_help(self) -> None:
        """Print lotus help."""
        print("""
LOTUS CLI - The ONE Entry Point
================================

USAGE:
    steward chat "your query here"
    steward chat --explain "query"     Show how resonance routes

THE 3×4 PATTERN (ALIVE):
    3 Branches (from dominant Holy Name):
        HARE    = Energy/Operations
        KRISHNA = Source/Governance
        RAMA    = Strength/Service

    4 Phases (from query intent):
        WAKE    = Discovery, status
        PURIFY  = Analysis, audit
        SERVE   = Execution, fetch
        SUSTAIN = Maintenance

EXAMPLES:
    steward chat "show governance status"     → KRISHNA/WAKE
    steward chat "audit protocols"            → KRISHNA/PURIFY
    steward chat "fetch intel from naga"      → HARE/SERVE
    steward chat "scan services"              → RAMA/WAKE

The query resonates with the Mahamantra to determine routing.
""")

    def _execute(self, route: LotusRoute) -> int:
        """Execute the routed handler."""
        # Get handler
        handler = LotusHandlerRegistry.get(route.branch, route.phase)

        if handler is None:
            print(f"No handler for {route.description}")
            return 1

        # Get the actual method
        method_name = handler.handler_name
        method = getattr(self, method_name, None)

        if method is None:
            print(f"Handler {method_name} not implemented")
            return 1

        # Execute
        print(f"[{route.description}] Routing: {route.query}")
        print()
        return method(route)

    # =========================================================================
    # HARE BRANCH HANDLERS (Energy/Operations)
    # =========================================================================

    def _hare_wake(self, route: LotusRoute) -> int:
        """HARE/WAKE: Status, monitoring, initialization."""
        print("HARE/WAKE: Energy Status")
        print("-" * 40)

        # Get NAGA intel status via injected _get_intel
        intel = self._get_intel()
        active = intel.get_active_nagas()

        print(f"  Active NAGAs: {len(active)}")
        if active:
            for naga in active:
                print(f"    - {naga}")
        else:
            print("    (No active NAGAs)")

        # Show resonance
        print(f"\n  Query Resonance: {route.resonance['magnitude']:.3f}")
        return 0

    def _hare_purify(self, route: LotusRoute) -> int:
        """HARE/PURIFY: Health check, validation."""
        print("HARE/PURIFY: Health Validation")
        print("-" * 40)

        intel = self._get_intel()
        critical = intel.get_critical()
        threats = intel.get_threats()

        if critical:
            print(f"\n  🚨 CRITICAL ({len(critical)}):")
            for item in critical:
                print(f"    - {item.summary}")

        if threats:
            print(f"\n  ⚠️ THREATS ({len(threats)}):")
            for item in threats:
                print(f"    - {item.summary}")

        if not critical and not threats:
            print("  ✅ All systems healthy")

        return 0

    def _hare_serve(self, route: LotusRoute) -> int:
        """HARE/SERVE: Fetch intel, operations data."""
        print("HARE/SERVE: Intel Fetch")
        print("-" * 40)

        intel = self._get_intel()
        recent = intel.get_recent(limit=5)

        if recent:
            print(f"\n  Recent Intel ({len(recent)}):")
            for item in recent:
                print(f"    {item.to_chat_message()}")
        else:
            print("  No recent intel")

        return 0

    def _hare_sustain(self, route: LotusRoute) -> int:
        """HARE/SUSTAIN: Cache, optimize operations."""
        print("HARE/SUSTAIN: Operations Optimization")
        print("-" * 40)
        print("  (Sustain operations - future implementation)")
        return 0

    # =========================================================================
    # KRISHNA BRANCH HANDLERS (Source/Governance)
    # =========================================================================

    def _krishna_wake(self, route: LotusRoute) -> int:
        """KRISHNA/WAKE: List, discover protocols."""
        print("KRISHNA/WAKE: Protocol Discovery")
        print("-" * 40)

        # Delegate to governance bridge
        from vibe_core.protocols.governance.bridge import audit

        report = audit()
        print(f"  Total Protocols: {report['total_protocols']}")
        print(f"  Governed: {report['governed_count']}")
        print(f"  Ungoverned: {report['ungoverned_count']}")
        print(f"  Health: {report['health_score'] * 100:.0f}%")

        return 0

    def _krishna_purify(self, route: LotusRoute) -> int:
        """KRISHNA/PURIFY: Audit, validate governance."""
        print("KRISHNA/PURIFY: Governance Audit")
        print("-" * 40)

        from vibe_core.protocols.governance.bridge import audit

        report = audit()

        # Owner distribution
        dist = report["owner_distribution"]
        print("\n  12 Mahajana Distribution:")
        for m, count in sorted(dist.items(), key=lambda x: -x[1])[:6]:
            bar = "#" * min(count, 20)
            print(f"    {m:12} {bar} {count}")

        if report["ungoverned_count"] > 0:
            print(f"\n  ⚠️ {report['ungoverned_count']} ungoverned protocols")

        return 0

    def _krishna_serve(self, route: LotusRoute) -> int:
        """KRISHNA/SERVE: Fetch, inspect protocols."""
        print("KRISHNA/SERVE: Protocol Fetch")
        print("-" * 40)

        from vibe_core.protocols.governance.bridge import ProtocolBridge

        # Try to extract a path from query
        query = route.query.lower()
        parts = route.query.split()

        # Look for something that might be a path
        path = None
        for part in parts:
            if ".py" in part or "/" in part:
                path = part
                break

        if path:
            entry = ProtocolBridge.get_entry(path)
            if entry:
                print(f"  Protocol: {entry['name']}")
                print(f"  Owner: {entry['owner'].upper()}")
                print(f"  Category: {entry['category']}")
            else:
                print(f"  Not found: {path}")
        else:
            print("  Specify a protocol path to inspect")
            print("  Example: steward chat 'fetch protocol defense.py'")

        return 0

    def _krishna_sustain(self, route: LotusRoute) -> int:
        """KRISHNA/SUSTAIN: Persist, schedule governance."""
        print("KRISHNA/SUSTAIN: Governance Persistence")
        print("-" * 40)
        print("  (Sustain governance - future implementation)")
        return 0

    # =========================================================================
    # RAMA BRANCH HANDLERS (Strength/Service)
    # =========================================================================

    def _rama_wake(self, route: LotusRoute) -> int:
        """RAMA/WAKE: Scan, find services."""
        print("RAMA/WAKE: Service Discovery")
        print("-" * 40)

        from pathlib import Path
        from collections import defaultdict

        vibe_core = Path(__file__).parent.parent
        by_dir: Dict[str, int] = defaultdict(int)

        for f in vibe_core.rglob("*.py"):
            try:
                rel = f.relative_to(vibe_core)
                parts = rel.parts
                top = parts[0] if len(parts) > 1 else "ROOT"
                by_dir[top] += 1
            except ValueError:
                pass

        print(f"\n  Directories scanned:")
        for d, count in sorted(by_dir.items(), key=lambda x: -x[1])[:10]:
            print(f"    {d:20} {count:>4} files")

        return 0

    def _rama_purify(self, route: LotusRoute) -> int:
        """RAMA/PURIFY: Test, verify services."""
        print("RAMA/PURIFY: Service Verification")
        print("-" * 40)
        print("  (Service verification - future implementation)")
        return 0

    def _rama_serve(self, route: LotusRoute) -> int:
        """RAMA/SERVE: Execute, run services."""
        print("RAMA/SERVE: Service Execution")
        print("-" * 40)
        print("  (Service execution - future implementation)")
        return 0

    def _rama_sustain(self, route: LotusRoute) -> int:
        """RAMA/SUSTAIN: Maintain, optimize services."""
        print("RAMA/SUSTAIN: Service Maintenance")
        print("-" * 40)
        print("  (Service maintenance - future implementation)")
        return 0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "LotusBranch",
    "LotusPhase",
    # Types
    "LotusRoute",
    "LotusHandler",
    # Functions
    "detect_phase",
    "compute_route",
    # Registry
    "LotusHandlerRegistry",
    # CLI
    "LotusCLI",
]
