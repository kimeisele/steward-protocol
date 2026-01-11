# THE 12 MAHAJANAS - Protocol Governance

```
svayambhūr nāradaḥ śambhuḥ kumāraḥ kapilo manuḥ
prahlādo janako bhīṣmo balir vaiyāsakir vayam

"Brahma, Narada, Shambhu, the Kumaras, Kapila, Manu,
Prahlada, Janaka, Bhishma, Bali, Shuka, and Yamaraja."
                                        — SB 6.3.20
```

## THE ANTI-MAYAVAD PRINCIPLE

Every protocol MUST have a PERSONAL owner. Not "universal", not "abstract" — PERSONAL.

**MAYAVAD (Dead):** `protocols/universal/dharma.py` — Who owns it? Nobody. It drifts.

**VAISHNAVA (Alive):** `protocols/mahajanas/manu/dharma.py` — Manu owns Dharma. Clear lineage.

## FOLDER = WIRING

When a protocol file is PHYSICALLY inside a Mahajana folder:
- It is automatically OWNED by that Mahajana
- It is automatically CONNECTED to the Parampara
- It is automatically TRACEABLE to source (Krishna → Brahma → ... → Prabhupada)

**NO MANUAL WIRING NEEDED. THE FOLDER STRUCTURE IS THE WIRING.**

## THE 12 MAHAJANAS & THEIR DOMAINS

```
┌─────────────────────────────────────────────────────────────────┐
│  QUARTER 1: GENESIS (HARE KRISHNA HARE KRISHNA)                │
├─────────────────────────────────────────────────────────────────┤
│  BRAHMA     │ Creation, Boot, DI, Loaders, Manifestation       │
│  NARADA     │ Communication, Events, Synapse, Messaging        │
│  SHAMBHU    │ Destruction, Cleanup, Garbage Collection         │
├─────────────────────────────────────────────────────────────────┤
│  QUARTER 2: DHARMA (KRISHNA KRISHNA HARE HARE)                 │
├─────────────────────────────────────────────────────────────────┤
│  KUMARAS    │ Knowledge, Memory, Cognition, Purity             │
│  KAPILA     │ Analysis, Samkhya, Reactor, Metrics              │
│  MANU       │ Law, Governance, GAD-000, Rules                  │
├─────────────────────────────────────────────────────────────────┤
│  QUARTER 3: KARMA (HARE RAMA HARE RAMA)                        │
├─────────────────────────────────────────────────────────────────┤
│  PRAHLADA   │ Resilience, Plugins, Cartridges, Devotion        │
│  JANAKA     │ Duty, Kernel, State, Task, Process               │
│  BHISHMA    │ Vow, Ledger, Commitment, Immutability            │
├─────────────────────────────────────────────────────────────────┤
│  QUARTER 4: MOKSHA (RAMA RAMA HARE HARE)                       │
├─────────────────────────────────────────────────────────────────┤
│  BALI       │ Surrender, Resources, Economy, Allocation        │
│  SHUKA      │ Vision, CLI, LLM, Narration, Output              │
│  YAMARAJA   │ Judgment, Security, NAGA, Audit, Death           │
└─────────────────────────────────────────────────────────────────┘
```

## OWNED PROTOCOL PATTERN

Every protocol inherits from `OwnedProtocol`:

```python
from vibe_core.protocols.mahajanas.owned_protocol import OwnedProtocol
from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

class ServiceRegistryProtocol(OwnedProtocol):
    """DI Container - Creates and registers services."""

    OWNER = Mahajana.BRAHMA          # Brahma creates
    OPCODES = [MantraOpCode.ALLOC_MEM, MantraOpCode.LOAD_ROOT]
    PROTOCOL_NAME = "service_registry"
    DESCRIPTION = "Dependency Injection container"

    def get_state(self) -> ProtocolState:
        return {
            "protocol_name": self.PROTOCOL_NAME,
            "owner": self.OWNER.value,
            "is_chanting": self.is_chanting,
            # ... WATERTIGHT - no Any!
        }
```

## THE CHANTING REQUIREMENT

Every protocol MUST chant:

```python
# In your protocol's tick/heartbeat:
def tick(self):
    self.chant()  # Links to Mahamantra
```

**THE AJAMIL EXCEPTION:** Even if a protocol fails GAD-000 tests, if it chants the Holy Name, it receives MERCY. In Kali Yuga, this is the ONLY way.

## MIGRATION CHECKLIST

When migrating a wild protocol:

1. **Identify Owner:** Which Mahajana should own this?
2. **Create File:** `protocols/mahajanas/{mahajana}/{protocol}.py`
3. **Inherit:** `class XxxProtocol(OwnedProtocol):`
4. **Set Constants:** OWNER, OPCODES, PROTOCOL_NAME, DESCRIPTION
5. **Implement:** `get_state()` → WATERTIGHT (no Any!)
6. **Chant:** Call `self.chant()` in heartbeat/tick
7. **Register:** Import in `{mahajana}/__init__.py`

## CURRENT STATUS

```
protocols/mahajanas/
├── brahma/          # Creation
│   └── __init__.py
│   └── di.py        # ← ServiceRegistry (MIGRATING)
├── narada/          # Communication
│   └── __init__.py
│   └── events.py    # ← EventBus (TODO)
├── shambhu/         # Destruction
├── kumaras/         # Knowledge
├── kapila/          # Analysis
├── manu/            # Law
├── prahlada/        # Resilience
├── janaka/          # Duty
│   └── kernel.py    # ← Kernel protocols (TODO)
├── bhishma/         # Vow
├── bali/            # Surrender
├── shuka/           # Vision
│   └── naga.py      # ← Already exists
└── yamaraja/        # Judgment
    └── security.py  # ← Already exists
```

## THE LOTUS PROTOCOL (FUTURE)

The `LotusProtocol` will provide:
- Auto-wrapper for legacy code
- NAGA protection injection
- Mahamantra heartbeat
- Holographic routing (any direction)

```python
# Future vision:
@lotus_protected
class LegacyService:
    # Automatically gets:
    # - OwnedProtocol base
    # - NAGA blessing
    # - Mahamantra chanting
    # - GAD-000 compliance checks
    pass
```

## PARAMPARA CONNECTION

```
Krishna (Source)
    ↓
Brahma (First Created, sits on Lotus from Vishnu's navel)
    ↓
Narada (Brahma's son, traveling preacher)
    ↓
Vyasadeva (Compiled Vedas)
    ↓
...
    ↓
Srila Prabhupada (Founder-Acarya, final link for us)
    ↓
This Protocol (connected via Mahajana ownership)
```

When a protocol has a Mahajana owner, it is AUTOMATICALLY connected to this chain.

## GAD-000 COMPLIANCE

Every owned protocol is automatically GAD-000 auditable:

```python
protocol = MyProtocol()
audit = protocol.audit()
print(audit.to_marker())  # "DSCRV:✓ OBSRV:✓ PARSE:✓ COMPS:✓ IDEMP:✓ RECVR:✓"
```

---

**"If it does not exist as protocol, it does not exist."**
**"If it has no owner, it is dead code."**
**"If it does not chant, it drifts into Maya."**
