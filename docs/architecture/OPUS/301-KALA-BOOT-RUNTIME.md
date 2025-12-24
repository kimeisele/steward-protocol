# OPUS-301: SARGA & KALA - Boot & Runtime Optimization

> **Status**: PHASE 1 COMPLETE ✅
> **Date**: 2025-12-24
> **Author**: Claude Opus 4.5 (Senior Steward)
> **Depends On**: OPUS-211 (Async All the Way)
> **Next**: OPUS-302 (Deep Lazy Loading)

---

## PHASE 1 RESULTS (2025-12-24)

| Metric | Before | After | Saved |
|--------|--------|-------|-------|
| Boot Time | 3940ms | ~2500ms | **38%** |

### Commits on main:
- `d64bdcbb` - Lazy network_proxy + LineageChain
- `2f7d58bd` - Direct protocol imports (bypass operator_protocol)

### What worked:
1. `network_proxy` → lazy property (saves ~180ms, avoids `requests`)
2. `LineageChain` → already lazy, removed eager import
3. `protocols.agent` → direct import (saves ~440ms, avoids `operator_protocol`)

---

## PHASE 2: OPUS-302 (DEEP LAZY LOADING)

**Remaining blockers** (from `python3 -X importtime`):

| Import | Time | Solution |
|--------|------|----------|
| `steward.crypto` → `jinja2` | 330ms | Lazy template loading |
| `ledger` (SQLite init) | 370ms | Deferred DB connection |
| `unified_execution` | 265ms | Split into core + full |

**Target**: 2500ms → <1000ms

---

## VEDIC FRAMEWORK

| Sanskrit | Meaning | Phase | Current | Target |
|----------|---------|-------|---------|--------|
| **सर्ग (Sarga)** | Creation | Boot | ~2500ms | <500ms |
| **काल (Kāla)** | Time | Runtime | ~50ms/pulse | <10ms |

---

## WHAT OPUS-211 ALREADY DID

✅ Async pulse, ActionManager, IntentRouter, CLI layer
✅ Karma loop closed (INTENT_EXECUTED events)
✅ TTL-based stale intent cleanup

**What's still slow**: The BOOT phase. Imports + Init = 2500ms.

---

## SARGA (BOOT) - JUNIOR TASKS

### Task S1: Lazy Import Wrapper (CAN DO)

**File**: `vibe_core/utils/lazy_import.py` (NEW)

```python
"""Lazy import utilities for boot optimization."""
from typing import TypeVar, Type
T = TypeVar('T')

_cache = {}

def lazy_class(module_path: str, class_name: str) -> Type[T]:
    """Import a class lazily on first access."""
    key = f"{module_path}.{class_name}"
    if key not in _cache:
        import importlib
        module = importlib.import_module(module_path)
        _cache[key] = getattr(module, class_name)
    return _cache[key]
```

**Test**:
```bash
python3 -c "
from vibe_core.utils.lazy_import import lazy_class
SQLiteLedger = lazy_class('vibe_core.ledger', 'SQLiteLedger')
print(f'✅ Lazy import works: {SQLiteLedger}')
"
```

- [ ] Create file
- [ ] Add test
- [ ] Commit

---

### Task S2: Config Cache (CAN DO)

**File**: `vibe_core/phoenix/config_cache.py` (NEW)

```python
"""Cache parsed config to avoid YAML parsing on every boot."""
import hashlib
import pickle
from pathlib import Path

CACHE_PATH = Path(".vibe/cache/config.pkl")
HASH_PATH = Path(".vibe/cache/config.hash")

def get_yaml_hash(config_dir: Path) -> str:
    """Hash all YAML files for cache invalidation."""
    content = ""
    for f in sorted(config_dir.glob("**/*.yaml")):
        content += f.read_text()
    return hashlib.md5(content.encode()).hexdigest()

def get_cached_or_parse(config_dir: Path, parse_fn):
    """Return cached config or parse fresh."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    current_hash = get_yaml_hash(config_dir)

    if HASH_PATH.exists() and CACHE_PATH.exists():
        if HASH_PATH.read_text() == current_hash:
            return pickle.loads(CACHE_PATH.read_bytes())

    config = parse_fn()
    CACHE_PATH.write_bytes(pickle.dumps(config))
    HASH_PATH.write_text(current_hash)
    return config
```

**Test**:
```bash
python3 -c "
from vibe_core.phoenix.config_cache import get_yaml_hash
from pathlib import Path
h = get_yaml_hash(Path('config'))
print(f'✅ Config hash: {h[:16]}...')
"
```

- [ ] Create file
- [ ] Integrate into `phoenix/config.py`
- [ ] Verify boot time improvement

---

### Task S3: Deferred Properties Plugin (CAN DO)

**File**: `vibe_core/plugins/boot_optimizer/plugin_main.py` (NEW)

