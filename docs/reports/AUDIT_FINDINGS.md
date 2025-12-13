# AUDIT FINDINGS - MD File Write Violations

**Date**: 2025-12-05
**Auditor**: Claude (Sonnet)

---

## 🔴 SEPARATION OF CONCERNS VIOLATIONS

### Problem: Plugins writing MD files directly
**Why this is bad**:
- No file locks (race conditions)
- No atomic writes (corruption risk)
- No consistent headers
- Can't auto-commit safely
- Merge conflicts everywhere

---

## 📊 FINDINGS

### ❌ VIOLATORS (Direct writes):

1. **`vibe_core/plugins/git_history.py`**
   - Writes: `GIT.md`
   - Line: `output_path.write_text(content)`
   - Should use: DocRenderer

2. **`vibe_core/plugins/ephemeral_ui.py`**
   - Writes: `EPHEMERAL.md`
   - Line: `EPHEMERAL_MD_PATH.write_text("\n".join(lines))`
   - Should use: DocRenderer

3. **`steward/system_agents/herald/tools/scribe_tool.py`**
   - Writes: `docs/chronicles.md`
   - Multiple direct writes
   - Status: UNCLEAR (agent tool, might be intentional?)

### ✅ GOOD ACTORS (Use DocRenderer):

- `vibe_core/plugins/settings_ui.py` → Uses `DocRenderer.render_settings()`
- `vibe_core/plugins/envoy_ui.py` → Uses `DocRenderer.render_envoy()`
- All SCRIBE renderers → Return content only, don't write

---

## 🏗️ ARCHITECTURE DISCOVERED

### 3 Patterns Exist:

**Pattern 1: Bidirectional Files** (✅ CORRECT)
- SETTINGS.md, ENVOY.md
- Use DocRenderer
- Have SettingsSection plugin system
- Parse user commands
- Preserve user input

**Pattern 2: Read-Only Dashboard Files** (❌ BROKEN)
- GIT.md, EPHEMERAL.md, OPERATIONS.md
- Some use DocRenderer, some write directly
- No consistency

**Pattern 3: SCRIBE-Generated Docs** (✅ CORRECT)
- AGENTS.md, README.md, HELP.md, etc.
- Tools return content
- Agent publishes through kernel
- Goes through `system.publish_artifact()`

---

## 🎯 ROOT CAUSE

**DocRenderer exists but is not enforced**:
- No abstraction layer that PREVENTS direct writes
- Plugins CAN write directly (no compile-time prevention)
- Each plugin does its own thing

**What's missing**:
- Unified rendering API that plugins MUST use
- File write permissions (only DocRenderer can write)
- Atomic write layer with locks

---

## 💡 SOLUTION OPTIONS

### Option A: Extend DocRenderer
Add method: `DocRenderer.render_document(name, content, type="readonly")`
- Handles file locks
- Atomic writes
- Consistent headers
- Optional auto-commit

All plugins call this instead of direct write_text().

### Option B: Kernel-Level Write Protection
- Only kernel can write to root *.md files
- Plugins must go through kernel.render_document()
- Enforced at OS level (file permissions?)

### Option C: Document Manager Plugin
- New plugin: `document_manager.py`
- Intercepts all MD writes
- Coordinates rendering
- Handles conflicts

---

## 📋 ACTION ITEMS

**P0 - Fix Violations**:
- [ ] Update `git_history.py` to use DocRenderer
- [ ] Update `ephemeral_ui.py` to use DocRenderer
- [ ] Audit `herald/scribe_tool.py` - intentional or violation?

**P1 - Prevent Future Violations**:
- [ ] Add DocRenderer method for read-only files
- [ ] Add linting rule: No direct .write_text() to *.md in root
- [ ] Document the pattern in CONTRIBUTING.md

**P2 - Long-term Architecture**:
- [ ] Consider kernel-level write protection
- [ ] Consider unified Document Manager
- [ ] Add integration tests that verify no direct writes

---

## 🔍 QUESTIONS FOR ARCHITECT

1. **Herald scribe_tool**: Is docs/chronicles.md supposed to bypass DocRenderer?
2. **Auto-commit**: Should DocRenderer auto-commit after write?
3. **File locks**: Are we okay with the FileLock we have in task_management/?
4. **Enforcement**: Should we PREVENT direct writes at runtime or just lint?

---

*This audit reveals architectural debt from rapid development. System works but lacks consistency.*
