# Phoenix Config V2 - Unified Configuration Architecture

> "A config that never dies, fractally extensible, eternal"

## Overview

Phoenix Config V2 replaces the fragmented configuration system with a unified, typed, fractal architecture based on the original `phoenix_config` package design.

## Problem Statement

**Current State (V1):**
- `PhoenixConfigEngine` - flat dict access to `phoenix.yaml`
- `config/matrix.yaml` - loaded with raw `yaml.safe_load()`
- `MATRIX.md` - parsed separately by `PlaybookRouter`
- Circuits - individual YAML files, no unified access
- No type safety, no validation, fragmented access patterns

**Issues:**
1. `engine.get("providers.llm_provider")` - string keys, no autocomplete
2. No construction-time validation
3. Multiple loaders doing the same thing differently
4. Can't easily see what's configurable

## Solution: Typed Composition

```
                    ┌─────────────────────────────────────┐
                    │           PhoenixConfig             │
                    │  (Single Entry Point - nie stirbt)  │
                    ├─────────────────────────────────────┤
                    │                                     │
                    │  kernel: KernelConfig      [STATIC] │
                    │  city: CityConfig          [STATIC] │
                    │  circuits: Dict[str, ...]  [DYNAMIC]│
                    │  routing: List[RoutingRule][DYNAMIC]│
                    │                                     │
                    └─────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  KernelConfig   │      │   CityConfig    │      │ CircuitsConfig  │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ provider: ...   │      │ governance: ... │      │ Dict[str, ...]  │
│ features: ...   │      │ economy: ...    │      │ Auto-discovered │
│ system: ...     │      │ agents: ...     │      │ from YAML files │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Architecture

### Directory Structure

```
vibe_core/phoenix/
├── __init__.py              # Public API: PhoenixConfig, get_config()
├── config.py                # Main PhoenixConfig dataclass
├── sections/
│   ├── __init__.py
│   ├── kernel.py            # KernelConfig, ProviderConfig, FeaturesConfig
│   ├── city.py              # CityConfig, GovernanceConfig, EconomyConfig, AgentsConfig
│   ├── circuits.py          # CircuitConfig, dynamic loading
│   └── routing.py           # RoutingRule, MATRIX.md parser
├── loader.py                # ConfigLoader: from_files(), from_env()
└── validators.py            # Schema validation
```

### Core Dataclasses

```python
@dataclass
class PhoenixConfig:
    """Unified configuration - the Phoenix that never dies."""

    kernel: KernelConfig                    # From phoenix.yaml
    city: CityConfig                        # From matrix.yaml
    circuits: Dict[str, CircuitConfig]      # From circuits/*.yaml
    routing: List[RoutingRule]              # From MATRIX.md

    @classmethod
    def from_files(cls,
                   phoenix_path: Path = Path("config/phoenix.yaml"),
                   matrix_path: Path = Path("config/matrix.yaml"),
                   circuits_dir: Path = Path("vibe_core/playbook/circuits"),
                   routing_path: Path = Path("MATRIX.md")) -> "PhoenixConfig":
        """Load configuration from all source files."""
        ...

    @classmethod
    def from_env(cls) -> "PhoenixConfig":
        """Load configuration from environment variables."""
        ...

    @classmethod
    def create_for_simulation(cls) -> "PhoenixConfig":
        """Factory: Safe simulation mode defaults."""
        ...

    @classmethod
    def create_for_live_fire(cls) -> "PhoenixConfig":
        """Factory: Production/live mode."""
        ...

    def validate(self) -> None:
        """Validate all configuration sections."""
        ...

    def save(self) -> None:
        """Persist configuration back to files."""
        ...

    def reload_routing(self) -> None:
        """Hot-reload MATRIX.md routing rules."""
        ...
```

### Section Dataclasses

```python
# kernel.py
@dataclass
class ProviderConfig:
    name: str = "anthropic"
    class_path: str = "vibe_core.runtime.providers.anthropic:AnthropicProvider"
    api_key_env: str = "ANTHROPIC_API_KEY"
    pro_model: str = "claude-sonnet-4-20250514"
    low_model: str = "claude-haiku-3-20240307"

@dataclass
class FeaturesConfig:
    live_fire_enabled: bool = False
    debug_mode: bool = False
    simulation_mode: bool = True

@dataclass
class KernelConfig:
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)

# city.py
@dataclass
class GovernanceConfig:
    voting_threshold: float = 0.5
    quorum_required: float = 0.3
    proposal_cost: int = 5
    proposal_duration_hours: int = 24

@dataclass
class EconomyConfig:
    initial_credits: int = 100
    refill_amount: int = 50
    broadcast_cost: int = 1
    research_cost: int = 2

@dataclass
class CityConfig:
    name: str = "Agent City Alpha"
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    economy: EconomyConfig = field(default_factory=EconomyConfig)

# routing.py
@dataclass
class RoutingRule:
    pattern: str          # Regex pattern
    circuit: str          # Target circuit name
    priority: str = "NORMAL"
    active: bool = True
