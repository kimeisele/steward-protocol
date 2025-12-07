# CONFIG MIGRATION PLAN
## Systematische Migration aller Hardcoded Config Values

**Status**: ACTIVE PLAN
**Author**: Claude Opus (auf Befehl von SS)
**Datum**: 2025-12-07

---

## PROBLEM

~80+ hardcoded config values sind im Code verstreut. Diese müssen:
1. SEMANTISCH kategorisiert werden (nicht alles ist ein "path")
2. In die richtige YAML section verschoben werden
3. Im Code durch `config.section.value` ersetzt werden

---

## SEMANTIC CATEGORIES

### CATEGORY 1: PATHS (config/paths.yaml) - EXISTS
**Section**: `PathsConfig` in `vibe_core/phoenix/sections/paths/`
**Status**: Section existiert, aber Code nutzt sie nicht!

| File | Line | Hardcoded Value | Target |
|------|------|-----------------|--------|
| `plugin_loader.py` | 235 | `"vibe_core/plugins"` | `config.paths.cartridges.plugins` |
| `semantic_engine.py` | 58 | `"data/models"` | `config.paths.system.models` |
| `lineage.py` | 64 | `"/tmp/vibe_os/kernel/lineage.db"` | `config.paths.system.resolve("lineage_db")` |
| `governance/invariants.py` | 60 | `"config/soul.yaml"` | `config.paths.knowledge.resolve("soul")` |
| `catalog_tool.py` | 27 | `"data/library/catalog.json"` | `config.paths.data.resolve("library_catalog")` |
| `recommend_tool.py` | 27 | `"data/library/catalog.json"` | `config.paths.data.resolve("library_catalog")` |
| `search_tool.py` | 27 | `"data/library/catalog.json"` | `config.paths.data.resolve("library_catalog")` |
| `ledger.py` | 116 | `"data/vibe_ledger.db"` | `config.paths.data.resolve("vibe_ledger")` |
| `scout_tool.py` | 31 | `"data/federation/pokedex.json"` | `config.paths.data.federation_pokedex` |
| `section_loader.py` | 98,350 | `"vibe_core/phoenix/sections"` | `config.paths.cartridges.phoenix_sections` |
| `templates/section_main.py` | 91 | `"knowledge/templates"` | `config.paths.knowledge.templates` |
| `prompts/section_main.py` | 108 | `"knowledge/prompts"` | `config.paths.knowledge.prompts` |
| `test_governance/section_main.py` | 58,104 | `"data/test_baselines.json"`, `"data/logs/test_mutations.log"` | NEW: `config.paths.data.test_*` |
| `lifecycle_manager.py` | 108 | `"data/registry/citizens.json"` | `config.paths.data.registry_citizens` |
| `city/section_main.py` | 108 | `"data/logs/transactions.log"` | NEW: `config.paths.data.resolve("logs_transactions")` |
| `interface/section_main.py` | 387 | `"knowledge/interface/templates"` | NEW: `config.paths.knowledge.resolve("interface_templates")` |
| `gap_report_tool.py` | 38-40 | `"data/registry/ledger.jsonl"`, `"data/registry/licenses.json"`, `"data/governance/executed"` | `config.paths.data.*` |
| `milk_ocean.py` | 86 | `"data/milk_ocean.db"` | NEW: `config.paths.data.resolve("milk_ocean_db")` |
| `config/schema.py` | 279 | `"config/matrix.yaml"` | `config.paths.knowledge.matrix` |
| `index.py` | 21 | `"vibe_core/playbook/circuits/doc_index_render.yaml"` | `config.paths.knowledge.legacy_circuits` |
| `kernel_impl.py` | 135,191 | `"data/vibe_ledger.db"`, `"/tmp/vibe_os/kernel/lineage.db"` | `config.paths.*` |

**Migration für paths.yaml**:
1. Erweitere `DataPathsConfig` um fehlende keys: `vibe_ledger`, `library_catalog`, `logs_transactions`, `milk_ocean_db`, `test_baselines`, `test_mutations_log`
2. Erweitere `KnowledgePathsConfig` um: `soul`, `interface_templates`
3. Erweitere `SystemPathsConfig` um: `lineage_db`

---

### CATEGORY 2: LLM PROVIDERS (config/llm.yaml) - NEEDS CREATION
**Section**: `LLMConfig` - MUSS ERSTELLT WERDEN in `vibe_core/phoenix/sections/llm/`

| File | Line | Hardcoded Value | Target |
|------|------|-----------------|--------|
| `local_llama_provider.py` | 21 | `DEFAULT_MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"` | `config.llm.local.model_name` |
| `local_llama_provider.py` | 22 | `DEFAULT_MODEL_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"` | `config.llm.local.model_repo` |
| `local_llama_provider.py` | 51-52 | `n_ctx: int = 2048`, `n_threads` | `config.llm.local.n_ctx`, `config.llm.local.n_threads` |
| `local_llama_provider.py` | 150-151 | `max_tokens=256`, `temperature=0.7` | `config.llm.local.default_max_tokens`, `config.llm.local.default_temperature` |
| `settings/sections/provider.py` | 16-81 | `PROVIDER_REGISTRY` dict | `config.llm.providers` (from YAML) |

**Neue Section: `config/llm.yaml`**:
```yaml
# LLM Provider Configuration
local:
  model_name: "qwen2.5-0.5b-instruct-q4_k_m.gguf"
  model_repo: "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
  n_ctx: 2048
  n_threads: null  # auto-detect
  default_max_tokens: 256
  default_temperature: 0.7

providers:
  anthropic:
    default_model: "claude-sonnet-4-20250514"
    api_key_env: "ANTHROPIC_API_KEY"
  openai:
    default_model: "gpt-4-turbo"
    api_key_env: "OPENAI_API_KEY"
  openrouter:
    default_model: "anthropic/claude-3.5-sonnet"
    api_key_env: "OPENROUTER_API_KEY"
  google:
    default_model: "gemini-2.0-flash"
    api_key_env: "GOOGLE_API_KEY"
```

