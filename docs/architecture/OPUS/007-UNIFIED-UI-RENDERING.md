# OPUS-007: UI Rendering Hardening

> **Status**: PLANNING
> **Created**: 2025-12-08
> **Scope**: Harden existing InterfacePlugin with production-grade safety
> **GAD-000**: Mandatory compliance - structured output, machine-parseable sections

---

## Executive Summary

**REALITY CHECK**: We are NOT reinventing the wheel. The InterfacePlugin already exists and is config-driven. This plan HARDENS the existing system with:

1. **Gemini's Three Laws of Rendering** (production safety)
2. **GAD-000 compliance** (machine-parseable)
3. **Bug fixes** (OPUS.md section preservation)

**What ALREADY EXISTS:**
- `InterfacePlugin` - Window Manager (config-driven from `config/interface.yaml`)
- `BaseRenderer` - With LIVE/AI/HUMAN section support
- 17 renderers - Each handling a specific Markdown file
- `on_task_completed()` hook - For immediate UI updates

**What's BROKEN:**
- OPUS.md sections get deleted (bug in OpusRenderer)
- No backup before write (data loss risk)
- No error boundaries (one bad template kills all rendering)
- Renders on every tick even if nothing changed (I/O waste)

---

## Gemini's Three Laws of Rendering (Critical!)

> **These are non-negotiable for production:**

### Law 1: Never Lose Data (Atomic Write with Backup)

**Problem**: If regex parser has bug, user content is lost forever.

**Solution**: Backup before write for bidirectional documents.

```python
# In BaseRenderer.merge_and_write()
def merge_and_write(self, new_content: str) -> None:
    """Safe write with backup for bidirectional docs."""
    config = self.get_config()
    if config and config.mode == "bidirectional":
        self._create_backup()

    # Write new content
    self._write_content(new_content)

    # Validate write (file size heuristic)
    if self._file_suspiciously_smaller():
        self._rollback_from_backup()
        raise StructuredError(
            code=ErrorCode.E3005_INTERNAL_ERROR,
            message="Render produced suspiciously small output",
            context={"document": self.name}
        )

    # Clean backup only on success
    self._cleanup_backup()

def _file_suspiciously_smaller(self) -> bool:
    """Detect if file shrunk >50% (likely data loss)."""
    backup_size = self._get_backup_size()
    current_size = self._get_current_size()
    if backup_size > 0 and current_size < backup_size * 0.5:
        return True
    return False
```

**Location**: `vibe_core/plugins/interface/renderers/base.py`

### Law 2: Never Crash Completely (Error Boundaries)

**Problem**: One agent's bad template crashes the entire UI system.

**Solution**: Wrap each renderer in error boundary.

```python
# In InterfacePlugin._render_scheduled()
def _render_scheduled(self) -> None:
    for name, renderer in self._renderers.items():
        if self._should_render(name):
            try:
                renderer.render()
                self._last_render[name] = time.time()
            except Exception as e:
                # Log but don't crash
                logger.error(f"Renderer '{name}' failed: {e}")
                self._render_error_placeholder(name, e)
                # Continue with other renderers!

def _render_error_placeholder(self, name: str, error: Exception) -> None:
    """Write error placeholder instead of crashing."""
    path = self._get_document_path(name)
    error_content = f"""<!--
UI ERROR: Renderer '{name}' failed
Error: {str(error)[:200]}
Time: {datetime.utcnow().isoformat()}
-->

# {name.upper()}.md

**Rendering Error**

The `{name}` renderer encountered an error.
System is still operational. This is a temporary placeholder.

Error: `{str(error)[:100]}`
"""
    path.write_text(error_content)
```

**Location**: `vibe_core/plugins/interface/plugin_main.py`

### Law 3: Never Work Unnecessarily (Render on Change)

**Problem**: 17 files rewritten every 2 seconds even if nothing changed.

**Solution**: Hash-based dirty tracking.

