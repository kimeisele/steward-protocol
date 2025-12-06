# Phoenix Config Fractal - Auto-Discovery für ALLE Configs

> **Status:** PLAN
> **Date:** 2025-12-06
> **Depends on:** PHOENIX_CONFIG_V2.md, CLI_IMPLEMENTATION.md

---

## Problem

**Aktuell:**
```
config/
├── phoenix.yaml       # Monolithisch, manuell geladen
├── matrix.yaml        # Manuell geladen
├── quality.yaml       # Section existiert ✓
├── cli.yaml           # Section existiert ✓
├── steward.yaml       # Section existiert ✓
├── test_governance.yaml  # Section existiert ✓
└── ...
```

**Issues:**
1. `phoenix.yaml` ist monolithisch (kernel + agents + providers in einer Datei)
2. Manche Configs sind Sections, manche nicht - inkonsistent
3. Kein einheitliches Pattern für "neue Config hinzufügen"
4. `PhoenixConfig.from_files()` hat hardcoded Pfade

---

## Lösung: Alles wird Section

**Ziel:**
```
config/
├── kernel.yaml        # → vibe_core/phoenix/sections/kernel/
├── agents.yaml        # → vibe_core/phoenix/sections/agents/     NEU
├── providers.yaml     # → vibe_core/phoenix/sections/providers/  NEU
├── city.yaml          # → vibe_core/phoenix/sections/city/
├── quality.yaml       # → vibe_core/phoenix/sections/quality/
├── cli.yaml           # → vibe_core/phoenix/sections/cli/
├── steward.yaml       # → vibe_core/phoenix/sections/steward/
└── test_governance.yaml  # → vibe_core/phoenix/sections/test_governance/

# phoenix.yaml wird AUFGELÖST - existiert nicht mehr!
```

**Jede Section hat:**
```
vibe_core/phoenix/sections/<section_id>/
├── manifest.json      # Metadata (id, priority, config_file)
├── section_main.py    # Dataclass mit from_dict(), to_dict(), validate()
└── __init__.py        # Package export
```

---

