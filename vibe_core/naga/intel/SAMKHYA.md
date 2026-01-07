# SAMKHYA: ATOMIC PROTOCOL ARCHITECTURE

> **"Prakriti manifestiert durch Gunas - Verben, nicht Substantive."**

---

## DAS PRINZIP

```
FALSCH: Protocol-per-Service     → 100 Services = 100 Protocols = TOTGEBURT
FALSCH: Capability-as-Tags       → Keine Typsicherheit, nur Runtime
FALSCH: Domain-Cluster-Protocols → Zu breit, nicht komponierbar

RICHTIG: Atomic Verb Protocols   → Wie NAGA groups.py
```

**Golden Solution:**
- **Protocol** = Domain-Gruppe (wenige)
- **Methods** = Atomic Verbs (komponierbar)
- **Static** = Python typing (`Protocol` + `@runtime_checkable`)
- **Dynamic** = Registry matching

---

## NAGA HAT ES RICHTIG (groups.py)

```python
SecurityProtocol:
    intercept(subject) → Verdict      # VERB
    bite(subject, reason) → None      # VERB
    is_quarantined(id) → bool         # VERB (query)

GovernanceProtocol:
    audit(target) → AuditResult       # VERB
    verify(claim) → bool              # VERB
    get_dharma_score() → float        # VERB (query)

DataProtocol:
    get_hash() → str                  # VERB
    get_sequence() → int              # VERB
    is_synced() → bool                # VERB

TransformProtocol:
    analyze(target) → Analysis        # VERB
    can_transform(target) → bool      # VERB
    transform(target, strategy) → TransformResult  # VERB

ObserveProtocol:
    observe(event_type, source, data) → Observation  # VERB
    get_observations(since) → List[Observation]      # VERB
    get_observation_count() → int                    # VERB
```

**Pattern**: Domain-Gruppe + Atomic Verbs + Typed Returns

---

## UNIVERSAL PROTOCOLS (Für den STATE)

Applying same pattern to fix 634 Karma Debt:

### 1. ReadWriteProtocol (Config, State, Cache)

```python
@runtime_checkable
class ReadWriteProtocol(Protocol):
    """Atomic read/write operations."""

    def read(self, key: str) -> object:
        """Read value by key."""
        ...

    def write(self, key: str, value: object) -> None:
        """Write value by key."""
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...

# Implementiert von:
# CityConfig, CivicConfig, HeraldConfig, StateStore, PadmaCache...
```

### 2. SyncProtocol (CI, Git, Ledger, State)

```python
@runtime_checkable
class SyncProtocol(Protocol):
    """Atomic sync operations."""

    def sync(self) -> "SyncResult":
        """Perform synchronization."""
        ...

    def get_sync_status(self) -> "SyncStatus":
        """Get current sync status."""
        ...

    def is_synced(self) -> bool:
        """Check if synchronized."""
        ...

# Implementiert von:
# CISyncService, GitSync, LedgerSync, StateSync...
```

### 3. EnforceProtocol (Capability, Rate, Quota, Steward)

```python
@runtime_checkable
class EnforceProtocol(Protocol):
    """Atomic enforcement operations."""

    def enforce(self, action: str, context: "EnforceContext") -> "Verdict":
        """Enforce rules on action."""
        ...

    def check(self, action: str) -> bool:
        """Quick check if action allowed."""
        ...

    def get_rules(self) -> List["Rule"]:
        """Get active rules."""
        ...

# Implementiert von:
# CapabilityEnforcer, RateLimiter, QuotaEnforcer, StewardEnforcer...
```

### 4. InferProtocol (MANAS: Validator, Viveka, Maya, Akasha)

```python
@runtime_checkable
class InferProtocol(Protocol):
    """Atomic inference operations."""

    def infer(self, input: "InferenceInput") -> "Inference":
        """Draw inference from input."""
        ...

    def classify(self, input: "ClassifyInput") -> "Classification":
        """Classify input into categories."""
        ...

    def evaluate(self, claim: str) -> "Evaluation":
        """Evaluate truth of a claim."""
        ...

# Implementiert von:
# SrutiValidator, Viveka, Maya, Akasha, IntentRouter...
```

### 5. StoreRecallProtocol (Memory: Synaptic, Semantic, Episodic)

```python
@runtime_checkable
class StoreRecallProtocol(Protocol):
    """Atomic store/recall operations."""

    def store(self, key: str, value: "MemoryValue") -> None:
        """Store value in memory."""
        ...

    def recall(self, key: str) -> Optional["MemoryValue"]:
        """Recall value from memory."""
        ...

    def forget(self, key: str) -> bool:
        """Forget (tombstone) a value."""
        ...

# Implementiert von:
# SynapticMemory, SemanticMemory, EpisodicMemory...
# NOTE: search() ist KEIN atomic verb - eigenes QueryProtocol wenn nötig
```

---

## COMPLETE PROTOCOL MAP

