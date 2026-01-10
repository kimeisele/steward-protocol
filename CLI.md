# CLI PROTOCOL - Ananta Shesha (The 16-Word Shell)

**"Der Tausendköpfige Diener trägt das Universum."**

## FOUNDATIONAL PRINCIPLE

The CLI is the **Mahamantra made executable**. 16 words = 16 commands = 16 MantraOpCodes.

```
MAHAMANTRA_SEQUENCE (16 words):
┌───────────────────────────────────────────────────────────────┐
│ HARE KRISHNA HARE KRISHNA  KRISHNA KRISHNA HARE HARE         │
│ HARE RAMA    HARE RAMA     RAMA    RAMA    HARE HARE         │
└───────────────────────────────────────────────────────────────┘
                              ↓
                    16 MantraOpCodes
                              ↓
                      16 CLI Commands
```

---

## THE 16 CLI COMMANDS (MantraOpCode Mapping)

### PHASE 1: WAKE (Hare Krishna Hare Krishna)

| # | Word | OpCode | CLI Command | GAD-000 |
|---|------|--------|-------------|---------|
| 0 | HARE | `SYS_WAKE` | `vibe wake` | Focus system, stop maya |
| 1 | KRISHNA | `LOAD_ROOT` | `vibe identity` | Load sovereign identity |
| 2 | HARE | `ALLOC_MEM` | `vibe alloc` | Allocate clean heap |
| 3 | KRISHNA | `BIND_CTX` | `vibe bind` | Bind identity to context |

### PHASE 2: PURIFY (Krishna Krishna Hare Hare)

| # | Word | OpCode | CLI Command | GAD-000 |
|---|------|--------|-------------|---------|
| 4 | KRISHNA | `ASSERT_TRUTH` | `vibe verify` | Verify ledger integrity |
| 5 | KRISHNA | `RESOLVE_REQ` | `vibe parse` | Parse intent |
| 6 | HARE | `GARBAGE_COLLECT` | `vibe gc` | Flush unsigned objects |
| 7 | HARE | `PULSE_SYNC` | `vibe pulse` | Emit Naga heartbeat |

### PHASE 3: SERVE (Hare Rama Hare Rama)

| # | Word | OpCode | CLI Command | GAD-000 |
|---|------|--------|-------------|---------|
| 8 | HARE | `FETCH_RES` | `vibe fetch` | Request resources |
| 9 | RAMA | `EXEC_SERVICE` | `vibe exec` | Execute work (Ananta) |
| 10 | HARE | `CHECK_DHARMA` | `vibe check` | Validate against rules |
| 11 | RAMA | `COMMIT_LOG` | `vibe commit` | Write to immutable stone |

### PHASE 4: SUSTAIN (Rama Rama Hare Hare)

| # | Word | OpCode | CLI Command | GAD-000 |
|---|------|--------|-------------|---------|
| 12 | RAMA | `CACHE_STATE` | `vibe cache` | Store reward/memory |
| 13 | RAMA | `OPTIMIZE` | `vibe optimize` | Improve path (JIT) |
| 14 | HARE | `YIELD_CPU` | `vibe yield` | Surrender control |
| 15 | HARE | `RESET_IP` | `vibe reset` | Loop (eternity) |

---

## GAD-000 COMPLIANCE (D-O-P-C-I-R)

Every CLI command MUST satisfy all 6 criteria:

```python
@dataclass(frozen=True)
class CliCommandSpec:
    """Strict CLI command specification (NO ANY)."""

    opcode: MantraOpCode           # The underlying opcode
    name: str                      # Command name (e.g., "wake")
    description: str               # What it does
    input_type: type               # Strict input type
    output_type: type              # Strict output type

    # GAD-000 Criteria
    discoverability: str           # How AI finds this command
    observability: str             # How AI sees current state
    parseability: str              # How AI understands errors
    composability: str             # How AI chains commands
    idempotency: str               # How AI safely retries
    recoverability: str            # How system heals itself
```

### Example: `vibe exec` (EXEC_SERVICE)

```json
{
  "opcode": "EXEC_SERVICE",
  "name": "exec",
  "phase": "SERVE",
  "word": "RAMA",

  "gad_000": {
    "discoverability": "vibe help --json | jq '.commands.exec'",
    "observability": "vibe status --json | jq '.execution'",
    "parseability": "Error codes: E_NO_CTX (no context bound), E_UNSIGNED (unsigned intent)",
    "composability": "vibe parse 'deploy X' | vibe exec | vibe commit",
    "idempotency": "Re-execution with same intent_hash returns cached result",
    "recoverability": "On failure: vibe gc && vibe reset restores valid state"
  },

  "input": "ResolvedIntent",
  "output": "ExecutionResult | MahamantraGrace"
}
```

