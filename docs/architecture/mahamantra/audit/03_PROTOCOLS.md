# TASK 03: PROTOCOLS FOLDER AUDIT

**Status:** PARTIAL (Purified)
**Estimated Time:** 2-3 hours
**Priority:** CRITICAL (This defines the interfaces)

> [!NOTE]
> This audit is currently focused on the CORE protocols and purification of research leakage.
> A full structural audit of all 54 auxiliary files is pending.
---

## QUESTION

What protocols are defined in protocols/?
These are the INTERFACES (WAS), not implementations (WIE).

---

## FILES TO LIST

```bash
ls -la /Users/ss/projects/steward-protocol/vibe_core/mahamantra/protocols/*.py
ls -la /Users/ss/projects/steward-protocol/vibe_core/mahamantra/protocols/sankalpa/*.py
```

---

## KNOWN FILES

| File | Purpose | Status |
|------|---------|--------|
| _seed.py | SSOT - All constants | CRITICAL |
| _sankirtan.py | SankirtanProtocol interface | VERIFIED |
| sankalpa/ | Intent system (SankalpaIntent, check_conscience) | VERIFIED |
| _maha_compute.py | MahaComputeProtocol (Purified) | VERIFIED |

---

## CHECKLIST

### _seed.py (THE SSOT)
- [ ] WORDS = 16?
- [ ] MALA = 108?
- [ ] PARAMPARA = 37?
- [ ] FLUTE_HOLES_SUM = 19 (6+9+4)?
- [ ] VENU_HOLES = 6, VAMSI_HOLES = 9, MURALI_HOLES = 4?
- [ ] MAHAMANTRA_WORD_PATTERN tuple?
- [ ] NavaBhakti enum?
- [ ] All derived constants from axioms?

### _sankirtan.py
- [ ] GenesisByte TypedDict?
- [ ] InjectionRequest TypedDict?
- [ ] WiringStats TypedDict?
- [ ] SankirtanProtocol interface?

### sankalpa/__init__.py
- [ ] SankalpaIntent export?
- [ ] INTENT_PERMISSION_MAP?
- [ ] ASHRAMA_PERMISSIONS?
- [ ] check_conscience() function?

### sankalpa/types.py
- [ ] Ashrama enum?
- [ ] GunaState enum?
- [ ] ConscienceVerdict dataclass?
- [ ] SankalpaMission, SankalpaStrategy?

### sankalpa/will.py
- [ ] SankalpaOrchestrator class?
- [ ] check_conscience() implementation?

### _maha_compute.py (Purified)
- [x] MahaComputeProtocol interface?
- [x] MahaComputeResult dataclass?
- [x] NO research imports? ✓
- [x] Uses substrate components for implementation? ✓

### OTHER _*.py FILES (discover during audit)
- [ ] _core.py - Core protocol definitions?
- [x] _pancha.py - PanchaTattvaProtocol?
- [ ] _lila.py - LilaBoundary, LilaPhase?
- [x] _gad.py - GAD compliance?
- [ ] _blueprint.py - StandardBlueprint?
- [ ] routing.py - PhoneticRoutingProtocol?
- [x] _seed.py - SSOT verified? ✓

---

## FINDINGS

(Fill in for each file)

### File: ________
```
Purpose:
Defines:
VERDICT: [ ] Essential [ ] Redundant [ ] Unknown
```

---

## INTERFACE vs IMPLEMENTATION CHECK

For each protocol, verify:

| Protocol | Interface File | Implementation File | Match? |
|----------|----------------|---------------------|--------|
| SankirtanProtocol | protocols/_sankirtan.py | substrate/sankirtan.py | YES |
| MahaComputeProtocol | protocols/_maha_compute.py | substrate/mantra/kirtan.py | YES |
| SankalpaProtocol | sankalpa/types.py | sankalpa/will.py | YES |

---

## CONSTANT VERIFICATION

All these MUST come from _seed.py:
- [ ] WORDS = 16
- [ ] MALA = 108
- [ ] PARAMPARA = 37
- [ ] QUARTERS = 4
- [ ] NAVA = 9

Search for hardcoded values:
```bash
grep -r "= 16" protocols/ | grep -v _seed.py
grep -r "= 108" protocols/ | grep -v _seed.py
grep -r "= 37" protocols/ | grep -v _seed.py
```

---

## SUMMARY

**SSOT Files (DO NOT TOUCH):**
-

**Interface Files:**
-

**Sankalpa System:**
-

**Redundant:**
-

---

*Last updated: ____*
