# UNION.md - State of the Universal Protocols

> "Ekam Sat Vipra Bahudha Vadanti" - Truth is One, the wise call it by many names.

---

## The Hierarchy

```
Layer -1: SUBSTRATE (substrate.py)
    └── IGeneHost, MantraOpCode, MAHAMANTRA_SEQUENCE
           │
Layer 1:  UNIVERSAL PROTOCOLS
           │
    ┌──────┴──────────────────────────────────────────────┐
    │                    OM PROTOCOL                       │
    │   (The Complete Holon - Implements ALL 8 below)      │
    └──────────────────────────────────────────────────────┘
           │
    ┌──────┼──────┬──────┬──────┬──────┬──────┬──────┐
    │      │      │      │      │      │      │      │
  Krishna Rama  Mantra Infer Enforce RW    SR   Sync
   WHO   WHAT   WHEN   WHY    HOW   WHERE WHENCE WHITHER
```

---

## Protocol Summary

| Protocol | File | Purpose | Key Methods |
|----------|------|---------|-------------|
| **OmProtocol** | om.py | UNIFIES ALL | (inherits all) |
| **KrishnaProtocol** | krishna.py | Identity + Genes | `sovereign_context`, `bind_genes()` |
| **RamaProtocol** | rama.py | Action/Work | `perform_dharma()` async |
| **MantraProtocol** | mantra.py | Time/Clock | `chant_mahamantra()`, `surrender()` |
| **InferProtocol** | infer.py | Thought/Cognition | `infer()`, `classify()`, `evaluate()` |
| **EnforceProtocol** | enforce.py | Law/Policy | `enforce()`, `check()`, `get_rules()` |
| **ReadWriteProtocol** | read_write.py | State/Config | `read()`, `write()`, `exists()` |
| **StoreRecallProtocol** | store_recall.py | Memory | `store()`, `recall()`, `forget()` |
| **SyncProtocol** | sync.py | Synchronization | `sync()`, `is_synced()` |
| **UnionProtocol** | union.py | Entity Report | `get_living_entities()` |

---

## Type Definitions (types.py)

| Type | Purpose |
|------|---------|
| `SovereignContext` | 37th Principle Identity (WHO) |
| `AlignmentScore` | Drift measurement (0.0 - 1.0) |
| `Resonance` | Heartbeat signal |
| `DriftContext` | Drift state snapshot |
| `ReadResult` | Read envelope with provenance |
| `SyncResult` / `SyncStatus` | Sync state |
| `Verdict` | ALLOW/DENY/ESCALATE/AUDIT |
| `EnforceContext` / `Rule` | Policy context |
| `Inference` / `Classification` | Cognition outputs |
| `MemoryValue` | Memory envelope |

---

## The 8 W's Mapping

```
WHO     → KrishnaProtocol (sovereign_context)
WHAT    → RamaProtocol (perform_dharma)
WHEN    → MantraProtocol (chant_mahamantra)
WHY     → InferProtocol (infer, classify)
HOW     → EnforceProtocol (enforce, check)
WHERE   → ReadWriteProtocol (read, write)
WHENCE  → StoreRecallProtocol (store, recall)
WHITHER → SyncProtocol (sync, is_synced)
```

---

## Flows

### 1. Identity Flow (Pratyabhijna)
```
SovereignContext → KrishnaProtocol.bind_genes() → IGeneHost
```

### 2. Work Flow (Karma)
```
SovereignContext → RamaProtocol.perform_dharma() → DharmaResult
```

### 3. Clock Flow (Kala)
```
MantraOpCode → MantraProtocol.chant_mahamantra() → AlignmentScore
```

### 4. Decision Flow (Buddhi)
```
InferenceInput → InferProtocol.infer() → Inference
```

### 5. Policy Flow (Dharma)
```
EnforceContext → EnforceProtocol.enforce() → Verdict
```

---

## Dependencies

```
substrate.py (Layer -1)
    ↑
    │ imports: IGeneHost, MantraOpCode, MAHAMANTRA_SEQUENCE
    │
krishna.py, mantra.py
    ↑
    │ composes into
    │
om.py (UNIFIES ALL)
```

---

## Errors Found

**NONE** - All files import correctly. Clean architecture.

---

## Who Manages What

| Manager | Responsibility |
|---------|----------------|
| `substrate.py` | Foundation DNA (MantraOpCode, IGeneHost) |
| `types.py` | All TypedDefs + Dataclasses |
| `om.py` | Unification of all protocols |
| `__init__.py` | Export surface |

---

*Last updated: 2026-01-08 00:55*