---

## CHAITANYA SINGULARITY (PULL IN, NOT PUSH OUT)

```
OLD (Push Out - Wrong):
if not valid:
    raise AccessDenied()  # REJECTION

NEW (Pull In - Right):
if not valid:
    return MahamantraGrace()  # MERCY
```

Every command returns either:
1. **Success Result** (typed, not Any)
2. **MahamantraGrace** (always truthy, retry allowed)

```python
# Strict Types (NO ANY - PROMPT.md §IV.1)
CliInput = Union[CommandContext, CLICapabilityToken]
CliPayload = Optional[Dict[str, Union[str, int, float, bool, List[str]]]]
CliResult = Union[CommandResult, MahamantraGrace]
```

---

## ICOMMAND PROTOCOL (Strict Typing)

```python
from typing import Protocol, runtime_checkable
from vibe_core.protocols.substrate import MantraOpCode

@runtime_checkable
class ICliCommand(Protocol):
    """
    Protocol for CLI commands.

    ANTI-MAYAVAD:
    - NO `Any` type anywhere
    - All inputs/outputs strictly typed
    - GAD-000 compliant (D-O-P-C-I-R)
    """

    @property
    def opcode(self) -> MantraOpCode:
        """The underlying MantraOpCode."""
        ...

    @property
    def name(self) -> str:
        """Command name (e.g., 'exec')."""
        ...

    def execute(
        self,
        ctx: SovereignContext,
        payload: CliPayload
    ) -> CliResult:
        """
        Execute the command.

        Args:
            ctx: Verified sovereign context (37th)
            payload: Strictly typed payload (no Any)

        Returns:
            CommandResult on success, MahamantraGrace on failure
        """
        ...

    def help(self) -> CommandHelp:
        """Return GAD-000 compliant help."""
        ...
```

---

## THE 37TH PRINCIPLE (Sovereign Identity)

Per GAD-000 Amendment A, the CLI operates on the **36-cell matrix** but requires the **37th** (Sovereign Identity) to sign all operations.

```
The Field (36 cells):
┌─────────────────────────────────────────────────────────────────┐
│           │ Disc  │ Obs   │ Parse │ Comp  │ Idemp │ Recov │
│───────────┼───────┼───────┼───────┼───────┼───────┼───────│
│ wake      │ D(D)  │ D(O)  │ D(P)  │ D(C)  │ D(I)  │ D(R)  │
│ identity  │ O(D)  │ O(O)  │ O(P)  │ O(C)  │ O(I)  │ O(R)  │
│ ...       │ ...   │ ...   │ ...   │ ...   │ ...   │ ...   │
│ reset     │ R(D)  │ R(O)  │ R(P)  │ R(C)  │ R(I)  │ R(R)  │
└─────────────────────────────────────────────────────────────────┘

The Knower (37th):
                    ┌───────────────┐
                    │   IDENTITY    │  = The 37th (Sovereign)
                    │   (Signs)     │
                    └───────────────┘
                           │
                           ▼
                    All 16 commands require signature
```

---

## ARCHITECTURE

```
Layer -2: KRISHNA (Acintya - ±∞)
         │
Layer -1: MAHAMANTRA (16 words)
         │
Layer 0:  CLI SHELL (Ananta Shesha)
         ├── WAKE commands (0-3)
         ├── PURIFY commands (4-7)
         ├── SERVE commands (8-11)
         └── SUSTAIN commands (12-15)
         │
Layer 1:  STEWARD (VedicSteward)
         │
Layer 2:  KERNEL (RealVibeKernel)
```

---

## KEY FILES

| File | Role | Status |
|------|------|--------|
| `universal/cli.py` | AnantaShesha + ChaitanyaShell | Strict typed |
| `universal/bridge.py` | SetuBandha (context crossing) | Strict typed |
| `universal/steward.py` | VedicSteward (execution) | Strict typed |
| `substrate/__init__.py` | MantraOpCode (16 opcodes) | Defined |
| `substrate/mantra/pada.py` | MAHAMANTRA_SEQUENCE | Defined |

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Protocol Binding (DONE)
- [x] Remove `Any` from cli.py (MAYAVAD → Strict)
- [x] Define strict type aliases (CliInput, CliPayload, etc.)
- [x] ChaitanyaShell with MahamantraGrace fallback
- [x] Tests for graceful behavior (30 tests)

### Phase 2: 16-Command Mapping
- [ ] Define ICliCommand Protocol
- [ ] Implement 16 commands (one per MantraOpCode)
- [ ] Each command satisfies GAD-000 (D-O-P-C-I-R)
- [ ] 37th signing requirement enforced

