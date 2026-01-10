# PROTOCOLS.md - The Living Protocol Registry

**"If no Protocol, it doesn't exist."**

## FOUNDATIONAL PRINCIPLE

```
PROTOCOL FIRST - Always.

Implementation without Protocol = MAYAVAD (impersonal, unverifiable)
Protocol with Implementation = PERSONAL (verified, accountable)

"Vishnu is God. Only if it says Vishnu, it is Vishnu - otherwise mayavad."
```

---

## THE 16-FOLD ARCHITECTURE

### MantraOpCode → Mahajana → Protocol

| # | Word | OpCode | Mahajana | Protocol Domain |
|---|------|--------|----------|-----------------|
| 0 | HARE | SYS_WAKE | (Avatara: PRITHU) | System boot |
| 1 | KRISHNA | LOAD_ROOT | BRAHMA | Identity loading |
| 2 | HARE | ALLOC_MEM | NARADA | Resource allocation |
| 3 | KRISHNA | BIND_CTX | SHAMBHU | Context binding |
| 4 | KRISHNA | ASSERT_TRUTH | (Avatara: VYASA) | Integrity verification |
| 5 | KRISHNA | RESOLVE_REQ | KUMARAS | Intent parsing |
| 6 | HARE | GARBAGE_COLLECT | KAPILA | Cleanup/analysis |
| 7 | HARE | PULSE_SYNC | MANU | Heartbeat/sync |
| 8 | HARE | FETCH_RES | (Avatara: PARASHURAMA) | Resource fetching |
| 9 | RAMA | EXEC_SERVICE | PRAHLADA | Execution |
| 10 | HARE | CHECK_DHARMA | JANAKA | Validation |
| 11 | RAMA | COMMIT_LOG | BHISHMA | Ledger commit |
| 12 | RAMA | CACHE_STATE | (Avatara: NRISIMHA) | State caching |
| 13 | RAMA | OPTIMIZE | BALI | Optimization |
| 14 | HARE | YIELD_CPU | SHUKA | Control surrender |
| 15 | HARE | RESET_IP | YAMARAJA | Cycle reset |

---

## PROTOCOL LAYERS

```
Layer -2: KRISHNA (Acintya - ±∞)
         │
Layer -1: SUBSTRATE (MantraOpCode, iGene, IAnantaBridge)
         │
Layer 0:  NAGA LOKA (Federation, Services, Flood)
         │
Layer 1:  MAHAJANAS (12 Protocol Owners)
         │
Layer 2:  CLI/COMMANDS (Protocol-Based Commands)
         │
Layer 3:  USER
```

---

## PROTOCOL REGISTRY

### SUBSTRATE (Layer -1)

| Protocol | File | Tests | Status |
|----------|------|-------|--------|
| `MantraOpCode` | `substrate/__init__.py` | ✓ | SEALED |
| `IGene` | `substrate/gene.py` | ✓ | SEALED |
| `IAnantaBridge` | `substrate/__init__.py` | ✓ | SEALED |
| `MantraByte` | `substrate/byte.py` | ✓ | SEALED |

### NAGA (Layer 0)

| Protocol | Mahajana | OpCode | Tests | Status |
|----------|----------|--------|-------|--------|
| `SeshaProtocol` | BRAHMA | LOAD_ROOT | ✓ | SEALED |
| `VasukiProtocol` | NARADA | ALLOC_MEM | ✓ | SEALED |
| `TakshakaProtocol` | YAMARAJA | RESET_IP | ✓ | SEALED |
| `FloodProtocol` | NARADA | PULSE_SYNC | 50 | NEW |
| `IntelBridgeProtocol` | SHUKA | YIELD_CPU | 51 | NEW |
| `NagaFederationProtocol` | - | - | ✓ | SEALED |

### SEMANTIC (Layer 1)

| Protocol | Mahajana | OpCode | Tests | Status |
|----------|----------|--------|-------|--------|
| `ChatProtocol` | PRAHLADA | EXEC_SERVICE | 27 | SEALED |
| `LanguageProtocol` | KUMARAS | RESOLVE_REQ | 119 | SEALED |
| `TranslationProtocol` | KUMARAS | RESOLVE_REQ | 114 | SEALED |
| `IntentOpCodeBridge` | - | - | 32 | SEALED |
| `SemanticRouter` | - | - | 25 | SEALED |

### MAHAJANAS (Layer 1)

| Mahajana | Protocol | Domain | OpCodes Owned |
|----------|----------|--------|---------------|
| BRAHMA | `BrahmaProtocol` | Creation | LOAD_ROOT |
| NARADA | `NaradaProtocol` | Communication | ALLOC_MEM, PULSE_SYNC |
| SHAMBHU | `ShambhuProtocol` | Destruction | BIND_CTX, GARBAGE_COLLECT |
| KUMARAS | `KumarasProtocol` | Purity | RESOLVE_REQ |
| KAPILA | `KapilaProtocol` | Analysis | - |
| MANU | `ManuProtocol` | Law | - |
| PRAHLADA | `PrahladaProtocol` | Resilience | EXEC_SERVICE |
| JANAKA | `JanakaProtocol` | Duty | CHECK_DHARMA |
| BHISHMA | `BhishmaProtocol` | Vow | COMMIT_LOG |
| BALI | `BaliProtocol` | Surrender | OPTIMIZE |
| SHUKA | `ShukaProtocol` | Vision | YIELD_CPU |
| YAMARAJA | `YamarajaProtocol` | Judgment | RESET_IP |

---

## CLI ARCHITECTURE (THE PROBLEM)

