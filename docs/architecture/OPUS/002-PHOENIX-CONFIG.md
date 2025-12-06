# PHOENIX CONFIG OPTIMIZATION

**Status:** Planned
**Priority:** P0
**Goal:** Reduce config loading from 4+ seconds to <100ms

## The Problem

Every `get_config()` call takes 4+ seconds because:

1. **No caching** - `SectionLoader.discover()` runs fresh every time
2. **Eager loading** - ALL sections loaded even if only one needed
3. **Heavy imports** - Each section imports heavy modules
4. **YAML parsing overhead** - 8+ YAML files parsed synchronously

Profile results:
```
6.018s  get_config()
├── 4.03s  SectionLoader.discover()
│   ├── Import all section modules
│   └── Parse all YAML files (25 safe_load calls!)
├── 1.2s  discover_circuits() (scanning directories)
└── 0.8s  Other initialization
```

## Why This Matters

- **Tests timeout** - Each test that calls get_config() takes 4s+
- **Boot is slow** - Kernel boot waits for full config
- **No isolation** - Can't test one section without loading all

## Solution: Lazy Loading + Caching

### 1. Global Cache (Quick Win)

```python
# Current (broken)
_config_cache: Optional[PhoenixConfig] = None

def get_config() -> PhoenixConfig:
    global _config_cache
    if _config_cache is None:
        _config_cache = PhoenixConfig.from_files()
    return _config_cache
```

Problem: Tests call `reset_config()` which clears cache, then each test reloads.

Fix: Don't reset in tests unless explicitly needed.

### 2. Lazy Section Loading

```python
class PhoenixConfig:
    _sections: Dict[str, Any] = {}
    _loaded: Set[str] = set()

    def get_section(self, section_id: str) -> Any:
        if section_id not in self._loaded:
            self._load_section(section_id)
            self._loaded.add(section_id)
        return self._sections[section_id]
```

### 3. Parallel YAML Parsing

```python
import concurrent.futures

def _load_all_yaml(paths: List[Path]) -> Dict[str, Any]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(yaml.safe_load, p.read_text()): p
                   for p in paths}
        results = {}
        for future in concurrent.futures.as_completed(futures):
            path = futures[future]
            results[path.stem] = future.result()
    return results
```

### 4. Skip Circuits/Routing on Boot

Circuits and routing can be loaded lazily when first accessed:

```python
@property
def circuits(self) -> Dict[str, CircuitConfig]:
    if self._circuits is None:
        self._circuits = discover_circuits(self._circuits_dir)
    return self._circuits
```

## Implementation Plan

### Phase 1: Quick Fixes (Today)
- [ ] Add proper caching to `get_config()`
- [ ] Don't reset cache in test fixtures
- [ ] Lazy load circuits/routing

### Phase 2: Lazy Sections (This Week)
- [ ] Sections loaded on-demand
- [ ] Section dependencies tracked
- [ ] Only load what's needed

### Phase 3: Parallel Loading (Later)
- [ ] Parallel YAML parsing
- [ ] Background section preloading
- [ ] Hot reload support

## Success Criteria

1. `get_config()` < 100ms (first call)
2. `get_config()` < 1ms (cached call)
3. Tests don't need full config load
4. Section can be loaded independently

## Test Impact

Current:
```
21 config tests × 4s = 84 seconds minimum
```

After optimization:
```
21 config tests × 0.1s = 2.1 seconds
```

Plus: Other tests don't need config at all!
