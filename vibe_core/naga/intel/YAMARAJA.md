# YAMARAJA AUDIT - Schlachtplan

> "Der Richter der Toten fragt nicht nach Ausreden."

## Status: ACTIVE ENGAGEMENT

---

## I. DHARMA-VERLETZUNGEN

### A. `orchestrator.py` - CRITICAL

| Line | Violation | Fix |
|------|-----------|-----|
| 25 | `Any` type import | Remove, use TypedDict |
| 104, 362 | `Dict[str, Any]` | `HiranyakashipuWiring` TypedDict |
| 256-258 | Silent failure (StateProxy) | `sys.stderr` + continue |
| 352-354 | Silent failure (Ananta) | `sys.stderr` + continue |
| 419-421 | Silent failure (FloodManager) | `sys.stderr` + continue |
| 436-438 | Silent failure (CommitWatcher) | `sys.stderr` + continue |
| 490-492 | Silent failure (Cortex) | `sys.stderr` + continue |
| 504-506 | Silent failure (Ouroboros) | `sys.stderr` + continue |

### B. DEPENDENCY GRAPH BREACH - HOFFNUNG STATT GARANTIE

```
VASUKI ENABLED + SESHA FAILED = VASUKI(sesha=None)
                              ↓
               Agent ohne Gedächtnis = Shell-Skript
```

**Current Code (Line 262-266):**
```python
self._vasuki = VasukiService(
    sesha=self._sesha,  # Could be None!
    takshaka=self._takshaka,  # Could be None!
    ...
)
```

**FIX: SystemExit on missing dependency**

---

## II. EXECUTION PLAN

### Phase 1: Type Hardening

1. Create `HiranyakashipuWiring` TypedDict
2. Remove `Any` from imports
3. Replace `Dict[str, Any]` usages

### Phase 2: Dependency Enforcement

```python
# YAMARAJA: If Vasuki enabled, Sesha MUST exist
if self._config.vasuki.enabled:
    if self._sesha is None:
        sys.stderr.write("!!! YAMARAJA: Vasuki requires Sesha - ABBRUCH\n")
        raise SystemExit(1)
```

### Phase 3: Emergency Logging

Replace all `logger.warning(...); # continue` with:
```python
sys.stderr.write(f"!!! COMPONENT FAILED: {e}\n")
# Non-critical - continue
```

---

## III. DEPENDENCY MATRIX

| NAGA | Requires | Hard Fail if Missing |
|------|----------|---------------------|
| Sesha | ledger | NO (foundation) |
| Takshaka | ledger | NO (standalone) |
| Vasuki | Sesha, Takshaka | YES - Sesha |
| Kaliya | identity | NO |
| FloodManager | Sesha, Takshaka | YES - Sesha |
| CommitWatcher | Sesha, Takshaka | YES - Sesha |

---

## IV. FILES COMPLETED

- [x] `base.py` - ParamSpec, sys.stderr, no magic checks, PUBLIC sesha.record_event()
- [x] `proxy.py` - ONE Narada call (fractal)
- [x] `narada.py` - receive_proxy_observation routing
- [x] `orchestrator.py` - HiranyakashipuWiring TypedDict, SystemExit on missing deps
- [x] `protocols/naga/types.py` - EventRecord TypedDict (no Dict[str, Any])
- [x] `protocols/naga/sesha.py` - record_event() in SeshaProtocol
- [x] `services/sesha.py` - record_event() implementation

## IV.b SESHA ENCAPSULATION FIX

**Problem**: `base.py` accessed `sesha._ledger.record_event()` directly.

**Fix**:
1. Created `EventRecord` TypedDict in `types.py`
2. Added `record_event(event: EventRecord) -> bool` to `SeshaProtocol`
3. Implemented in `SeshaService` with validation
4. Fixed all 3 encapsulation breaches in `base.py`

**WRITE Breaches Fixed (11 total)**:
- `cortex_main.py` (3x)
- `flood.py`
- `ouroboros.py`
- `commit_watcher.py`
- `narada.py`
- `naga_cli.py`
- `naga_guard/plugin_main.py`
- `sesha_cli.py`

**READ Breaches Fixed (3 files)**:
- [x] `naga_cli.py` - Now uses `sesha.get_recent_events()` and `sesha.get_events_by_type()`
- [x] `cartridge_main.py` - Now uses `sesha.get_recent_events()` and `sesha.get_events_by_type()`
- [x] `prahlad/chaos.py` - Now uses `sesha.get_recent_events()`

**READ API Added to SeshaProtocol**:
- `get_recent_events(limit: int = 10) -> List[EventDict]`
- `get_events_by_type(event_type: str, limit: int = 100) -> List[EventDict]`

---

## V. YAMARAJA PRINCIPLES

1. **Keine Silent Failures** - `sys.stderr.write()` oder `raise`
2. **Keine Any Types** - TypedDict, ParamSpec, TypeVar
3. **Dependency = Contract** - If A needs B, validate B exists
4. **Hoffnung ist kein Plan** - Validate at boot, not at use