## VEDA-4 Pattern auf Config

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHOENIX CONFIG FRACTAL                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PhoenixConfig.load()                                          │
│       │                                                         │
│       ▼                                                         │
│   ┌─────────────────┐                                          │
│   │  SHABDA         │  Scan vibe_core/phoenix/sections/        │
│   │  (Discovery)    │  Find all manifest.json files            │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  ARTHA          │  Load manifest.json                      │
│   │  (Parse)        │  Import section_main.py                  │
│   │                 │  Load config/*.yaml                      │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  PRATYAYA       │  Call section.validate()                 │
│   │  (Validate)     │  Check required fields                   │
│   │                 │  Type coercion                           │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │  KARMA          │  section.from_dict(yaml_data)            │
│   │  (Instantiate)  │  Return typed instance                   │
│   └─────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Migration: phoenix.yaml → Sections

### Phase 1: Extrahiere `agents` Section

**Aus phoenix.yaml:**
```yaml
agents:
  system_agents:
    - name: "DiscoveryAgent"
      class: "vibe_core.cartridges.system.discoverer.agent:Discoverer"
      ...
```

**Nach config/agents.yaml:**
```yaml
# Agents Configuration
# Auto-discovered system and city agents

system_agents:
  - name: "DiscoveryAgent"
    class: "vibe_core.cartridges.system.discoverer.agent:Discoverer"
    protocol: "VibeAgent"
    enabled: true
  # ... alle anderen agents

city_agents:
  - name: "AnalystAgent"
    # ...
```

**Neue Section: vibe_core/phoenix/sections/agents/**
```
agents/
├── manifest.json
├── section_main.py    # AgentsConfig dataclass
└── __init__.py
```

### Phase 2: Extrahiere `providers` Section

**Nach config/providers.yaml:**
```yaml
# Provider Configuration
# LLM, search, storage providers

llm:
  default: "anthropic"
  anthropic:
    api_key_env: "ANTHROPIC_API_KEY"
    pro_model: "claude-sonnet-4-20250514"
    low_model: "claude-haiku-3-20240307"
  openrouter:
    api_key_env: "OPENROUTER_API_KEY"
    # ...

search:
  tavily:
    api_key_env: "TAVILY_API_KEY"
```

### Phase 3: Lösche phoenix.yaml

Nach Migration enthält `phoenix.yaml` nur noch `system.kernel` - das gehört in `kernel.yaml` (existiert schon als Section).

**phoenix.yaml wird gelöscht.**

### Phase 4: Update PhoenixConfig

```python
# vibe_core/phoenix/config.py

class PhoenixConfig:
    """Unified config - auto-discovers all sections."""

    def __init__(self):
        self._sections: Dict[str, Any] = {}

    @classmethod
    def load(cls) -> "PhoenixConfig":
        """Load all config sections via auto-discovery."""
        config = cls()
        sections, metadata = SectionLoader.discover()
        config._sections = sections
        return config

    def get_section(self, section_id: str) -> Any:
        """Get a specific section."""
        return self._sections.get(section_id)

    # Typed accessors for common sections
    @property
    def kernel(self) -> "KernelConfig":
        return self._sections.get("kernel")

    @property
    def agents(self) -> "AgentsConfig":
        return self._sections.get("agents")

    @property
    def providers(self) -> "ProvidersConfig":
        return self._sections.get("providers")

    @property
    def city(self) -> "CityConfig":
        return self._sections.get("city")

    @property
    def cli(self) -> "CLIConfig":
        return self._sections.get("cli")
```

---

## Section Template

### manifest.json
```json
{
  "type": "section",
  "id": "my_section",
  "name": "My Section",
  "version": "1.0.0",
  "description": "Configuration for X",

  "entry_point": "section_main.py",
  "entry_class": "MySectionConfig",

  "priority": 100,
  "config_file": "config/my_section.yaml"
}
```

### section_main.py
```python
"""My Section Configuration."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MySectionConfig:
    """Configuration for X."""

    section_id: str = "my_section"
    source_file: str = "my_section.yaml"

    # Config fields
    enabled: bool = True
    some_setting: str = "default"
    nested: "NestedConfig" = field(default_factory=lambda: NestedConfig())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MySectionConfig":
        """Create from YAML data."""
        return cls(
            enabled=data.get("enabled", True),
            some_setting=data.get("some_setting", "default"),
            nested=NestedConfig.from_dict(data.get("nested", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "enabled": self.enabled,
            "some_setting": self.some_setting,
            "nested": self.nested.to_dict(),
        }

    def validate(self) -> List[str]:
        """Validate configuration."""
        errors = []
        if not self.some_setting:
            errors.append("some_setting cannot be empty")
        return errors


@dataclass
class NestedConfig:
    """Nested configuration example."""

    value: int = 42

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NestedConfig":
        return cls(value=data.get("value", 42))

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}
```

---

## Golden Template Location

```
docs/templates/config_section/
├── manifest.json
├── section_main.py
├── __init__.py
└── README.md
```

**Usage:**
```bash
# Create new config section
cp -r docs/templates/config_section vibe_core/phoenix/sections/my_section

# Create config file
touch config/my_section.yaml

# Edit manifest.json + section_main.py
# Done - auto-discovered on next load!
```

---

## Benefits

| Aspekt | Vorher | Nachher |
|--------|--------|---------|
| Neue Config | Hardcode in loader | Ordner kopieren |
| Validation | Manuell, inkonsistent | `validate()` überall |
| Type Safety | String keys | Typed dataclasses |
| Testing | Schwer zu mocken | Section isoliert testbar |
| Discovery | Manuell registrieren | Auto-discovery |
| Skalierung | Monolithisch | Fractal |

---

## Implementation Order

1. **Create Golden Template** `docs/templates/config_section/`
2. **Create `agents` Section** (extrahiere aus phoenix.yaml)
3. **Create `providers` Section** (extrahiere aus phoenix.yaml)
4. **Update `kernel` Section** (übernimm Rest aus phoenix.yaml)
5. **Delete phoenix.yaml**
6. **Update PhoenixConfig** (typed accessors)
7. **Update all consumers** (use new accessors)
8. **Tests** für jede Section

---

## Nicht im Scope

- matrix.yaml → bleibt erstmal (City-spezifisch)
- Circuits → eigenes Loader-Pattern (PlaybookLoader)
- MATRIX.md routing → eigenes Pattern

Diese können später auch Sections werden, aber erstmal Focus auf Core Config.

---

## Verification

Nach Implementation:
```bash
# Alle Sections werden discovered
python -c "from vibe_core.phoenix import get_config; c = get_config(); print(list(c._sections.keys()))"
# Output: ['kernel', 'agents', 'providers', 'city', 'cli', 'quality', 'steward', 'test_governance']

# Typed access funktioniert
python -c "from vibe_core.phoenix import get_config; print(get_config().agents.system_agents[0].name)"
# Output: DiscoveryAgent

# phoenix.yaml existiert nicht mehr
ls config/phoenix.yaml
# ls: config/phoenix.yaml: No such file or directory
```

---

## Related Docs

- [PHOENIX_CONFIG_V2.md](./PHOENIX_CONFIG_V2.md) - Dataclass design
- [CLI_IMPLEMENTATION.md](./CLI_IMPLEMENTATION.md) - CLI fractal pattern (same approach)
- [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) - Config inconsistencies to fix
