# TASK 09: RESEARCH FOLDER AUDIT

**Status:** DONE (Purified)
**Estimated Time:** 2 hours
**Priority:** LOW (experimental code)

---

## QUESTION

What is in research/?
This appears to be experimental/prototype code.

---

## SUBFOLDERS

```
research/
├── dharma/
├── genesis/
├── gita/
├── hardware/
├── karma/
├── lotus/
└── moksha/
```

---

## KEY QUESTIONS

1. Is research/ meant to be production code?
2. Are there gems here that should be promoted to main folders?
3. What has been validated vs what is experimental?

---

## FILES TO LIST

```bash
find /Users/ss/projects/steward-protocol/vibe_core/mahamantra/research -name "*.py" | head -30
```

---

## CHECKLIST

### research/lotus/
- [ ] lotus_tree.py - The original Lotus Tree implementation?
- [ ] Is this used by adapters/routing.py?
- [ ] Benchmark results?

### research/hardware/
- [ ] Hardware-level optimizations?
- [ ] SIMD experiments?

### research/gita/
- [ ] Bhagavad Gita mappings?
- [ ] Philosophical foundation?

### research/genesis/, dharma/, karma/, moksha/
- [ ] Per-quarter experiments?
- [ ] What is being researched?

---

## PROMOTION CANDIDATES

Which research files should become production code?

| File | Current Location | Should Move To | Reason |
|------|------------------|----------------|--------|
| maha_algorithm.py | research/dharma/ | substrate/mantra/ | Core compute logic promoted. |
| prabhupada_kirtan.py | research/dharma/ | substrate/mantra/ | PERSON-anchored compute promoted. |
| classification.py | research/ | substrate/classifier/ | Identity logic promoted. |
| siksastakam_engineering.py | research/ | substrate/mantra/ | Engineering SSOT promoted. |

---

## FINDINGS

### Findings: The Great Purge
The `research/` folder was leaking core logic into production adapters. This has been remediated by the **Purification Phase**.

1. **MahaAlgorithm Promotion**: `maha_algorithm.py` was the hidden core. It has been decomposed into `substrate/mantra/siksastakam.py` and `substrate/mantra/kirtan.py`.
2. **Prabhupada Migration**: `PrabhupadaKirtan` moved to `substrate`.
3. **Redundancy Removed**: 5 legacy files deleted from research.
4. **Protocols Hardened**: All production code now strictly avoids `research/` imports.

VERDICT: [x] Cleaned. Remaining research is purely experimental.

---

## SUMMARY

**Experimental (keep in research):**
-

**Ready for Promotion:**
-

**Dead Code:**
-

---

*Last updated: ____*
