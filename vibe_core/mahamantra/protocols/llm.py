from typing import Protocol, runtime_checkable, List, Optional, Dict, Union, Callable, Tuple
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
    CREATE = 1
    CONNECT = 2
    ANALYZE = 3
    EXECUTE = 4
    TRANSFORM = 5
    INVOKE = 6
    SUSTAIN = 7
    EXPAND = 8
    INTEGRATE = 9
    VALIDATE = 10
    PROTECT = 11
    GUIDE = 12
    SURRENDER = 13
    COMPLETE = 14
    TRANSCEND = 15

@dataclass(frozen=True)
class RouteResult:
    """Result of a routing operation."""
    intent_id: int
    agent: Optional[str]
    category: Optional[IntentCategory]
    category_name: str
    ops: int
    found: bool
    address: Tuple[int, ...]
    handler: Optional[Callable[..., object]] = None

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

@dataclass(frozen=True)
class RouterStats:
    """Router statistics."""
    total_agents: int
    total_intents: int
    depth: int
    collisions: int