```python
# In BaseRenderer
def __init__(self, kernel):
    self._last_content_hash: Optional[str] = None

def render(self) -> None:
    """Only write if content changed."""
    new_content = self._generate_content()
    new_hash = hashlib.md5(new_content.encode()).hexdigest()

    if new_hash == self._last_content_hash:
        logger.debug(f"{self.name}: No changes, skipping write")
        return

    self.merge_and_write(new_content)
    self._last_content_hash = new_hash
```

**Location**: `vibe_core/plugins/interface/renderers/base.py`

---

## OPUS.md Bug Fix (Priority 1)

### Problem

OPUS.md deletes `<!-- @AI:... -->` and `<!-- @HUMAN:... -->` sections on refresh.

**Root Cause**: OpusRenderer generates content from scratch without preserving existing sections.

### Solution

1. OpusRenderer MUST call `merge_and_write()` instead of direct file write
2. `merge_and_write()` preserves AI/HUMAN sections from existing file

```python
# In opus/renderer.py - FIX
def render(self) -> None:
    # Generate LIVE sections
    content = self._generate_panels()

    # CRITICAL: Use merge_and_write to preserve AI/HUMAN sections
    self.merge_and_write(content)  # NOT self._write_file(content)
```

**Location**: `vibe_core/plugins/interface/renderers/opus/renderer.py`

---

## GAD-000 Compliance

### Test 1: Discoverability

```python
# InterfacePlugin must expose this
def get_registered_documents(self) -> List[dict]:
    """GAD-000: Machine-discoverable document registry."""
    return [
        {
            "id": name,
            "path": str(renderer.get_output_path()),
            "mode": renderer.get_config().mode if renderer.get_config() else "unidirectional",
            "sections": self._get_section_schema(renderer)
        }
        for name, renderer in self._renderers.items()
    ]
```

### Test 3: Parseability

```python
# All render errors are StructuredError
try:
    plugin.render_all()
except StructuredError as e:
    assert e.code in [ErrorCode.E2007_VALIDATION_FAILED, ErrorCode.E3005_INTERNAL_ERROR]
    assert "document" in e.context
```

### Test 4: Composability

```python
# Section markers are machine-parseable
# <!-- @LIVE:section_id --> content <!-- /@LIVE -->
# <!-- @AI:section_id --> content <!-- /@AI -->
# <!-- @HUMAN:section_id --> content <!-- /@HUMAN -->
```

---

## Implementation Phases

### Phase 1: Three Laws Implementation (CRITICAL)

**Files to Modify:**
- `vibe_core/plugins/interface/renderers/base.py`
- `vibe_core/plugins/interface/plugin_main.py`

**Tasks:**
1. Add atomic write with backup (`_create_backup`, `_rollback_from_backup`)
2. Add error boundaries in `_render_scheduled()`
3. Add content hashing for dirty tracking

**GAD-000 DoD:**
- Render failures are `StructuredError`
- Backup files created for bidirectional docs

**Verification:**
```bash
# Test Law 1: Backup
ls -la .ENVOY.md.bak  # Should exist after render

# Test Law 2: Error boundary
# Inject bad template, verify other renderers still work

# Test Law 3: No unnecessary writes
# Check file mtime after multiple renders with no data changes
```

### Phase 2: OPUS.md Fix

**Files to Modify:**
- `vibe_core/plugins/interface/renderers/opus/renderer.py`

**Tasks:**
1. Change direct file write to `merge_and_write()`
2. Verify AI/HUMAN sections preserved

**Verification:**
```python
# Write to AI section
# Run render
# AI section still exists
```

### Phase 3: GAD-000 API

**Files to Modify:**
- `vibe_core/plugins/interface/plugin_main.py`

**Tasks:**
1. Add `get_registered_documents()` method
2. Document section schema

---

## Existing Architecture (DO NOT CHANGE)

```
vibe_core/plugins/interface/
├── plugin_main.py          # InterfacePlugin (Window Manager) ← ADD error boundaries
├── renderers/
│   ├── base.py             # BaseRenderer (LIVE/AI/HUMAN support) ← ADD backup, hashing
│   ├── envoy.py            # ENVOY.md (bidirectional)
│   ├── opus/
│   │   └── renderer.py     # OPUS.md ← FIX merge_and_write
│   └── ... (15 other renderers)
```