---

### CATEGORY 3: QUOTAS & LIMITS (config/quotas.yaml) - NEEDS CREATION
**Section**: `QuotasConfig` - MUSS ERSTELLT WERDEN in `vibe_core/phoenix/sections/quotas/`

| File | Line | Hardcoded Value | Target |
|------|------|-----------------|--------|
| `quota_manager.py` | 100 | `requests_per_minute: int = 10` | `config.quotas.requests_per_minute` |
| `quota_manager.py` | 101 | `tokens_per_minute: int = 10000` | `config.quotas.tokens_per_minute` |
| `quota_manager.py` | 104 | `cost_per_hour_usd: float = 2.0` | `config.quotas.cost_per_hour_usd` |
| `quota_manager.py` | 105 | `cost_per_day_usd: float = 5.0` | `config.quotas.cost_per_day_usd` |
| `llm_client.py` | 221-222 | `failure_threshold=5`, `recovery_timeout_seconds=30` | `config.quotas.circuit_breaker.*` |
| `circuit_breaker.py` | 58-61 | `failure_threshold=5`, `recovery_timeout_seconds=30`, `window_size_seconds=60` | `config.quotas.circuit_breaker.*` |
| `store/sqlite_store.py` | 198 | `alert_threshold = 0.80` | `config.quotas.budget_alert_threshold` |

**Neue Section: `config/quotas.yaml`**:
```yaml
# Rate Limits & Budget Controls
rate_limits:
  requests_per_minute: 10
  tokens_per_minute: 10000

budget:
  cost_per_hour_usd: 2.0
  cost_per_day_usd: 5.0
  cost_per_request_usd: 0.10
  alert_threshold: 0.80

circuit_breaker:
  failure_threshold: 5
  recovery_timeout_seconds: 30
  window_size_seconds: 60
  success_threshold_half_open: 1
```

---

### CATEGORY 4: TIMEOUTS & INTERVALS (config/runtime.yaml) - NEEDS CREATION
**Section**: `RuntimeConfig` - MUSS ERSTELLT WERDEN in `vibe_core/phoenix/sections/runtime/`

| File | Line | Hardcoded Value | Target |
|------|------|-----------------|--------|
| `operator_adapter.py` | 65 | `timeout: float = 300.0` | `config.runtime.operator_timeout` |
| `boot_orchestrator.py` | 433 | `RITUAL_INTERVAL = 300.0` | `config.runtime.ritual_interval` |
| `cli.py` | 125 | `pulse_age <= 10.0` | `config.runtime.pulse_threshold` |
| `circuit_executor.py` | 506 | `MAX_RECURSION_DEPTH = 5` | `config.runtime.max_recursion_depth` |
| `circuit_executor.py` | 549 | `max_transitions = 20` | `config.runtime.max_circuit_transitions` |
| `circuit_executor.py` | 1102-1104 | `reflection_interval=3`, `stuck_threshold=3`, `max_retry=5` | `config.runtime.circuit_recovery.*` |
| `process_manager.py` | 38 | `MAX_MESSAGE_SIZE = 1 * 1024 * 1024` | `config.runtime.max_message_size` |
| `process_manager.py` | 220 | `MAX_RESTARTS = 3` | `config.runtime.max_agent_restarts` |
| `event_bus.py` | 116 | `max_history: int = 1000` | `config.runtime.event_history_size` |
| `protocols/testable.py` | 103 | `timeout_ms: int = 5000` | `config.runtime.test_timeout_ms` |
| `semantic_actions.py` | 97,119-120 | `timeout_seconds=300`, `retry_count=3` | `config.runtime.action_timeout`, `config.runtime.action_retry_count` |
| `scripts/vibe_launcher.py` | 34 | `HEALTH_CHECK_INTERVAL = 2.0` | `config.runtime.orchestration.health_check_interval` |
| `scripts/heartbeat.py` | 68-89 | HeartbeatEngine pulse cycle | `config.runtime.orchestration.heartbeat_*` (GitHub Actions cron) |
| `vibe_core/cartridges/system/discoverer/agent.py` | 127 | `time.sleep(interval)` (param) | `config.runtime.orchestration.discovery_interval` |
| `vibe_core/pulse.py` | 136 | `asyncio.sleep(sleep_duration)` | `config.runtime.orchestration.pulse_sleep` |
| `vibe_core/file_operator.py` | 55 | `await asyncio.sleep(2)` | `config.runtime.orchestration.file_poll_interval` |
| `gateway/api.py` | 230 | `interval=10.0` (monitoring) | `config.runtime.orchestration.monitoring_interval` |

**Neue Section: `config/runtime.yaml`**:
```yaml
# Runtime Configuration
timeouts:
  operator_timeout: 300.0
  action_timeout: 300
  test_timeout_ms: 5000
  ritual_interval: 300.0

limits:
  max_recursion_depth: 5
  max_circuit_transitions: 20
  max_message_size: 1048576  # 1MB
  max_agent_restarts: 3
  event_history_size: 1000
  pulse_threshold: 10.0

circuit_recovery:
  reflection_interval: 3
  stuck_threshold: 3
  max_retry_attempts: 5

action_defaults:
  retry_count: 3

# === ORCHESTRATION (User-Frage: "die ganze orchestration!") ===
orchestration:
  # Kernel tick coordination
  health_check_interval: 2.0       # vibe_launcher supervisor loop
  discovery_interval: 60.0         # Discoverer cartridge scan interval
  pulse_sleep: 1.0                 # Pulse async sleep between updates
  file_poll_interval: 2.0          # FileOperator polling delay
  monitoring_interval: 10.0        # Gateway monitoring start interval

  # Heartbeat engine (GitHub Actions cron = 15 min external trigger)
  # Note: Actual cron is in .github/workflows - these are internal limits
  heartbeat_max_tasks_per_pulse: 5  # Don't execute more than 5 tasks per heartbeat
  heartbeat_commit_changes: true    # Auto-commit task progress
```

