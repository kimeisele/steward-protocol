# PROTOCOL AUDIT - 2026-01-12

## EXECUTIVE SUMMARY

| Metric | Count | Status |
|--------|-------|--------|
| Total Protocols Found | ~100+ | |
| Protocols using `Any` | 40+ | NOT WATERTIGHT |
| Types files with vibe_core imports | 6 | CIRCULAR RISK |
| Mahajanas with impure types | 5/10 | NEEDS FIX |

**Verdict: System has SIGNIFICANT entropy. Protocol-first refactor required.**

---

## 1. CIRCULAR DEPENDENCY MAP

### 1.1 Critical Import Chains (CIRCULAR)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CIRCULAR DEPENDENCY HELL                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  brahma/types/capability_registry.py                            │
│       │                                                          │
│       └── from vibe_core.kernel import VibeLedger               │
│                    │                                             │
│                    └── kernel imports from protocols             │
│                              │                                   │
│                              └── protocols imports from mahajanas│
│                                        │                         │
│                                        └── mahajanas imports...  │
│                                                   LOOP!          │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  vyasa/types/ledger.py                                          │
│       │                                                          │
│       └── from vibe_core.kernel import VibeLedger               │
│                    │                                             │
│                    └── SAME LOOP                                │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  brahma/types/agent_interface.py                                │
│       │                                                          │
│       └── from vibe_core.protocols.event import Event           │
│                    │                                             │
│                    └── event imports from ???                   │
│                              POTENTIAL LOOP                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Impure Types Files (vibe_core imports)

| File | Import | Circular Risk |
|------|--------|---------------|
| `brahma/types/capability_registry.py` | `vibe_core.kernel.VibeLedger` | HIGH |
| `brahma/types/capability_registry.py` | `vibe_core.protocols.capability.CapabilityModifyResult` | MEDIUM |
| `brahma/types/identity.py` | `vibe_core.protocols.VibeAgent` | MEDIUM |
| `brahma/types/agent_interface.py` | `vibe_core.protocols.event.Event` | MEDIUM |
| `bali/types/resource_manager.py` | `vibe_core.protocols.resource.ResourceQuota` | MEDIUM |
| `parashurama/types/file_operator.py` | `vibe_core.protocols.operator_protocol` | HIGH |
| `vyasa/types/ledger.py` | `vibe_core.kernel.VibeLedger` | HIGH |

### 1.3 Pure Types Files (NO vibe_core imports)

| Mahajana | Status |
|----------|--------|
| kapila/types/ | PURE (only internal imports) |
| manu/types/ | PURE |
| janaka/types/ | PURE (needs verification) |
| narada/types/ | PURE |
| prithu/types/ | PURE |
| nrisimha/types/ | PURE |

---

## 2. WATERTIGHT COMPLIANCE

### 2.1 Protocols Using `Any` (NOT WATERTIGHT)

**vibe_core/protocols/state.py:**
```python
def save(self, filename: str, data: Any, ...) -> Any:  # NOT WATERTIGHT
def load(self, filename: str, default: Any = None) -> Any:  # NOT WATERTIGHT
```

**vibe_core/protocols/auditor.py:**
```python
def verify_ledger(self, events: List[Dict[str, Any]]) -> Any:  # NOT WATERTIGHT
def register_rule(self, rule: Any) -> None:  # NOT WATERTIGHT
```

**vibe_core/protocols/naga/base.py:**
```python
def serve(self, request: Any) -> Any:  # NOT WATERTIGHT
def bind(self, host: Any, ...) -> Any:  # NOT WATERTIGHT
```

**vibe_core/protocols/naga/prahlad.py:**
```python
def remember(self, key: str, value: Any, ...) -> bool:  # NOT WATERTIGHT
def recall(self, key: str, ...) -> Optional[Any]:  # NOT WATERTIGHT
```

**vibe_core/protocols/agent.py:**
```python
data: Optional[Dict[str, Any]] = None  # NOT WATERTIGHT
def process(self, task: Task) -> Dict[str, Any]:  # NOT WATERTIGHT
```

### 2.2 Protocols That ARE WATERTIGHT

**vibe_core/protocols/substrate/__init__.py:**
- Uses TypedDicts throughout
- Explicit comment: "No Dict[str, Any]"

