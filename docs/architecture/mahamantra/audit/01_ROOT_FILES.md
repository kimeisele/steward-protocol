# TASK 01: ROOT FILES AUDIT

**Status:** TODO
**Estimated Time:** 1-2 hours
**Priority:** CRITICAL (These are the core files)

---

## QUESTION

What are the root-level files in mahamantra/ and what do they do?
Are there redundancies between them?

---

## FILES TO READ

```
vibe_core/mahamantra/
├── __init__.py         # Main exports
├── __main__.py         # Entry point
├── _lotus.py           # ?
├── _mahamantra_lotus.py # ?
├── _types.py           # Type definitions
├── cell.py             # MahaCellUnified
├── chamber.py          # SankirtanChamber
├── chat.py             # Chat integration
├── commands.py         # CLI commands
├── orchestrator.py     # VenuOrchestrator
├── research_gateway.py # ?
```

---

## CHECKLIST

For each file, answer:

### __init__.py
- [ ] What does it export?
- [ ] Does it re-export from subfolders?
- [ ] Is there a `mahamantra` singleton here?

### __main__.py
- [ ] What happens when you run `python -m vibe_core.mahamantra`?
- [ ] Does it duplicate cli/entry.py?

### _lotus.py vs _mahamantra_lotus.py
- [ ] What is the difference between these two?
- [ ] Are they redundant?
- [ ] Which one is used?

### _types.py
- [ ] What types are defined here?
- [ ] Are they used elsewhere?
- [ ] Do they overlap with protocols/?

### cell.py
- [ ] MahaCellUnified structure?
- [ ] Header + Lifecycle pattern?
- [ ] How does it relate to chamber.py?

### chamber.py
- [ ] SankirtanChamber structure?
- [ ] Does it own the Orchestrator?
- [ ] dance(), kirtan(), sankirtan() methods?

### chat.py
- [ ] What is this for?
- [ ] Does it duplicate cli/chat functionality?
- [ ] Gateway integration?

### commands.py
- [ ] What commands are defined?
- [ ] How do they relate to cli/?
- [ ] Are there duplicate command definitions?

### orchestrator.py
- [ ] VenuOrchestrator with 19-bit DIW?
- [ ] THE_FLUTE_CYCLE LUT?
- [ ] route(), harmonize(), verify_divinity()?

### research_gateway.py
- [ ] What is this?
- [ ] Is it production or experimental?

---

## FINDINGS

(Fill in as you read each file)

### __init__.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### __main__.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### _lotus.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### _mahamantra_lotus.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### _types.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### cell.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### chamber.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### chat.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### commands.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### orchestrator.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

### research_gateway.py
```
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

---

## RELATIONSHIPS

Draw connections between files:

```
orchestrator.py
     ↓
chamber.py (owns orchestrator?)
     ↓
cell.py (transformed by chamber?)
```

---

## REDUNDANCY CHECK

| File A | File B | Overlap? | Action |
|--------|--------|----------|--------|
| _lotus.py | _mahamantra_lotus.py | ? | |
| chat.py | cli/? | ? | |
| commands.py | cli/? | ? | |

---

## SUMMARY

(Write after completing audit)

**Essential Files:**
-

**Redundant Files:**
-

**Unknown/Needs More Investigation:**
-

---

*Last updated: ____*
