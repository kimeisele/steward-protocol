# OPUS Architecture Documents

This folder contains architectural analysis and refactoring plans created by Claude Opus.

## Purpose

When the system is stuck, broken, or needs deep refactoring - these documents capture:
- Root cause analysis
- Extraction plans
- Migration strategies
- Success criteria

## Current Status

| Doc | Title | Status | Priority |
|-----|-------|--------|----------|
| 001 | Kernel Extraction | Draft | P0 |
| 002 | Phoenix Config Optimization | Planned | P0 |
| 003 | Test Suite Refactor | Planned | P1 |

## The Core Problem (2025-12-06)

**Symptom:** Tests hang, everything is slow, changes break random things.

**Root Cause:** The "kernel" is not a kernel - it's a monolith. 1705 LOC doing everything.

**Solution:** Extract to true microkernel + plugins pattern.

## Manifest

See `manifest.json` for machine-readable document index.

## Philosophy

> "The kernel should be so simple that you can hold it in your head."

A real OS kernel does:
1. Process scheduling
2. Memory management
3. Hardware abstraction
4. IPC

Our kernel should do:
1. Agent scheduling (tick)
2. Resource management (via plugins)
3. I/O abstraction (io_service)
4. Plugin communication (event bus)

Everything else is a plugin.
