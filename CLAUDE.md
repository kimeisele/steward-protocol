# CLAUDE.md - AI Interaction Guide for Steward Protocol

**Created:** 2026-02-03  
**Status:** Evidence-based documentation for AI assistants  
**Philosophy:** Trust only what's in the code, not assumptions

---

## 🔧 Build/Run Commands

**Evidence Source:** `Makefile` (lines 1-69), `pyproject.toml` (lines 80-82)

### Installation
```bash
# Using pip (standard)
pip install -e ".[dev]"

# Using uv (if available)
uv sync
```

### Boot & Run
```bash
# Main entry point (CLI)
steward boot              # Start the kernel daemon
steward status           # Check system health
steward introspect       # Deep kernel inspection

# Alternative entry points (found in root directory)
python boot.py           # Binary entry point
python run.py            # Simple runner
python run_server.py     # Server mode
```

### Development Workflow
```bash
# Linting (VERIFIED in Makefile line 37-38)
make lint                # ruff check vibe_core scripts

# Formatting (VERIFIED in Makefile line 40-42)
make format              # ruff format + ruff check --fix

# Cleanup (VERIFIED in Makefile line 52-56)
make clean              # Remove build artifacts, __pycache__, etc.

# Container building (VERIFIED in Makefile line 45-49)
make containers         # Build all .vibe containers
make containers-inplace # Build containers in-place
```

---

## 🧪 Testing

**Evidence Source:** `Makefile` (lines 20-34), `pyproject.toml` (lines 89-150)

### Test Commands (VERIFIED)
```bash
# Fast tests only
make test               # pytest --test-profile=fast

# Full test suite with coverage
make test-full          # pytest --test-profile=full

# CI-optimized tests
make test-ci            # pytest --test-profile=ci

# Unit tests only
make test-unit          # pytest --test-profile=unit

# Integration tests only
make test-integration   # pytest --test-profile=integration
```

### Test Framework Details
- **Runner:** pytest (v7.4.0+)
- **Async:** pytest-asyncio (asyncio_mode = "auto")
- **Timeout:** 120 seconds per test (SATYA enforcement)
- **Location:** `tests/` directory
- **Pattern:** `test_*.py` files only
- **Excluded:** `tests/archive/`, `tests/fractal/` (broken/legacy)

### Test Quality Settings (OPUS-060 SATYA: Truth Enforcement)
- **Strict Mode:** Unknown markers = IMMEDIATE FAILURE
- **No Silent Failures:** All failures must be loud
- **Markers Required:** All markers must be registered in pyproject.toml
- **Warning Filters:** Treats unknown marks as errors

---

## 📚 Tech Stack (Core Technologies Actually Used)

**Evidence Source:** Code inspection, `pyproject.toml` dependencies

### Language & Runtime
- **Python:** 3.9+ (minimum version from pyproject.toml line 10)
- **Build System:** hatchling (pyproject.toml lines 2-3)

### Core Framework (VERIFIED imports in codebase)
- **FastAPI:** Web framework (gateway/api.py line 14-22)
- **Uvicorn:** ASGI server (gateway/api.py line 40)
- **Pydantic:** Data validation (found in protocols/)
- **PyYAML:** Configuration (pyproject.toml line 37)

### Cryptography & Security (VERIFIED in dependencies)
- **ecdsa:** Elliptic curve signatures (pyproject.toml line 38)
- **cryptography:** Core crypto operations (pyproject.toml line 41)
- **msgpack:** NAGA wire protocol (pyproject.toml line 39)

### AI/LLM (OPTIONAL - not always loaded)
- **openai:** LLM provider (found in runtime/providers/)
- **google-generativeai:** Alternative LLM (pyproject.toml line 61)
- **sentence-transformers:** OPTIONAL (commented out, line 46-47)

### Development Tools
- **ruff:** Linting + formatting (pyproject.toml lines 158-206)
- **pre-commit:** Git hooks (`.pre-commit-config.yaml`)
- **pytest:** Testing framework with plugins

### Infrastructure
- **SQLite:** Embedded database (Dockerfile line 6)
- **Docker:** Containerization (Dockerfile exists)
- **Git:** Version control (numerous git scripts)

---

## 📝 Naming Conventions (What's Really Used)

**Evidence Source:** Direct code inspection of `vibe_core/kernel_impl.py`, `gateway/api.py`

### Python Code Style
- **Indentation:** 4 spaces (NO TABS) - Verified via cat -A
- **Semicolons:** NONE (Python standard)
- **Line Length:** 120 characters (ruff config line 159)
- **Quotes:** Double quotes (ruff format config line 204)

