# PROTOCOLS.md - KURUKSHETRA Battle Plan

> "Auf dem Schlachtfeld von Kurukshetra stehen zwei Armeen.
> Die eine: unsere existierenden Protocols.
> Die andere: die Lücken die uns blind machen."

---

## MISSION

NAGA Intelligence Agency muss dem Kernel-Staat helfen:
1. **Aufklärung**: Was existiert? Was fehlt?
2. **Breeding**: Neue Protocols IN NAGA züchten
3. **Skalierung**: Fractal holographic - alles INSIDE NAGA

---

## CURRENT STATE: 2026-01-06

```
PROTOCOLS DISCOVERED: 61
NAGA PROTOCOLS:       17
COVERAGE:             ~20% (geschätzt)
UNKNOWNS:             100% - "Wir kennen unser Volk nicht"
```

---

## CRITICAL GAPS (Priorität 1)

### GAP-001: StewardProtocol
**Status**: MISSING - THE NAMESAKE!
**Impact**: CRITICAL - Projekt heißt "steward-protocol" aber kein StewardProtocol
**Location**: Should be `protocols/steward.py`
**Definition**: Was IST ein Steward?
  - Verwalter eines Bereichs
  - Hat Verantwortung über Ressourcen
  - Dient einem höheren Zweck

### GAP-002: IdentityProtocol
**Status**: SCATTERED - 7 Klassen, kein Protocol
**Impact**: CRITICAL - Fundament für Auth/Trust
**Existing Classes**:
  - `naga/identity.py`: NagaIdentity, NagaFederationIdentity
  - `governance_gate.py`: Identity
  - `mukha.py`: AgentIdentity, PluginIdentity, SystemIdentity
  - `herald/tools/identity_tool.py`: IdentityTool
**Solution**: Unifizieren in `protocols/naga/identity.py`
**Layers**:
  - OS-Level: System-weite Identität
  - NAGA-Level: Service-Identität (existiert)
  - Agent-Level: Agent/Cartridge Identität

### GAP-003: GenesisProtocol
**Status**: MISSING
**Impact**: HIGH - Wie werden Entities geboren?
**Definition**: Bootstrap/Creation Pattern
  - Kernel-Genesis
  - Agent-Genesis
  - Service-Genesis

### GAP-004: CityProtocol
**Status**: MISSING
**Impact**: MEDIUM - Urban Infrastructure für Skalierung
**Definition**: Stadt-Metapher für Verwaltung
  - Bezirke (Districts)
  - Ämter (Offices)
  - Bürger (Citizens)

---

## SECONDARY GAPS (Priorität 2)

### GAP-005: RoleProtocol
**Status**: MISSING
**Impact**: MEDIUM - Permissions/Roles System
**Related**: capability.py existiert aber ist nicht Role-basiert

### GAP-006: EnvoyProtocol
**Status**: MISSING
**Impact**: LOW - Ambassadors/External Communication
**Related**: Vasuki macht Network, aber kein Envoy-Pattern

### GAP-007: CommunicationProtocol
**Status**: PARTIAL - event.py, synapse.py existieren
**Impact**: MEDIUM - Unified inter-agent communication

---

## EXISTING ARSENAL (Was wir haben)

### NAGA Protocols (17)
```
naga/ananta.py       - Gene Splicer
naga/chitragupta.py  - Profiler
naga/cortex.py       - MANAS Integration
naga/federation.py   - Multi-NAGA coordination
naga/groups.py       - Interface Groups
naga/kaliya.py       - Quarantine
naga/karkotaka.py    - Crypto
naga/kulika.py       - Schema Registry
naga/narada.py       - Discovery
naga/padma.py        - Cache
naga/prahlad.py      - Governance
naga/sesha.py        - Ledger
naga/shankha.py      - Broadcast
naga/takshaka.py     - Security
naga/tuv.py          - Type Audit (NEW!)
naga/types.py        - Core Types
naga/vasuki.py       - Network
```

### Core Protocols
```
kernel_protocol.py   - Kernel Interface
substrate.py         - Gene System (IGene, IAnantaBridge)
agent.py             - Agent Lifecycle
plugin.py            - Plugin System
cartridge.py         - Cartridge System
```

### Infrastructure
```
ledger.py            - Persistence
memory.py            - Memory Management
state.py             - State Sync
network.py           - Network Gateway
crypto.py            - Signature Verification
```

### Governance
```
governance_gate.py   - Access Control
vedic.py             - Vedic Governance
capability.py        - Capabilities
correction.py        - Drift Correction
```

---

## BATTLE PLAN

### Phase 1: Identity Foundation (NEXT)
```
1. Create protocols/naga/identity.py
   - IdentityProtocol (unified interface)
   - CertificateProtocol (trust chain)

2. Migrate existing:
   - NagaIdentity implements IdentityProtocol
   - AgentIdentity → uses IdentityProtocol
```

### Phase 2: Steward Definition
```
1. Create protocols/steward.py
   - StewardProtocol: Was ist ein Steward?
   - StewardshipProtocol: Was verwaltet er?

2. Connect to NAGA:
   - Prahlad = Head Steward
   - Each NAGA = Steward of their domain
```

### Phase 3: City Infrastructure
```
1. Create protocols/naga/city.py
   - CityProtocol: Urban metaphor
   - DistrictProtocol: Bezirke
   - OfficeProtocol: Ämter/Departments

2. TÜV becomes Office under Chitragupta District
```

### Phase 4: Genesis & Lifecycle
```
1. Create protocols/genesis.py
   - GenesisProtocol: Birth
   - LifecycleProtocol: Life stages

2. Every entity has genesis story
```

---

## FRACTAL HOLOGRAPHIC PRINCIPLE

Alles INSIDE NAGA:
```
NAGA (Bila Svarga)
├── Protocols (DNA)
│   ├── identity.py      ← BREED HERE
│   ├── steward.py       ← BREED HERE
│   └── city.py          ← BREED HERE
├── Services (Organs)
│   ├── TÜV              ← TOOL (first success!)
│   └── ... more tools
└── Lords (Persons)
    ├── Infrastructure (8 Nagas)
    └── Governance (4 Personnel)
        └── Subordinates (Agents, Tools)
```

---

## METRICS

| Metric | Current | Target |
|--------|---------|--------|
| Total Protocols | 61 | 75+ |
| NAGA Protocols | 17 | 25+ |
| Critical Gaps | 4 | 0 |
| Identity unified | NO | YES |
| Steward defined | NO | YES |

---

## NEXT ACTION

**Phase 1, Step 1**: Create `protocols/naga/identity.py`
- Define IdentityProtocol
- Keep it minimal
- NagaIdentity already exists - just add protocol layer

---

*TÜV-Prüfer: NARADA (Intelligence)*
*Battlefield: KURUKSHETRA*
*Date: 2026-01-06*