---

### CATEGORY 5: API KEYS REGISTRY (config/apis.yaml) - NEEDS CREATION
**Keys bleiben Environment Variables - aber WO sie definiert sind muss in YAML!**

**Problem**: Env var Namen sind hardcoded im Code verstreut:
```python
# BAD - hardcoded env var names
self.api_key = os.getenv("TAVILY_API_KEY")  # research.py:32
self.consumer_key = os.getenv("TWITTER_API_KEY")  # broadcast.py:28
```

**Lösung**: Zentrales Registry in `config/apis.yaml`:

| File | Line | Hardcoded Env Var | Target |
|------|------|-------------------|--------|
| `runtime/providers/factory.py` | 184-186 | `"GOOGLE_API_KEY"` etc. | `config.apis.llm["google"].env_var` |
| `settings/sections/provider.py` | 20-34 | `PROVIDER_REGISTRY` dict | `config.llm.providers` (schon in LLM section) |
| `herald/capabilities/research.py` | 32 | `"TAVILY_API_KEY"` | `config.apis.external["tavily"].env_var` |
| `herald/capabilities/broadcast.py` | 28 | `"TWITTER_API_KEY"` | `config.apis.external["twitter"].env_var` |
| `herald/capabilities/creative.py` | 117 | `"OPENROUTER_API_KEY"` | `config.llm.providers["openrouter"].api_key_env` |
| `science/tools/web_search_tool.py` | 152-156 | `"TAVILY_API_KEY"` | `config.apis.external["tavily"].env_var` |
| `herald/tools/research_tool.py` | 61 | `"TAVILY_API_KEY"` | `config.apis.external["tavily"].env_var` |
| `marketer/tools/marketer_content_tool.py` | 43 | `"OPENROUTER_API_KEY"` | `config.llm.providers["openrouter"].api_key_env` |

**Neue Section**: `config/apis.yaml` für NICHT-LLM APIs:
```yaml
# External API Configuration
# Keys stay in environment - this defines WHERE to find them

external:
  tavily:
    env_var: "TAVILY_API_KEY"
    description: "Web search API"
    required: false
  twitter:
    env_var: "TWITTER_API_KEY"
    description: "Twitter/X API for broadcasting"
    required: false
    additional_vars:
      - "TWITTER_API_SECRET"
      - "TWITTER_ACCESS_TOKEN"
      - "TWITTER_ACCESS_SECRET"
```

**Code Migration Pattern**:
```python
# BEFORE (hardcoded)
self.api_key = os.getenv("TAVILY_API_KEY")

# AFTER (config-driven)
def _get_api_config():
    try:
        from vibe_core.phoenix.config import get_config
        return get_config().apis
    except Exception:
        return None

class ResearchCapability:
    def __init__(self):
        apis = _get_api_config()
        env_var = apis.external["tavily"].env_var if apis else "TAVILY_API_KEY"
        self.api_key = os.getenv(env_var)
```

---

## EXECUTION PLAN

### PHASE 1: Create Missing Sections (Opus designs, Sonnet implements)

**Task 1.1**: Create `vibe_core/phoenix/sections/llm/` section
- `__init__.py`
- `manifest.json`
- `section_main.py` with `LLMConfig` dataclass

**Task 1.2**: Create `vibe_core/phoenix/sections/quotas/` section
- Same structure as above
- `QuotasConfig` dataclass

**Task 1.3**: Create `vibe_core/phoenix/sections/runtime/` section
- Same structure as above
- `RuntimeConfig` dataclass

**Task 1.4**: Create YAML files
- `config/llm.yaml`
- `config/quotas.yaml`
- `config/runtime.yaml`

### PHASE 2: Extend Existing Sections

**Task 2.1**: Extend `PathsConfig`
- Add missing keys to `DataPathsConfig`
- Add missing keys to `KnowledgePathsConfig`
- Add missing keys to `SystemPathsConfig`

**Task 2.2**: Update `config/paths.yaml`
- Add new path definitions

### PHASE 3: Migrate Code to Use Config

**Task 3.1**: Migrate LLM files (4 files)
- `local_llama_provider.py`
- `settings/sections/provider.py`

**Task 3.2**: Migrate Quota/Budget files (4 files)
- `quota_manager.py`
- `llm_client.py`
- `circuit_breaker.py`
- `store/sqlite_store.py`

**Task 3.3**: Migrate Runtime files (8 files)
- `operator_adapter.py`
- `boot_orchestrator.py`
- `cli.py`
- `circuit_executor.py`
- `process_manager.py`
- `event_bus.py`
- `protocols/testable.py`
- `semantic_actions.py`

**Task 3.4**: Migrate Path files (20+ files)
- All files listed in CATEGORY 1

### PHASE 4: Verify

**Task 4.1**: Run grep to verify no hardcoded values remain
```bash
grep -rn "= Path(" vibe_core/ --include="*.py" | grep -v "test" | grep -v "__pycache__"
grep -rn "DEFAULT_" vibe_core/ --include="*.py" | grep -v "test" | grep -v "__pycache__"
```

**Task 4.2**: Run tests
```bash
python -m pytest tests/test_config*.py -v
```

---

## FILES TO CREATE

1. `vibe_core/phoenix/sections/llm/__init__.py`
2. `vibe_core/phoenix/sections/llm/manifest.json`
3. `vibe_core/phoenix/sections/llm/section_main.py`
4. `vibe_core/phoenix/sections/quotas/__init__.py`
5. `vibe_core/phoenix/sections/quotas/manifest.json`
6. `vibe_core/phoenix/sections/quotas/section_main.py`
7. `vibe_core/phoenix/sections/runtime/__init__.py`
8. `vibe_core/phoenix/sections/runtime/manifest.json`
9. `vibe_core/phoenix/sections/runtime/section_main.py`
10. `config/llm.yaml`
11. `config/quotas.yaml`
12. `config/runtime.yaml`

## FILES TO MODIFY

