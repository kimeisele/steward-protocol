# OPUS-161: Zollamt - The Customs Office

> **Status**: IMPLEMENTING
> **Created**: 2025-12-20
> **Pattern**: Compliance Gate
> **Depends**: OPUS-159 (Vibe Core Genesis)

---

## Preamble: Dreckiger Code darf nicht rein

Das Stadtamt baut Infrastruktur. Aber wer prüft, ob Code überhaupt reingelassen werden sollte?

Das Zollamt ist der Grenzposten. Bevor ein Modul geladen wird, prüft es: "Bist du GAD-000 compliant?"

## The Problem

```
BEFORE:
┌──────────────┐
│ base_loader  │
│              │
│  SHABDA      │  ← Find manifest
│  ARTHA       │  ← Validate manifest
│  PRATYAYA    │  ← Load config        ← Loads ANYTHING!
│  KARMA       │  ← Instantiate
└──────────────┘
```

```
AFTER:
┌──────────────┐
│ base_loader  │
│              │
│  SHABDA      │  ← Find manifest
│  ARTHA       │  ← Validate manifest
│  ┌────────┐  │
│  │ZOLLAMT │  │  ← Check compliance  ← NEW GATE
│  └────────┘  │
│  PRATYAYA    │  ← Load config
│  KARMA       │  ← Instantiate
└──────────────┘
```

## Implementation

### Integration Point

**File:** `vibe_core/loaders/base_loader.py`

**Method:** `_process_item_directory()`

**Location:** After ARTHA (validate_manifest), before PRATYAYA (load_config)

```python
# === ARTHA: Validate manifest ===
validation_errors = cls._validate_manifest(manifest)
if validation_errors:
    return ItemMeta(...)

# === ZOLLAMT: GAD-000 Compliance Check ===
if not cls._check_gad000_compliance(item_dir, manifest):
    return ItemMeta(
        item_id=item_id,
        item_type=cls.item_type,
        manifest=manifest,
        manifest_path=manifest_path,
        entry_path=None,
        entry_class=None,
        loaded_successfully=False,
        error="GAD-000 compliance check failed",
    )

# === PRATYAYA: Load config, check enabled ===
```

### Graceful Degradation

If `vibe_core.genesis` is not available (e.g., minimal install), the Zollamt gate is skipped with a warning.

```python
@classmethod
def _check_gad000_compliance(cls, item_dir: Path, manifest: Dict) -> bool:
    """
    ZOLLAMT: GAD-000 Compliance Gate.

    Returns True if module passes compliance check.
    Returns True if genesis service unavailable (graceful degradation).
    """
    try:
        from vibe_core.genesis import GenesisService
        genesis = GenesisService.get_instance()
        return genesis.quick_check(item_dir)
    except ImportError:
        logger.debug("Genesis service unavailable, skipping compliance check")
        return True
```

## Configuration

Compliance checking can be disabled via config:

```yaml
loader:
  compliance_check: true  # default
  compliance_mode: "warn"  # "warn" | "block" | "silent"
```

- `block`: Reject non-compliant modules (production)
- `warn`: Log warning but load anyway (development)
- `silent`: Skip check entirely (testing)

---

## HARNESS Verification

<!-- @HARNESS
files:
  - path: vibe_core/loaders/base_loader.py
    required: true
wiring:
  - pattern: "_check_gad000_compliance"
    in: vibe_core/loaders/base_loader.py
  - pattern: "from vibe_core.genesis import GenesisService"
    in: vibe_core/loaders/base_loader.py
-->

---

## Related Documents

- [OPUS-159: Vibe Core Genesis](159-VIBE-CORE-GENESIS.md)
- [OPUS-160: The Great Wiring](160-THE-GREAT-WIRING.md)
- [GAD-000: Operator Inversion Principle](../GAD-0XX/GAD-000.md)
