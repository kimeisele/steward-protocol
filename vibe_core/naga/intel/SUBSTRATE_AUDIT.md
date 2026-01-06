# SUBSTRATE AUDIT - Level -1 Entwirrung

> "Ananta ist EINER - zwei Köpfe sind Mayavada!"

## Status: ARCHITECTURE BREACH DETECTED

---

## I. DAS PROBLEM: ZWEI WAHRHEITSQUELLEN

### AnantaShesha (ouroboros/ananta_shesha.py)
```
Layer: -1 (System Bridge)
Type: SINGLETON via get_system_anchor()
Implements: IGeneHost

Storage:
- _genes: Dict[str, IGene]
- _gene_statuses: Dict[str, GeneStatus]
- _capability_providers: Dict[str, str]
- _event_listeners: Dict[str, List[str]]
- _event_handlers: Dict[str, List[Callable]]

Methods:
- get_gene(name) → Gene lookup
- has_gene(name) → Gene check
- get_capability(cap) → Capability lookup
- emit_event(type, data) → SHANKHA broadcast
- register_gene(gene) → Gene registration
- subscribe(event_type, gene_name) → Event subscription
```

### AnantaService (naga/services/ananta.py)
```
Layer: 0 (NAGA Service)
Type: NagaBaseService (instantiated per Orchestrator)
Implements: AnantaProtocol (Splicer) + IGeneHost??? (BREACH!)

Storage (DUPLICATE!):
- _genes: Dict[str, IGene]           ← SAME AS SHESHA!
- _gene_statuses: Dict[str, GeneStatus] ← SAME AS SHESHA!
- _capability_providers: Dict[str, str]  ← SAME AS SHESHA!
- _event_listeners: Dict[str, List[str]] ← SAME AS SHESHA!

Splicer Storage (UNIQUE - OK):
- _available_mixins: Dict[str, Type]
- _flood_history: List[VetoDecision]
```

---

## II. WARUM IST DAS SCHLECHT?

### Scenario A: Gene Registration
```python
# CURRENT (BROKEN)
ananta_service.register_gene(my_gene)  # Stored in AnantaService._genes
anchor = get_system_anchor()
anchor.get_gene("my_gene")  # NOT FOUND! Different _genes dict!
```

### Scenario B: Capability Lookup
```python
# CURRENT (BROKEN)
# Gene registered in AnantaShesha
anchor.get_capability("ledger")  # Works

# But if someone uses AnantaService directly:
ananta_service.get_capability("ledger")  # NOT FOUND! Different dict!
```

### Scenario C: Event Routing
```python
# System Ouroboros emits via AnantaShesha
anchor.emit_event("violation.detected", data)  # Goes to AnantaShesha listeners

# NAGA binds via AnantaService (wrong!)
ananta_service.subscribe("violation.detected", naga_name)  # Wrong listener dict!
# → NAGA never receives event!
```

---

## III. DIE LÖSUNG: 1 ENTRY POINT

### Architektur SOLL:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer -2: Prakriti (State Store)                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer -1: AnantaShesha (SINGLETON - THE Substrate)         │
│            - Gene Registry (ONE truth)                       │
│            - Event Routing (SHANKHA)                         │
│            - Capability Lookup                               │
│            get_system_anchor() → THE ENTRY POINT             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 0: AnantaService (Gene SPLICER - NOT Host)           │
│           - Uses get_system_anchor() for hosting            │
│           - Keeps _available_mixins (Mixin registry)        │
│           - Keeps _flood_history (Splice audit)             │
│           - REMOVES _genes, _gene_statuses etc.             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: NAGA Services (Sesha, Takshaka, Vasuki, etc.)     │
│           - Bind to AnantaShesha (via get_system_anchor())  │
│           - NOT to AnantaService                             │
└─────────────────────────────────────────────────────────────┘
```

### Code Fix:

```python
# AnantaService __init__ SOLL:
class AnantaService(NagaBaseService, AnantaProtocol):  # NOT IGeneHost!
    def __init__(self, ledger=None):
        super().__init__(service_name="Ananta")

        # Get the REAL substrate (1 ENTRY POINT)
        from vibe_core.ouroboros.ananta_shesha import get_system_anchor
        self._substrate = get_system_anchor()

        # Splicer state ONLY
        self._available_mixins: Dict[str, Type] = {}
        self._flood_history: List[VetoDecision] = []

        # NO MORE:
        # self._genes = {}           ← DELETE
        # self._gene_statuses = {}   ← DELETE
        # self._capability_providers = {} ← DELETE
        # self._event_listeners = {} ← DELETE

    # IGeneHost methods DELEGATE to substrate
    def get_gene(self, name: str) -> Optional[IGene]:
        return self._substrate.get_gene(name)

    def has_gene(self, name: str) -> bool:
        return self._substrate.has_gene(name)

    def get_capability(self, cap: str) -> Optional[object]:
        return self._substrate.get_capability(cap)

    def emit_event(self, event_type: str, data: SubstrateEventData) -> None:
        self._substrate.emit_event(event_type, data)

    def register_gene(self, gene: IGene) -> bool:
        return self._substrate.register_gene(gene)
```

---

## IV. DEPENDENCY GRAPH

### CURRENT (BROKEN):
```
NagaOrchestrator
    └── creates AnantaService (has _genes)
    └── creates NAGAs
        └── NAGAs bind to... AnantaService? AnantaShesha? UNCLEAR!

System Ouroboros
    └── uses get_system_anchor() → AnantaShesha (has different _genes)
    └── emits events → AnantaShesha listeners only
    └── NAGAs not subscribed! (wrong host)
```

### TARGET (FIXED):
```
NagaOrchestrator
    └── creates AnantaService (splicer only, no _genes)
    └── AnantaService uses get_system_anchor() → AnantaShesha
    └── creates NAGAs
        └── NAGAs bind to AnantaShesha (THE substrate)
        └── NAGAs subscribe to AnantaShesha events

System Ouroboros
    └── uses get_system_anchor() → AnantaShesha (SAME instance!)
    └── emits events → All listeners (including NAGAs)
```

---

## V. FILES TO MODIFY

| File | Action |
|------|--------|
| `naga/services/ananta.py` | Remove _genes etc., delegate to substrate |
| `naga/orchestrator.py` | Ensure NAGAs bind to substrate |
| `protocols/naga/ananta.py` | Remove IGeneHost from AnantaProtocol? |

---

## VI. MAYAVADA PRINCIPLE

**MAYAVADA** (Impersonalism): "Everything is one undifferentiated mass"
→ Two hosts storing the same data = confusion about identity

**VAISHNAVA** (Personalism): "One Supreme, personal relationship"
→ ONE substrate (AnantaShesha), clear delegation chain

**1 ENTRY POINT = 1 TRUTH = 1 PERSONALITY (Ananta)**