### Phase 2 (Extend existing):
1. `vibe_core/phoenix/sections/paths/section_main.py` - Add missing path keys

### Phase 3 (Migrate code):
1. `vibe_core/llm/local_llama_provider.py`
2. `vibe_core/settings/sections/provider.py`
3. `vibe_core/runtime/quota_manager.py`
4. `vibe_core/runtime/llm_client.py`
5. `vibe_core/runtime/circuit_breaker.py`
6. `vibe_core/store/sqlite_store.py`
7. `vibe_core/operator_adapter.py`
8. `vibe_core/boot_orchestrator.py`
9. `vibe_core/cli.py`
10. `vibe_core/circuit_executor.py`
11. `vibe_core/process_manager.py`
12. `vibe_core/event_bus.py`
13. `vibe_core/protocols/testable.py`
14. `vibe_core/runtime/semantic_actions.py`
15. `vibe_core/plugin_loader.py`
16. `vibe_core/cortex/engines/semantic_engine.py`
17. `vibe_core/lineage.py`
18. `vibe_core/governance/invariants.py`
19. `vibe_core/cartridges/agent_city/librarian/tools/catalog_tool.py`
20. `vibe_core/cartridges/agent_city/librarian/tools/recommend_tool.py`
21. `vibe_core/cartridges/agent_city/librarian/tools/search_tool.py`
22. `vibe_core/ledger.py`
23. `vibe_core/cartridges/system/herald/tools/scout_tool.py`
24. `vibe_core/phoenix/section_loader.py`
25. `vibe_core/phoenix/sections/templates/section_main.py`
26. `vibe_core/phoenix/sections/prompts/section_main.py`
27. `vibe_core/phoenix/sections/test_governance/section_main.py`
28. `vibe_core/cartridges/system/civic/tools/lifecycle_manager.py`
29. `vibe_core/phoenix/sections/city/section_main.py`
30. `vibe_core/phoenix/sections/interface/section_main.py`
31. `vibe_core/cartridges/system/envoy/tools/gap_report_tool.py`
32. `vibe_core/cartridges/system/envoy/tools/milk_ocean.py`
33. `vibe_core/config/schema.py`
34. `vibe_core/plugins/interface/renderers/index.py`
35. `vibe_core/kernel_impl.py`

---

## SUMMARY

| Category | New Section | New YAML | Files to Modify |
|----------|-------------|----------|-----------------|
| Paths | EXISTS | EXISTS | 20+ |
| LLM | CREATE | CREATE | 2 |
| Quotas | CREATE | CREATE | 4 |
| Runtime | CREATE | CREATE | 8 |
| APIs | CREATE | CREATE | 8 |

**Total**: 4 new sections, 4 new YAML files, 42 code files to migrate

---

# SONNET EXECUTION TEMPLATES

## TEMPLATE A: New Section Creation

### A.1: manifest.json Template
```json
{
  "type": "section",
  "id": "SECTION_ID",
  "name": "SECTION_NAME Configuration",
  "version": "1.0.0",
  "description": "DESCRIPTION",

  "entry_point": "section_main.py",
  "entry_class": "SECTION_CLASS",

  "priority": 10,

  "config_file": "config/SECTION_ID.yaml",

  "author": "STEWARD Protocol",
  "tags": ["config", "SECTION_ID"]
}
```

### A.2: section_main.py Template
```python
"""
SECTION_NAME Configuration - DESCRIPTION.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/SECTION_ID/
    ARTHA: Parsed from config/SECTION_ID.yaml
    PRATYAYA: Validated
    KARMA: Instantiated as SECTION_CLASS dataclass
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SubConfig1:
    """Sub-configuration for X."""

    field1: str = "default1"
    field2: int = 100

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubConfig1":
        return cls(
            field1=data.get("field1", "default1"),
            field2=data.get("field2", 100),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field1": self.field1,
            "field2": self.field2,
        }


@dataclass
class SECTION_CLASS:
    """
    SECTION_NAME Configuration.

    Auto-discovered by SectionLoader -> loads from config/SECTION_ID.yaml
    """

    section_id: str = "SECTION_ID"
    source_file: str = "SECTION_ID.yaml"

    sub1: SubConfig1 = field(default_factory=SubConfig1)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SECTION_CLASS":
        return cls(
            sub1=SubConfig1.from_dict(data.get("sub1", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sub1": self.sub1.to_dict(),
        }

    def validate(self) -> List[str]:
        errors = []
        # Add validation logic
        return errors
```

---

## TEMPLATE B: Code Migration Pattern

### B.1: BEFORE (Hardcoded)
```python
# BAD - hardcoded value
DEFAULT_MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"

class LocalLlamaProvider:
    def __init__(self, n_ctx: int = 2048):
        self.n_ctx = n_ctx
```

### B.2: AFTER (Config Injected)
```python
# GOOD - config injected
from vibe_core.phoenix.config import get_config

def _get_llm_config():
    """Get LLM config with fallback for standalone usage."""
    try:
        return get_config().llm
    except Exception:
        # Fallback for standalone/testing
        from vibe_core.phoenix.sections.llm.section_main import LLMConfig
        return LLMConfig()

class LocalLlamaProvider:
    def __init__(self, n_ctx: int | None = None):
        llm_config = _get_llm_config()
        self.n_ctx = n_ctx or llm_config.local.n_ctx
```

### B.3: Migration Checklist per File
1. Add import: `from vibe_core.phoenix.config import get_config`
2. Add fallback getter function (see B.2)
3. Replace hardcoded DEFAULT_* constants with config access
4. Replace hardcoded function parameter defaults with `None`, then resolve from config
5. Test: `python -c "from MODULE import CLASS; print('OK')"`

---

## CONCRETE TASKS FOR SONNET

### TASK 1: Create LLM Section

**Create files:**

1. `vibe_core/phoenix/sections/llm/__init__.py` (empty file)

