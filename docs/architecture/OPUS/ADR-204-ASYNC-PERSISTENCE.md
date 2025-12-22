# ADR-204: Async State Persistence

**Status**: DRAFT
**Date**: 2025-12-22
**Author**: Gemini (YOLO Mode)
**Supersedes**: N/A
**Related**: OPUS-203 (Unified Async Kernel), OPUS-096 (Weaver)

---

## Executive Summary

The current `StateService` triggers Git commits synchronously within the Kernel's `pulse()` loop. This causes significant latency (1-2 seconds per tick) and blocks the heart rate of the system.

**Decision**: Decouple state writing from Git persistence using a background task/worker pattern.

---

## Problem Statement

### The "Lazy Scribe" Pattern
Currently, every `StateService.save()` or `KernelIOService.write_snapshot()` call triggers:
`save()` → `mark_dirty()` → `_maybe_auto_commit()` → `subprocess.run(["git", "commit"])` (BLOCKING).

In a 76MB repository, this blocking call can take seconds, effectively "lobotomizing" the kernel during persistence.

---

## Decision

### Decoupled Background Persistence
1.  **Non-Blocking Writes**: `save()` will write the file and mark it as dirty but will **NOT** trigger a commit immediately.
2.  **Background Committer**: A dedicated asyncio task will monitor dirty files and perform commits at a lower frequency (e.g., every 60s) or when the kernel is idle.
3.  **Thread-Safe Queue**: All dirty file notifications move into a queue processed by the background worker.

---

## Implementation Plan

### Phase 1: Async StateService
- Modify `StateService` to support an `asyncio` background task.
- Change `_maybe_auto_commit` to be a non-blocking request to the background worker.

### Phase 2: Kernel Integration
- Register the persistence task in `RealVibeKernel.boot_async()`.
- Ensure clean shutdown of the persistence task in `RealVibeKernel.shutdown_async()`.

### Phase 3: Weaver Optimization
- Move `Weaver.pulse()` execution to the background task.

---

## Validation

- Kernel tick speed should remain < 100ms even during large commits.
- `vibe_snapshot.json` updates should not trigger immediate Git activity.
