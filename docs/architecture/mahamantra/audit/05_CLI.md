# TASK 05: CLI FOLDER AUDIT

**Status:** DONE (Unified)
**Estimated Time:** 2 hours
**Priority:** HIGH (This is what users interact with)

---

## QUESTION

What is the CLI architecture?
How does a command flow from user input to execution?

---

## FILES TO LIST

```bash
ls -la /Users/ss/projects/steward-protocol/vibe_core/mahamantra/cli/*.py
```

---

## KNOWN FILES

| File | Purpose | Status |
|------|---------|--------|
| protocol.py | CLIResult, CLIError, CLICapability types | VERIFIED |
| entry_protocol.py | CLIEntryProtocol interface | VERIFIED |
| entry.py | MahamantraCLIEntry implementation | VERIFIED |
| bridge.py | DOMAIN_KEYWORDS (HARDCODED - TO BE REPLACED) | VERIFIED |
| auto.py | cli_auto Protocol introspection | VERIFIED |
| steward.py | Universal Resonance Router | VERIFIED |
| kirtan_cli.py | Live Maha Computing Interface | VERIFIED |

---

## CHECKLIST

### protocol.py
- [ ] CLIErrorCode enum (error codes)?
- [ ] CLIOutput, CLIOutputItem dataclasses?
- [ ] CLIError dataclass?
- [ ] CLIResult dataclass?
- [ ] CLICapability dataclass?
- [ ] CLIState, CLIHealth dataclasses?
- [ ] CLIContext dataclass?
- [ ] CLIExecutable Protocol?
- [ ] CLIExecutableBase base class?

### entry_protocol.py
- [ ] CLIEntryProtocol interface?
- [ ] run(), discover(), get_state(), check_health() methods?
- [ ] CLIEntryResult dataclass?

### entry.py
- [ ] MahamantraCLIEntry class?
- [ ] Implements CLIEntryProtocol?
- [ ] Routes via cli_auto.execute()?
- [ ] Singleton pattern (get_entry())?

### bridge.py
- [ ] DOMAIN_KEYWORDS dict (lines 44-78)?
- [ ] MahamantraCLIBridge class?
- [ ] get_position() method?
- [ ] route() method?
- [ ] LEGACY_SYSTEM_COMMANDS set?

### auto.py
- [x] cli_auto singleton? Yes.
- [x] discover_all() method? Yes.
- [x] execute(command, args) method? Yes.
- [x] Protocol introspection? Yes.
- [x] Purified: Imports from substrate.mantra instead of research! ✓

### steward.py (The Universal Router)
- [x] Steward class? Yes.
- [x] prabhupada_kirtan property (Lazy load)? Yes.
- [x] Routes via MahaCompute protocol? Yes.
- [x] PERSON-anchored computation? ✓

### kirtan_cli.py
- [x] Live operator interface? Yes.
- [x] Uses PersonAnchoredOperator? ✓
- [x] All constants derived from seed.py? ✓

### OTHER FILES
- [ ] engine.py - ?
- [ ] venu_router.py - ?
- [ ] loader.py - ?

---

## FLOW DIAGRAM

Trace the path of a command:

```
User: steward analyze --deep
         ↓
entry.py: MahamantraCLIEntry.run(["analyze", "--deep"])
         ↓
???
         ↓
Result
```

Fill in the ??? during audit.

---

## REDUNDANCY CHECK

| File A | File B | Same Purpose? |
|--------|--------|---------------|
| entry.py | bridge.py | ? |
| protocol.py | entry_protocol.py | NO (types vs interface) |
| auto.py | bridge.py | ? |

---

## DOMAIN_KEYWORDS PROBLEM

The hardcoded DOMAIN_KEYWORDS in bridge.py:44-78 should be replaced with:
```python
from vibe_core.mahamantra.cli.venu_dispatch import venu_dispatch, get_position_venu
```

Verify:
- [ ] venu_dispatch.py exists?
- [ ] If not, needs to be created (see VENU_CLI_UNIFICATION.md plan)

---

## FINDINGS

(Fill in for each file)

### File: steward.py
```
Purpose: The universal gateway and persona-anchored router.
Key Classes: Steward
Flow: Command -> PERSON check -> Siksastakam Pipeline -> Result
VERDICT: [x] Essential (CORE)
```

### File: auto.py
```
Purpose: Automated command discovery and protocol-based implementation fetching.
Key Classes: CLIAuto (cli_auto)
Flow: Command -> Protocol Discovery -> Substrate Execution
VERDICT: [x] Essential (Vajra Infrastructure)
```

---

## SUMMARY

**Essential CLI Files:**
-

**Deprecated/To Remove:**
-

**Missing Files:**
-

---

*Last updated: ____*