2. `vibe_core/phoenix/sections/llm/manifest.json`:
```json
{
  "type": "section",
  "id": "llm",
  "name": "LLM Provider Configuration",
  "version": "1.0.0",
  "description": "Local LLM and provider settings",
  "entry_point": "section_main.py",
  "entry_class": "LLMConfig",
  "priority": 10,
  "config_file": "config/llm.yaml",
  "author": "STEWARD Protocol",
  "tags": ["config", "llm", "providers"]
}
```

3. `vibe_core/phoenix/sections/llm/section_main.py`:
```python
"""
LLM Configuration - Local LLM and provider settings.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/llm/
    ARTHA: Parsed from config/llm.yaml
    PRATYAYA: Validated
    KARMA: Instantiated as LLMConfig dataclass
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LocalLLMConfig:
    """Local LLM (llama.cpp) configuration."""

    model_name: str = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    model_repo: str = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
    n_ctx: int = 2048
    n_threads: Optional[int] = None  # None = auto-detect
    n_batch: int = 512
    default_max_tokens: int = 256
    default_temperature: float = 0.7

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocalLLMConfig":
        return cls(
            model_name=data.get("model_name", "qwen2.5-0.5b-instruct-q4_k_m.gguf"),
            model_repo=data.get("model_repo", "Qwen/Qwen2.5-0.5B-Instruct-GGUF"),
            n_ctx=data.get("n_ctx", 2048),
            n_threads=data.get("n_threads"),
            n_batch=data.get("n_batch", 512),
            default_max_tokens=data.get("default_max_tokens", 256),
            default_temperature=data.get("default_temperature", 0.7),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_repo": self.model_repo,
            "n_ctx": self.n_ctx,
            "n_threads": self.n_threads,
            "n_batch": self.n_batch,
            "default_max_tokens": self.default_max_tokens,
            "default_temperature": self.default_temperature,
        }


@dataclass
class ProviderEntry:
    """Single LLM provider configuration."""

    default_model: str = ""
    api_key_env: str = ""
    base_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderEntry":
        return cls(
            default_model=data.get("default_model", ""),
            api_key_env=data.get("api_key_env", ""),
            base_url=data.get("base_url"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "default_model": self.default_model,
            "api_key_env": self.api_key_env,
        }
        if self.base_url:
            result["base_url"] = self.base_url
        return result


@dataclass
class LLMConfig:
    """
    LLM Configuration.

    Auto-discovered by SectionLoader -> loads from config/llm.yaml
    """

    section_id: str = "llm"
    source_file: str = "llm.yaml"

    local: LocalLLMConfig = field(default_factory=LocalLLMConfig)
    providers: Dict[str, ProviderEntry] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMConfig":
        providers = {}
        for name, pdata in data.get("providers", {}).items():
            providers[name] = ProviderEntry.from_dict(pdata)

        return cls(
            local=LocalLLMConfig.from_dict(data.get("local", {})),
            providers=providers,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "local": self.local.to_dict(),
            "providers": {name: p.to_dict() for name, p in self.providers.items()},
        }

    def validate(self) -> List[str]:
        errors = []
        if not self.local.model_name:
            errors.append("local.model_name is required")
        return errors

    def get_provider(self, name: str) -> Optional[ProviderEntry]:
        """Get provider config by name."""
        return self.providers.get(name)
```

4. `config/llm.yaml`:
```yaml
# LLM Configuration
# Auto-loaded by PhoenixConfig -> config.llm

local:
  model_name: "qwen2.5-0.5b-instruct-q4_k_m.gguf"
  model_repo: "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
  n_ctx: 2048
  n_threads: null  # auto-detect
  n_batch: 512
  default_max_tokens: 256
  default_temperature: 0.7

providers:
  anthropic:
    default_model: "claude-sonnet-4-20250514"
    api_key_env: "ANTHROPIC_API_KEY"
  openai:
    default_model: "gpt-4-turbo"
    api_key_env: "OPENAI_API_KEY"
  openrouter:
    default_model: "anthropic/claude-3.5-sonnet"
    api_key_env: "OPENROUTER_API_KEY"
  google:
    default_model: "gemini-2.0-flash"
    api_key_env: "GOOGLE_API_KEY"
```

**Then migrate `vibe_core/llm/local_llama_provider.py`:**

REPLACE lines 21-22:
```python
DEFAULT_MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
DEFAULT_MODEL_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
```

WITH:
```python
def _get_llm_config():
    """Get LLM config with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config
        return get_config().llm
    except Exception:
        from vibe_core.phoenix.sections.llm.section_main import LLMConfig
        return LLMConfig()
```

UPDATE `_get_model_search_paths()` to use config:
```python
def _get_model_search_paths() -> List[Path]:
    """Get model search paths."""
    llm_config = _get_llm_config()
    model_name = llm_config.local.model_name
    model_dir = _get_model_dir()
    return [
        model_dir / model_name,
        Path.home() / ".cache" / "steward" / "models" / model_name,
    ]
```

UPDATE `__init__` defaults to use config:
```python
def __init__(
    self,
    model_path: Optional[str] = None,
    n_ctx: Optional[int] = None,
    n_threads: Optional[int] = None,
    verbose: bool = False,
):
    llm_config = _get_llm_config()
    self.n_ctx = n_ctx or llm_config.local.n_ctx
    self.n_threads = n_threads or llm_config.local.n_threads or self._get_optimal_threads()
    # ... rest unchanged
```

UPDATE `download_default_model()`:
```python
def download_default_model(target_dir: Optional[Path] = None) -> Path:
    """Download the default model from HuggingFace."""
    llm_config = _get_llm_config()
    # ... use llm_config.local.model_name and llm_config.local.model_repo
```

---

### TASK 2: Create Quotas Section

**Create files:**

1. `vibe_core/phoenix/sections/quotas/__init__.py` (empty)

