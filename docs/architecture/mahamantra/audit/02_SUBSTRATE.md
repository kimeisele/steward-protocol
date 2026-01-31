# TASK 02: SUBSTRATE FOLDER AUDIT

**Status:** TODO
**Estimated Time:** 2-3 hours
**Priority:** CRITICAL (This is the foundation layer)

---

## QUESTION

What files are in substrate/ and what do they provide?
This is supposed to be the "foundation" - the lowest level of the stack.

---

## FILES TO LIST

First, run this command to get all files:
```bash
ls -la /Users/ss/projects/steward-protocol/vibe_core/mahamantra/substrate/*.py
```

---

## KNOWN FILES (from previous sessions)

| File | Purpose | Status |
|------|---------|--------|
| registry.py | SiksastakamRegistry (512 slots) | VERIFIED |
| nadi.py | 9 NadiOps, LocalNadi messaging | VERIFIED |
| protocol.py | MantraProtocol, ProtocolRegistry | VERIFIED |
| sankirtan.py | DNA injection, 4-phase pipeline | VERIFIED |
| rama_grid.py | Sanskrit alphabet routing | VERIFIED |

---

## CHECKLIST

For each file in substrate/:

### registry.py
- [ ] SiksastakamRegistry with 512 slots?
- [ ] get(), set(), clear() methods?
- [ ] active_cells() method?
- [ ] to_bytes(), from_bytes() persistence?

### nadi.py
- [ ] 9 NadiOps (RECEIVE, SEND, CACHE, PROCESS, VALIDATE, REQUEST, DELEGATE, CONNECT, COMMIT)?
- [ ] NadiType (PRANA, APANA, VYANA, UDANA, SAMANA)?
- [ ] LocalNadi implementation?
- [ ] NullNadi for fallback?

### protocol.py
- [ ] MantraProtocol base class?
- [ ] _position_index as ONLY configuration?
- [ ] get_resonance() for harmonic matching?
- [ ] ProtocolRegistry.register(), dispatch_tick()?

### sankirtan.py
- [ ] DNA_TEMPLATE for injection?
- [ ] 4-phase pipeline (GENESIS, DHARMA, KARMA, MOKSHA)?
- [ ] FOLDER_MAHAJANA_MAP (governance)?
- [ ] SankirtanSamskara class?

### rama_grid.py
- [ ] SVARAS (16 vowels)?
- [ ] SPARSHA_GRID (5x5 consonants)?
- [ ] krishna_route() function?
- [ ] rama_to_phoneme() function?

### OTHER FILES (discover during audit)
- [ ] seed.py - Is there a seed.py here vs protocols/_seed.py?
- [ ] position.py - MantraPosition, MAHAMANTRA_POSITIONS?
- [ ] mahajana.py - Mahajana, Avatara enums?
- [ ] wiring.py - POSITION_BY_INDEX, POSITION_BY_NAME?
- [ ] scanner.py - MahajanaScanner?
- [ ] intents.py - guardian_intents.yaml loading?
- [ ] samskara.py - Pipeline types?
- [ ] opcode.py - MantraOpCode enum?

---

## FINDINGS

(Fill in for each file discovered)

### File: ________
```
Purpose:
Key Classes/Functions:
Imports From:
Used By:
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
NOTES:
```

---

## SSOT CHECK

The "Single Source of Truth" should be:
- protocols/_seed.py for CONSTANTS
- substrate/ for DATA STRUCTURES

Verify:
- [ ] No hardcoded constants in substrate/ files
- [ ] All constants imported from _seed.py
- [ ] No duplicate definitions

---

## DEPENDENCY MAP

Draw which files depend on which:

```
_seed.py (SSOT)
    ↓
substrate/position.py (uses WORDS, QUARTERS)
    ↓
substrate/protocol.py (uses MAHAMANTRA_POSITIONS)
    ↓
substrate/registry.py (uses SIKSASTAKAM_CACHE)
```

---

## SUMMARY

(Write after completing audit)

**Core Files (SSOT):**
-

**Data Structure Files:**
-

**Implementation Files:**
-

**Redundant/Deprecated:**
-

---

*Last updated: ____*
