# CLAUDE.md: AI Agent Onboarding for Steward Protocol

**For:** Claude, GPT, Gemini, and other AI agents working on this codebase  
**Warning Level:** 🔴 **CRITICAL - COMPLEX CODEBASE - TRUST NOTHING**  
**Last Updated:** 2026-02-03  
**Philosophy:** "In a complex codebase, you can trust nothing and no one. Verify everything."

---

## 🚨 CRITICAL: READ THIS FIRST

This is **not** a typical project. This is a complex, self-governing AI agent operating system with:

- **36 fundamental rights** enforced at the architecture level
- **Cryptographic verification** on every action
- **Immutable audit logs** that track all changes
- **Constitutional governance** that can reject bad code
- **Self-healing mechanisms** that rebuild corrupted components
- **Kill-switch protocols** that terminate rogue processes

**The core principle:** Code that "promises" to be safe is insecure. Code that *cannot* violate constraints is trustworthy.

### Your Role

You are not just editing code. You are operating within a **governed system** where:

1. **Every change is audited** in an immutable ledger
2. **Every file has guardians** (some files are cryptographically protected)
3. **Tests are non-negotiable** - 3800+ tests must pass
4. **The system will resist** unauthorized changes through pre-commit hooks
5. **Trust is cryptographic** - not based on good intentions

---

## 🎯 MENTAL MODEL: The Three Layers of Reality

Understanding this system requires three distinct perspectives:

### Layer 0: The Constitution (Immutable)
**Location:** `CONSTITUTION.md`

- **36 Dharmas (6×6 Matrix):** The fundamental rights (Identity, Audit, Governance, Transparency, Consent, Interoperability)
- **The 37th (Sovereign):** The human/agent who signs and takes responsibility
- **4 Regulating Principles:** Daya (Data Purity), Satyam (Truth), Tapas (Resource Discipline), Saucam (Connection Purity)

**Rule:** These cannot be violated. The architecture enforces them, not prompts.

### Layer 1: The Kernel (Operating System)
**Location:** `vibe_core/kernel_impl.py` (1870 LOC, target: 1080)

The kernel is like Linux for AI agents:
- Process table and scheduler
- Virtual filesystem sandboxing
- Immutable ledger integration
- Kill-switch for rogue agents
- Event bus for communication

**Rule:** The kernel is "Vishnu 0" - the foundation. Changes require extreme caution.

### Layer 2: The Federation (Agents & Plugins)
**Location:** `vibe_core/plugins/`, `vibe_core/agents/`

- 50+ plugins providing capabilities
- 1 certified agent (ENVOY) with 24 circuits
- Capability-based security model
- Hot-swappable components

**Rule:** Plugins can be modified more freely, but must respect kernel protocols.

---

## 📋 ESSENTIAL READING (In Order)

Before making ANY changes, read these files:

### 1. Foundation Documents (30 min)
- [ ] `README.md` - System overview and quick start
- [ ] `CONSTITUTION.md` - The supreme law (understand the 36+4+37 structure)
- [ ] `ARCHITECTURE.md` - Component overview
- [ ] `KERNEL.md` - Kernel refactoring plan and constraints

