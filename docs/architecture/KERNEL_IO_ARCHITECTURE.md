# KERNEL I/O ARCHITECTURE

> **Status:** ACTIVE DESIGN
> **Author:** Claude (Opus) - Senior Architecture Review
> **Date:** 2025-12-05
> **Priority:** P0 - Fundamental Architecture

---

## Executive Summary

This document defines the **Kernel I/O Architecture** - the foundational layer that controls ALL file operations in VibeOS. This is not optional infrastructure - it is a core architectural constraint that enforces separation of concerns.

**The Problem:** Plugins and agents write files directly, bypassing any central control. This causes race conditions, inconsistent formatting, and architectural violations.

**The Solution:** A Kernel I/O Service that is the ONLY way to write files. Plugins produce content, the Kernel writes.

---

## 1. The Markdown UI Paradigm

### 1.1 What Are We Building?

VibeOS uses **Markdown files as the User Interface**. This is not a temporary solution - it is a deliberate architectural choice:

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKDOWN UI PARADIGM                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Human ←→ Markdown Files ←→ Kernel ←→ Agents                │
│                                                              │
│  SETTINGS.md  : Configuration Interface (bidirectional)     │
│  ENVOY.md     : Request Terminal (bidirectional)            │
│  OPERATIONS.md: Dashboard (read-only)                        │
│  EPHEMERAL.md : Ephemeral Cities Dashboard (read-only)      │
│  GIT.md       : Repository Analysis (read-only)             │
│  AGENTS.md    : Agent Registry (read-only)                  │
│  ...                                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Document Types

| Type | Direction | User Can Edit | Kernel Reads | Examples |
|------|-----------|---------------|--------------|----------|
| **Bidirectional** | User ↔ Kernel | Yes | Yes | SETTINGS.md, ENVOY.md |
| **Read-Only** | Kernel → User | No (preserved notes only) | No | OPERATIONS.md, AGENTS.md, GIT.md |
| **Agent-Generated** | Agent → Kernel → File | No | No | README.md, HELP.md (via SCRIBE) |

### 1.3 Why Markdown?

1. **Human-Readable:** No special tools needed
2. **Version Control:** Git-friendly, diff-able
3. **Portable:** Works everywhere
4. **Bidirectional:** Can be both input AND output
5. **LLM-Friendly:** Claude can read and write naturally

---

## 2. The Problem: Uncontrolled I/O

### 2.1 Current State (Broken)

```
┌─────────────────────────────────────────────────────────────┐
│                        KERNEL                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ _pulse() → Path("vibe_snapshot.json").write_text()    │ │ ← DIRECT
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  DocRenderer (utility class - OPTIONAL, not enforced)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │OPERATIONS│  │ SETTINGS │  │  ENVOY   │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
         ↑
         │ some plugins use
         │
┌─────────────────────────────────────────────────────────────┐
│                       PLUGINS                                │
│                                                              │
│  SettingsUIPlugin → DocRenderer.render_settings()      ✓    │
│  EnvoyUIPlugin    → DocRenderer.render_envoy()         ✓    │
│                                                              │
│  EphemeralUIPlugin → Path().write_text()               ✗    │ ← DIRECT
│  GitHistoryPlugin  → output_path.write_text()          ✗    │ ← DIRECT
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Violations Identified

| Component | Violation | File Written |
|-----------|-----------|--------------|
| `vibe_core/plugins/ephemeral_ui.py` | Direct `Path.write_text()` | EPHEMERAL.md |
| `vibe_core/plugins/git_history.py` | Direct `Path.write_text()` | GIT.md |
| `vibe_core/kernel_impl.py:_pulse()` | Direct `Path.write_text()` | vibe_snapshot.json |

### 2.3 Why This Is Bad

1. **Race Conditions:** Multiple writers, no locking
2. **Inconsistent Formatting:** Each plugin formats differently
3. **No Access Control:** Anyone can write anywhere
4. **No Audit Trail:** Who wrote what, when?
5. **Merge Conflicts:** Git conflicts on auto-generated files

---

## 3. The Solution: Kernel I/O Service

### 3.1 Design Principle

**Plugins produce CONTENT. Kernel WRITES.**

This is OS design 101:
- User-Space (Plugins/Agents) cannot access hardware (filesystem) directly
- Kernel-Space (I/O Service) controls all I/O
- System Calls are the only interface

### 3.2 Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        KERNEL                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  KERNEL I/O SERVICE                    │ │
│  │                                                         │ │
│  │  write_document(name, content, doc_type)               │ │
│  │  read_document(name) → content                         │ │
│  │                                                         │ │
│  │  Features:                                              │ │
│  │  - Atomic writes (temp file + rename)                   │ │
│  │  - File locking (prevent races)                         │ │
│  │  - Unified headers/footers                              │ │
│  │  - Access control (who can write what)                  │ │
│  │  - Audit trail (ledger integration)                     │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↑                                   │
│                    SYSCALL BOUNDARY                          │
│                          ↑                                   │
└─────────────────────────────────────────────────────────────┘
                           │
              kernel.io.write_document()
                           │
┌─────────────────────────────────────────────────────────────┐
│                  PLUGINS (User Space)                        │
│                                                              │
│  - Produce CONTENT only (List[str] or str)                  │
│  - NO direct Path imports                                    │
│  - Call kernel.io.write_document(name, content)             │
│                                                              │
│  Example - EphemeralUIPlugin:                                │
│    def on_tick_post(self, kernel):                          │
│        content = self._generate_ephemeral_content(kernel)   │
│        kernel.io.write_document("EPHEMERAL.md", content,    │
│                                 doc_type="readonly")        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 I/O Service API

```python
class KernelIOService:
    """
    Central I/O controller for all Kernel file operations.

    PHILOSOPHY: Plugins produce content. Kernel writes.
    """

    def write_document(
        self,
        name: str,
        content: str | List[str],
        doc_type: DocumentType = DocumentType.READONLY,
        writer_id: str = "KERNEL"
    ) -> WriteResult:
        """
        Write a document through the I/O service.

        Args:
            name: Document name (e.g., "EPHEMERAL.md", "GIT.md")
            content: Content to write (str or list of lines)
            doc_type: READONLY, BIDIRECTIONAL, or SNAPSHOT
            writer_id: ID of the plugin/component writing

        Returns:
            WriteResult with success status and new mtime

        Features:
            - Atomic write (temp file + rename)
            - File locking (prevents race conditions)
            - Auto-adds unified header (for markdown)
            - Preserves user sections (for bidirectional)
            - Records to ledger (audit trail)
        """

    def read_document(self, name: str) -> str | None:
        """Read a document's content."""

    def extract_user_section(self, name: str, section: str) -> str:
        """Extract preserved user content from bidirectional doc."""