### Current State (MAYAVAD - God File)

```
vibe_core/cli/naga_cli.py = 1235 lines (GOD FILE!)
├── 11 cmd_* methods
├── 19 private _* methods
└── NO PROTOCOL = NO ACCOUNTABILITY
```

### Target State (PROTOCOL-BASED)

```
vibe_core/cli/
├── __init__.py              # CLI Registry
├── protocols/
│   ├── cli_command.py       # ICliCommand Protocol
│   └── cli_registry.py      # Command discovery
├── commands/
│   ├── wake/                # Phase 1: WAKE
│   │   ├── status.py        # SYS_WAKE
│   │   └── identity.py      # LOAD_ROOT
│   ├── purify/              # Phase 2: PURIFY
│   │   ├── scan.py          # ASSERT_TRUTH
│   │   ├── detect.py        # RESOLVE_REQ
│   │   └── gc.py            # GARBAGE_COLLECT
│   ├── serve/               # Phase 3: SERVE
│   │   ├── chat.py          # EXEC_SERVICE
│   │   ├── intel.py         # FETCH_RES
│   │   └── commit.py        # COMMIT_LOG
│   └── sustain/             # Phase 4: SUSTAIN
│       ├── cache.py         # CACHE_STATE
│       └── reset.py         # RESET_IP
└── naga/                    # Naga-specific (delegates to commands/)
```

### Command Protocol

```python
@runtime_checkable
class ICliCommand(Protocol):
    """Every CLI command is a protocol."""

    @property
    def opcode(self) -> MantraOpCode:
        """Which MantraOpCode does this command execute?"""
        ...

    @property
    def mahajana(self) -> str:
        """Which Mahajana owns this command?"""
        ...

    @property
    def name(self) -> str:
        """Command name (e.g., 'scan', 'chat')."""
        ...

    def execute(self, args: List[str]) -> int:
        """Execute the command. Returns exit code."""
        ...

    def help(self) -> str:
        """GAD-000 compliant help text."""
        ...
```

---

## BALARAMA PATTERN (Auto-Expansion)

```python
# Balarama injects life into commands
class BalaramaCLI:
    """
    The First Expansion of CLI.
    Discovers and injects commands at runtime.
    """

    def __init__(self):
        self._commands: Dict[str, ICliCommand] = {}
        self._discover_commands()

    def _discover_commands(self):
        """Discover all ICliCommand implementations."""
        # Scan commands/ directory
        # Each file that exports ICliCommand is registered
        pass

    def inject(self, command: ICliCommand) -> None:
        """Balarama injects a command into the registry."""
        self._commands[command.name] = command
```

---

## PROTOCOL COVERAGE

```
Current:  ~15% of codebase has protocols
Target:   100% of public interfaces have protocols

Without protocol = CANNOT EXIST
With protocol = VERIFIED EXISTENCE
```

---

## IMPLEMENTATION STATUS

### Completed (Phase 32-34)

| Task | Status | Tests |
|------|--------|-------|
| `INagaCommand` protocol | SEALED | 79 |
| `NagaCommandRegistry` (Balarama) | SEALED | included |
| `StatusCommand` (PRITHU) | SEALED | 14 |
| `ScanCommand` (VYASA) | SEALED | 17 |
| `ChatCommand` (PRAHLADA) | SEALED | 12 |
| `IntelCommand` (SHUKA) | SEALED | 13 |
| `@naga_command` decorator | SEALED | included |
| Mahajana enum (16 members) | SEALED | 17 |
| Phase enum (4 members) | SEALED | 4 |
| OpCode→Mahajana mapping | SEALED | 18 |

### New Fractal Structure

```
vibe_core/
├── protocols/naga/
│   └── cli_command.py       # INagaCommand, NagaCommandRegistry
│
└── cli/naga_commands/
    ├── __init__.py          # Auto-discovery (Balarama)
    ├── wake/                # Phase 0: WAKE (0-3)
    │   └── status.py        # PRITHU - SYS_WAKE (Position 0)
    ├── purify/              # Phase 1: PURIFY (4-7)
    │   └── scan.py          # VYASA - ASSERT_TRUTH (Position 4)
    └── serve/               # Phase 2: SERVE (8-11)
        ├── chat.py          # PRAHLADA - EXEC_SERVICE
        └── intel.py         # SHUKA - FETCH_RES
```

### Test Coverage

```
tests/protocols/naga/test_cli_command.py         # 79 tests
tests/cli/naga_commands/test_wake_commands.py    # 26 tests
tests/cli/naga_commands/test_purify_commands.py  # 33 tests
tests/cli/naga_commands/test_serve_commands.py   # 34 tests
                                                 --------
                                                 172 tests
```

---

## NEXT STEPS

1. [x] Create `INagaCommand` protocol
2. [x] Create `NagaCommandRegistry` with Balarama pattern
3. [x] Map commands to MantraOpCode + Mahajana
4. [x] Implement chat (PRAHLADA) and intel (SHUKA) commands
5. [x] Add status (PRITHU) - HEAD of WAKE phase
6. [x] Add scan (VYASA) - HEAD of PURIFY phase
7. [ ] Add remaining WAKE phase commands (identity, resources, context)
8. [ ] Add remaining PURIFY phase commands (detect, gc, pulse)
9. [ ] Add remaining SERVE phase commands (validate, commit)
10. [ ] Add SUSTAIN phase commands (cache, optimize, yield, reset)
11. [ ] Migrate naga_cli.py to use NagaCommandRegistry
12. [ ] Delete the god file

---

*"Hare Krishna - Protocol First, Implementation Second."*
