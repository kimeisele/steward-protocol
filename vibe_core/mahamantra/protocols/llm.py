from typing import Protocol, runtime_checkable, List, Optional, Dict, Union, Callable, Tuple
from vibe_core.mahamantra.protocols._seed import (HALVES, HARE_COUNT, KSETRAJNA, MAHAJANA_COUNT, NAVA, PANCHA, QUARTERS, SEVEN, SHARANAGATI, TEN, TRINITY)
from dataclasses import dataclass
from enum import Enum

# Strict Type Declaration for JSON-like metadata
JsonValue = Union[str, int, float, bool, None, Dict[str, "JsonValue"], List["JsonValue"]]

@runtime_checkable
class MahaLLMProtocol(Protocol):
    """
    Protocol for MahaLLM: Holographic Intent Router.
    
    Responsible for O(4) routing of intents to agents.
    NO ANY types allowed.
    """
    
    def route(self, intent_id: int) -> "RouteResult":
        """Route based on raw intent ID."""
        ...
        
    def route_text(self, text: str) -> "RouteResult":
        """Route based on text (via vibration/classification)."""
        ...
        
    def register(
        self, 
        agent_name: str, 
        *, 
        intent_id: Optional[int] = None,
        category: Optional["IntentCategory"] = None,
        handler: Optional[Callable[..., object]] = None,
        metadata: Optional[Dict[str, JsonValue]] = None
    ) -> "RegistrationResult":
        """Register an agent in the holographic tree."""
        ...

    def stats(self) -> "RouterStats":
        """Get router statistics."""
        ...

    def execute(self, intent_id: int, *args: object, **kwargs: object) -> object:
        """Execute intent by ID."""
        ...

class IntentCategory(Enum):
    """The 16 primary intent categories."""
    OBSERVE = 0
    CREATE = KSETRAJNA
    CONNECT = HALVES
    ANALYZE = TRINITY
    EXECUTE = QUARTERS
    TRANSFORM = PANCHA
    INVOKE = SHARANAGATI
    SUSTAIN = SEVEN
    EXPAND = HARE_COUNT
    INTEGRATE = NAVA
    VALIDATE = TEN
    PROTECT = 11
    GUIDE = MAHAJANA_COUNT
    SURRENDER = 13
    COMPLETE = 14
    TRANSCEND = 15

@dataclass(frozen=True)
class RouteResult:
    """Result of a routing operation."""
    intent_id: int
    category_name: str = ""
    found: bool = False
    agent: Optional[str] = None
    category: Optional[IntentCategory] = None
    ops: int = QUARTERS  # Always 4 (holographic guarantee)
    address: Tuple[int, ...] = ()
    handler: Optional[Callable[..., object]] = None

    @property
    def is_routed(self) -> bool:
        return self.found and self.agent is not None

@dataclass(frozen=True)
class RegistrationResult:
    """Result of a registration operation."""
    agent_name: str
    intent_id: int
    category: IntentCategory
    success: bool
    message: str
    
    @property
    def address(self) -> str:
        """Hex address string (e.g. 0xBEAF)."""
        return f"0x{self.intent_id:04X}"

@dataclass
class RouterStats:
    """Router statistics."""
    total_agents: int = 0
    agents_by_category: Dict[str, int] = None  # type: ignore
    total_routes: int = 0
    routes_found: int = 0
    routes_missed: int = 0

    def __post_init__(self) -> None:
        if self.agents_by_category is None:
            object.__setattr__(self, 'agents_by_category', {})

    @property
    def hit_rate(self) -> float:
        return self.routes_found / self.total_routes if self.total_routes > 0 else 0.0
