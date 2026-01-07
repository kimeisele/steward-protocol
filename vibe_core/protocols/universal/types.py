from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# --- SYNC TYPES ---


@dataclass
class SyncResult:
    success: bool
    items_synced: int
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SyncStatus:
    is_synced: bool
    last_sync: Optional[datetime]
    pending_items: int
    details: Dict[str, Any] = field(default_factory=dict)


# --- ENFORCE TYPES ---


class Verdict(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    AUDIT = "audit"


@dataclass
class EnforceContext:
    caller_id: str
    resource: str
    action: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    id: str
    pattern: str
    verdict: Verdict
    priority: int
    description: str = ""


# --- INFER TYPES ---


@dataclass
class InferenceInput:
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None


@dataclass
class Inference:
    conclusion: str
    confidence: float
    reasoning: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassifyInput:
    content: str
    categories: List[str]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Classification:
    category: str
    confidence: float
    alternatives: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Evaluation:
    valid: bool
    score: float
    violations: List[str]
    notes: List[str] = field(default_factory=list)


# --- MEMORY TYPES ---


@dataclass
class MemoryValue:
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    ttl: Optional[int] = None
    embedding: Optional[List[float]] = None