2. `vibe_core/phoenix/sections/quotas/manifest.json`:
```json
{
  "type": "section",
  "id": "quotas",
  "name": "Quota Configuration",
  "version": "1.0.0",
  "description": "Rate limits, budgets, circuit breaker settings",
  "entry_point": "section_main.py",
  "entry_class": "QuotasConfig",
  "priority": 10,
  "config_file": "config/quotas.yaml",
  "author": "STEWARD Protocol",
  "tags": ["config", "quotas", "limits"]
}
```

3. `vibe_core/phoenix/sections/quotas/section_main.py`:
```python
"""
Quotas Configuration - Rate limits, budgets, circuit breaker settings.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RateLimitsConfig:
    """Rate limiting configuration."""

    requests_per_minute: int = 10
    tokens_per_minute: int = 10000

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RateLimitsConfig":
        return cls(
            requests_per_minute=data.get("requests_per_minute", 10),
            tokens_per_minute=data.get("tokens_per_minute", 10000),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests_per_minute": self.requests_per_minute,
            "tokens_per_minute": self.tokens_per_minute,
        }


@dataclass
class BudgetConfig:
    """Budget limits configuration."""

    cost_per_hour_usd: float = 2.0
    cost_per_day_usd: float = 5.0
    cost_per_request_usd: float = 0.10
    alert_threshold: float = 0.80

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BudgetConfig":
        return cls(
            cost_per_hour_usd=data.get("cost_per_hour_usd", 2.0),
            cost_per_day_usd=data.get("cost_per_day_usd", 5.0),
            cost_per_request_usd=data.get("cost_per_request_usd", 0.10),
            alert_threshold=data.get("alert_threshold", 0.80),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cost_per_hour_usd": self.cost_per_hour_usd,
            "cost_per_day_usd": self.cost_per_day_usd,
            "cost_per_request_usd": self.cost_per_request_usd,
            "alert_threshold": self.alert_threshold,
        }


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    window_size_seconds: int = 60
    success_threshold_half_open: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CircuitBreakerConfig":
        return cls(
            failure_threshold=data.get("failure_threshold", 5),
            recovery_timeout_seconds=data.get("recovery_timeout_seconds", 30),
            window_size_seconds=data.get("window_size_seconds", 60),
            success_threshold_half_open=data.get("success_threshold_half_open", 1),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_seconds": self.recovery_timeout_seconds,
            "window_size_seconds": self.window_size_seconds,
            "success_threshold_half_open": self.success_threshold_half_open,
        }


@dataclass
class QuotasConfig:
    """Quotas Configuration."""

    section_id: str = "quotas"
    source_file: str = "quotas.yaml"

    rate_limits: RateLimitsConfig = field(default_factory=RateLimitsConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuotasConfig":
        return cls(
            rate_limits=RateLimitsConfig.from_dict(data.get("rate_limits", {})),
            budget=BudgetConfig.from_dict(data.get("budget", {})),
            circuit_breaker=CircuitBreakerConfig.from_dict(data.get("circuit_breaker", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rate_limits": self.rate_limits.to_dict(),
            "budget": self.budget.to_dict(),
            "circuit_breaker": self.circuit_breaker.to_dict(),
        }

    def validate(self) -> List[str]:
        errors = []
        if self.rate_limits.requests_per_minute < 1:
            errors.append("rate_limits.requests_per_minute must be >= 1")
        if self.budget.alert_threshold < 0 or self.budget.alert_threshold > 1:
            errors.append("budget.alert_threshold must be between 0 and 1")
        return errors
```

4. `config/quotas.yaml`:
```yaml
# Quotas Configuration
# Auto-loaded by PhoenixConfig -> config.quotas

rate_limits:
  requests_per_minute: 10
  tokens_per_minute: 10000

budget:
  cost_per_hour_usd: 2.0
  cost_per_day_usd: 5.0
  cost_per_request_usd: 0.10
  alert_threshold: 0.80

circuit_breaker:
  failure_threshold: 5
  recovery_timeout_seconds: 30
  window_size_seconds: 60
  success_threshold_half_open: 1
```

---

### TASK 3: Create Runtime Section

**Create files:**

1. `vibe_core/phoenix/sections/runtime/__init__.py` (empty)

2. `vibe_core/phoenix/sections/runtime/manifest.json`:
```json
{
  "type": "section",
  "id": "runtime",
  "name": "Runtime Configuration",
  "version": "1.0.0",
  "description": "Timeouts, intervals, limits for runtime behavior",
  "entry_point": "section_main.py",
  "entry_class": "RuntimeConfig",
  "priority": 10,
  "config_file": "config/runtime.yaml",
  "author": "STEWARD Protocol",
  "tags": ["config", "runtime", "timeouts"]
}
```

