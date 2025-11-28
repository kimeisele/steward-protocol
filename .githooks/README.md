# Steward Protocol Git Hooks

## Installation

Git hooks in `.githooks/` are NOT automatically activated (they need to be in `.git/hooks/`).

To install the hooks:

```bash
# Option 1: Symlink (recommended - auto-updates)
ln -sf ../../.githooks/pre-commit .git/hooks/pre-commit

# Option 2: Copy (manual updates needed)
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Hooks

### `pre-commit` - The Electric Fence (Phase 3.1)

**Purpose:** Block architectural violations before they get committed.

**Performance:** <50ms (fast pattern matching, no agent boot)

**Guards:**
1. ❌ Block `requirements.txt` in `steward/system_agents/*/`
2. ❌ Block `Path("data/...")` patterns
3. ⚠️  Warn about hardcoded paths in `__init__()`

**Example output:**

```
⚡ Running Steward Protocol Pre-Commit Guards...
  🔍 Checking for requirements.txt in agent dirs... OK
  🔍 Checking for direct Path('data/...') calls... OK
  🔍 Checking for hardcoded paths in __init__... OK
✅ All pre-commit guards passed
```

**If blocked:**

```
❌ VIOLATION: Direct Path('data/...') detected

Violations found:
  • steward/system_agents/foo/cartridge_main.py:42: self.data = Path("data/foo")

To fix:
  1. Use agent.system.get_sandbox_path() instead
  2. Convert to lazy-loading @property pattern
  3. See Phase 2.3 migration examples (Herald, Forum, Civic)
```

## Bypassing Hooks (Emergency Only)

```bash
# Skip pre-commit (use only in emergencies)
git commit --no-verify

# NEVER use --no-verify to bypass architecture violations!
# The CI/CD will still catch you (Watchman + Auditor)
```

## Defense in Depth

The pre-commit hook is **Layer 1** of a 3-layer defense:

1. **Pre-Commit** (this) - Fast pattern matching, blocks 95% of violations
2. **Watchman** (CI/CD) - AST-based deep analysis via StandardsInspectionTool
3. **Auditor** (CI/CD) - Constitutional verdict, build gate

See: `docs/AGENT_CLI_ENFORCEMENT_PLAN.md`