```

## Usage

### Before (V1)
```python
from vibe_core.phoenix_config import get_phoenix_engine

engine = get_phoenix_engine()
provider = engine.get("providers.llm_provider", "")
live_fire = engine.get("features.live_fire_enabled", False)

# No autocomplete, no type safety, string keys everywhere
```

### After (V2)
```python
from vibe_core.phoenix import get_config

config = get_config()

# Typed access with autocomplete
provider_name = config.kernel.provider.name
live_fire = config.kernel.features.live_fire_enabled
initial_credits = config.city.economy.initial_credits

# Dynamic access for circuits
agent_birth_circuit = config.circuits.get("agent_birth")

# Hot-swappable routing
config.reload_routing()
for rule in config.routing:
    if rule.active:
        print(f"{rule.pattern} -> {rule.circuit}")
```

## Fractal Property

Every level of the configuration follows the same pattern:
- **Dataclass** with typed fields and defaults
- **Validation** method
- **Serialization** to/from dict/YAML

This means:
```python
config.kernel                    # KernelConfig - same interface
config.kernel.provider           # ProviderConfig - same interface
config.city.governance           # GovernanceConfig - same interface
```

## Hot-Swap Semantics

| Section | Hot-Swap | Notes |
|---------|----------|-------|
| `kernel.provider` | No | Requires restart |
| `kernel.features` | Partial | Some flags instant, others restart |
| `city.*` | No | Startup only |
| `circuits` | No | Loaded once |
| `routing` | **Yes** | `reload_routing()` re-parses MATRIX.md |

## Migration Path

1. Create `vibe_core/phoenix/` alongside existing `phoenix_config.py`
2. Implement core dataclasses
3. Add `get_config()` as new entry point
4. Gradually migrate consumers to new API
5. Deprecate old `get_phoenix_engine()`
6. Remove old code

## Source Files Mapping

| Config Section | Source File | Format |
|----------------|-------------|--------|
| `kernel` | `config/phoenix.yaml` | YAML |
| `city` | `config/matrix.yaml` | YAML |
| `circuits` | `vibe_core/playbook/circuits/*.yaml` | YAML (auto-discovered) |
| `routing` | `MATRIX.md` | Markdown table |

## Design Principles

1. **Typed over stringly-typed** - Dataclasses with proper types
2. **Composition over inheritance** - Nested dataclasses
3. **Validation at construction** - Fail fast
4. **Sensible defaults** - Works out of the box
5. **Single source of truth** - One `get_config()` for everything
6. **Fractal architecture** - Same pattern at every level

---

## 4D Hypercube: Ephemeral Cities

The final piece that makes the system truly fractal: **Agents can spawn child kernels with custom configurations.**

### The Concept

```
Parent Kernel (Agent City Alpha)
├── Governance: Democracy (voting_threshold=0.5)
├── Economy: Standard credits
│
└── Agent detects complex task...
    │
    └── SPAWN EPHEMERAL CITY
        │
        ├── Child Kernel (Fast Coding Swarm)
        │   ├── Governance: Dictatorship (voting_threshold=0)
        │   ├── Economy: Unlimited credits
        │   └── Agents: 5 coders, 1 tester
        │
        └── Task solved → Result + Proof → MERGE BACK
```

### Implementation

```python
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.phoenix import PhoenixConfig

# Parent kernel (main city)
parent = RealVibeKernel()

# Agent generates custom config for sub-task
fast_config = PhoenixConfig.from_files()
fast_config.city.governance.voting_threshold = 0  # No democracy
fast_config.city.name = "Fast Coding Swarm"

# Spawn ephemeral child
child = parent.spawn_child_kernel(fast_config)

# Child executes task...
result = {"code": "...", "tests": "passed"}

# Merge back with cryptographic proof
merge = parent.merge_child_result(child, result)
# merge = {
#   "type": "EPHEMERAL_CITY_MERGE",
#   "child_ledger_hash": "4f53cda18c2baa0c",
#   "result": "...",
# }
```

### Key Properties

1. **Isolation**: Child kernel runs in-memory, doesn't affect parent state
2. **Custom Physics**: Different governance rules, economy, agent configurations
3. **Proof of Work**: Child's ledger hash is recorded in parent
4. **Recursive**: Child can spawn grandchildren (infinite depth)

### Use Cases

| Scenario | Parent Config | Child Config |
|----------|---------------|--------------|
| Fast Coding | Democracy | Dictatorship (speed) |
| Experimentation | Production | Sandbox (safe) |
| Specialized Task | General | Domain-specific agents |
| Parallel Swarm | 1 executor | N parallel workers |

---

## Playbook Operations: spawn_city

The `spawn_city` operation provides a clean API for playbooks to invoke 4D Hypercube:

```python
from vibe_core.playbook.operations import spawn_city, SpawnCityResult

# Simple usage - spawn child with config overrides
result = await spawn_city(
    task="Build the authentication module",
    circuit="fast_code",
    config_overrides={
        "city.governance.voting_threshold": 0,
        "city.governance.quorum_required": 0,
    }
)

if result.success:
    print(f"Output: {result.output}")
    print(f"Proof: {result.proof}")  # Ledger hash from child
```

### Pre-built Config Factories

```python
from vibe_core.playbook.operations.kernel_spawn import (
    fast_code_config,      # No governance overhead
    sandbox_config,        # Isolated experimentation
    research_swarm_config, # Parallel research workers
)

# Use factory function
result = await spawn_city(
    task="Build feature X",
    config_factory=fast_code_config,  # Applies optimal settings
)
```

---

## Neural Link (FUTURE - Design Only)

> **Status**: Design phase. Requires architecture review before implementation.

### The Vision

What if the routing table wasn't static? What if an LLM could dynamically modify routing based on context?

```
User Request → LLM Analyzes → "This needs Deep Research Circuit"
                    ↓
          Temporarily modify MATRIX.md routing
                    ↓
          Execute with optimal circuit
                    ↓
          Restore original routing (or persist if approved)
```

### Proposed API (Conceptual)

```python
# NOT IMPLEMENTED - Design only
class NeuralRouter:
    """LLM-assisted dynamic routing."""

    def suggest_circuit(self, intent: str) -> CircuitSuggestion:
        """LLM analyzes intent and suggests optimal circuit."""
        pass

    def temporary_route(self, pattern: str, circuit: str, duration_seconds: int):
        """Temporarily add routing rule."""
        pass

    def explain_routing_decision(self, intent: str) -> str:
        """LLM explains why it chose a particular circuit."""
        pass
```

### Security Considerations

1. **Audit Trail**: Every routing change must be logged
2. **Approval Gate**: Changes above threshold require human approval
3. **Rollback**: Automatic revert if circuit fails
4. **Scope Limits**: LLM can't route to privileged circuits
5. **Rate Limits**: Max N routing changes per time window

### Why Not Now?

- Security implications need thorough review
- Governance model for routing changes unclear
- Performance impact of LLM in routing path
- Need clear rollback semantics

**Recommendation**: Implement static routing + spawn_city first. Neural Link is Phase 2.

---

## Airlock Pattern: Harvesting from Ephemeral Cities

When a child kernel creates files in its VFS, those files die with the child. The **Airlock Pattern** solves this:

```python
result = await spawn_city(
    task="Generate report",
    circuit="research",
    artifacts=["reports/*.md", "data/*.json"],  # Glob patterns
    artifacts_destination="data/harvested/",     # Where to copy in parent VFS
)

# result.harvested_artifacts contains:
# [
#   HarvestedArtifact(source="reports/analysis.md", dest="data/harvested/analysis.md", success=True),
#   HarvestedArtifact(source="data/metrics.json", dest="data/harvested/metrics.json", success=True),
# ]
```

### How It Works

1. Child executes task, creates files in its VFS
2. Before merge, spawn_city harvests files matching glob patterns
3. Files are copied from child VFS to parent VFS
4. Child dies, but artifacts survive in parent
5. Harvest metadata included in merge record

### Security

- Only files in child's VFS can be harvested (sandboxed)
- Destination is validated against parent VFS root
- No path traversal allowed

---

## Dual Config Architecture (Legacy Transition)

> **Important**: The system currently has TWO config systems. This is intentional during migration.

### Config System Comparison

| System | Location | Type | Used By |
|--------|----------|------|---------|
| **Legacy** | `vibe_core/config/schema.py` | Pydantic | System agent cartridges |
| **Phoenix V2** | `vibe_core/phoenix/sections/` | Dataclass | Kernel, spawn_city |

### Why Two Systems?

1. **Legacy System**: Provides rich Pydantic validation with `extra="forbid"`, used by 13+ agent cartridges for their specific configs (HeraldConfig, ScienceConfig, etc.)

2. **Phoenix V2**: Provides unified typed access for kernel-level config, supports serialization for child kernel spawning, and is designed for the 4D Hypercube

### Relationship

```
vibe_core/phoenix/config.py:PhoenixConfig
├── kernel: KernelConfig (phoenix/sections/kernel.py)
├── city: CityConfig (phoenix/sections/city.py)  ← DATACLASS version
├── circuits: Dict[str, CircuitConfig]
└── routing: List[RoutingRule]

vibe_core/config/schema.py:CityConfig  ← PYDANTIC version (legacy)
├── governance: GovernanceConfig
├── economy: EconomyConfig
└── agents: AgentParametersConfig
```

### Migration Path

1. **Phase 1 (Current)**: Both systems coexist
   - Kernel uses Phoenix V2 (`vibe_core.phoenix`)
   - Agents use Legacy (`vibe_core.config`)

2. **Phase 2 (Future)**: Converge agent configs
   - Agents import from `config.phoenix.city` instead of `config.schema`
   - Add backward-compatible aliases

3. **Phase 3 (Future)**: Remove legacy
   - Delete `vibe_core/config/schema.py`
   - All code uses `vibe_core/phoenix/`

### For New Code

Always use Phoenix V2:
```python
from vibe_core.phoenix import get_config, PhoenixConfig

config = get_config()
```

---

*Based on the original `phoenix_config` package by kimeisele*