**vibe_core/protocols/mahajanas/*/:**
- Most mahajana protocols use TypedDicts
- Explicit WATERTIGHT comments

**vibe_core/protocols/governance/bridge.py:**
- Comment: "WATERTIGHT: No Dict[str, Any] - all typed"

---

## 3. PROTOCOL OWNERSHIP

### 3.1 Mahajana Protocol Distribution

| Position | Mahajana | Protocols Owned |
|----------|----------|-----------------|
| 0 | PRITHU | WakeProtocol, BootProtocol |
| 1 | BRAHMA | GenesisProtocol, DIProtocol, BootstrapProtocol |
| 2 | NARADA | EventBusProtocol, BroadcastProtocol |
| 3 | KAPILA | CognitiveProtocol, SamkhyaProtocol |
| 4 | VYASA | TruthProtocol, LineageProtocol |
| 5 | MANU | DharmaProtocol, VarnashramaProtocol |
| 6 | KAPILA | AnalysisProtocol (duplicate?) |
| 7 | NARADA | (duplicate position) |
| 8 | PARASHURAMA | FetchProtocol, IOProtocol |
| 9 | JANAKA | ExecutionProtocol, CycleProtocol, SchedulerProtocol |
| 10 | BALI | SurrenderProtocol, ShutdownProtocol, YieldProtocol |
| 11 | YAMARAJA | JudgmentProtocol |
| 12 | NRISIMHA | CacheProtocol, SecurityProtocol |
| 13 | KUMARAS | WisdomProtocol |
| 14 | BHISHMA | GuardProtocol |
| 15 | PRAHLAD | DevotionProtocol |

### 3.2 Orphan Protocols (No Clear Owner)

| Protocol | Current Location | Suggested Owner |
|----------|------------------|-----------------|
| StateServiceProtocol | protocols/state.py | NRISIMHA (cache) |
| AuditorProtocol | protocols/auditor.py | VYASA (truth) |
| PluginServiceProtocol | protocols/plugin.py | BRAHMA (genesis) |
| SchedulerProtocol | protocols/scheduler.py | JANAKA (execution) |
| ProcessSupervisorProtocol | protocols/process.py | PRITHU (system) |
| NetworkGatewayProtocol | protocols/network.py | PARASHURAMA (fetch) |
| LineageProtocol | protocols/lineage.py | VYASA (records) |
| IntegrityCheckProtocol | protocols/integrity.py | YAMARAJA (judgment) |

---

## 4. ACTION ITEMS

### 4.1 Immediate (Phase 1)

1. **PURIFY brahma/types/capability_registry.py**
   - Remove: `from vibe_core.kernel import VibeLedger`
   - Add: `class LedgerProtocol(Protocol): ...`

2. **PURIFY brahma/types/agent_interface.py**
   - Remove: `from vibe_core.protocols.event import Event`
   - Add: `class EventProtocol(Protocol): ...`

3. **PURIFY vyasa/types/ledger.py**
   - Remove: `from vibe_core.kernel import VibeLedger`
   - Define local protocol

4. **PURIFY bali/types/resource_manager.py**
   - Remove: `from vibe_core.protocols.resource import ResourceQuota`
   - Define local protocol

5. **PURIFY parashurama/types/file_operator.py**
   - Remove: `from vibe_core.protocols.operator_protocol import ...`
   - Define local protocols

### 4.2 Medium Term (Phase 2)

1. Replace `Any` with TypedDicts in:
   - protocols/state.py
   - protocols/auditor.py
   - protocols/agent.py
   - protocols/naga/base.py
   - protocols/naga/prahlad.py
   - protocols/naga/sesha.py

2. Move orphan protocols to mahajana ownership

### 4.3 Long Term (Phase 3-4)

1. Implement Autobahn (auto __init__.py)
2. Implement TÜV (runtime validation)
3. Migrate ALL imports to mahamantra pattern

---

## 5. DEPENDENCY GRAPH

```
                         MAHAMANTRA
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼─────┐        ┌────▼────┐
   │ PRITHU  │         │  BRAHMA   │        │ KAPILA  │
   │(system) │         │ (genesis) │        │(analysis)│
   └────┬────┘         └─────┬─────┘        └────┬────┘
        │                    │                    │
        │              ┌─────┴─────┐              │
        │              │           │              │
        │         ┌────▼───┐ ┌────▼────┐         │
        │         │NARADA  │ │ VYASA   │         │
        │         │(events)│ │(records)│         │
        │         └────┬───┘ └────┬────┘         │
        │              │          │              │
        └──────────────┼──────────┼──────────────┘
                       │          │
                  ┌────▼──────────▼────┐
                  │                    │
             ┌────▼────┐          ┌────▼────┐
             │  MANU   │          │PARASHU- │
             │(dharma) │          │ RAMA    │
             └────┬────┘          └────┬────┘
                  │                    │
             ┌────▼────┐          ┌────▼────┐
             │ JANAKA  │          │  BALI   │
             │ (karma) │          │(yield)  │
             └────┬────┘          └────┬────┘
                  │                    │
             ┌────▼────┐          ┌────▼────┐
             │YAMARAJA │          │NRISIMHA │
             │(justice)│          │(protect)│
             └─────────┘          └─────────┘
```

---

## 6. METRICS TARGET

| Metric | Current | Target |
|--------|---------|--------|
| Types files with vibe_core imports | 6 | 0 |
| Protocols using Any | 40+ | 0 |
| Orphan protocols | 8+ | 0 |
| Test coverage for protocols | ? | 100% |
| WATERTIGHT certification | 0% | 100% |

---

## CONCLUSION

The codebase has significant protocol entropy. The circular dependency problem is STRUCTURAL - moving files around won't fix it.

**The only solution is Protocol-First:**
1. Make ALL types files PURE (no vibe_core imports)
2. Make ALL protocols WATERTIGHT (no Any)
3. Route EVERYTHING through Mahamantra

This requires discipline and patience. No shortcuts.

Hare Krishna.
