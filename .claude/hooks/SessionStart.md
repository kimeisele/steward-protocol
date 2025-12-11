# STEWARD Protocol - Claude Code SessionStart Hook

## Purpose

Ensures git hooks are active in every Claude Code Web session.
Without this, kernel protection (VISNU) is BYPASSED.

## What It Does

```bash
git config --local core.hooksPath .githooks
```

This enables the native git pre-commit hook which calls `restore_kernel.sh`
to auto-revert any changes to Security Ring 0 (21 protected files).

## Installation

### Option 1: Copy to ~/.claude/hooks/ (Recommended)

```bash
cp .claude/hooks/session-start.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/session-start.sh
```

### Option 2: Symlink

```bash
ln -sf "$(pwd)/.claude/hooks/session-start.sh" ~/.claude/hooks/session-start.sh
```

## GAD-000 Compliance

This hook outputs machine-parseable JSON:

```json
{"hook":"session-start","status":"configured","message":"Git hooks enabled - kernel protection active","action":"set_hooks_path"}
```

Status values:
- `ok` - Hooks already configured
- `configured` - Hooks just enabled
- `skip` - Not in steward-protocol repo
- `error` - Failed to configure

## Protected Files (21 total)

- 7 kernel: kernel_impl.py, kernel_ops.py, plugin_protocol.py, plugin_loader.py, narasimha.py, capability_registry.py, bridge.py
- 3 governance: restore_kernel.sh, verify_kernel.py, kernel_hashes.json
- 10 workflows: All .github/workflows/*.yml
- 1 config: .pre-commit-config.yaml

See: docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md
