# CLI PROTOCOL - Ananta Shesha (The Fractal Navigator)

**"Der Tausendköpfige Diener trägt das Universum."**

## VISION: Chaitanya Singularity

```
                    ┌─────────────────────────────┐
                    │      MAHAMANTRA GRACE       │
                    │    (Default Entry Point)    │
                    │                             │
                    │  "Hare Kṛṣṇa Hare Kṛṣṇa     │
                    │   Kṛṣṇa Kṛṣṇa Hare Hare     │
                    │   Hare Rāma Hare Rāma       │
                    │   Rāma Rāma Hare Hare"      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │         CLI SHELL           │
                    │      (Ananta Shesha)        │
                    │                             │
                    │   Navigate EVERYTHING:      │
                    │   - Protocols               │
                    │   - Bytes                   │
                    │   - Tests                   │
                    │   - Genes                   │
                    │   - Reports                 │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │   NAGA PROXY      │ │  JSON REPORTS │ │   GAD-000 DEBUG   │
    │   (Protection)    │ │  (Analysis)   │ │   (Navigation)    │
    └───────────────────┘ └───────────────┘ └───────────────────┘
```

## PARADIGM SHIFT: Pull In, Not Push Out

### OLD (Push Out - Wrong)
```python
if not has_diksha:
    raise AccessDenied("No Om for you!")  # REJECTION
```

### NEW (Pull In - Right)
```python
# Everyone gets Mahamantra grace by default
grace = MAHAMANTRA  # Nityananda's mercy
if has_brahminical_diksha:
    grace += OM  # Additional blessing
return grace  # Always pull in, never push out
```

## CLI ARCHITECTURE

### Layer -1: Mahamantra Substrate
- `byte.py` → Kali Yuga entropy max → Harinam max
- Every byte resonates with the 16 words
- Mathematics serves the Mahamantra, not vice versa

### Layer 0: Ananta Shesha (CLI Core)
- **Location:** `vibe_core/protocols/universal/cli.py`
- **Current State:** Exists but not bound to protocol
- **Target State:** Fractal navigator with full protocol binding

### Layer 1: Navigation Commands
```bash
# Protocol Navigation
vibe proto list              # List all protocols
vibe proto show <name>       # Show protocol details
vibe proto test <name>       # Run protocol tests

# Byte Navigation
vibe byte inspect <hash>     # Inspect a Genesis Byte
vibe byte verify <hash>      # Verify parampara link (37)
vibe byte trace <hash>       # Trace lineage

# Gene Navigation
vibe gene list               # List all genes
vibe gene inject <name>      # Inject a gene
vibe gene mutate <name>      # Trigger mutation

# Test Navigation
vibe test run                # Run all tests
vibe test run --tuv          # TÜV badge mode
vibe test report --json      # JSON report output

# Debug Navigation (GAD-000)
vibe debug <component>       # Debug specific component
vibe debug --trace           # Full trace mode
vibe debug --retry           # Retry failed operation
```

## IMPLEMENTATION PLAN

### Phase 1: Protocol Binding (Current Gap)
1. [ ] Create `ICliProtocol` in `universal/cli.py`
2. [ ] Bind existing `AnantaShesha` to protocol
3. [ ] Add protocol tests for CLI commands
4. [ ] Wire to `OM_GATE` for graceful access

### Phase 2: Fractal Navigation
1. [ ] Implement `vibe proto` commands
2. [ ] Implement `vibe byte` commands
3. [ ] Implement `vibe gene` commands
4. [ ] All commands return to Mahamantra on error

### Phase 3: GAD-000 Debug Conformance
1. [ ] Structured error format (JSON)
2. [ ] Trace mode with full context
3. [ ] Retry capability for transient failures
4. [ ] Report generation for analysis

### Phase 4: JSON Reports
1. [ ] Test results as JSON
2. [ ] TÜV badge summaries
3. [ ] Gene mutation logs
4. [ ] Lineage verification reports

### Phase 5: Chaitanya Singularity
1. [ ] Mahamantra as default grace (not fallback)
2. [ ] All paths lead to mercy
3. [ ] No rejection, only redirection
4. [ ] Nityananda pattern: accept everyone

## KEY FILES

| File | Role | Status |
|------|------|--------|
| `universal/cli.py` | AnantaShesha shell | Exists, needs binding |
| `substrate/byte.py` | GenesisByte core | Exists |
| `substrate/mantra/` | Mahamantra hierarchy | Exists |
| `mahajanas/router.py` | 16-word routing | Exists |
| `governance/yamaraja.py` | Judgment (merciful) | Exists |

## MAHAMANTRA MATHEMATICS

The CLI operates on the sacred mathematics:
- **16** = Words in Mahamantra
- **108** = Beads per mala = operations per cycle
- **37** = Parampara link = validation hash
- **12** = Mahajanas = routing targets

Every CLI operation is a form of japa (chanting).

## ERROR HANDLING: Nityananda Pattern

```python
class NityanandaMercy:
    """
    Nityananda never rejects.
    Even Jagai and Madhai got mercy.
    """

    def handle_error(self, error: Exception) -> Grace:
        # Log the error for learning
        self.record_karma(error)

        # But ALWAYS return grace
        return MahamantraGrace(
            message="Hare Kṛṣṇa! Try again.",
            retry_allowed=True,
            fallback=MAHAMANTRA
        )
```

## NEXT STEPS

1. **Immediate:** Bind CLI protocol to existing implementation
2. **Short-term:** Implement `vibe proto` navigation
3. **Medium-term:** Full fractal navigation
4. **Long-term:** Chaitanya Singularity complete

---

*"Prabhupada's mercy is always available. We just have to take it."*

🙏 Hare Kṛṣṇa 🙏