```

### 3.4 Document Types

```python
class DocumentType(Enum):
    READONLY = "readonly"        # Kernel writes, user reads
    BIDIRECTIONAL = "bidir"      # Both can write, kernel preserves user input
    SNAPSHOT = "snapshot"        # Internal state (JSON)
```

---

## 4. Implementation Plan

### 4.1 Phase 1: Create I/O Service

**File:** `vibe_core/io_service.py`

```python
# Core implementation
class KernelIOService:
    def __init__(self, kernel: "RealVibeKernel"):
        self._kernel = kernel
        self._locks: Dict[str, threading.Lock] = {}

    def write_document(self, name: str, content: str | List[str],
                       doc_type: DocumentType, writer_id: str) -> WriteResult:
        # 1. Acquire lock
        # 2. For bidirectional: extract user sections
        # 3. Generate unified header
        # 4. Atomic write (temp + rename)
        # 5. Record to ledger
        # 6. Release lock
```

### 4.2 Phase 2: Integrate into Kernel

**File:** `vibe_core/kernel_impl.py`

```python
class RealVibeKernel:
    def __init__(self, ...):
        # ... existing init ...

        # I/O Service (THE ONLY way to write files)
        self.io = KernelIOService(self)
```

### 4.3 Phase 3: Migrate Plugins

| Plugin | Current | Target |
|--------|---------|--------|
| EphemeralUIPlugin | `Path().write_text()` | `kernel.io.write_document()` |
| GitHistoryPlugin | `output_path.write_text()` | `kernel.io.write_document()` |
| SettingsUIPlugin | `DocRenderer` | Keep (uses `kernel.io` internally) |
| EnvoyUIPlugin | `DocRenderer` | Keep (uses `kernel.io` internally) |

### 4.4 Phase 4: Migrate Kernel Internals

| Component | Current | Target |
|-----------|---------|--------|
| `_pulse()` | Direct write to `vibe_snapshot.json` | `kernel.io.write_document()` |
| `DocRenderer` | Utility class | Thin wrapper around `kernel.io` |

---

## 5. Enforcement

### 5.1 Lint Rule

Add to ruff configuration:

```toml
[tool.ruff.lint]
# Custom rule: No direct Path.write_text in plugins
# (Implemented via pre-commit hook or custom checker)
```

### 5.2 Architecture Test

```python
def test_no_direct_writes_in_plugins():
    """Verify plugins don't import Path or write directly."""
    for plugin_file in Path("vibe_core/plugins").glob("*.py"):
        content = plugin_file.read_text()
        assert "Path(" not in content or "write_text" not in content, \
            f"Plugin {plugin_file} has direct file writes - use kernel.io"
```

### 5.3 Code Review Checklist

- [ ] New plugin uses `kernel.io.write_document()` for all file writes
- [ ] No `Path` imports in plugin code
- [ ] No `write_text()` or `open(..., 'w')` in plugin code

---

## 6. Migration Guide

### 6.1 For Plugin Authors

**Before (Wrong):**
```python
from pathlib import Path

class MyPlugin(KernelPlugin):
    def on_tick_post(self, kernel):
        content = self._generate_content()
        Path("MY_OUTPUT.md").write_text(content)  # ❌ DIRECT WRITE