3. `vibe_core/phoenix/sections/runtime/section_main.py`:
```python
"""
Runtime Configuration - Timeouts, intervals, limits.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TimeoutsConfig:
    """Timeout configuration."""

    operator_timeout: float = 300.0
    action_timeout: int = 300
    test_timeout_ms: int = 5000
    ritual_interval: float = 300.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeoutsConfig":
        return cls(
            operator_timeout=data.get("operator_timeout", 300.0),
            action_timeout=data.get("action_timeout", 300),
            test_timeout_ms=data.get("test_timeout_ms", 5000),
            ritual_interval=data.get("ritual_interval", 300.0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator_timeout": self.operator_timeout,
            "action_timeout": self.action_timeout,
            "test_timeout_ms": self.test_timeout_ms,
            "ritual_interval": self.ritual_interval,
        }


@dataclass
class LimitsConfig:
    """System limits configuration."""

    max_recursion_depth: int = 5
    max_circuit_transitions: int = 20
    max_message_size: int = 1048576  # 1MB
    max_agent_restarts: int = 3
    event_history_size: int = 1000
    pulse_threshold: float = 10.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LimitsConfig":
        return cls(
            max_recursion_depth=data.get("max_recursion_depth", 5),
            max_circuit_transitions=data.get("max_circuit_transitions", 20),
            max_message_size=data.get("max_message_size", 1048576),
            max_agent_restarts=data.get("max_agent_restarts", 3),
            event_history_size=data.get("event_history_size", 1000),
            pulse_threshold=data.get("pulse_threshold", 10.0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_recursion_depth": self.max_recursion_depth,
            "max_circuit_transitions": self.max_circuit_transitions,
            "max_message_size": self.max_message_size,
            "max_agent_restarts": self.max_agent_restarts,
            "event_history_size": self.event_history_size,
            "pulse_threshold": self.pulse_threshold,
        }


@dataclass
class CircuitRecoveryConfig:
    """Circuit recovery configuration."""

    reflection_interval: int = 3
    stuck_threshold: int = 3
    max_retry_attempts: int = 5

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CircuitRecoveryConfig":
        return cls(
            reflection_interval=data.get("reflection_interval", 3),
            stuck_threshold=data.get("stuck_threshold", 3),
            max_retry_attempts=data.get("max_retry_attempts", 5),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reflection_interval": self.reflection_interval,
            "stuck_threshold": self.stuck_threshold,
            "max_retry_attempts": self.max_retry_attempts,
        }


@dataclass
class ActionDefaultsConfig:
    """Default action configuration."""

    retry_count: int = 3

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionDefaultsConfig":
        return cls(
            retry_count=data.get("retry_count", 3),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retry_count": self.retry_count,
        }


@dataclass
class RuntimeConfig:
    """Runtime Configuration."""

    section_id: str = "runtime"
    source_file: str = "runtime.yaml"

    timeouts: TimeoutsConfig = field(default_factory=TimeoutsConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)
    circuit_recovery: CircuitRecoveryConfig = field(default_factory=CircuitRecoveryConfig)
    action_defaults: ActionDefaultsConfig = field(default_factory=ActionDefaultsConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuntimeConfig":
        return cls(
            timeouts=TimeoutsConfig.from_dict(data.get("timeouts", {})),
            limits=LimitsConfig.from_dict(data.get("limits", {})),
            circuit_recovery=CircuitRecoveryConfig.from_dict(data.get("circuit_recovery", {})),
            action_defaults=ActionDefaultsConfig.from_dict(data.get("action_defaults", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeouts": self.timeouts.to_dict(),
            "limits": self.limits.to_dict(),
            "circuit_recovery": self.circuit_recovery.to_dict(),
            "action_defaults": self.action_defaults.to_dict(),
        }

    def validate(self) -> List[str]:
        errors = []
        if self.limits.max_recursion_depth < 1:
            errors.append("limits.max_recursion_depth must be >= 1")
        if self.limits.max_message_size < 1024:
            errors.append("limits.max_message_size must be >= 1024")
        return errors
```

4. `config/runtime.yaml`:
```yaml
# Runtime Configuration
# Auto-loaded by PhoenixConfig -> config.runtime

timeouts:
  operator_timeout: 300.0
  action_timeout: 300
  test_timeout_ms: 5000
  ritual_interval: 300.0

limits:
  max_recursion_depth: 5
  max_circuit_transitions: 20
  max_message_size: 1048576  # 1MB
  max_agent_restarts: 3
  event_history_size: 1000
  pulse_threshold: 10.0

circuit_recovery:
  reflection_interval: 3
  stuck_threshold: 3
  max_retry_attempts: 5

action_defaults:
  retry_count: 3
```

---

### TASK 4: Create APIs Section

**Create files:**

1. `vibe_core/phoenix/sections/apis/__init__.py` (empty)

2. `vibe_core/phoenix/sections/apis/manifest.json`:
```json
{
  "type": "section",
  "id": "apis",
  "name": "External APIs Configuration",
  "version": "1.0.0",
  "description": "Registry of external API env var names",
  "entry_point": "section_main.py",
  "entry_class": "APIsConfig",
  "priority": 10,
  "config_file": "config/apis.yaml",
  "author": "STEWARD Protocol",
  "tags": ["config", "apis", "external"]
}
```

3. `vibe_core/phoenix/sections/apis/section_main.py`:
```python
"""
APIs Configuration - External API registry.

Keys stay in environment variables - this section defines
WHERE to find them (which env var names).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os


@dataclass
class ExternalAPIEntry:
    """Single external API configuration."""

    env_var: str = ""
    description: str = ""
    required: bool = False
    additional_vars: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExternalAPIEntry":
        return cls(
            env_var=data.get("env_var", ""),
            description=data.get("description", ""),
            required=data.get("required", False),
            additional_vars=data.get("additional_vars", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "env_var": self.env_var,
            "description": self.description,
            "required": self.required,
        }
        if self.additional_vars:
            result["additional_vars"] = self.additional_vars
        return result

    def get_key(self) -> Optional[str]:
        """Get the API key from environment."""
        return os.getenv(self.env_var) if self.env_var else None

    def is_configured(self) -> bool:
        """Check if API key is set in environment."""
        return bool(self.get_key())


@dataclass
class APIsConfig:
    """
    External APIs Configuration.

    Auto-discovered by SectionLoader -> loads from config/apis.yaml
    """

    section_id: str = "apis"
    source_file: str = "apis.yaml"

    external: Dict[str, ExternalAPIEntry] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIsConfig":
        external = {}
        for name, edata in data.get("external", {}).items():
            external[name] = ExternalAPIEntry.from_dict(edata)

        return cls(external=external)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "external": {name: e.to_dict() for name, e in self.external.items()},
        }

    def validate(self) -> List[str]:
        errors = []
        for name, entry in self.external.items():
            if entry.required and not entry.is_configured():
                errors.append(f"Required API '{name}' not configured (set {entry.env_var})")
        return errors

    def get_api(self, name: str) -> Optional[ExternalAPIEntry]:
        """Get API config by name."""
        return self.external.get(name)

    def get_env_var(self, name: str, fallback: str = "") -> str:
        """Get env var name for an API, with fallback."""
        entry = self.external.get(name)
        return entry.env_var if entry else fallback

    def list_configured(self) -> List[str]:
        """List all APIs that have keys configured."""
        return [name for name, entry in self.external.items() if entry.is_configured()]

    def list_missing(self) -> List[str]:
        """List all APIs that are missing keys."""
        return [name for name, entry in self.external.items() if not entry.is_configured()]
```

