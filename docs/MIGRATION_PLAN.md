# KERNEL I/O SERVICE MIGRATION PLAN

**Date**: 2025-12-05
**Status**: IN PROGRESS
**Branch**: feat/core-io-migration

---

## 🎯 MISSION

Complete migration of ALL file write operations to centralized `KernelIOService` for:
- Atomic writes (temp file + rename)
- File locking (race condition prevention)
- Audit trail (ledger integration)
- Consistent headers for markdown files
- User section preservation for bidirectional docs

---

## ✅ COMPLETED

### Core Infrastructure
- [x] `vibe_core/io_service.py` - Central I/O controller (DONE in PR #295)
- [x] `vibe_core/kernel_impl.py` - Move `self.io` init BEFORE tool discovery (CRITICAL FIX)
- [x] `vibe_core/doc_renderer.py` - Already uses io_service (DONE)

### Tools
- [x] `vibe_core/tools/agenda_tools.py` - AddTaskTool, CompleteTaskTool migrated
- [x] `steward/system_agents/herald/tools/scribe_tool.py` - Reference implementation (DONE)

### Plugins
- [x] `vibe_core/plugins/git_history.py` - Uses `kernel.io.write_document()` (DONE)
- [x] `vibe_core/plugins/ephemeral_ui.py` - Uses `kernel.io.write_document()` (DONE)
- [x] `vibe_core/plugins/settings_ui.py` - Uses DocRenderer (DONE)
- [x] `vibe_core/plugins/envoy_ui.py` - Uses DocRenderer (DONE)

### Task Management
- [x] `vibe_core/task_management/task_manager.py` - Partial migration (constructor accepts io_service)

---

## 🔴 CRITICAL - MUST FIX NOW

### Kernel Hashes BROKEN
- [ ] **BLOCKER**: `kernel_impl.py` changed → Constitutional hashes INVALID
  - File: `scripts/governance/kernel_hashes.json`
  - Must run: `python scripts/verify_system.py --update-hashes`
  - **WHY**: Changed `__init__` order - moved `self.io` before tool discovery
  - **RISK**: Constitutional oath verification will fail

### Tests Hanging/Broken
- [ ] **BLOCKER**: Test suite hangs on full run
  - File: `tests/fractal/test_example_fractal.py` - Missing import
  - File: `tests/test_crypto_verification.py` - Missing `ecdsa` module
  - File: `tests/hardening/test_governance_security.py` - Missing `ecdsa` module
  - **ACTION**: Document broken tests, fix or skip

---

## ⚠️ HIGH PRIORITY - P0

### Sync Modules (Bidirectional Files)
- [ ] `vibe_core/settings_sync.py` - Direct write at line 233
  - **Impact**: SETTINGS.md writes bypass audit trail
  - **Fix**: Inject `kernel.io` in constructor

- [ ] `vibe_core/envoy_sync.py` - Direct write at line 272
  - **Impact**: ENVOY.md writes bypass audit trail
  - **Fix**: Inject `kernel.io` in constructor

### File Tools
- [ ] `vibe_core/tools/file_tools.py` - Direct write_text
  - **Impact**: User file operations bypass audit
  - **Decision needed**: Should user files go through io_service?

### Task Management Completeness
- [ ] `vibe_core/task_management/archive.py` - Line 452 direct write
- [ ] `vibe_core/task_management/export_engine.py` - Lines for export bypass io_service
  - **Decision**: These are user-requested exports - maybe OK to bypass?

---

## 📋 MEDIUM PRIORITY - P1

### Plugin Refactoring (Gemini's Feedback)
- [ ] `vibe_core/runtime/tool_safety_guard.py` → Convert to KernelPlugin
  - **Current**: Standalone class, manually called
  - **Target**: Plugin with `on_tool_execute` hook
  - **Benefit**: Systemwide enforcement, no bypass possible

### Sarga Boot Wiring
- [ ] `vibe_core/sarga.py` - Missing plugin discovery in boot sequence
  - **Risk**: Kernel boots "naked" without plugins
  - **Fix**: Add `PluginLoader.discover()` in AKASHA phase

### Performance Warning
- [ ] Review `on_tick_pre`/`on_tick_post` plugins for I/O operations
  - **Risk**: 10 plugins doing I/O on every tick = slow heartbeat
  - **Fix**: Make tick hooks lightweight or async

---

## 🔒 ENFORCEMENT - P1

### Prevent Future Violations
- [ ] Add pytest test: Grep for `.write_text(` violations in vibe_core
  - **Exclude**: VFS, io_service itself, test files
  - **Action**: Fail CI if violations found

- [ ] Add ruff/flake8 rule: Ban direct `Path.write_text` in core
  - **Config**: `.ruff.toml` or `pyproject.toml`

- [ ] Document pattern in `CONTRIBUTING.md`
  - **Rule**: All MD writes MUST use `kernel.io.write_document()`
  - **Exception**: VFS internal operations only

---

## 📊 REMAINING DIRECT WRITES (Audit Results)

```bash
# As of 2025-12-05
vibe_core/tools/file_tools.py:            path.write_text(content, encoding="utf-8")
vibe_core/tools/agenda_tools.py:          BACKLOG_PATH.write_text(content, encoding="utf-8")  # FALLBACK ONLY
vibe_core/task_management/file_lock.py:   self.lock_path.write_text(json.dumps(...))  # OK - internal locking
vibe_core/task_management/task_manager.py: path.write_text(content, encoding="utf-8")  # FALLBACK ONLY
vibe_core/task_management/archive.py:     archive_file.write_text(json.dumps(...))
vibe_core/task_management/export_engine.py: output_path.write_text(...)
```

---

## 🚫 KNOWN EXCLUSIONS (Intentional Direct Writes)

These are ALLOWED to bypass io_service:
- `vibe_core/vfs.py` - VFS layer itself (Line 195)
- `vibe_core/io_service.py` - I/O Service internals (temp file writes)
- `vibe_core/task_management/file_lock.py` - Lock file management
- `tests/**` - Test files (mocking, fixtures)

---

## 🧪 TEST STATUS

### Passing Tests
- ✅ `tests/test_p0_topology_integration.py` (5/5 passed)
- ✅ `tests/test_roadmap.py` (7/7 passed)

### Broken/Hanging Tests
- ❌ `tests/fractal/test_example_fractal.py` - ModuleNotFoundError
- ❌ `tests/test_crypto_verification.py` - Missing ecdsa module
- ❌ `tests/hardening/test_governance_security.py::test_forged_oath_rejection` - Missing ecdsa

### CI Failures (from PR #295)
- ❌ Integration Tests / test (3.11) - Failing after 3m
- ❌ SCRIBE Documentation - Unknown
- ❌ Deploy to Cloud Run - Unknown

---

## 📝 COMMIT STRATEGY

### Commit 1: Core Migration (CURRENT)
```
feat: migrate core tools and task_manager to io_service

- agenda_tools.py: AddTaskTool, CompleteTaskTool use io_service injection
- task_manager.py: Accept io_service in constructor, use for JSON writes
- kernel_impl.py: Move self.io init BEFORE tool discovery (critical fix)

BREAKING: kernel_impl.py __init__ order changed
```

### Commit 2: Fix Constitutional Hashes
```
chore: update kernel hashes after io_service init order change

- Run: python scripts/verify_system.py --update-hashes
- Update: scripts/governance/kernel_hashes.json
```

### Commit 3: Sync Modules Migration
```
feat: migrate settings_sync and envoy_sync to io_service

- settings_sync.py: Inject kernel.io, use write_document
- envoy_sync.py: Inject kernel.io, use write_document
```

### Commit 4: Enforcement
```
test: add enforcement for io_service usage

- Add pytest test to detect write_text violations
- Document pattern in CONTRIBUTING.md
```

---

## 🎯 DEFINITION OF DONE

Migration complete when:
- [ ] All P0 items completed
- [ ] Kernel hashes updated
- [ ] CI tests passing (or documented as broken pre-existing)
- [ ] Enforcement tests in place
- [ ] CONTRIBUTING.md updated with pattern
- [ ] PR reviewed and merged

---

## 🔥 URGENCY NOTES

From user feedback:
- "lieblos nicht zu ende gearbeitet" - Previous work was incomplete
- "kein spaghetti shit" - No quick hacks, do it right
- "fucking important. musst auch nciht gleich pushen" - Commit locally first, push together
- "keine halben sachen pls" - No half-finished work

**Senior mindset**: Understand the full system, track ALL debt, complete thoroughly.

---

## 🧠 ARCHITECTURAL INSIGHTS (Gemini Feedback)

### Fractal Plugin Pattern is CORRECT
- ✅ Inversion of Control via plugins
- ✅ Open-Closed Principle (extend, don't modify kernel)
- ⚠️ BUT: Must wire plugins in Sarga boot sequence

### Lost Cables (Broken Connections)
1. **ToolSafetyGuard**: Standalone → needs to be Plugin
2. **Sarga Boot**: Doesn't call PluginLoader.discover()
3. **Watchman**: Uses grep → should use plugin telemetry

### Next Level Architecture
- Plugin audit trail → Watchman reads ledger (not regex files)
- `on_tool_execute` hook → Safety guard enforcement
- Lightweight tick hooks → Async I/O in plugins

---

*This is the REAL roadmap. Code is truth, not README.md.*