**Config Location**: `config/interface.yaml`

```yaml
# Already config-driven!
renderers:
  envoy:
    enabled: true
    output: ENVOY.md
    interval: 2
    mode: bidirectional  # ← Uses this for backup decision
```

---

## Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `renderers/base.py` | Add backup, hashing, error handling | P0 |
| `plugin_main.py` | Add error boundaries, GAD-000 API | P0 |
| `renderers/opus/renderer.py` | Fix to use `merge_and_write()` | P0 |

---

## Verification Checklist

### Phase 1 (Three Laws):
- [ ] Backup created before bidirectional write
- [ ] Rollback works when file too small
- [ ] Error boundary catches renderer failures
- [ ] Error placeholder rendered instead of crash
- [ ] Content hash prevents redundant writes

### Phase 2 (OPUS.md Fix):
- [ ] AI sections preserved after render
- [ ] HUMAN sections preserved after render
- [ ] LIVE sections update correctly

### Phase 3 (GAD-000):
- [ ] `get_registered_documents()` returns list
- [ ] Section schema documented
- [ ] Errors are `StructuredError`

---

## Success Criteria

1. **No data loss** - Bidirectional docs backed up before write
2. **Graceful degradation** - One bad renderer doesn't kill UI
3. **Efficient I/O** - Only write when content actually changed
4. **OPUS.md works** - AI/HUMAN sections preserved
5. **GAD-000 compliant** - Structured errors, discoverable API

---

## Non-Goals

- Replacing existing renderers (they work fine)
- Adding new Markdown files
- Template engine rewrite (not needed)
- Breaking config/interface.yaml format

---

## Related Documents

- **OPUS-006**: GAD-000 Compliance Audit
- **OPUS-005**: Unification Roadmap (Phase 4 = UI)
- **OPUS-003**: AOS Foundation Repair (mentions renderer issues)

---

## Why EVOLUTION, not REVOLUTION

The existing architecture is SOUND:
- Config-driven ✅
- Section ownership (LIVE/AI/HUMAN) ✅
- Plugin-based ✅
- Interval scheduling ✅

What's missing is HARDENING:
- Data safety (backups)
- Fault tolerance (error boundaries)
- Efficiency (dirty tracking)

**We fix bugs and add safety. We don't rewrite working code.**

---

## HAIKU EXECUTION BLOCKS

> **For AI Agent Execution**: Copy-paste these blocks to implement the Three Laws.

### TASK 1: Law 1 - Atomic Write with Backup (base.py)

```
FILE: vibe_core/plugins/interface/renderers/base.py
LOCATION: In BaseRenderer class, add before merge_and_write()
ADD_METHODS:
    def _create_backup(self) -> None:
        """Law 1: Create backup before writing bidirectional doc."""
        path = self.get_output_path()
        backup_path = path.with_suffix(path.suffix + '.bak')
        if path.exists():
            import shutil
            shutil.copy2(path, backup_path)
            self._backup_path = backup_path

    def _rollback_from_backup(self) -> None:
        """Law 1: Restore from backup on suspicious write."""
        if hasattr(self, '_backup_path') and self._backup_path.exists():
            import shutil
            shutil.copy2(self._backup_path, self.get_output_path())

    def _cleanup_backup(self) -> None:
        """Law 1: Remove backup after successful write."""
        if hasattr(self, '_backup_path') and self._backup_path.exists():
            self._backup_path.unlink()

VERIFY: ls -la *.bak after running kernel with bidirectional docs
```

### TASK 2: Law 2 - Error Boundaries (plugin_main.py)

