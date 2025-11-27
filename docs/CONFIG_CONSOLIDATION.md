# Configuration System Consolidation

**Document Purpose:** Clarify the unified configuration system for Steward Protocol.

**Status:** Phase 3 consolidation documentation
**Date:** 2025-11-27

---

## Executive Summary

Steward Protocol has a single, unified configuration system with multiple entry points:

1. **Single Source of Truth:** `vibe_core/config/schema.py` defines all configuration models (CityConfig)
2. **Primary Loader:** `vibe_core/config/loader.py` provides ConfigLoader service
3. **Config Files:** Multiple YAML files (agent_city.yaml, steward.yaml, config/matrix.yaml)
4. **Environment Variables:** Can override config values (future enhancement)

**The Hierarchy:**
```
Environment Variables > Config Files > Defaults (Pydantic models)
```

---

## Configuration System Architecture

### Layer 1: Schema & Validation (vibe_core/config/schema.py)

**Purpose:** Define all configuration parameters with type safety and defaults

**Key Components:**
- `CityConfig` - Root configuration object (THE DHARMA)
- `GovernanceConfig` - Constitutional parameters (voting, quorum, proposals)
- `EconomyConfig` - Credit system parameters (costs, rewards, supply cap)
- `AgentParametersConfig` - Agent-specific settings (Herald, Science, Forum, Civic)
- `SecurityConfig` - Security parameters (signatures, rate limits, ledger)
- `IntegrationsConfig` - External integrations (Tavily, Twitter, Reddit, Database)
- `MonitoringConfig` - System monitoring and audit parameters

**Validation:**
- Uses Pydantic v2 with `BaseModel`
- All fields have type hints and default values
- Invalid configurations are rejected at load time
- Extra fields are forbidden (strict validation)

**Key Design Principle:**
```
If the Soul (Config) is corrupted, the Body (Kernel) must not wake.
```

---

### Layer 2: Loading Service (vibe_core/config/loader.py)

**Purpose:** High-level interface for loading and validating YAML configuration files

**Primary Function:** `load_config(config_path: str) -> CityConfig`
- Reads YAML file from disk
- Parses YAML syntax
- Validates against CityConfig schema
- Raises descriptive errors if validation fails

**Secondary Interface:** `ConfigLoader` class
```python
from vibe_core.config import ConfigLoader

loader = ConfigLoader("config/matrix.yaml")
config = loader.load()

# Access configuration
print(config.city_name)
print(config.governance.voting_threshold)
print(config.economy.initial_credits)
```

**Methods:**
- `load()` - Load and validate configuration
- `config` - Property to get loaded configuration
- `is_loaded()` - Check if configuration has been loaded
- `validate()` - Run diagnostics on loaded configuration
- `print_summary()` - Human-readable summary output

---

### Layer 3: Public API (vibe_core/config/__init__.py)

**Purpose:** Export public API for config access

**Exports:**
```python
from vibe_core.config import (
    CityConfig,           # Type for type hints
    load_config,          # Primary function (canonical)
    ConfigLoader,         # Class for service-based loading
    get_config,           # Alias for backward compatibility (Phase 2)
)
```

**Aliases (Phase 2):**
- `get_config = load_config` (Phase 2 compatibility, will be removed in v2.0)

---

## Configuration Files

### agent_city.yaml (Root Level)
- **Purpose:** Agent City system configuration
- **Location:** `/agent_city.yaml`
- **Scope:** Overall Agent City behavior

### steward.yaml (Root Level)
- **Purpose:** Steward Protocol system configuration
- **Location:** `/steward.yaml`
- **Scope:** Steward-specific settings

### config/matrix.yaml (Config Directory)
- **Purpose:** Primary configuration file
- **Location:** `/config/matrix.yaml`
- **Scope:** Default configuration loaded by ConfigLoader
- **Format:** YAML (human-readable)

### config/semantic_compliance.yaml (Config Directory)
- **Purpose:** Semantic compliance rules
- **Location:** `/config/semantic_compliance.yaml`
- **Scope:** Compliance-specific configuration

### .env.example (Root Level)
- **Purpose:** Example environment variables
- **Location:** `/.env.example`
- **Note:** Not currently used, reserved for Phase 4 enhancement

---

## Configuration Hierarchy

### Current Hierarchy (Phase 3)

