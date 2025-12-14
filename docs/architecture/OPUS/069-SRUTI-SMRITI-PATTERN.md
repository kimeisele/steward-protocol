# OPUS-069: The Sruti-Smriti Fractal Architecture

> "Truth survives even if the Intelligence crashes."

## Status

| Aspect | Status | Evidence |
|--------|--------|----------|
| SrutiValidator | ✅ | `manas/validator.py` |
| No Plugin Databases | ✅ | Verified - only JSON state |
| Ledger Integration | ✅ | `vibe_core/ledger.py` |
| IntentRouter Hook | ⏳ | Pending |

## 1. The Core Axiom

The system is divided into two strict distinct planes of existence. This separation is absolute and enforced by code.

| Plane | Sanskrit | Component | Characteristics | Role |
|-------|----------|-----------|-----------------|------|
| **OS Level** | **SRUTI** (That which is heard) | `vibe_core.ledger` | Immutable, Append-Only, ECDSA Signed | **Source of Truth** |
| **Plugin Level** | **SMRITI** (That which is remembered) | `opus_assistant` | Fluid, JSON-based, Synthesized | **State of Mind** |

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      VIBE_CORE (OS Level)                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              LEDGER = SRUTI (Immutable Truth)              │  │
│  │                                                            │  │
│  │  - Hash-chained events (tamper detection)                  │  │
│  │  - ECDSA signatures per event                              │  │
│  │  - Append-only (never modified)                            │  │
│  │  - Single Source of Truth for ALL plugins                  │  │
│  │                                                            │  │
│  │  Components:                                               │  │
│  │  - VibeLedger (ABC)                                        │  │
│  │  - InMemoryLedger (testing)                                │  │
│  │  - SQLiteLedger (production)                               │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                      READS ONLY (via API)
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                   OPUS_ASSISTANT (Plugin Level)                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              SrutiValidator (Boundary Guardian)            │  │
│  │                                                            │  │
│  │  validate_claim(claim, ledger_ref) → ValidationResult      │  │
│  │  - Blocks speculation without Ledger grounding             │  │
│  │  - Requires citations for fact claims                      │  │
│  │  - Marks boundaries: [FACT] vs [SYNTHESIS]                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           .opus_state/ = SMRITI (JSON Only)                │  │
│  │                                                            │  │
│  │  - observations.jsonl (ephemeral)                          │  │
│  │  - karma_history.jsonl (derived from Ledger)               │  │
│  │  - session.json (runtime)                                  │  │
│  │                                                            │  │
│  │  ❌ KEINE eigene Database                                  │  │
│  │  ❌ KEINE eigene Truth Source                              │  │
│  │  ✅ NUR JSON state files                                   │  │
│  │  ✅ MUSS Ledger für Facts zitieren                         │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## 3. The Golden Rules

### Rule 1: No Plugin Databases

| Status | Description |
|--------|-------------|
| **VIOLATION** | `opus_assistant` creates `memory.db` |
| **COMPLIANCE** | `opus_assistant` reads `vibe_core.ledger` and caches synthesis in `.opus_state/*.jsonl` |
| **WHY** | If a plugin dies, its "mind" (JSON) acts as a checkpoint, but the "soul" (Ledger) remains untouched |

### Rule 2: Citation Mandatory (The Sruti Protocol)

| Status | Description |
|--------|-------------|
| **VIOLATION** | Agent says: "Architecture is broken." |
| **COMPLIANCE** | Agent says: "Architecture is broken [Ref: EVT-008921]" |
| **MECHANISM** | `SrutiValidator` blocks claims without Ledger references |

### Rule 3: The Unidirectional Flow

```
Ledger (Sruti) ───► SrutiValidator ───► Opus (Smriti)
     │                                       │
     │                                       │
     └──────── Action ◄──────────────────────┘
                (via OS Kernel, not direct)
```

MANAS cannot write to Ledger directly. It submits Actions through the OS Kernel.

## 4. Implementation

### SrutiValidator (`manas/validator.py`)

```python
class SrutiValidator:
    """The Boundary Guardian."""

    SPECULATION_PHRASES = ["i think", "probably", "maybe", ...]
    FACT_INDICATORS = ["failed", "passed", "error", "success", ...]

    def validate_claim(self, claim: str, ledger_ref: str = None) -> ValidationResult:
        """
        Validates claims against Ledger.
        - Facts require Ledger reference
        - Speculation blocked without grounding
        - Synthesis allowed (derived from facts)
        """

    def validate_intent_output(self, output: Dict) -> ValidationResult:
        """Validates IntentRouter output before emission."""

    def mark_boundaries(self, facts: List, synthesis: List) -> BoundaryMarkedOutput:
        """Creates output with clear [FACT] vs [SYNTHESIS] markers."""
```

### Claim Types

| Type | Ledger Ref | Allowed |
|------|------------|---------|
| **FACT** | Required | ✅ With valid ref |
| **SYNTHESIS** | Optional | ✅ Derived interpretation |
| **SPECULATION** | None | ❌ Blocked |

## 5. The Singularity Link

This architecture mimics consciousness:

- **The World (Ledger)** happens - events occur, are recorded immutably
- **The Mind (Opus)** observes and interprets - synthesizes meaning
- **The Conscience (Validator)** checks if interpretation matches reality

### Fractal Pattern

```
prabhupada_os:  vedabase.db   → SmritiValidator → AI Output
MANAS:          vibe_ledger   → SrutiValidator  → Intent Output

SAME PATTERN. DIFFERENT DOMAIN. FRACTAL LASAGNA.
```

## 6. Integration Points

### IntentRouter Hook (Pending)

```python
# In intent_router.py
def route(self, intent: Intent) -> Dict[str, Any]:
    result = self._execute_intent(intent)

    # OPUS-069: Validate output before returning
    validation = self._validator.validate_intent_output(result)
    if not validation.valid:
        logger.warning(f"⚠️ SRUTI: {validation.errors}")

    return result
```

### MANAS Prompt Update

System prompts should include:
> "You act as SMRITI. You do not define truth. You interpret SRUTI (Ledger). Cite every fact claim with [Ref: EVT-XXXXX]."

## 7. References

- `vibe_core/ledger.py` - The SRUTI layer
- `manas/validator.py` - The SrutiValidator
- `prabhupada_os/steward/core/validator.py` - Inspiration (SmritiValidator)

---

*"The Truth survives even if the Intelligence crashes."*