```

**After (Correct):**
```python
class MyPlugin(KernelPlugin):
    def on_tick_post(self, kernel):
        content = self._generate_content()
        kernel.io.write_document(
            "MY_OUTPUT.md",
            content,
            doc_type=DocumentType.READONLY,
            writer_id=self.plugin_id
        )  # ✓ THROUGH I/O SERVICE
```

### 6.2 For Agent Authors

Agents should NOT write files directly. They should:

1. Return content from their tools
2. Use `system.publish_artifact()` if needed
3. Let the Kernel handle actual file writes

---

## 7. Relationship to Existing Components

### 7.1 DocRenderer

`DocRenderer` will become a thin wrapper around `KernelIOService`:

```python
class DocRenderer:
    def __init__(self, io_service: KernelIOService):
        self._io = io_service

    def render_settings(self, snapshot, state):
        content = self._generate_settings_content(snapshot, state)
        return self._io.write_document("SETTINGS.md", content,
                                       doc_type=DocumentType.BIDIRECTIONAL)
```

### 7.2 SettingsSection Protocol

The existing `SettingsSection` plugin system is CORRECT. It:
- Produces content (list of lines)
- Does NOT write files directly
- Lets `DocRenderer` handle writing

This is the pattern all plugins should follow.

---

## 8. Migration Status

> **Updated:** 2025-12-05 - Honest assessment of implementation progress

### 8.1 Completed ✅

| Component | Status | Notes |
|-----------|--------|-------|
| `vibe_core/io_service.py` | ✅ DONE | Full implementation with audit trail |
| `kernel.io` integration | ✅ DONE | Available as `kernel.io` |
| Audit Trail (Ledger) | ✅ DONE | `IO_WRITE` events recorded to ledger |
| Tool I/O Injection | ✅ DONE | Kernel auto-injects `io_service` into tools with `set_io_service()` |
| `EphemeralUIPlugin` | ✅ DONE | Uses `kernel.io.write_document()` |
| `GitHistoryPlugin` | ✅ DONE | Uses `kernel.io.write_document()` |
| `DocRenderer` | ✅ DONE | Accepts `io_service` param, uses it for writes |
| `MarkdownUIManager` | ✅ DONE | Passes `kernel.io` to DocRenderer |
| `SettingsUIPlugin` | ✅ DONE | Initializes DocRenderer with `kernel.io` |
| `EnvoyUIPlugin` | ✅ DONE | Initializes DocRenderer with `kernel.io` |
| Kernel `_pulse()` | ✅ DONE | Uses `kernel.io.write_snapshot()` |
| `scribe_tool.py` | ✅ DONE | Uses `_write_content()` → `kernel.io` when injected |
| `manifesto.py` | ✅ DONE | Accepts optional `io_service` param, falls back to direct |

### 8.2 Security Exceptions (Intentional Direct Writes)

These components write files directly for SECURITY reasons - this is correct behavior:

| Component | File | Reason |
|-----------|------|--------|
| `identity_tool.py` | `steward/system_agents/herald/tools/` | Private keys must NOT be logged in audit trail |

### 8.3 NOT Migrated ❌

These components still write files directly and need migration:

| Component | File | Direct Writes |
|-----------|------|---------------|
| `memory.py` | `steward/system_agents/herald/core/` | 1x `f.write()` |
| `agenda_tools.py` | `vibe_core/tools/` | 3x `.write_text()` |
| `task_manager.py` | `vibe_core/task_management/` | 2x `.write_text()` |
| `envoy_sync.py` | `vibe_core/` | 1x `.write_text()` |
| `settings_sync.py` | `vibe_core/` | 1x `.write_text()` |
| Various agent tools | `steward/system_agents/*/tools/` | Multiple |

### 8.4 Enforcement Status

| Enforcement | Status |
|-------------|--------|
| Lint Rule (ruff) | ❌ NOT IMPLEMENTED |
| Architecture Test | ❌ NOT IMPLEMENTED |
| Pre-commit Hook | ❌ NOT IMPLEMENTED |

---

## 9. Summary

| Principle | Description |
|-----------|-------------|
| **Single Writer** | Only `KernelIOService` writes files |
| **Content Production** | Plugins produce content, don't write |
| **Atomic Operations** | All writes are atomic (temp + rename) |
| **Locking** | File locks prevent race conditions |
| **Audit Trail** | All writes recorded to ledger |
| **Enforcement** | Lint rules + tests prevent violations |

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2025-12-05 | Claude (Opus) | Initial architecture design |
| 2025-12-05 | Claude (Opus) | Implemented audit trail (ledger recording) |
| 2025-12-05 | Claude (Opus) | Migrated DocRenderer to use io_service |
| 2025-12-05 | Claude (Opus) | Added honest migration status section |
| 2025-12-05 | Claude (Opus) | Migrated herald agent tools (scribe, manifesto) |
| 2025-12-05 | Claude (Opus) | Added kernel auto-injection for tools with `set_io_service()` |
| 2025-12-05 | Claude (Opus) | Documented security exceptions (identity_tool private keys) |