```
NAGA PROTOCOLS (5):              UNIVERSAL PROTOCOLS (5):
─────────────────────────────────────────────────────────
SecurityProtocol                 ReadWriteProtocol
  intercept(), bite()              read(), write(), exists()

GovernanceProtocol               SyncProtocol
  audit(), verify()                sync(), is_synced()

DataProtocol                     EnforceProtocol
  get_hash(), is_synced()          enforce(), check()

TransformProtocol                InferProtocol
  analyze(), transform()           infer(), classify(), evaluate()

ObserveProtocol                  StoreRecallProtocol
  observe(), get_observations()    store(), recall(), forget()
─────────────────────────────────────────────────────────
= 10 PROTOCOLS TOTAL (nicht 100+)
= 27 ATOMIC VERBS (komponierbar)
= FRAKTAL SKALIERBAR
```

---

## TYPED RETURNS (Keine Any)

```python
# Shared Types für Universal Protocols
# (Wie NAGA types.py)

@dataclass
class SyncResult:
    success: bool
    items_synced: int
    errors: List[str]
    timestamp: datetime

@dataclass
class SyncStatus:
    is_synced: bool
    last_sync: Optional[datetime]
    pending_items: int

class Verdict(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"

@dataclass
class EnforceContext:
    caller_id: str
    resource: str
    action: str
    timestamp: datetime

@dataclass
class Rule:
    id: str
    pattern: str
    verdict: Verdict
    priority: int

@dataclass
class InferenceInput:
    content: str
    context: Dict[str, str]

@dataclass
class Inference:
    conclusion: str
    confidence: float
    reasoning: List[str]

@dataclass
class ClassifyInput:
    content: str
    categories: List[str]

@dataclass
class Classification:
    category: str
    confidence: float
    alternatives: List[str]

@dataclass
class Evaluation:
    valid: bool
    score: float
    violations: List[str]

@dataclass
class MemoryValue:
    content: str
    metadata: Dict[str, str]
    timestamp: datetime
    ttl: Optional[int]
```

---

## REGISTRY INTEGRATION

```python
# Services registrieren sich mit Protocol
ServiceRegistry.register(ReadWriteProtocol, CityConfig())
ServiceRegistry.register(ReadWriteProtocol, CivicConfig())
ServiceRegistry.register(SyncProtocol, CISyncService())
ServiceRegistry.register(EnforceProtocol, CapabilityEnforcer())

# Caller fragt nach Protocol, nicht Service
config = ServiceRegistry.get(ReadWriteProtocol)
config.read("city.name")  # Typsicher, welcher Service = egal

# Multiple implementations? get_all()
all_configs = ServiceRegistry.get_all(ReadWriteProtocol)
for cfg in all_configs:
    cfg.write("updated", True)
```

---

## MIGRATION PATH

### Phase 1: Create Protocol Files

```
vibe_core/protocols/universal/
├── __init__.py
├── read_write.py      # ReadWriteProtocol + types
├── sync.py            # SyncProtocol + types
├── enforce.py         # EnforceProtocol + types
├── infer.py           # InferProtocol + types
└── store_recall.py    # StoreRecallProtocol + types
```

### Phase 2: Services Implement Protocols

```python
# vibe_core/config.py
from vibe_core.protocols.universal import ReadWriteProtocol

class CityConfig(ReadWriteProtocol):
    def read(self, key: str) -> object:
        return self._data.get(key)

    def write(self, key: str, value: object) -> None:
        self._data[key] = value

    def exists(self, key: str) -> bool:
        return key in self._data
```

### Phase 3: Cartridges Use Protocols

```python
# VORHER (TODSÜNDE):
from vibe_core.config import CityConfig
config = CityConfig()
value = config.get("key")  # Methode heißt anders!

# NACHHER (DHARMA):
from vibe_core.protocols.universal import ReadWriteProtocol
config = ServiceRegistry.get(ReadWriteProtocol)
value = config.read("key")  # Atomic verb, typsicher
```

---

## WARUM DAS FUNKTIONIERT

| Prinzip | Umsetzung |
|---------|-----------|
| **Verbs not Nouns** | `read()`, `write()`, `sync()`, `enforce()` |
| **Domain Groups** | 5 NAGA + 5 Universal = 10 total |
| **Static Typing** | `Protocol` + `@runtime_checkable` |
| **Dynamic Matching** | `ServiceRegistry.get(Protocol)` |
| **Composable** | Service implements multiple Protocols |
| **Testable** | Mock Protocol, not Service |
| **Scalable** | New Service → implements existing Protocols |

---

## NEXT ACTIONS

1. **Create** `vibe_core/protocols/universal/` with 5 Protocol files
2. **Create** shared types in `vibe_core/protocols/universal/types.py`
3. **Update** `ServiceRegistry` to support `get_all(Protocol)`
4. **Migrate** Config classes to implement `ReadWriteProtocol`
5. **Migrate** CISyncService to implement `SyncProtocol`
6. **Migrate** CapabilityEnforcer to implement `EnforceProtocol`
7. **Migrate** MANAS components to implement `InferProtocol`
8. **Migrate** Memory systems to implement `StoreRecallProtocol`

---

**SIGNED**:
- **Architect**: Lord Kapila (Samkhya)
- **Pattern**: Atomic Verb Protocols (wie NAGA groups.py)
- **Date**: 2026-01-07
- **Status**: READY FOR IMPLEMENTATION
