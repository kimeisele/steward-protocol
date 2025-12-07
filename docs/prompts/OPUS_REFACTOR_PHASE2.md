# OPUS Refactor Phase 2 - Technical Debt Resolution

**Priority:** CRITICAL
**Assignee:** Sonnet
**Reviewer:** The Watcher (Senior Architect)

---

## Context

The OPUS Unified Execution Model (commit `551f1b0`) is functional but has accumulated technical debt that will cause problems at scale. This prompt defines the refactoring work required to achieve true architectural cleanliness.

## Current State Assessment

| Component | Status | Issue |
|-----------|--------|-------|
| UnifiedRouter | 🟡 Partial | Runs parallel to legacy routers |
| EphemeralStorage | 🔴 Broken | Global singleton, not kernel-bound |
| Panel System | 🔴 Blocking | Synchronous I/O in render loop |
| Templates | 🟡 Hardcoded | Embedded in Python, not externalized |
| Test Coverage | 🔴 Weak | Only integration, no unit tests |

---

## Task 1: Kill Legacy Routers (UNIFIED means ONE)

### Location
- `vibe_core/plugins/envoy/plugin_main.py`

### Current Problem
```python
# Line 116: Initialize UNIFIED ROUTER
self._init_unified_runtime()

# Line 119: Legacy routers (for backwards compatibility)
self._init_routers()  # <-- THIS MUST DIE
```

Both systems run in parallel. This is not "unified", this is "split-brain".

### Required Changes

1. **Remove `_init_routers()` call completely** from `boot()` method
2. **Delete or deprecate** these legacy attributes:
   - `self._playbook_router`
   - `self._semantic_router`
   - `self._milk_ocean_router`
3. **Audit all code paths** that reference legacy routers:
   ```bash
   grep -r "_playbook_router\|_semantic_router\|_milk_ocean_router" vibe_core/
   ```
4. **Redirect any remaining calls** through `UnifiedRouter`
5. **Add deprecation warnings** if you cannot delete immediately:
   ```python
   @property
   def _playbook_router(self):
       warnings.warn("Legacy router deprecated, use unified_router", DeprecationWarning)
       return self._unified_router
   ```

### Acceptance Criteria
- [ ] Only ONE router exists: `UnifiedRouter`
- [ ] `grep -r "_init_routers" vibe_core/` returns nothing
- [ ] All tests pass with legacy routers removed

---

## Task 2: Fix EphemeralStorage Lifecycle

### Location
- `vibe_core/playbook/ephemeral_storage.py`

### Current Problem
```python
_instance: Optional[EphemeralStorage] = None  # GLOBAL SINGLETON

def get_ephemeral_storage():
    global _instance
    if _instance is None:
        _instance = EphemeralStorage()
    return _instance
```

This causes:
- Test pollution (parallel tests share state)
- Memory leaks on kernel reboot
- No isolation between agents

### Required Changes

1. **Remove the global singleton pattern**
2. **Bind EphemeralStorage to EnvoyPlugin lifecycle**:
   ```python
   # In EnvoyPlugin.__init__
   self._ephemeral = EphemeralStorage()

   # In EnvoyPlugin.shutdown() or kernel halt
   self._ephemeral.clear()
   ```
3. **Pass storage as dependency injection**, not global access:
   ```python
   class UnifiedExecutor:
       def __init__(self, ephemeral: EphemeralStorage):
           self._ephemeral = ephemeral
   ```
4. **Update all callers** of `get_ephemeral_storage()` to use injected instance
5. **Add kernel lifecycle hook**:
   ```python
   # In kernel halt/shutdown
   if hasattr(self, 'envoy') and hasattr(self.envoy, '_ephemeral'):
       self.envoy._ephemeral.clear()
   ```

### Acceptance Criteria
- [ ] No global `_instance` variable in ephemeral_storage.py
- [ ] EphemeralStorage cleared on kernel shutdown
- [ ] Parallel tests don't share ephemeral state

---

## Task 3: Async Panel Rendering

### Location
- `vibe_core/plugins/interface/renderers/opus/panels/code_health.py`
- `vibe_core/plugins/interface/renderers/opus/panels/__init__.py`

### Current Problem
```python
def render(self) -> str:
    todos = self._scan_pattern(r"#\s*TODO", ["vibe_core/**/*.py"])  # BLOCKS!
```

Synchronous file I/O during render cycle. At 10,000 files, the kernel freezes.

### Required Changes

1. **Add caching layer** to BasePanel:
   ```python
   class BasePanel(ABC):
       _cache: Dict[str, Any] = {}
       _cache_ttl: int = 300  # 5 minutes

       def get_cached(self, key: str) -> Optional[Any]:
           entry = self._cache.get(key)
           if entry and time.time() - entry['ts'] < self._cache_ttl:
               return entry['data']
           return None

       def set_cached(self, key: str, data: Any):
           self._cache[key] = {'data': data, 'ts': time.time()}
   ```

