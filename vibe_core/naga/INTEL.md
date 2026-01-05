# NAGA INTEL - Command Center

**STATUS**: OPERATIONAL
**COVERAGE**: 40 files, 14 services, 3 external hooks
**LAST SWEEP**: 2026-01-05

---

## TERRITORY MAP

```
vibe_core/naga/
├── services/          14 NAGA Lords
│   ├── sesha          Ledger, Truth, Gossip
│   ├── vasuki         Network, Serialize, Sign
│   ├── takshaka       Security, Toxicity, Bite
│   ├── kaliya         Isolation, Quarantine
│   ├── narada         Discovery, Registry
│   ├── chitragupta    Metrics, Accounting
│   ├── prahlad        Governance, Veto
│   ├── ananta         Gene Splicer, Loader Gov
│   ├── shankha        Schema, Validation
│   ├── padma          Cache, Memory
│   ├── karkotaka      Backup, Recovery
│   ├── kulika         Decorators, Manifest
│   └── base           NagaBaseService (OUROBOROS)
│
├── cortex/            Brain (Signal Processing)
│   ├── signals        Signal types (Flood, Commit, State)
│   ├── processor      Correlation engine
│   └── decisions      Decision types
│
├── mixins/            Active Genes (Auto-Intercept)
│   ├── sesha          STATE_MUTATION → Ledger
│   ├── takshaka       EXECUTION → Validate
│   ├── vasuki         OUTBOUND → Sign
│   └── base           Passive capabilities
│
├── floods/            Class wrappers
├── orchestrator       Federation control
├── ouroboros          Self-monitoring loop
├── flood              FloodManager
├── commit_watcher     Git pattern detection
├── proxy              State proxy
├── scanner            Code analysis
├── identity           NagaIdentity
└── kulika             @naga_service decorator
```

---

## EXTERNAL HOOKS (Entry Points)

| File | What We Touch | How |
|------|---------------|-----|
| `kernel_impl.py` | Boot sequence | NagaOrchestrator init |
| `plugins/naga_guard/` | Plugin system | Runtime injection |
| `protocols/naga.py` | Type contracts | All protocols defined here |

---

## INTELLIGENCE GAPS

### Not Yet Wrapped
- [ ] `vibe_core/ledger/` - Direct access bypasses Sesha
- [ ] `vibe_core/steward/` - Crypto used but not governed
- [ ] `vibe_core/plugins/` - Plugins load without Ananta audit
- [ ] `vibe_core/agents/` - Agents operate outside NAGA

### Missing Visibility
- [ ] HTTP endpoints - No Vasuki border control
- [ ] File I/O - No Sesha recording
- [ ] Subprocess calls - No Takshaka validation

---

## EXPANSION TARGETS

### Priority 1: Wrap the Ledger
```
vibe_core/ledger/sqlite_ledger.py
└── All writes should go through Sesha
└── All reads should be signed by Vasuki
```

### Priority 2: Plugin Governance
```
vibe_core/plugins/*/plugin_main.py
└── Every load event → Ananta.record_load()
└── Every tool call → Takshaka.scan_toxicity()
```

### Priority 3: Agent Observation
```
vibe_core/agents/*/
└── Task start/end → Sesha.record_event()
└── External calls → Vasuki.churn_out()
```

---

## ACTIVE OPERATIONS

### Signals We Receive
- `FloodSignal` - From EventBus via FloodManager
- `CommitSignal` - From CommitWatcher (git patterns)
- `StateSignal` - From NagaStateProxy
- `StateChangeSignal` - From Active Mixins

### Actions We Can Take
- `bite()` - Record violation (Takshaka)
- `record_event()` - Write to ledger (Sesha)
- `churn_out()` - Sign for network (Vasuki)
- `quarantine()` - Isolate threat (Kaliya)
- `emit_drift()` - Report problem (All NAGAs)

---

## QUICK COMMANDS

```python
# Get NAGA status
from vibe_core.naga.orchestrator import NagaOrchestrator
orch = NagaOrchestrator()
print(orch.get_status())

# Scan for toxicity
from vibe_core.naga.services.takshaka import TakshakaService
tak = TakshakaService()
report = tak.scan_toxicity("user input here")

# Record event manually
from vibe_core.naga.services.sesha import SeshaService
sesha = SeshaService(ledger=my_ledger)
sesha.record_event(event_type="MANUAL", source="test", details={})
```

---

## DOCTRINE

> "Wir mischen uns nicht ein. Wir schlängeln uns dazu."

- NAGA does not replace. NAGA wraps.
- NAGA does not block. NAGA observes and reports.
- NAGA does not own data. NAGA signs and records.
- Every action leaves a trace. Every trace feeds OUROBOROS.