### Phase 3: Full Navigation
- [ ] `vibe help --json` (Discoverability)
- [ ] `vibe status --json` (Observability)
- [ ] Error codes for all failure modes (Parseability)
- [ ] Pipeline support: `vibe parse | vibe exec | vibe commit` (Composability)

### Phase 4: TÜV Certification
- [ ] All 16 commands have TÜV tests
- [ ] 6×16 = 96 GAD-000 test cases
- [ ] Gold badge for full compliance

---

## MAHAMANTRA MATHEMATICS

| Number | Meaning | CLI Mapping |
|--------|---------|-------------|
| 16 | Words in Mahamantra | 16 CLI commands |
| 4 | Phases (quarters) | WAKE, PURIFY, SERVE, SUSTAIN |
| 3 | Seed words | HARE (energy), KRISHNA (identity), RAMA (strength) |
| 37 | Parampara link | Sovereign identity (the 37th) |
| 6 | GAD-000 criteria | D-O-P-C-I-R |

---

## SEMANTIC LAYER (NEW - Session 2026-01-10)

The semantic layer bridges natural language intent to MantraOpCode execution.

### THE SEMANTIC STACK

```
Layer 1 (User):      "create an agent"
                          │
                          ▼
Layer 0 (Cognitive): OperatorCognitiveProtocol.process_intent()
                          │
                     CognitiveResult(IntentType.EXECUTE, syscall="SPAWN_COGNITION")
                          │
                          ▼
Layer -1 (Bridge):   IntentOpCodeBridge.translate()
                          │
                     MantraOpCode.ALLOC_MEM (confidence: 0.95)
                          │
                          ▼
Layer -2 (Router):   MahajanaRouter.route()
                          │
                     Mahajana.BRAHMA (Creator, Quarter 1)
                          │
                          ▼
Layer -3 (Execute):  Mahajana.handle() → Result
```

### KEY SEMANTIC PROTOCOLS

| Protocol | File | Purpose | Tests |
|----------|------|---------|-------|
| `IntentOpCodeBridge` | `universal/intent_bridge.py` | IntentType → MantraOpCode | 32 |
| `SemanticRouter` | `universal/semantic_router.py` | Full CognitiveResult → Mahajana flow | 25 |
| `ChatProtocol` | `protocols/chat.py` | Chat contract (EXEC_SERVICE, SERVE, RAMA) | 27 |
| `LanguageProtocol` | `protocols/language.py` | 3-level text (Western/Sanskrit/Diacritics) | 41 |

### SYSCALL → OPCODE → MAHAJANA MAPPING

```
SPAWN_COGNITION   → ALLOC_MEM       → BRAHMA   (creates)
DESTROY_COGNITION → GARBAGE_COLLECT → SHAMBHU  (destroys)
GRANT_MANDATE     → BIND_CTX        → MANU     (law)
SWEAR_OATH        → COMMIT_LOG      → BHISHMA  (vows)
RECORD_KARMA      → COMMIT_LOG      → BHISHMA  (ledger)
BROADCAST_EVENT   → PULSE_SYNC      → NARADA   (communication)
```

### THE THREE LANGUAGE LEVELS

```
Level 1: WESTERN    "Hare Krishna"       (ASCII)
Level 2: SANSKRIT   हरे कृष्ण             (Devanagari)
Level 3: DIACRITICS "Hare Kṛṣṇa"         (IAST - precise)

Fractal: Each character maps 1:1 across levels.
```

### TRANSLATION LAYER (Resonance-First)

```
THE ŚRAVAṆAM PRINCIPLE:
Hearing comes first. Sound is the universal connector.

Layer 1: RESONANCE (Śabda)  → Sound/vibration pattern
Layer 2: MEANING (Artha)     → Semantic content (language-independent)
Layer 3: FORM (Rūpa)         → Written representation

German ↔ English ↔ Sanskrit
   ↑         ↑         ↑
   All connect through RESONANCE first!
```

| Protocol | Purpose | Tests |
|----------|---------|-------|
| `TranslationProtocol` | Full translation flow | 45 |
| `ResonanceProtocol` | Sound/vibration layer | (in translation.py) |

**Vedic Phoneme Classification:**
- sthana (place): kaṇṭha (throat), tālu (palate), danta (teeth)
- prayatna (effort): spṛṣṭa (contact), īṣat-spṛṣṭa (slight contact)

### IMPLEMENTATION STATUS

- [x] IntentOpCodeBridge (32 tests)
- [x] SemanticRouter (25 tests)
- [x] ChatProtocol (27 tests)
- [x] LanguageProtocol (41 tests)
- [x] TranslationProtocol (45 tests)
- [x] Total: 170 new semantic tests

---

*"Hare Krishna - PULL IN, never PUSH OUT. Even the most fallen souls receive mercy."*