```
┌─────────────────────────────────────┐
│  Pydantic Defaults (schema.py)       │
│  (Lowest Priority)                   │
│                                      │
│  - voting_threshold: 0.5             │
│  - initial_credits: 100              │
│  - broadcast_cost: 1                 │
│  - etc.                              │
└────────────┬────────────────────────┘
             ▲
             │ (Overrides defaults)
             │
┌────────────┴────────────────────────┐
│  YAML Config Files                   │
│  (Medium Priority)                   │
│                                      │
│  - config/matrix.yaml                │
│  - agent_city.yaml                   │
│  - steward.yaml                      │
│                                      │
│  Loaded via: ConfigLoader.load()     │
└────────────┬────────────────────────┘
             ▲
             │ (Future enhancement)
             │
┌────────────┴────────────────────────┐
│  Environment Variables               │
│  (Highest Priority)                  │
│  Not yet implemented                 │
│                                      │
│  - CITY_VOTING_THRESHOLD=0.6         │
│  - ECONOMY_INITIAL_CREDITS=200       │
│  - etc.                              │
└─────────────────────────────────────┘
```

### Future Hierarchy (Phase 4)

Environment variable support will be added to allow runtime configuration:

```python
import os
from vibe_core.config import load_config

# Load from file
config = load_config("config/matrix.yaml")

# Override from environment variables
if os.getenv("CITY_VOTING_THRESHOLD"):
    config.governance.voting_threshold = float(os.getenv("CITY_VOTING_THRESHOLD"))

if os.getenv("ECONOMY_INITIAL_CREDITS"):
    config.economy.initial_credits = float(os.getenv("ECONOMY_INITIAL_CREDITS"))
```

---

## Single Source of Truth

### Definition
The **single source of truth** for all configuration parameters is the **Pydantic schema** (`vibe_core/config/schema.py`).

This file defines:
- All valid configuration parameters
- Default values for each parameter
- Type constraints and validation rules
- Field descriptions and documentation

### Why Single Source of Truth?
1. **Type Safety:** Pydantic enforces types at validation time
2. **Defaults:** No hidden defaults scattered across code
3. **Documentation:** All fields documented in one place
4. **Validation:** Invalid configs are caught immediately
5. **Discoverability:** Easy to find all available config options

### How It Works
1. YAML files can define any subset of parameters
2. Pydantic fills in missing parameters from defaults
3. Pydantic validates all provided parameters
4. The resulting CityConfig object is the complete, valid configuration

---

## Usage Patterns

### Pattern 1: Simple Function Call
```python
from vibe_core.config import load_config

# Load configuration from YAML file
config = load_config("config/matrix.yaml")

# Access nested parameters
print(config.governance.voting_threshold)  # 0.5 (from default or file)
print(config.economy.initial_credits)     # 100 (from default or file)
```

### Pattern 2: Service Class
```python
from vibe_core.config import ConfigLoader

loader = ConfigLoader("config/matrix.yaml")
config = loader.load()

# Check if loaded
if loader.is_loaded():
    loader.print_summary()

# Validate configuration
report = loader.validate()
print(report["checks"]["governance"])
```

### Pattern 3: Type-Safe Access
```python
from vibe_core.config import CityConfig

def setup_system(config: CityConfig):
    # Type hints provide IDE autocompletion and static analysis
    gov = config.governance
    econ = config.economy

    print(f"Voting threshold: {gov.voting_threshold * 100}%")
    print(f"Initial credits: {econ.initial_credits}")
```

### Pattern 4: Agent-Specific Configuration
```python
from vibe_core.config import load_config

config = load_config("config/matrix.yaml")

# Get Herald agent configuration
herald_config = config.get_agent_config("herald")
print(f"Herald posting frequency: {herald_config.posting_frequency_hours} hours")

# Get integration configuration
tavily_config = config.get_integration_config("tavily")
print(f"Tavily enabled: {tavily_config.enabled}")
```

---

## Validation & Diagnostics

### Validation at Load Time
```python
from vibe_core.config import load_config

try:
    config = load_config("config/matrix.yaml")
    print("✅ Configuration valid")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

### Diagnostic Report
```python
from vibe_core.config import ConfigLoader

loader = ConfigLoader("config/matrix.yaml")
config = loader.load()