### Variable Naming
- **Functions/Methods:** `snake_case` (e.g., `_get_config`, `cli_entry`)
- **Classes:** `PascalCase` (e.g., `RealVibeKernel`, `FastAPI`)
- **Constants:** `UPPERCASE_SNAKE_CASE` (e.g., `__mahajana__`, `PROJECT_ROOT`)
- **Private:** Prefix with `_` (e.g., `_get_config`, `_cors_origins`)

### File Naming
- **Modules:** `snake_case.py` (e.g., `kernel_impl.py`, `event_bus.py`)
- **Special:** Dunder files like `__init__.py`

### Module Structure Patterns
- Every module has a "MAHAJANA DECLARATION" comment block:
  ```python
  # === MAHAJANA DECLARATION (machine-readable) ===
  __mahajana__ = "brahma"
  __position__ = 1
  __genesis__ = "0x..."  # GenesisByte: parampara % 37 == 0
  ```
  This is a **CORE PATTERN** - do not remove or modify these declarations.

---

## 🏗️ Architecture/Structure

**Evidence Source:** Directory listing, code inspection

### Architecture Style
**Domain-Driven + Plugin-Based Kernel Architecture**

This is NOT a typical framework. It's an actual operating system for AI agents with:
- Real kernel (`vibe_core/kernel_impl.py`) with process table
- Plugin system (`.vibe` containers)
- Constitutional governance (immutable rules)
- Cryptographic identity per agent

### Directory Structure
```
steward-protocol/
├── vibe_core/              # Core kernel implementation (~102k LOC)
│   ├── kernel_impl.py      # Actual kernel (not a mock)
│   ├── protocols/          # ABCs and interfaces
│   ├── mahamantra/         # Core services (16 mahajanas)
│   ├── cartridges/         # Agent implementations
│   ├── cli/                # Command-line interface
│   ├── gateway/            # FastAPI web gateway
│   ├── llm/                # LLM provider abstraction
│   ├── naga/               # Security/crypto layer
│   ├── phoenix/            # Configuration system
│   ├── shuddhi/            # Code analysis/healing
│   ├── vajra/              # Dependency injection
│   └── ...                 # Many more subsystems
├── gateway/                # Web API entry point
│   ├── api.py              # FastAPI application
│   └── takshaka_lite.py    # Security verification
├── tests/                  # Test suite
│   ├── integration/        # Integration tests
│   ├── security/           # Security tests
│   └── archive/            # Excluded from runs
├── scripts/                # Utility scripts (100+ files)
├── docs/                   # Documentation
├── boot.py                 # Main entry point
├── pyproject.toml          # Python project config
├── Makefile                # Build commands
└── Dockerfile              # Container definition
```

### Key Architectural Concepts
1. **Kernel-First:** Everything goes through the kernel (no bypassing)
2. **Immutable Ledger:** All events logged to append-only chain
3. **Plugin-Based:** Extensions as `.vibe` containers
4. **Lazy Loading:** Heavy imports deferred (boot.py pattern)
5. **Mahajana System:** 16 "guardians" manage different system aspects
6. **Constitutional:** Rules enforced at architecture level, not prompts

### Feature Organization
- **Feature-based** (e.g., `naga/` for security, `phoenix/` for config)
- **NOT MVC** - More like microkernel with services
- **Plugin Cartridges** in `vibe_core/cartridges/`

---

## ⚠️ DO NOT (Critical Constraints)

### Code Modification Rules
1. **NEVER modify kernel protection files** - Pre-commit hook will auto-restore:
   - `scripts/governance/restore_kernel.sh`
   - `scripts/governance/verify_kernel.py`
   - `.github/workflows/*.yml`
   - `.pre-commit-config.yaml`
   
2. **NEVER bypass kernel in tests:**
   - ❌ `RealVibeKernel()` directly
   - ✅ `TestKernel.minimal()` or `TestKernel.with_plugins()`
   - Pre-commit hook enforces this (`.pre-commit-config.yaml` lines 64-74)

3. **NEVER remove MAHAJANA declarations:**
   - Every module has `__mahajana__`, `__position__`, `__genesis__`
   - These are machine-readable system metadata
   - Removing them breaks the lineage system

4. **NEVER commit secrets:**
   - `.env` files are gitignored
   - `*.pem`, `*.key` files excluded
   - `data/security/master.key` must never be committed

