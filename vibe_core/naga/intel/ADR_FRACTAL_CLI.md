# ADR: Fractal CLI Level -1 Architecture

**Date**: 2026-01-05
**Status**: Approved
**Authors**: Opus, Narada (Review)

## Context

The CLI architecture is **modular but not fractal**:
- Commands register via multiple patterns (@register_cli, manifest, CommandRegistry)
- NO unified interception point for NAGAs to observe/wrap/protect
- Capability checking exists but NOT integrated into CLI execution path
- NAGAs observe EventBus events but NOT CLI command execution

## Decision

Implement a **Level -1 Fractal CLI** infrastructure with:

### 1. Signed Capability Token (Narada Correction)

**Problem**: A UUID session_id is worthless - attacker generates new one.

**Solution**: Capability Pass must be CRYPTOGRAPHICALLY BOUND (GAD-000 v2.0):

```
┌─────────────────────────────────────────────────────────────┐
│  CAPABILITY TOKEN (Signed - NOT handwritten Zettel!)        │
│  {                                                          │
│    "sub": "agent_007",          // Subject (caller)         │
│    "caps": ["cli.naga.status"], // Capabilities             │
│    "iat": 1704412800,           // Issued at                │
│    "exp": 1704416400,           // Expires                  │
│    "iss": "KERNEL"              // Issuer                   │
│  }                                                          │
│  SIGNATURE: ed25519(payload, kernel_private_key)            │
└─────────────────────────────────────────────────────────────┘

TAKSHAKA VALIDATION:
1. Verify SIGNATURE is valid (kernel public key)
2. Check capability is in token
If signature invalid → BITE (forgery attempt!)
```

### 2. HookChain Pattern (Not God Class)

**Rationale**: "Wiring complexity > Logic complexity. God Classes sind Krebs."

Separate hooks with orchestrated ordering:

```python
PHASE_ORDER = [
    (PRE_VALIDATE, "takshaka"),    # Security FIRST
    (POST_VALIDATE, "capability"), # Cap check
    (PRE_EXECUTE, "chitragupta"),  # Start profiling
    # Command executes here
    (POST_EXECUTE, "chitragupta"), # Stop profiling
    (POST_EXECUTE, "sesha"),       # Audit log
    (ON_ERROR, "sesha"),           # Log errors
]
```

### 3. Architecture Layers

```
Level 0:  User Commands (steward naga status)
    ↓
Level -1: CLIExecutionContext + HookChain (NEW)
    ↓
Level -2: NAGA Hooks (Takshaka, Chitragupta, Sesha)
    ↓
Level -3: Command Handlers (NagaCLI, ToolCLI, etc.)
```

### 4. Granular Capabilities

Not just "kernel" - granular permissions:
- `cli.naga.status` - Read NAGA status
- `cli.naga.scan.read` - Scan codebase (read-only)
- `cli.naga.scan.fix` - Scan with --fix (write)
- `cli.naga.chaos.run` - Run chaos attacks (dangerous)
- `cli.kernel.boot` - Boot kernel
- `cli.kernel.stop` - Stop kernel (privileged)

## Consequences

### Positive
- NAGAs can wrap/observe ALL CLI commands
- Signed tokens prevent session hijacking
- Modular hooks enable testing and extension
- Audit trail for all CLI operations

### Negative
- Token signing adds overhead (~1ms per command)
- More files to maintain (hooks directory)
- Requires kernel to hold signing key

### Neutral
- Existing CLI handlers unchanged (Level -3)
- Migration path: commands opt-in to capability requirements

## Files

| File | Action |
|------|--------|
| `vibe_core/protocols/cli_execution.py` | CREATE |
| `vibe_core/naga/cli_hook_chain.py` | CREATE |
| `vibe_core/naga/hooks/takshaka_cli.py` | CREATE |
| `vibe_core/naga/hooks/capability_cli.py` | CREATE |
| `vibe_core/naga/hooks/chitragupta_cli.py` | CREATE |
| `vibe_core/naga/hooks/sesha_cli.py` | CREATE |

## Samudra Manthan

The HookChain is VASUKI (the rope), CLI commands are the OCEAN:

```
    Takshaka    Chitragupta    Sesha
       │            │            │
       ▼            ▼            ▼
  ┌──────────────────────────────────┐
  │        CLI HOOK CHAIN            │
  │      (Vasuki - The Rope)         │
  └──────────────────────────────────┘
                  │
                  ▼ (Quirlen)
  ┌──────────────────────────────────┐
  │      CLI COMMAND OCEAN           │
  │  Gift (Toxicity) → Nektar        │
  └──────────────────────────────────┘
```