2. **Use EphemeralStorage for cross-render caching**:
   ```python
   def render(self) -> str:
       cache_key = f"panel:{self.panel_id}:scan_result"
       cached = self._ephemeral.get(cache_key)
       if cached:
           return self._format_cached(cached)

       # Background scan scheduled, return stale or placeholder
       self._schedule_background_scan()
       return self._render_placeholder()
   ```

3. **Alternative: Pre-compute on kernel boot**:
   ```python
   # In InterfacePlugin.boot()
   self._precompute_panel_data()  # Run once, cache forever until restart
   ```

4. **Add scan limits** as safety net:
   ```python
   MAX_FILES_TO_SCAN = 500

   def _scan_pattern(self, pattern, paths):
       count = 0
       for file in self._iter_files(paths):
           if count >= MAX_FILES_TO_SCAN:
               break
           # ...
   ```

### Acceptance Criteria
- [ ] Panel render time < 100ms (even with 10k files)
- [ ] Scan results cached for at least 5 minutes
- [ ] Fallback placeholder when cache is cold

---

## Task 4: Externalize Templates

### Location
- `vibe_core/playbook/action_handlers.py`

### Current Problem
```python
class RenderTemplateHandler:
    BUILTIN_TEMPLATES = {
        "status_summary": """...""",  # 50+ lines of Jinja2 in Python
        "agent_list": """...""",
    }
```

Templates embedded in Python = unwartable mess.

### Required Changes

1. **Create template directory**:
   ```
   knowledge/templates/
   ├── status_summary.j2
   ├── agent_list.j2
   ├── error_report.j2
   └── ...
   ```

2. **Load templates from files**:
   ```python
   class RenderTemplateHandler:
       TEMPLATE_DIR = Path("knowledge/templates")

       def _load_template(self, name: str) -> str:
           path = self.TEMPLATE_DIR / f"{name}.j2"
           if path.exists():
               return path.read_text()
           # Fallback to builtin only if file missing
           return self.BUILTIN_TEMPLATES.get(name, "")
   ```

3. **Keep builtins as fallback only**, not primary source

4. **Add template hot-reload** for development:
   ```python
   def _get_template(self, name: str) -> Template:
       # Check file mtime, reload if changed
       ...
   ```

### Acceptance Criteria
- [ ] All templates exist as `.j2` files in `knowledge/templates/`
- [ ] Python code loads from files first, falls back to builtin
- [ ] Template changes don't require Python restart

---

## Task 5: Unit Test Coverage

### Location
- `tests/unit/test_unified_router.py` (NEW)
- `tests/unit/test_unified_executor.py` (NEW)
- `tests/unit/test_ephemeral_storage.py` (NEW)

### Required Tests

1. **UnifiedRouter unit tests**:
   ```python
   def test_router_routes_to_correct_handler():
       router = UnifiedRouter(kernel=mock_kernel)
       result = router.route(ExecutionRequest(intent="status"))
       assert result.handler == "status_handler"

   def test_router_fallback_on_unknown_intent():
       ...

   def test_router_does_not_use_legacy_routers():
       # Assert legacy routers are not called
       ...
   ```

2. **UnifiedExecutor unit tests**:
   ```python
   def test_executor_runs_deterministic_playbook():
       ...

   def test_executor_handles_missing_playbook():
       ...

   def test_executor_returns_structured_result():
       ...
   ```

3. **EphemeralStorage unit tests**:
   ```python
   def test_storage_isolates_per_instance():
       s1 = EphemeralStorage()
       s2 = EphemeralStorage()
       s1.set("key", "value1")
       s2.set("key", "value2")
       assert s1.get("key") == "value1"  # Not polluted by s2

   def test_storage_clears_on_shutdown():
       ...
   ```

### Acceptance Criteria
- [ ] Each new class has dedicated unit test file
- [ ] Test coverage for UnifiedRouter > 80%
- [ ] Test coverage for UnifiedExecutor > 80%
- [ ] Tests run in < 5 seconds (no kernel boot required)

---

## Execution Order

1. **Task 2 first** (EphemeralStorage) - foundation for everything else
2. **Task 1 second** (Kill legacy routers) - simplifies codebase
3. **Task 3 third** (Async panels) - uses fixed ephemeral
4. **Task 4 fourth** (Templates) - cleanup
5. **Task 5 last** (Tests) - validates all changes

---

## Verification Commands

After completion, run:

```bash
# 1. No legacy router references
grep -r "_playbook_router\|_semantic_router" vibe_core/ && echo "FAIL: Legacy routers still exist"

# 2. No global singleton
grep -r "^_instance" vibe_core/ && echo "FAIL: Global singletons found"

# 3. Templates externalized
ls knowledge/templates/*.j2 | wc -l  # Should be > 0

# 4. Unit tests exist
ls tests/unit/test_unified*.py | wc -l  # Should be >= 2

# 5. All tests pass
python -m pytest tests/ -v --timeout=60
```

---

## Notes for Sonnet

- **DO NOT create new files unless listed above**
- **DO NOT add features** - this is refactoring only
- **DO NOT touch kernel_impl.py** - Kernel is eternal
- **COMMIT after each task** with clear message
- **RUN tests after each commit** before proceeding

---

*Generated by The Watcher (Senior Architect)*
*Review requested before merge to main*