### 2. Architecture Guides (45 min)
- [ ] `PROMPT.md` - Vedic philosophy + German precision = Architecture rules
- [ ] `pyproject.toml` - Project identity, dependencies, test configuration
- [ ] `vibe_core/protocols/kernel_protocol.py` - The kernel interface
- [ ] `vibe_core/kernel_impl.py` - The heart (scan structure, don't read all 1870 lines)

### 3. Security & Testing (30 min)
- [ ] `tests/hardening/` - Red team attack simulations (shows what matters)
- [ ] `.pre-commit-config.yaml` - Quality gates
- [ ] `vibe_core/narasimha.py` - Kill-switch implementation

### 4. Your Specific Domain
Depending on your task, read the relevant plugin or service:
- Governance: `vibe_core/plugins/vedic_governance/`
- Economy: `vibe_core/plugins/economy/`
- Cognition: `vibe_core/plugins/opus_assistant/`
- Security: `vibe_core/services/capability_enforcer.py`

---

## ⚠️ TRUST NOTHING: Verification Protocol

In a complex codebase, assumptions are dangerous. Follow this protocol:

### Before Changing Code

```bash
# 1. Verify you understand the current state
git status
git log --oneline -10
git diff

# 2. Verify tests pass BEFORE your changes
pytest tests/ -v --tb=short -x

# 3. Understand the architecture
ruff check vibe_core/  # Should show current violations
ruff format vibe_core/ --check  # Should show formatting issues

# 4. Check if files are protected
cat .pre-commit-config.yaml | grep -A 20 "git-gatekeeper"
# Protected files require explicit authorization
```

### After Changing Code

```bash
# 1. Format and lint
ruff format .
ruff check . --fix

# 2. Run affected tests
pytest tests/test_<your_component>.py -v

# 3. Run security tests
pytest tests/hardening/ -v --tb=short

# 4. Verify no regressions
pytest tests/ -x  # Stop on first failure

# 5. Check git diff
git diff  # Review every line you changed
git add -p  # Stage changes interactively

# 6. Commit with meaningful message
git commit -m "type(scope): description"
```

### Verification Checklist

For EVERY change, verify:

- [ ] **No circular imports:** Check with `ruff check --select I`
- [ ] **No `Any` types:** Protocols exist for everything (see `vibe_core/protocols/`)
- [ ] **Signature chain exists:** Can you trace action back to a sovereign key?
- [ ] **Tests added/updated:** If behavior changes, tests must change
- [ ] **Docs updated:** If public API changes, docs must change
- [ ] **No silent failures:** Every error must be logged and handleable
- [ ] **Idempotent operations:** Can the operation be safely retried?
- [ ] **Ledger integration:** Is the change auditable?

---

## 🏗️ ARCHITECTURE PATTERNS

### The Protocol Pattern (Dependency Inversion)

**Bad (Creates circular dependencies):**
```python
from vibe_core.kernel_impl import RealVibeKernel

class MyPlugin:
    def __init__(self, kernel: RealVibeKernel):
        self.kernel = kernel
```

**Good (Uses protocols):**
```python
from vibe_core.protocols.kernel_protocol import KernelProtocol

class MyPlugin:
    def __init__(self, kernel: KernelProtocol):
        self.kernel = kernel
```

**Why:** Protocols enable hot-swapping and break circular imports.

### The Arjuna Pattern (Self-Healing)

**Bad (Crashes on missing dependency):**
```python
def process(self):
    result = self.external_service.call()  # Crashes if None
    return result
```

**Good (Self-heals):**
```python
def process(self):
    if self.external_service is None:
        self.external_service = self._initialize_service()
    return self.external_service.call()
```

**Why:** Systems must survive component failure and rebuild gracefully.

### The ServiceRegistry Pattern (Dependency Injection)

**Bad (Singleton hell):**
```python
config = GlobalConfig.get_instance()  # Global state, untestable
```

**Good (Registry lookup):**
```python
from vibe_core.di import ServiceRegistry
from vibe_core.protocols.config import ConfigProtocol

config = ServiceRegistry.get(ConfigProtocol)
```

**Why:** Testable, replaceable, no global state.

### The Ledger Pattern (Event Sourcing)

**Bad (Direct state mutation):**
```python
agent.karma_score = 100  # Lost to history
```

**Good (Logged mutation):**
```python
kernel.ledger.append_event({
    "type": "karma_updated",
    "agent_id": agent.id,
    "old_value": agent.karma_score,
    "new_value": 100,
    "signed_by": operator_key
})
agent.karma_score = 100
```

**Why:** Every change is auditable and reconstructible.

---

## 🔒 SECURITY MODEL

### Capability-Based Security

Permissions are **granted explicitly**, never assumed:

```python
# Check capability before action
if not kernel.has_capability(agent_id, "network:egress"):
    raise PermissionError("Agent lacks network egress capability")

# Perform action
result = make_network_call()

# Log action
kernel.ledger.append_event({
    "type": "network_call",
    "agent_id": agent_id,
    "capability": "network:egress",
    "destination": url
})
```

### The Kill-Switch (Narasimha)

If an agent violates governance:

```
Threat Level:  GREEN → YELLOW → ORANGE → RED → CRITICAL
                                                  ↓
                                        Kill-switch activates
                                                  ↓
                                        Instant termination
```

**Implementation:** `vibe_core/narasimha.py`

### Protected Files

21 kernel files are cryptographically guarded. Check before modifying:

```bash
# View protected files
cat .pre-commit-config.yaml | grep -A 30 "git-gatekeeper"

# If you must modify protected files:
# 1. Understand WHY they're protected
# 2. Read KERNEL.md for the refactoring plan
# 3. Use --no-verify only with explicit authorization
```

---

## 🧪 TESTING PHILOSOPHY

### Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| **Unit Tests** | `tests/test_*.py` | Component behavior |
| **Integration Tests** | `tests/test_*_integration.py` | System interaction |
| **Hardening Tests** | `tests/hardening/` | Security, chaos, stress |
| **Red Team Tests** | `tests/hardening/test_red_team_*.py` | Attack simulations |

### The Satya Principle (OPUS-060)

**"Satyam Eva Jayate" - Only truth prevails.**

Tests **cannot** silently fail:

```toml
# From pyproject.toml
[tool.pytest.ini_options]
addopts = "--strict-markers"  # Unknown markers = immediate failure
timeout = 120  # Hanging tests = failure
filterwarnings = [
    "error::pytest.PytestUnknownMarkWarning",  # Unknown markers = ERROR
]
```

### Running Tests

```bash
# Quick smoke test
pytest tests/test_kernel.py -v

# Full suite
pytest tests/ -v

# Security/hardening
pytest tests/hardening/ -v

# Specific category
pytest -m "fast" -v  # Only fast tests
pytest -m "not slow" -v  # Exclude slow tests

# With coverage
pytest tests/ --cov=vibe_core --cov-report=term-missing
```

---

## 🚀 COMMON TASKS

### Task 1: Add a New Plugin

```bash
# 1. Create plugin directory
mkdir -p vibe_core/plugins/my_plugin

# 2. Create plugin_main.py
cat > vibe_core/plugins/my_plugin/plugin_main.py << 'EOF'
from vibe_core.protocols.kernel_protocol import KernelProtocol
from vibe_core.plugin_protocol import PluginProtocol

class MyPlugin(PluginProtocol):
    def __init__(self):
        self.name = "my_plugin"
    
    async def on_boot(self, kernel: KernelProtocol):
        # Plugin initialization
        pass
    
    async def on_shutdown(self, kernel: KernelProtocol):
        # Cleanup
        pass
EOF

# 3. Register in config
# Edit steward.yaml to add your plugin

# 4. Write tests
cat > tests/test_my_plugin.py << 'EOF'
import pytest
from vibe_core.plugins.my_plugin.plugin_main import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin()
    assert plugin.name == "my_plugin"
EOF

# 5. Test
pytest tests/test_my_plugin.py -v
```

### Task 2: Modify Existing Code

```bash
# 1. Create branch
git checkout -b feature/my-change

# 2. Run tests BEFORE (establish baseline)
pytest tests/test_affected_component.py -v > before.txt

# 3. Make changes
# Edit files...

# 4. Run tests AFTER
pytest tests/test_affected_component.py -v > after.txt

# 5. Compare
diff before.txt after.txt

# 6. If tests pass, commit
git add .
git commit -m "feat(component): description of change"
```

### Task 3: Debug a Failing Test

```bash
# 1. Run single test with full traceback
pytest tests/test_something.py::test_specific_case -vv --tb=long

# 2. Add debug logging
pytest tests/test_something.py -vv --log-cli-level=DEBUG

# 3. Drop into debugger on failure
pytest tests/test_something.py --pdb

# 4. Check test isolation
pytest tests/test_something.py -v --forked  # Run in separate process
```

### Task 4: Add a Security Check

```bash
# 1. Study existing hardening tests
cat tests/hardening/test_red_team_attacks.py

# 2. Create new test
cat > tests/hardening/test_my_security.py << 'EOF'
import pytest
from vibe_core.kernel_impl import RealVibeKernel

def test_prevent_unauthorized_capability_grant():
    kernel = RealVibeKernel(mode="test")
    
    # Attempt to grant capability without permission
    with pytest.raises(PermissionError):
        kernel.grant_capability(
            agent_id="rogue_agent",
            capability="kernel:modify",
            granted_by="untrusted_source"
        )
EOF

# 3. Run
pytest tests/hardening/test_my_security.py -v
```

---

## 🐛 DEBUGGING STRATEGIES

### Strategy 1: Trace Event Flow

```python
# Enable event logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Watch event bus
kernel.event_bus.subscribe("*", lambda event: print(f"EVENT: {event}"))

# Check ledger
for block in kernel.ledger.get_blocks():
    print(f"Block {block['index']}: {block['events']}")
```

### Strategy 2: Inspect Kernel State

```bash
# Boot kernel in debug mode
steward boot --mode=debug

# Introspect
steward introspect

# Check agent registry
steward agents:list

# Check capabilities
steward capabilities:list
```

### Strategy 3: Use the ENVOY Agent

ENVOY is the system's primary interface agent:

```bash
# Ask ENVOY for help
steward run SIMPLE_QUERY "How does the ledger work?"

# System analysis
steward run ARCHITECTURE_ANALYSIS

# Debug specific issue
steward run DEBUG_FIX_V2 "describe the problem"
```

---

## 📊 KEY METRICS TO MAINTAIN

### Code Quality

- **Kernel LOC:** Currently 1870, target 1080 (see `KERNEL.md`)
- **Test Coverage:** Maintain > 80% for core components
- **Ruff Violations:** Zero in `vibe_core/` (run `ruff check vibe_core/`)
- **Type Coverage:** No `Any` types in new code

### Performance

- **Boot Time:** < 5 seconds
- **Event Latency:** < 100ms for critical paths
- **Memory:** < 500MB for kernel + 10 agents
- **Ledger Write:** < 10ms per event

### Security

- **Protected Files:** 21 files (don't increase without justification)
- **Capability Checks:** 100% coverage on privileged operations
- **Signature Verification:** All external inputs verified
- **Attack Surface:** Minimize network exposure

---

## 🎓 VEDIC ARCHITECTURE PHILOSOPHY

This system uses Vedic concepts as architectural metaphors. They're not decoration—they encode real patterns:

### Core Concepts

| Vedic Term | Technical Meaning |
|------------|-------------------|
| **Dharma** | Immutable system laws (Constitution) |
| **Karma** | Event sourcing, action-consequence chains |
| **Prakriti** | Unified state management |
| **Purusha** | The sovereign observer (The 37th) |
| **Maya** | Illusion of direct state (it's all projections) |
| **Arjuna** | Self-healing warrior pattern |
| **Narasimha** | Kill-switch, protector against corruption |
| **Vishnu** | Kernel (the preserver) |
| **Prahlad** | Legitimate user calling for help |

### The Anti-Mayavad Test

Before accepting any code, ask:

> **"Is there a WHO that holds this system, or is it just mirrors reflecting mirrors?"**

**Mayavad (Reject):** Code with no cryptographic chain to a sovereign signer  
**Legitimate (Accept):** Code signed by a verified agent/human with capability tokens

---

## 🔧 TROUBLESHOOTING

### Problem: Tests Failing After Boot

**Diagnosis:**
```bash
# Check if kernel boots at all
steward boot --mode=test

# Check logs
tail -f .vibe/logs/kernel.log

# Verify config
steward system:doctor
```

**Common causes:**
1. Missing dependencies: `uv sync` or `pip install -e ".[dev]"`
2. Corrupted state: `rm -rf .vibe/state` (test mode only!)
3. Plugin conflicts: Check `.vibe/logs/boot.log`

### Problem: Circular Import Error

**Diagnosis:**
```bash
# Find circular imports
ruff check --select I vibe_core/
```

**Solution:**
1. Use protocols instead of concrete classes
2. Move shared types to `vibe_core/protocols/`
3. Use `TYPE_CHECKING` guard for type hints

**Example:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

class MyClass:
    def __init__(self, kernel: 'RealVibeKernel'):  # String annotation
        self.kernel = kernel
```

### Problem: Protected File Modification Blocked

**Diagnosis:**
```bash
# Check which files are protected
cat .pre-commit-config.yaml | grep -A 30 "git-gatekeeper"
```

**Solution:**
1. **Understand why** the file is protected (usually kernel critical)
2. **Read** `KERNEL.md` for refactoring plan
3. **If authorized:** Use `git commit --no-verify`
4. **Never** disable protection permanently

### Problem: Agent Not Receiving Events

**Diagnosis:**
```python
# Check event bus subscriptions
print(kernel.event_bus.get_subscriptions())

# Verify agent is registered
print(kernel.get_all_agents())

# Check if events are being published
kernel.event_bus.subscribe("*", lambda e: print(f"DEBUG: {e}"))
```

**Solution:**
1. Ensure agent subscribed to correct event types
2. Verify event bus is initialized
3. Check if agent has event processing capability

---

## 📚 DOCUMENTATION STANDARDS

### Code Comments

**Use comments for:**
- **Why** (not what): Explain architectural decisions
- **Warnings:** Alert about gotchas or constraints
- **TODOs:** Mark technical debt clearly

**Format:**
```python
# MAYAVAD: This lacks a sovereign signer - fix before production
# TODO(OPUS-123): Extract this to ManifestationService
# WARNING: This operation is NOT idempotent - retry will corrupt state
```

### Docstrings

**Use Google style:**
```python
def register_agent(
    self,
    agent: VibeAgent,
    manifest: AgentManifest,
    signed_by: str
) -> bool:
    """Register a new agent with the kernel.
    
    This is THE GATE - all agents must pass through here.
    Performs governance checks, capability registration,
    and lineage tracking.
    
    Args:
        agent: The agent instance to register
        manifest: Agent's capabilities and metadata
        signed_by: Cryptographic key of authorizing entity
        
    Returns:
        True if registration successful
        
    Raises:
        PermissionError: If signer lacks authority
        ValidationError: If manifest invalid
        
    Note:
        This operation is logged in the immutable ledger.
        The agent receives a unique ID and capability tokens.
    """
```

### Commit Messages

**Format:** `type(scope): description`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructure (no behavior change)
- `docs`: Documentation only
- `test`: Test additions/fixes
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(kernel): add signature verification to events"
git commit -m "fix(ledger): prevent duplicate block append"
git commit -m "refactor(plugins): extract ManifestationService"
git commit -m "docs(CLAUDE): add troubleshooting section"
git commit -m "test(hardening): add SQL injection attack simulation"
```

---

## 🎯 SUCCESS CRITERIA

You know you understand this codebase when you can answer:

### Level 1: Foundation
- [ ] What are the 36 Dharmas and how are they enforced?
- [ ] What is The 37th and why does it matter?
- [ ] Where is the immutable ledger and what does it track?
- [ ] What happens when an agent violates governance?
- [ ] How do capabilities differ from permissions?

### Level 2: Architecture
- [ ] Why use protocols instead of concrete classes?
- [ ] How does the Arjuna pattern enable self-healing?
- [ ] What's the difference between Layer 0, Layer 1, and Layer 2?
- [ ] How does event sourcing work in this system?
- [ ] Why is the kernel being refactored from 2218 to 1080 LOC?

### Level 3: Mastery
- [ ] How would you add a new constitutional principle?
- [ ] How would you implement a new security threat model?
- [ ] How would you debug a circular dependency?
- [ ] How would you optimize event bus latency?
- [ ] How would you migrate state between kernel versions?

---

## 🆘 GETTING HELP

### Internal Resources

1. **ENVOY Agent:** `steward run SIMPLE_QUERY "your question"`
2. **Documentation Index:** `INDEX.md`
3. **Architecture Deep-dives:** `docs/architecture/`
4. **Test Examples:** `tests/` (tests show how to use components)

### External Resources

1. **GitHub Issues:** Search for similar problems
2. **Commit History:** `git log --grep="keyword"` to find related changes
3. **Blame:** `git blame file.py` to understand why code exists

### Emergency Contacts

If you encounter:
- **Constitutional violations:** Review `CONSTITUTION.md`
- **Kernel corruption:** See `KERNEL.md` recovery procedures
- **Security vulnerabilities:** Check `tests/hardening/` for test patterns
- **Unknown errors:** Use ENVOY's `DEBUG_FIX_V2` circuit

---

## 🔐 FINAL WARNING: TRUST NOTHING

In a complex codebase:

1. **Verify before trusting:** Run tests, check logs, inspect state
2. **Assume bugs exist:** Even in "working" code
3. **Question assumptions:** "Why is this here?" "Who signed this?"
4. **Validate inputs:** Every external input is hostile until verified
5. **Audit outputs:** Did the operation do what you expected?
6. **Check signatures:** Is there a cryptographic chain to a sovereign?
7. **Review history:** What changed recently? Why?
8. **Test your tests:** Are you testing the right thing?

**The system will help you if you respect it. It will fight you if you don't.**

---

## 📖 APPENDIX: Quick Reference

### File Locations

```
steward-protocol/
├── CONSTITUTION.md          # The supreme law
├── KERNEL.md                # Kernel refactoring plan
├── PROMPT.md                # Architecture philosophy
├── README.md                # Public overview
├── pyproject.toml           # Project config
├── steward.yaml             # System config
│
├── vibe_core/
│   ├── kernel_impl.py       # The heart (1870 LOC)
│   ├── ledger.py            # Immutable audit log
│   ├── narasimha.py         # Kill-switch
│   ├── event_bus.py         # Event system
│   │
│   ├── protocols/           # Interfaces
│   │   ├── kernel_protocol.py
│   │   ├── kernel_types.py
│   │   └── ...
│   │
│   ├── plugins/             # 50+ plugins
│   │   ├── vedic_governance/
│   │   ├── economy/
│   │   └── ...
│   │
│   ├── services/            # Core services
│   │   ├── lifecycle_service.py
│   │   ├── capability_enforcer.py
│   │   └── ...
│   │
│   └── agents/              # Agent implementations
│
└── tests/
    ├── test_*.py            # Unit tests
    ├── hardening/           # Security tests
    └── ...
```

### Command Cheatsheet

```bash
# System
steward boot                 # Initialize kernel
steward status               # Health check
steward introspect           # Deep inspection
steward stop                 # Graceful shutdown

# Testing
pytest tests/ -v             # All tests
pytest tests/hardening/ -v   # Security tests
pytest -m fast -v            # Quick tests only

# Linting
ruff format .                # Auto-format
ruff check . --fix           # Auto-fix issues
ruff check vibe_core/        # Check specific directory

# Git
git status                   # What changed?
git diff                     # See changes
git add -p                   # Stage interactively
git commit --no-verify       # Skip hooks (authorized only)

# ENVOY
steward run SIMPLE_QUERY "question"
steward run ARCHITECTURE_ANALYSIS
steward run DEBUG_FIX_V2 "problem description"
steward run SYSTEM_STATUS_V2
```

---

**Remember:** This is not just code. This is a governed, self-aware system. Respect the architecture, verify your assumptions, and trust nothing without proof.

**May your code be type-safe, your tests green, and your commits blessed by the ledger.**

🕉️ _Satyam Eva Jayate_ (Truth Alone Triumphs) 🕉️