4. `config/apis.yaml`:
```yaml
# External APIs Configuration
# Keys stay in environment - this defines WHERE to find them
# Auto-loaded by PhoenixConfig -> config.apis

external:
  tavily:
    env_var: "TAVILY_API_KEY"
    description: "Web search API for research capabilities"
    required: false

  twitter:
    env_var: "TWITTER_API_KEY"
    description: "Twitter/X API for broadcasting"
    required: false
    additional_vars:
      - "TWITTER_API_SECRET"
      - "TWITTER_ACCESS_TOKEN"
      - "TWITTER_ACCESS_SECRET"

  # Note: LLM provider keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
  # are defined in config/llm.yaml under providers section
```

**Then migrate files that hardcode env var names:**

1. `vibe_core/cartridges/system/herald/capabilities/research.py`:
```python
# BEFORE
self.api_key = os.getenv("TAVILY_API_KEY")

# AFTER
def _get_apis_config():
    try:
        from vibe_core.phoenix.config import get_config
        return get_config().apis
    except Exception:
        return None

# In __init__:
apis = _get_apis_config()
env_var = apis.get_env_var("tavily", "TAVILY_API_KEY") if apis else "TAVILY_API_KEY"
self.api_key = os.getenv(env_var)
```

2. Same pattern for:
   - `herald/capabilities/broadcast.py` (twitter)
   - `science/tools/web_search_tool.py` (tavily)
   - `herald/tools/research_tool.py` (tavily)

---

---

## MANDATORY: Tests für jede neue Section

**JEDE neue Section MUSS Tests haben. Sonnet MUSS diese erstellen.**

### Test Template für neue Sections

Erstelle `tests/test_config_SECTION_ID.py` für jede neue Section:

```python
"""Tests for SECTION_ID configuration section."""

import pytest
from vibe_core.phoenix.sections.SECTION_ID.section_main import SECTION_CLASS


class TestSECTION_CLASS:
    """Test SECTION_CLASS loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = SECTION_CLASS.from_dict({})
        assert config.section_id == "SECTION_ID"
        # Add assertions for default values

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            # Add custom test data
        }
        config = SECTION_CLASS.from_dict(data)
        # Add assertions for custom values

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = SECTION_CLASS.from_dict({})
        serialized = original.to_dict()
        restored = SECTION_CLASS.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()

    def test_validate_valid_config(self):
        """Test validation passes for valid config."""
        config = SECTION_CLASS.from_dict({})
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_config(self):
        """Test validation catches invalid config."""
        # Test with invalid data that should fail validation
        pass


class TestSECTION_CLASSIntegration:
    """Test SECTION_CLASS integration with PhoenixConfig."""

    def test_section_auto_discovered(self):
        """Test section is auto-discovered by SectionLoader."""
        from vibe_core.phoenix.config import get_config, reset_config
        reset_config()
        config = get_config()
        assert hasattr(config, "SECTION_ID")
        assert config.SECTION_ID is not None

    def test_section_accessible_via_getattr(self):
        """Test section accessible via config.SECTION_ID."""
        from vibe_core.phoenix.config import get_config, reset_config
        reset_config()
        config = get_config()
        section = config.SECTION_ID
        assert section.section_id == "SECTION_ID"
```

### Konkrete Test-Dateien die Sonnet erstellen MUSS:

1. `tests/test_config_llm.py` - Tests für LLMConfig
2. `tests/test_config_quotas.py` - Tests für QuotasConfig
3. `tests/test_config_runtime.py` - Tests für RuntimeConfig
4. `tests/test_config_apis.py` - Tests für APIsConfig

### Test-Kriterien (MUST PASS):

- [ ] `from_dict` mit leeren dict → defaults
- [ ] `from_dict` mit custom values → correct parsing
- [ ] `to_dict` → `from_dict` roundtrip
- [ ] `validate()` für valid config → empty errors
- [ ] `validate()` für invalid config → catches errors
- [ ] Section wird von PhoenixConfig auto-discovered
- [ ] Section ist via `config.section_id` erreichbar

---

## CATEGORY 6: PER-CARTRIDGE CONFIG (FUTURE - Document for completeness)

**Status**: NOT IN SCOPE für diesen Plan, aber dokumentiert für Vollständigkeit.

Per-Tool/Per-Cartridge params wie `max_tokens=100` in `marketer_content_tool.py:229` sind NICHT system-global.

**Zukünftige Lösung**:
- Cartridge-spezifische params gehören in `cartridge.yaml`
- Beispiel: `vibe_core/cartridges/agent_city/marketer/cartridge.yaml`
- Format:
```yaml
tools:
  marketer_content:
    max_tokens: 100
    temperature: 0.8
```

**Warum nicht jetzt**:
- Erfordert Änderungen am Cartridge-Loader
- System-weite Config hat höhere Priorität
- Kann als Phase 2 nach diesem Plan gemacht werden

**ABER**: Diese Lücke ist dokumentiert. Nicht vergessen.

---

## VERIFICATION COMMANDS

After each task, Sonnet should run:

```bash
# Test section loads
python -c "from vibe_core.phoenix.config import get_config; c = get_config(); print(f'llm: {c.llm}'); print(f'quotas: {c.quotas}'); print(f'runtime: {c.runtime}'); print(f'apis: {c.apis}')"

# Test NEW section tests (MANDATORY)
python -m pytest tests/test_config_llm.py tests/test_config_quotas.py tests/test_config_runtime.py tests/test_config_apis.py -v --tb=short

# Test all config tests
python -m pytest tests/test_config*.py -v --tb=short

# Grep for remaining hardcoded values
grep -rn "DEFAULT_MODEL" vibe_core/ --include="*.py" | grep -v __pycache__
grep -rn "= Path(" vibe_core/ --include="*.py" | grep -v __pycache__ | grep -v section_main
```
