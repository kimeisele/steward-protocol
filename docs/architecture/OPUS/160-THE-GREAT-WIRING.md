# OPUS-160: The Great Wiring

> **Status**: IMPLEMENTING
> **Created**: 2025-12-20
> **Pattern**: Service Integration
> **Depends**: OPUS-159 (Vibe Core Genesis)

---

## Preamble: Das Telefon klingelt endlich

OPUS-159 hat das Stadtamt gebaut. Aber niemand ruft an.
OPUS-160 legt die Stromleitungen - jetzt klingelt das Telefon.

## The Problem

```
BEFORE (Spaghetti):
┌───────────────────────┐    ┌───────────────────────┐
│  Engineer BuilderTool │    │  MANAS Genesis        │
│  - Own templates      │    │  - Own templates      │
│  - Own placeholders   │    │  - Own generator      │
│  - Own logic          │    │  - Duplicated code    │
└───────────────────────┘    └───────────────────────┘
         ↓                            ↓
    Creates Files              Creates Files
    (Different Format)         (Different Format)
```

```
AFTER (Lasagna):
┌───────────────────────┐    ┌───────────────────────┐
│  Engineer BuilderTool │    │  MANAS CognitiveKernel│
│  - Delegates to →     │    │  - Delegates to →     │
└───────────┬───────────┘    └───────────┬───────────┘
            │                            │
            └──────────┬─────────────────┘
                       ▼
            ┌───────────────────────┐
            │  GenesisService       │
            │  (vibe_core/genesis)  │
            │  - Single source      │
            │  - GAD-000 compliant  │
            │  - Tested (36 tests)  │
            └───────────────────────┘
```

## Changes Required

### 1. Engineer BuilderTool Refactor

**File:** `vibe_core/cartridges/system/engineer/tools/builder_tool.py`

**Before:**
```python
def scaffold_from_template(self, ...):
    # Read template files manually
    # Replace YOUR_AGENT_ID placeholders
    # Write files directly
```

**After:**
```python
def scaffold_from_template(self, ...):
    from vibe_core.genesis import GenesisService, ModuleType

    genesis = GenesisService.get_instance()
    result = genesis.scaffold_new(
        path=target_dir,
        module_type=ModuleType.CARTRIDGE,
        context={
            "id": agent_id,
            "name": agent_name,
            "domain": domain,
            "description": description,
        }
    )
    return self._convert_result(result)
```

### 2. MANAS Delegation

**File:** `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`

**Before:**
```python
def _process_genesis_vibrations(self, perception):
    # Uses own InfrastructureClassifier
    # Uses own InfrastructureGenerator
```

**After:**
```python
def _process_genesis_vibrations(self, perception):
    from vibe_core.genesis import GenesisService

    genesis = GenesisService.get_instance()

    for vibration in perception.vibrations:
        if vibration.event_type == "created" and vibration.is_directory:
            result = genesis.ensure_compliance(vibration.path)
            # Log result
```

### 3. Keep OPUS-158 as Fallback

MANAS Genesis (OPUS-158) bleibt als:
- MANAS-spezifische Erweiterungen
- Fallback wenn vibe_core nicht verfügbar
- Legacy support

---

## HARNESS Verification

<!-- @HARNESS
files:
  - path: vibe_core/cartridges/system/engineer/tools/builder_tool.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
wiring:
  - pattern: "from vibe_core.genesis import GenesisService"
    in: vibe_core/cartridges/system/engineer/tools/builder_tool.py
  - pattern: "genesis.scaffold_new"
    in: vibe_core/cartridges/system/engineer/tools/builder_tool.py
  - pattern: "from vibe_core.genesis import GenesisService"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
-->

---

## Related Documents

- [OPUS-158: MANAS Genesis PoC](158-INFRASTRUCTURE-GENESIS.md)
- [OPUS-159: Vibe Core Genesis](159-VIBE-CORE-GENESIS.md)