```
FILE: vibe_core/plugins/interface/plugin_main.py
FIND: def _render_scheduled(self) -> None:
MODIFY: Wrap each renderer.render() in try/except:
    def _render_scheduled(self) -> None:
        for name, renderer in self._renderers.items():
            if self._should_render(name):
                try:
                    renderer.render()
                    self._last_render[name] = time.time()
                except Exception as e:
                    logger.error(f"Renderer '{name}' failed: {e}")
                    self._render_error_placeholder(name, e)
                    # Continue with other renderers!

ADD_METHOD:
    def _render_error_placeholder(self, name: str, error: Exception) -> None:
        """Law 2: Write error placeholder instead of crashing."""
        from datetime import datetime
        path = self._get_document_path(name)
        error_content = f'''<!--
UI ERROR: Renderer '{name}' failed
Error: {str(error)[:200]}
Time: {datetime.utcnow().isoformat()}
-->

# {name.upper()}.md

**Rendering Error** - System still operational.
'''
        path.write_text(error_content)

VERIFY: Inject exception in one renderer, verify others still render
```

### TASK 3: Law 3 - Hash-based Dirty Tracking (base.py)

```
FILE: vibe_core/plugins/interface/renderers/base.py
LOCATION: In BaseRenderer.__init__()
ADD: self._last_content_hash: Optional[str] = None

LOCATION: In BaseRenderer.render()
MODIFY:
    def render(self) -> None:
        """Only write if content changed."""
        import hashlib
        new_content = self._generate_content()
        new_hash = hashlib.md5(new_content.encode()).hexdigest()

        if new_hash == self._last_content_hash:
            return  # Skip write - no changes

        self.merge_and_write(new_content)
        self._last_content_hash = new_hash

VERIFY: Check file mtime stays same after multiple renders with no data change
```

### TASK 4: OPUS.md Fix - Use merge_and_write

```
FILE: vibe_core/plugins/interface/renderers/opus/renderer.py
FIND: self._write_file(content) OR direct file.write_text()
REPLACE_WITH: self.merge_and_write(content)
VERIFY: Add content to @AI section, render, verify section preserved
```

---

## Phoenix Config Integration

> **Key Insight**: The UI system is ALREADY fraktal - it follows the same pattern as PhoenixConfig.

### Existing Fractal Architecture

```
PhoenixConfig Pattern              InterfaceConfig Pattern
───────────────────────            ───────────────────────
vibe_core/phoenix/sections/   ↔    config/interface.yaml
SectionLoader.discover()      ↔    renderers: {...}
config/{section_id}.yaml      ↔    custom_renderers: {...}
__getattr__ dynamic access    ↔    _renderers dict
```

### What `config/interface.yaml` Already Provides (486 LOC!)

| Category | Elements | Purpose |
|----------|----------|---------|
| `element_types` | table, status, list, terminal, metric, nav | Reusable UI atoms |
| `layouts` | fullpage, dashboard, terminal, content_only | Document structures |
| `ownership_types` | LIVE, AI, HUMAN | Section ownership markers |
| `view_types` | docs, dashboard, terminal, workspace, workflow | Application contexts |
| `renderers` | 17 built-in | System UI files |
| `custom_renderers` | {} | **Agent extension point!** |

### How Agents Extend UI (Already Works!)

```yaml
# config/interface.yaml - Agent adds custom renderer
custom_renderers:
  broker_btc:
    enabled: true
    output: BROKER_BTC.md
    view_type: dashboard
    interval: 18000  # 5 hours
    sections:
      - id: price
        owner: live
        source: broker.btc_price
      - id: notes
        owner: ai
```

### Scalability Path (Future)

For extreme scale (100+ renderers), split into:
```
config/
├── interface.yaml           # Core settings + system renderers
└── interface/
    └── agents/
        ├── broker.yaml      # Broker agent UI
        └── {agent_id}.yaml  # Auto-discovered
```

**Implementation**: Modify `InterfaceConfig.from_dict()` to glob `config/interface/agents/*.yaml` and merge into `custom_renderers`.

### GAD-000: UI Discoverability API

```python
# InterfacePlugin must expose:
def get_ui_schema(self) -> dict:
    """GAD-000 Test 1: Machine-discoverable UI system."""
    return {
        "element_types": list(self._config.element_types.keys()),
        "layouts": list(self._config.layouts.keys()),
        "ownership_types": list(self._config.ownership_types.keys()),
        "renderers": self.get_registered_documents(),
        "custom_renderers": list(self._config.custom_renderers.keys()),
    }
```

---

**Status**: HAIKU-READY