# Generate diagnostic report
report = loader.validate()
# Returns:
# {
#     "valid": True,
#     "city_name": "Agent City Alpha",
#     "federation_version": "1.0.0",
#     "checks": {
#         "governance": {...},
#         "economy": {...},
#         "security": {...},
#         "integrations": {...}
#     }
# }
```

---

## Configuration Parameters Reference

### Governance
- `voting_threshold: float` (0.0-1.0, default: 0.5)
- `quorum_required: float` (0.0-1.0, default: 0.3)
- `proposal_cost: float` (default: 5)
- `proposal_duration_hours: int` (default: 24)
- `license_revocation_enabled: bool` (default: True)
- `credit_audit_frequency_hours: int` (default: 6)

### Economy
- `initial_credits: float` (default: 100)
- `broadcast_cost: float` (default: 1)
- `proposal_cost: float` (default: 5)
- `research_cost: float` (default: 2)
- `media_cost: float` (default: 1)
- `vote_reward: float` (default: 0)
- `verification_reward: float` (default: 1)
- `total_credit_supply_cap: float` (default: 100000)
- `inflation_monthly_percent: float` (0-100, default: 5)

### Security
- `require_signatures: bool` (default: True)
- `signature_algorithm: str` (default: "ecdsa")
- `global_rate_limit_requests_per_minute: int` (default: 100)
- `per_agent_rate_limit_per_minute: int` (default: 10)
- `immutable_ledger: bool` (default: True)
- `enable_access_logs: bool` (default: True)

### Integrations
- **Tavily:** `enabled`, `model`, `timeout_seconds`
- **Twitter:** `enabled`, `max_tweets_per_agent`, `rate_limit_window_minutes`
- **Reddit:** `enabled`, `subreddits`, `rate_limit_window_minutes`
- **Database:** `path`, `backup_enabled`, `backup_interval_hours`

### Monitoring
- `health_check_interval_minutes: int` (default: 5)
- `log_level: str` (default: "INFO")
- `log_all_transactions: bool` (default: True)
- `transaction_log_path: str` (default: "data/logs/transactions.log")
- `metrics_collection_enabled: bool` (default: True)
- `metrics_export_frequency_hours: int` (default: 1)

---

## Consolidation Status

### Phase 2 State
- ✅ Pydantic schema defined and validated
- ✅ ConfigLoader service implemented
- ✅ Multiple config files created
- ❌ Environment variable support (TODO: Phase 4)
- ❌ Config file merging (not needed - YAML single file approach)

### Phase 3 Actions
- ✅ Document schema as single source of truth
- ✅ Document config loading hierarchy
- ✅ Clarify ConfigLoader as primary entry point
- ✅ Create CONFIG_CONSOLIDATION.md

### Phase 4 Enhancements
- Add environment variable override support
- Implement config hot-reload (if needed)
- Add config validation CLI tool
- Expand agent-specific config options

---

## Best Practices

### 1. Always Use ConfigLoader or load_config()
```python
# ✅ Good
from vibe_core.config import load_config
config = load_config("config/matrix.yaml")

# ❌ Avoid
import yaml
with open("config/matrix.yaml") as f:
    config = yaml.safe_load(f)  # No validation!
```

### 2. Type-Hint Configuration Parameters
```python
# ✅ Good
from vibe_core.config import CityConfig

def setup(config: CityConfig):
    voting_threshold = config.governance.voting_threshold

# ❌ Avoid
def setup(config):
    voting_threshold = config["governance"]["voting_threshold"]
```

### 3. Access Nested Config Safely
```python
# ✅ Good
tavily_config = config.get_integration_config("tavily")
if tavily_config and tavily_config.enabled:
    # Use Tavily

# ✅ Also Good (Pydantic ensures this never fails)
if config.integrations.tavily.enabled:
    # Use Tavily
```

### 4. Document Configuration Usage
```python
def process_research(agent_name: str, config: CityConfig):
    """
    Process research using configuration.

    Configuration used:
    - config.integrations.tavily.enabled: Whether Tavily is available
    - config.agents.science.max_search_results: Max results per search
    - config.agents.science.searches_per_hour: Rate limit

    Args:
        agent_name: Name of research agent
        config: System configuration (CityConfig)
    """
    # Implementation...
```

---

## Troubleshooting

### Configuration File Not Found
```
FileNotFoundError: Configuration file not found: config/matrix.yaml
```
**Solution:** Check the file path is relative to project root or use absolute path.

### Configuration Validation Failed
```
ValueError: Configuration validation failed: ...
```
**Solution:** Check YAML syntax and ensure all provided fields match schema. Use `print(CityConfig.model_json_schema())` to see expected structure.

### Missing Required Configuration
```
ValueError: 1 validation error for CityConfig ...
```
**Solution:** Some fields might be required. Check schema defaults or add missing fields to YAML.

---

## References

- **Schema Definition:** `vibe_core/config/schema.py` (Pydantic models)
- **Loading Service:** `vibe_core/config/loader.py` (ConfigLoader)
- **Public API:** `vibe_core/config/__init__.py` (Exports)
- **Configuration Files:**
  - `config/matrix.yaml` (Default configuration)
  - `agent_city.yaml` (Agent City system config)
  - `steward.yaml` (Steward Protocol config)

---

**Document Version:** 1.0
**Status:** ✅ Complete - Single Source of Truth Established
**Last Updated:** 2025-11-27
**Next Review:** Phase 4 (if environment variable support is added)
