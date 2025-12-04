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

*Based on the original `phoenix_config` package by kimeisele*