### Testing Rules
1. **NEVER skip test failures silently** (SATYA protocol)
2. **NEVER use unknown pytest markers** (strict mode enabled)
3. **NEVER run tests from `tests/archive/` or `tests/fractal/`** (excluded in config)

### Code Style Rules
1. **NEVER use tabs** - Always 4 spaces
2. **NEVER exceed 120 char line length** (ruff enforced)
3. **NEVER add semicolons** (Python convention)
4. **NEVER use single quotes for strings** (ruff: double quotes preferred)

### Import Rules
1. **NEVER import from deprecated bridges** - Use canonical sources:
   - ❌ `from vibe_core.lineage import LineageChain`
   - ✅ `from vibe_core.mahamantra import LineageChain`
   
2. **NEVER import heavy libraries at module level** (lazy loading pattern)
3. **NEVER bypass the `mahamantra` entry point** in boot.py

### Architectural Rules
1. **NEVER add features to kernel directly** - Use plugins
2. **NEVER bypass the event bus** - All events must be logged
3. **NEVER modify the immutable ledger structure**
4. **NEVER hardcode paths** - Use Path objects and PROJECT_ROOT

---

## 🔍 Common Patterns (What to Expect)

### 1. SSOT Proxies (Single Source of Truth)
Many files are just re-exports from canonical locations:
```python
# DEPRECATED: Use canonical import
from vibe_core.mahamantra import ProcessManager
```
**Pattern:** Old files redirect to new centralized locations

### 2. Lazy Loading
Heavy imports deferred to runtime:
```python
def __getattr__(name: str):
    if name == "HeavyModule":
        from . import heavy_module
        return heavy_module
```
**Why:** Fast boot times (<0.5s for help display)

### 3. Type Checking Imports
```python
if TYPE_CHECKING:
    from vibe_core.boot_mode import BootMode
```
**Pattern:** Imports only for type hints, not runtime

### 4. Docker Path Fixes
```python
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```
**Why:** Ensures imports work in Docker containers

### 5. Migration Comments
You'll see MANY deprecation notices:
```python
# DEPRECATED: Phase 4 Migration to Mahamantra
# MIGRATION PATH: Use mahamantra.<quarter>.<mahajana>
```
**Meaning:** Codebase is actively being refactored but old code still works

---

## 📊 Codebase Statistics (Evidence-Based)

- **Total Python LOC:** ~102,000 lines (verified via wc -l)
- **Main Package:** `vibe_core/` (34+ subdirectories)
- **Scripts:** 100+ utility scripts in `scripts/`
- **Tests:** Integration + security + unit tests
- **Documentation:** 80+ markdown files in root
- **Test Count:** "3800 passed" (from README badge)

---

## 🚨 Known Issues/Warnings

### Inconsistencies Found
1. **Deprecated Code Present:**
   - Many "DEPRECATED" proxies still in use
   - Migration to "mahamantra" pattern ongoing
   - Old imports still work but discouraged

2. **Exclusions in Test Suite:**
   - `tests/archive/` - Legacy tests (excluded)
   - `tests/fractal/` - Missing framework (excluded)
   - These are INTENTIONALLY skipped

3. **Optional Dependencies:**
   - `sentence-transformers` commented out (line 46-47)
   - Local LLM support optional
   - Some imports may fail if extras not installed

### Security Context
- **Ring 0 Protection:** Kernel files protected by pre-commit hook
- **Auto-Restore:** Changes to governance files automatically reverted
- **Signature Verification:** All `.vibe` containers must be signed

---

## 💡 Development Philosophy

**From the code evidence:**

1. **"Trust No One"** - Verification over configuration
2. **"Kernel is Eternal"** - Core protected from modification
3. **"Satyam Eva Jayate"** (Truth Alone Triumphs) - No silent failures
4. **"The Thin Kernel"** - Binary ships minimal, extend at runtime
5. **Constitutional Governance** - Rules in architecture, not prompts

**This is not a typical Python project.** It's a complete operating system for AI agents with cryptographic guarantees, immutable audit logs, and architectural enforcement of governance rules.

---

## 📚 Additional Resources

- **Main Docs:** 80+ `.md` files in root (ARCHITECTURE.md, KERNEL.md, etc.)
- **Architecture:** `docs/` directory
- **Examples:** `scripts/` directory has many working examples
- **Config:** `pyproject.toml` has complete dependency list
- **Tests:** `tests/` directory shows usage patterns

---

**Last Updated:** 2026-02-03  
**Generated By:** Evidence-based analysis of codebase  
**Confidence Level:** HIGH - All claims verified against actual files
