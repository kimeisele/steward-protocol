# TASK 05: CLI FOLDER AUDIT

**Status:** TODO
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
| auto.py | cli_auto Protocol introspection | NEEDS VERIFICATION |

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
- [ ] cli_auto singleton?
- [ ] discover_all() method?
- [ ] execute(command, args) method?
- [ ] get_capabilities() method?
- [ ] Protocol introspection?

### OTHER FILES
- [ ] engine.py - ?
- [ ] steward.py - ?
- [ ] venu_router.py - Does this exist?
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

### File: ________
```
Purpose:
Key Classes:
Flow:
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
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
