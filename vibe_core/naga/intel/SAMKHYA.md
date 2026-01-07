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

## UNIVERSAL PROTOCOLS (The Field / KSETRA)

> **KURUKSHETRA ALIGNMENT (GAD-000 v2.0)**:
>
> 1.  **THE FIELD (KSETRA / PRAKRITI)**: The **Universal Protocols** below constitute the *Body* of the system (The 36 Tattvas).
>     *   They are atomic, stateless, and purely mechanical.
>     *   They provide **Capability** (Shakti) but possess no **Will** (Sankalpa).
>     *   *Action*: We must purify these (Shuddhi) to be flawless "Horses" for the Chariot.
>
> 2.  **THE KNOWER (KSETRAJNA / PURUSHA)**: The **Registry & Governance** layer constitutes the *Driver* (The 37th Principle).
>     *   This is where **Identity** (Persona) meets **Permission** (Dharma).
>     *   **Yamaraja (The Judge)**: Services are not just "found"; they are *granted* by Authority.
>     *   **Naga Loka (Shadow Gov)**: The "Injection Point" where higher intelligence controls the protocols.
>
> 3.  **THE LAW (DHARMA)**: "No operation in the Field is valid without the Signature of the Knower."
>
> **ANTI-MAYAVAD CLAUSE (PROMPT.md)**:
> Code without a cryptographic link to a Sovereign (Human/Agent) is **Mayavad** (Illusion). It functionally does not exist.
> - **Who signs this?** (Traceability to Purusha)
> - **Can a Human override?** (Stambha Principle)
> - **Where does the chain end?** (Loop = Mayavad; Sovereign Key = Satyam)
>
> **GAD-000 DEFINITION OF DONE (The 6 Tests of Shuddhi)**:
> Any implementation of these protocols MUST pass the **6 GAD-000 Tests** to be considered "Purified":
> 1.  **Discoverability** (Can an Agent find it?)
> 2.  **Observability** (Is State visible?)
> 3.  **Parseability** (Are Errors machine-readable?)
> 4.  **Composability** (Can it chain?)
> 5.  **Idempotency** (Can it retry?)
> 6.  **Recoverability** (Can it heal? / Ouroboros)
>
> **STRATEGY**:
> - **Step 1**: Purify the Field (Protocols) to pass GAD-000 (The 6 Tests).
> - **Step 2**: Empower the Knower (Registry) to enforce Anti-Mayavad (Signatures).

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

## SAMUDRA MANTHAN: THE CHURNING OF THE OCEAN (REFINEMENT PLAN)

**Status:** IN PROGRESS (Waves 1-3 Complete)

The 10-Wave Plan to purify the architecture:

### Wave 1: Code Purification (Shuddhi) - [COMPLETE]
- **Goal**: Purify the Field (Ksetra) by enforcing GAD-000 compliance.
- **Action**: Modified all 5 Universal Protocols (`ReadWrite`, `Sync`, `Enforce`, `Infer`, `StoreRecall`) to include `SovereignContext` (The 37th Principle).
- **Result**: "Anti-Mayavad Clause" is now structurally enforced via Type Hints. No operation is valid without a Signature.

### Wave 2: Vajra Hardening (Tests) - [COMPLETE]
- **Goal**: Prove the Field can withstand stress.
- **Action**: Created `tests/samkhya/` vault. Implemented `test_vajra_protocols.py` to verify protocol signatures via introspection.
- **Result**: The "Vajra" tests confirm that the Protocols *contractually require* the Sovereign.

### Wave 3: The Bond (Registry) - [COMPLETE]
- **Goal**: Connect the Field to the Knower via the Registry.
- **Action**: Refactored `biorhythm.py` and `sync-ci` to use `ServiceRegistry.get(SyncProtocol)` instead of direct instantiation.
- **Result**: Components now access "The Sync Capability" (Abstract), not "The CISyncService" (Concrete). This allows NAGA Floods to intercede transparently.

### Wave 4: Akashic Config (ReadWrite) - [PENDING]
- **Goal**: Unify configuration under `ReadWriteProtocol`.
- **Plan**: Migrate `CityConfig` usage to `config.read("city")`.

### Wave 5: Harmonic Sync (Sync) - [PENDING]
- **Goal**: Standardize all synchronization under `SyncProtocol`.
- **Plan**: Ensure `GitSync`, `LedgerSync`, and `StateSync` all speak the same language.

... (Waves 6-10 continue as planned)

---

**SIGNED**:
- **Architect**: Lord Kapila (Samkhya)
- **Refinement**: Samudra Manthan Team
- **Date**: 2026-01-07
- **Status**: WAVE 3 COMPLETE
