# Steward Protocol Git Hooks

## Installation

Git hooks in `.githooks/` are NOT automatically activated (they need to be in `.git/hooks/`).

**Recommended:** Use the automated installer:

```bash
# Check if hooks are installed
python scripts/setup_hooks.py

# Auto-install/repair hooks
python scripts/setup_hooks.py --fix
```

**Manual installation:**

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
4. 🎨 Auto-format + auto-fix with **ruff** (replaces black + isort + flake8)
   - Formats code to 120 char line length
   - Fixes import sorting automatically
   - Catches critical syntax errors (E9, F63, F7, F82)

**Tools:** `ruff` (single unified tool - replaced black, flake8, isort)

**Example output:**

```
⚡ Running Steward Protocol Pre-Commit Guards...
  🔍 Checking for requirements.txt in agent dirs... OK
  🔍 Checking for direct Path('data/...') calls... OK
  🔍 Checking for hardcoded paths in __init__... OK
  🎨 Running ruff format + check... OK (auto-formatted + checked)
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

## Migration to Ruff (Phase 3.6)

**What changed:**
- Replaced `black`, `flake8`, and `isort` with single `ruff` tool
- All configuration now in `pyproject.toml` (SSOT)
- 10-100x faster linting and formatting
- Same or better error detection
- Simpler dependency management (1 tool instead of 3)

**For developers:**
```bash
# Format code locally (optional, CI enforces)
ruff format .

# Check for issues
ruff check .

# Auto-fix safe issues
ruff check --fix .
```

**CI enforcement:** All linting enforced in CI - local hook installation is optional.

---

## Bypassing Hooks (Emergency Only)

```bash
# Skip pre-commit (use only in emergencies)
git commit --no-verify

# NEVER use --no-verify to bypass architecture violations!
# The CI/CD will still catch you (Watchman + Auditor)
```

## Defense in Depth

The pre-commit hook is part of a **4-layer defense** architecture:

0. **Infrastructure Health** (Layer 0) - Foundation checks
   - `scripts/setup_hooks.py` - Hook installation/repair (operator-run)
   - WATCHMAN `system_health` check - Read-only monitoring (agent)
   - CI job: `infrastructure-check`

1. **Pre-Commit** (Layer 1) - Fast pattern matching, blocks 95% of violations
   - `.githooks/pre-commit` - grep-based, <50ms
   - Guards against: requirements.txt, Path("data/..."), hardcoded paths

2. **Watchman** (Layer 2) - AST-based deep analysis via StandardsInspectionTool
   - CI job: `watchman-inspection`
   - Detects: architectural violations, mock returns, placeholders

3. **Auditor** (Layer 3) - Constitutional verdict, build gate
   - CI job: `auditor-verdict`
   - Enforces: STEWARD.md, steward.json, VibeAgent protocol

## AGENT CITY Architecture

This follows AGENT CITY principles:

- **Layer 0 (Infrastructure)**: Operator-run scripts in `scripts/`
  - `scripts/setup_hooks.py` modifies `.git/hooks/` (requires filesystem access)
  - WATCHMAN agent monitors (read-only) via `system_health` action

- **Layers 1-3 (Enforcement)**: Kernel-integrated agents
  - WATCHMAN: Code quality enforcement
  - AUDITOR: Constitutional compliance

**Philosophy**: "Agents monitor. Operators execute infrastructure changes."

See: `docs/AGENT_CLI_ENFORCEMENT_PLAN.md`