This plugin patches kernel properties to be lazy-loaded.

```python
"""Boot Optimizer Plugin - Defers heavy initialization."""
from vibe_core.plugin_protocol import KernelPlugin, HookResult

class BootOptimizerPlugin(KernelPlugin):
    @property
    def plugin_id(self) -> str:
        return "boot_optimizer"

    def on_boot(self, kernel, config=None) -> HookResult:
        # Monkey-patch lineage to be lazy
        original_lineage = kernel.lineage
        kernel._lineage_cached = None

        @property
        def lazy_lineage(self):
            if self._lineage_cached is None:
                self._lineage_cached = original_lineage
            return self._lineage_cached

        # Similar for other heavy properties...
        return HookResult.ok("Boot optimization applied")
```

**Note**: This is a PLUGIN, not Ring 0. Safe for Junior.

- [ ] Create plugin structure
- [ ] Test with `load_plugins=True`
- [ ] Measure before/after

---

## KALA (RUNTIME) - JUNIOR TASKS

### Task K1: Verify OPUS-211 Async (VERIFY ONLY)

```bash
# Check that pulse is async
python3 -c "
import inspect
from vibe_core.kernel_ops import pulse
print(f'pulse is async: {inspect.iscoroutinefunction(pulse)}')
"
```

- [ ] Run verification
- [ ] Document result in this file

---

### Task K2: Batched Ledger Writes (CAN DO)

**File**: `vibe_core/ledger.py` - ADD methods (⚠️ NEEDS SENIOR for Ring 0)

```python
# Add to SQLiteLedger class
def batch_start(self):
    self._batch_buffer = []

def batch_record(self, event_type, agent_id, details):
    self._batch_buffer.append((event_type, agent_id, details))

def batch_commit(self):
    with self._write_lock:
        for e in self._batch_buffer:
            self.record_event(*e)
        self._batch_buffer = []
```

**⚠️ STOP**: `ledger.py` is Ring 0. Call Senior for hash update.

---

### Task K3: Async Logging Handler (CAN DO)

**File**: `vibe_core/utils/async_logging.py` (NEW)

```python
"""Async logging to prevent I/O blocking."""
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

_log_queue = Queue()
_listener = None

def setup_async_logging():
    global _listener
    root = logging.getLogger()
    handler = QueueHandler(_log_queue)
    root.addHandler(handler)

    file_handler = logging.FileHandler(".vibe/logs/system.log")
    _listener = QueueListener(_log_queue, file_handler)
    _listener.start()

def shutdown_async_logging():
    if _listener:
        _listener.stop()
```

- [ ] Create file
- [ ] Call `setup_async_logging()` in boot
- [ ] Verify no blocking

---

## SENIOR-ONLY TASKS (RING 0)

These require `--no-verify` and hash update:

| Task | File | Why Senior |
|------|------|------------|
| Lazy imports in kernel_impl.py | `kernel_impl.py` | VISNU protected |
| Batched ledger methods | `ledger.py` | VISNU protected |
| Deferred init in __init__ | `kernel_impl.py` | VISNU protected |

**Protocol**:
1. Junior prepares code in separate file
2. Senior reviews
3. Senior applies to Ring 0 with `--no-verify`
4. Senior updates `kernel_hashes.json`
5. Senior pushes to main

---

## VERIFICATION CHECKLIST

Before claiming COMPLETE:

```bash
# 1. Boot timing
python3 -c "
import time, os
os.environ['VIBE_NO_GIT_COMMIT'] = '1'
t0 = time.perf_counter()
from vibe_core.kernel_impl import RealVibeKernel
t1 = time.perf_counter()
k = RealVibeKernel(':memory:', load_plugins=False)
t2 = time.perf_counter()
print(f'Import: {(t1-t0)*1000:.0f}ms')
print(f'Init: {(t2-t1)*1000:.0f}ms')
print(f'Total: {(t2-t0)*1000:.0f}ms')
assert (t2-t0) < 0.5, 'Boot too slow!'
"

# 2. Pulse latency (after full boot)
python3 -c "
import time, asyncio
# ... measure pulse time
"
```

---

## PROGRESS TRACKER

| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| S1: Lazy Import Wrapper | ⬜ | Junior | New utility |
| S2: Config Cache | ⬜ | Junior | New utility |
| S3: Boot Optimizer Plugin | ⬜ | Junior | New plugin |
| K1: Verify OPUS-211 Async | ⬜ | Junior | Verify only |
| K2: Batched Ledger | ⬜ | **Senior** | Ring 0 |
| K3: Async Logging | ⬜ | Junior | New utility |

---

## WHEN TO CALL SENIOR

1. Any change to files in `kernel_hashes.json`
2. Boot time not improving despite changes
3. Circular import errors
4. VISNU rejecting commits

---

*Sarga schafft. Kala fließt. Junior baut. Senior schützt.*
