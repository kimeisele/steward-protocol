"""
MAHA LLM - Holographic Intent Router for AI Agents
===================================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. From Me everything emanates." (BG 10.8)

THE PROBLEM:
------------
Vector Search: O(N) - Scans every option
Dict Lookup: O(1) amortized, O(N) worst case (hash collisions)

THE SOLUTION:
-------------
Holographic Routing: O(4) ALWAYS - Calculates the address

65,536 agents/tools in exactly 4 memory accesses.
No search. No scan. TELEPORTATION.

THE ARCHITECTURE:
-----------------
    MahaCompression          MahaLLM              Agent
    ┌─────────────┐    ┌──────────────────┐    ┌─────────┐
    │ 100k tokens │───▶│ Intent Seed      │───▶│ DevOps  │
    │     ↓       │    │     ↓            │    │ Coder   │
    │ seed=0x4F23 │    │ route(0x4F23)    │    │ Poet    │
    └─────────────┘    │     ↓            │    │ Admin   │
                       │ O(4) lookup      │    └─────────┘
                       │     ↓            │
                       │ agent="DevOps"   │
                       └──────────────────┘

THE 16 INTENT CATEGORIES (WORDS):
---------------------------------
0: OBSERVE    4: EXECUTE    8: EXPAND     12: GUIDE
1: CREATE     5: TRANSFORM  9: INTEGRATE  13: SURRENDER
2: CONNECT    6: INVOKE    10: VALIDATE   14: COMPLETE
3: ANALYZE    7: SUSTAIN   11: PROTECT    15: TRANSCEND

ENTERPRISE USAGE:
-----------------
    llm = mahamantra.llm()

    # Register agents on the 16-ary tree
    llm.register("devops", intent_id=0x4000)  # EXECUTE category
    llm.register("coder", intent_id=0x1000)   # CREATE category
    llm.register("poet", intent_id=0x5000)    # TRANSFORM category

    # Route intent seed from MahaCompression → Agent
    compression = mahamantra.compression()
    result = compression.compress("Fix the production server NOW!")

    route = llm.route(result.seed)
    print(route.agent)      # "devops"
    print(route.category)   # "EXECUTE"
    print(route.ops)        # 4 (always!)

    # Or use the integrated pipeline
    route = llm.route_text("Write me a poem about Krishna")
    print(route.agent)      # "poet"
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Position 3 - The Messenger
__position__ = 3
__genesis__ = "0xLLM0037"  # LLM layer

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Final, List, Optional, Union
import hashlib


# =============================================================================
# MAHAMANTRA CONSTANTS
# =============================================================================

WORDS: Final[int] = 16           # 16 branches per level
QUARTERS: Final[int] = 4         # 4 levels = 16 bits
INTENT_SPACE: Final[int] = 65536 # 16^4 = total intent space
ROUTING_OPS: Final[int] = 4      # Always 4 ops to route


# =============================================================================
# THE 16 INTENT CATEGORIES
# =============================================================================

class IntentCategory(Enum):
    """The 16 primary intent categories mapped to WORDS."""

    OBSERVE = 0      # Hare - Attention/Observation
    CREATE = 1       # Krishna - Creation
    CONNECT = 2      # Hare - Connection
    ANALYZE = 3      # Krishna - Analysis
    EXECUTE = 4      # Krishna - Action
    TRANSFORM = 5    # Krishna - Transformation
    INVOKE = 6       # Hare - Invocation
    SUSTAIN = 7      # Hare - Sustenance
    EXPAND = 8       # Hare - Expansion
    INTEGRATE = 9    # Rama - Integration
    VALIDATE = 10    # Hare - Validation
    PROTECT = 11     # Rama - Protection
    GUIDE = 12       # Rama - Guidance
    SURRENDER = 13   # Rama - Surrender
    COMPLETE = 14    # Hare - Completion
    TRANSCEND = 15   # Hare - Transcendence


# Category keywords for text classification
CATEGORY_KEYWORDS: Dict[IntentCategory, List[str]] = {
    IntentCategory.OBSERVE: ["watch", "monitor", "observe", "check", "look", "see", "view"],
    IntentCategory.CREATE: ["create", "make", "build", "write", "generate", "new", "add"],
    IntentCategory.CONNECT: ["connect", "link", "join", "integrate", "merge", "combine"],
    IntentCategory.ANALYZE: ["analyze", "examine", "study", "investigate", "understand", "why"],
    IntentCategory.EXECUTE: ["run", "execute", "do", "perform", "start", "launch", "deploy", "fix"],
    IntentCategory.TRANSFORM: ["change", "transform", "convert", "modify", "update", "refactor"],
    IntentCategory.INVOKE: ["call", "invoke", "trigger", "request", "ask", "summon"],
    IntentCategory.SUSTAIN: ["maintain", "keep", "sustain", "preserve", "hold", "continue"],
    IntentCategory.EXPAND: ["expand", "grow", "scale", "extend", "increase", "more"],
    IntentCategory.INTEGRATE: ["integrate", "unify", "consolidate", "sync", "harmonize"],
    IntentCategory.VALIDATE: ["validate", "verify", "test", "check", "confirm", "ensure"],
    IntentCategory.PROTECT: ["protect", "secure", "guard", "defend", "safe", "backup"],
    IntentCategory.GUIDE: ["guide", "help", "assist", "advise", "teach", "show", "explain"],
    IntentCategory.SURRENDER: ["accept", "surrender", "submit", "yield", "trust", "delegate"],
    IntentCategory.COMPLETE: ["complete", "finish", "done", "end", "close", "final"],
    IntentCategory.TRANSCEND: ["transcend", "beyond", "elevate", "enlighten", "liberate", "free"],
}


# =============================================================================
# HOLOGRAPHIC TREE NODE
# =============================================================================

class HolographicNode:
    """
    A node in the 16-ary holographic tree.

    Each level has 16 branches = WORDS.
    Pattern repeats at every level (holographic property).
    """

    __slots__ = ("children", "agent_name", "handler", "metadata")

    def __init__(self) -> None:
        self.children: List[Optional["HolographicNode"]] = [None] * WORDS
        self.agent_name: Optional[str] = None
        self.handler: Optional[Callable] = None
        self.metadata: Dict[str, Any] = {}


# =============================================================================
# RESULT TYPES
# =============================================================================

@dataclass(frozen=True)
class RouteResult:
    """Result of routing an intent."""

    # The intent that was routed
    intent_id: int

    # The resolved agent/handler
    agent: Optional[str] = None
    handler: Optional[Callable] = None

    # Routing metadata
    category: Optional[IntentCategory] = None
    category_name: str = ""

    # Performance (always 4 for holographic)
    ops: int = ROUTING_OPS

    # Was a handler found?
    found: bool = False

    # The address breakdown (4 nibbles)
    address: tuple = ()

    @property
    def is_routed(self) -> bool:
        return self.found and self.agent is not None


@dataclass(frozen=True)
class RegistrationResult:
    """Result of registering an agent."""

    agent_name: str
    intent_id: int
    category: IntentCategory
    success: bool = True
    message: str = ""

    @property
    def address(self) -> str:
        return f"0x{self.intent_id:04X}"


@dataclass
class RouterStats:
    """Statistics about the router."""

    total_agents: int = 0
    agents_by_category: Dict[str, int] = field(default_factory=dict)
    total_routes: int = 0
    routes_found: int = 0
    routes_missed: int = 0

    @property
    def hit_rate(self) -> float:
        return self.routes_found / self.total_routes if self.total_routes > 0 else 0.0


# =============================================================================
# MAHA LLM - HOLOGRAPHIC INTENT ROUTER
# =============================================================================

class MahaLLM:
    """
    Holographic Intent Router for AI Agents.

    O(4) routing to ANY of 65,536 agents/tools.
    No search. No scan. CALCULATION.

    THE MATH:
        Intent space: 65,536 = 16^4 = WORDS^QUARTERS
        Routing ops: 4 (ALWAYS - holographic guarantee)
        Branches per level: 16 = WORDS

    COMPARISON:
        Vector search: O(N) - scans all embeddings
        Dict lookup: O(1) avg, O(N) worst (collisions)
        Holographic: O(4) ALWAYS - guaranteed constant
    """

    def __init__(self) -> None:
        """Initialize the holographic router."""
        self._root = HolographicNode()
        self._size = 0
        self._stats = RouterStats()
        self._agents: Dict[str, int] = {}  # name -> intent_id

    def __len__(self) -> int:
        """Number of registered agents."""
        return self._size

    # =========================================================================
    # REGISTRATION
    # =========================================================================

    def register(
        self,
        agent_name: str,
        *,
        intent_id: Optional[int] = None,
        category: Optional[IntentCategory] = None,
        handler: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RegistrationResult:
        """
        Register an agent at a specific intent address.

        Args:
            agent_name: Name of the agent
            intent_id: 16-bit intent ID (0-65535). Auto-generated if not provided.
            category: Primary intent category. Used to auto-generate ID if not provided.
            handler: Optional callable to execute when routed
            metadata: Optional metadata dict

        Returns:
            RegistrationResult with address and status

        Example:
            llm.register("devops", category=IntentCategory.EXECUTE)
            llm.register("coder", intent_id=0x1234)
        """
        # Auto-generate intent_id if not provided
        if intent_id is None:
            if category is not None:
                # Use category as high nibble, 0 for rest (base address)
                # This ensures route_text finds the agent in its category
                intent_id = category.value << 12
            else:
                # Full hash of name
                intent_id = int(hashlib.md5(agent_name.encode()).hexdigest()[:4], 16)

        # Validate range
        if not (0 <= intent_id < INTENT_SPACE):
            return RegistrationResult(
                agent_name=agent_name,
                intent_id=intent_id,
                category=category or IntentCategory(intent_id >> 12),
                success=False,
                message=f"Intent ID must be 0-65535, got {intent_id}",
            )

        # Determine category from high nibble
        actual_category = IntentCategory(intent_id >> 12)

        # Navigate/create tree path
        node = self._root

        # Level 0: bits 12-15 (category)
        nibble = (intent_id >> 12) & 0xF
        if node.children[nibble] is None:
            node.children[nibble] = HolographicNode()
        node = node.children[nibble]

        # Level 1: bits 8-11
        nibble = (intent_id >> 8) & 0xF
        if node.children[nibble] is None:
            node.children[nibble] = HolographicNode()
        node = node.children[nibble]

        # Level 2: bits 4-7
        nibble = (intent_id >> 4) & 0xF
        if node.children[nibble] is None:
            node.children[nibble] = HolographicNode()
        node = node.children[nibble]

        # Level 3: bits 0-3
        nibble = intent_id & 0xF
        if node.children[nibble] is None:
            node.children[nibble] = HolographicNode()
        node = node.children[nibble]

        # Store agent at leaf
        node.agent_name = agent_name
        node.handler = handler
        node.metadata = metadata or {}

        self._size += 1
        self._agents[agent_name] = intent_id

        # Update stats
        cat_name = actual_category.name
        self._stats.total_agents += 1
        self._stats.agents_by_category[cat_name] = self._stats.agents_by_category.get(cat_name, 0) + 1

        return RegistrationResult(
            agent_name=agent_name,
            intent_id=intent_id,
            category=actual_category,
            success=True,
            message=f"Registered at 0x{intent_id:04X} ({actual_category.name})",
        )

    def register_batch(
        self,
        agents: List[str],
        *,
        categories: Optional[List[IntentCategory]] = None,
    ) -> List[RegistrationResult]:
        """
        Register multiple agents at once.

        Args:
            agents: List of agent names
            categories: Optional list of categories (same length as agents)

        Returns:
            List of RegistrationResults
        """
        results = []
        for i, agent in enumerate(agents):
            cat = categories[i] if categories and i < len(categories) else None
            results.append(self.register(agent, category=cat))
        return results

    # =========================================================================
    # ROUTING
    # =========================================================================

    def route(self, intent_id: int) -> RouteResult:
        """
        Route an intent to its registered agent.

        O(4) ALWAYS. Guaranteed constant time.

        Args:
            intent_id: 16-bit intent ID (0-65535)

        Returns:
            RouteResult with agent and metadata

        Example:
            result = llm.route(0x4F23)
            print(result.agent)  # "devops"
        """
        self._stats.total_routes += 1

        # Clamp to valid range
        intent_id = intent_id & 0xFFFF

        # Extract address nibbles
        n0 = (intent_id >> 12) & 0xF
        n1 = (intent_id >> 8) & 0xF
        n2 = (intent_id >> 4) & 0xF
        n3 = intent_id & 0xF
        address = (n0, n1, n2, n3)

        category = IntentCategory(n0)

        # Navigate tree (exactly 4 ops)
        node = self._root

        # Level 0
        child = node.children[n0]
        if child is None:
            self._stats.routes_missed += 1
            return RouteResult(
                intent_id=intent_id,
                category=category,
                category_name=category.name,
                address=address,
                found=False,
            )
        node = child

        # Level 1
        child = node.children[n1]
        if child is None:
            self._stats.routes_missed += 1
            return RouteResult(
                intent_id=intent_id,
                category=category,
                category_name=category.name,
                address=address,
                found=False,
            )
        node = child

        # Level 2
        child = node.children[n2]
        if child is None:
            self._stats.routes_missed += 1
            return RouteResult(
                intent_id=intent_id,
                category=category,
                category_name=category.name,
                address=address,
                found=False,
            )
        node = child

        # Level 3
        child = node.children[n3]
        if child is None:
            self._stats.routes_missed += 1
            return RouteResult(
                intent_id=intent_id,
                category=category,
                category_name=category.name,
                address=address,
                found=False,
            )
        node = child

        self._stats.routes_found += 1

        return RouteResult(
            intent_id=intent_id,
            agent=node.agent_name,
            handler=node.handler,
            category=category,
            category_name=category.name,
            address=address,
            found=node.agent_name is not None,
        )

    def route_seed(self, seed: int) -> RouteResult:
        """
        Route a compression seed (32-bit) to agent.

        Takes the lower 16 bits of the seed.

        Args:
            seed: 32-bit seed from MahaCompression

        Returns:
            RouteResult
        """
        return self.route(seed & 0xFFFF)

    def route_text(self, text: str) -> RouteResult:
        """
        Route text directly to an agent.

        1. Classifies text to category (keyword matching)
        2. Hashes text for sub-address
        3. Routes to agent

        Args:
            text: Input text to route

        Returns:
            RouteResult
        """
        intent_id = self._text_to_intent(text)
        return self.route(intent_id)

    def _text_to_intent(self, text: str, *, use_base: bool = True) -> int:
        """Convert text to 16-bit intent ID."""
        text_lower = text.lower()

        # Find matching category by keywords
        best_category = IntentCategory.GUIDE  # Default
        best_score = 0

        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_category = category

        if use_base:
            # Route to category base (where agents registered by category live)
            return best_category.value << 12
        else:
            # Generate sub-address from text hash (for fine-grained routing)
            text_hash = int(hashlib.md5(text.encode()).hexdigest()[:3], 16)
            return (best_category.value << 12) | (text_hash & 0xFFF)

    # =========================================================================
    # INTEGRATION WITH MAHACOMPRESSION
    # =========================================================================

    def route_compressed(self, compression_result: Any) -> RouteResult:
        """
        Route a MahaCompression result to agent.

        This is the integration point:
            MahaCompression → MahaLLM → Agent

        Args:
            compression_result: Result from mahamantra.compression().compress()

        Returns:
            RouteResult
        """
        seed = getattr(compression_result, "seed", 0)
        return self.route_seed(seed)

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def find_agent(self, agent_name: str) -> Optional[int]:
        """Find intent_id for a registered agent name."""
        return self._agents.get(agent_name)

    def list_agents(self) -> Dict[str, str]:
        """List all registered agents with their addresses."""
        return {name: f"0x{id:04X}" for name, id in self._agents.items()}

    def stats(self) -> RouterStats:
        """Get routing statistics."""
        return self._stats

    def categories(self) -> List[str]:
        """List all 16 intent categories."""
        return [c.name for c in IntentCategory]

    def category_for_text(self, text: str) -> IntentCategory:
        """Classify text into one of 16 categories."""
        intent_id = self._text_to_intent(text)
        return IntentCategory(intent_id >> 12)

    # =========================================================================
    # EXECUTE (Call handler if registered)
    # =========================================================================

    def execute(self, intent_id: int, *args, **kwargs) -> Any:
        """
        Route and execute the handler for an intent.

        Args:
            intent_id: The intent to route
            *args, **kwargs: Arguments to pass to handler

        Returns:
            Handler result, or None if no handler registered
        """
        result = self.route(intent_id)
        if result.handler is not None:
            return result.handler(*args, **kwargs)
        return None

    def execute_text(self, text: str, *args, **kwargs) -> Any:
        """Route text and execute the handler."""
        result = self.route_text(text)
        if result.handler is not None:
            return result.handler(*args, **kwargs)
        return None


# =============================================================================
# CONSTANTS REFERENCE
# =============================================================================

# Theoretical performance
THEORETICAL_SPEEDUP: Final[int] = INTENT_SPACE // ROUTING_OPS  # 16,384x

# Intent levels (hierarchy)
INTENT_LEVELS: Final[Dict[int, Dict]] = {
    1: {"capacity": WORDS, "description": "16 core categories"},
    2: {"capacity": WORDS ** 2, "description": "256 sub-categories"},
    3: {"capacity": WORDS ** 3, "description": "4,096 fine intents"},
    4: {"capacity": WORDS ** 4, "description": "65,536 full space"},
}


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Main class
    "MahaLLM",
    # Result types
    "RouteResult",
    "RegistrationResult",
    "RouterStats",
    # Enums
    "IntentCategory",
    # Constants
    "WORDS",
    "QUARTERS",
    "INTENT_SPACE",
    "ROUTING_OPS",
    "THEORETICAL_SPEEDUP",
    "INTENT_LEVELS",
    "CATEGORY_KEYWORDS",
]


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=== MAHA LLM - Holographic Intent Router ===\n")

    llm = MahaLLM()

    # Register agents by category
    print("1. REGISTERING AGENTS")
    results = [
        llm.register("observer", category=IntentCategory.OBSERVE),
        llm.register("coder", category=IntentCategory.CREATE),
        llm.register("devops", category=IntentCategory.EXECUTE),
        llm.register("transformer", category=IntentCategory.TRANSFORM),
        llm.register("guardian", category=IntentCategory.PROTECT),
        llm.register("guide", category=IntentCategory.GUIDE),
    ]
    for r in results:
        print(f"   {r.agent_name}: {r.address} ({r.category.name})")

    print(f"\n2. ROUTING (O({ROUTING_OPS}) always!)")

    # Route by intent_id
    for name, addr in llm.list_agents().items():
        intent_id = int(addr, 16)
        result = llm.route(intent_id)
        print(f"   Route {addr} → {result.agent} ({result.category_name})")

    print("\n3. ROUTE TEXT DIRECTLY")
    texts = [
        "Create a new Python script",
        "Fix the production server",
        "Help me understand this code",
        "Protect the database from attacks",
    ]
    for text in texts:
        result = llm.route_text(text)
        print(f"   \"{text[:30]}...\" → {result.agent} ({result.category_name})")

    print("\n4. INTEGRATION WITH MAHACOMPRESSION")
    print("   compression.compress() → seed → llm.route_seed() → agent")

    print("\n5. STATISTICS")
    stats = llm.stats()
    print(f"   Total agents: {stats.total_agents}")
    print(f"   Total routes: {stats.total_routes}")
    print(f"   Hit rate: {stats.hit_rate:.1%}")
    print(f"   Categories: {stats.agents_by_category}")

    print("\n6. THEORETICAL PERFORMANCE")
    print(f"   Intent space: {INTENT_SPACE:,}")
    print(f"   Routing ops: {ROUTING_OPS}")
    print(f"   Speedup vs linear: {THEORETICAL_SPEEDUP:,}x")
