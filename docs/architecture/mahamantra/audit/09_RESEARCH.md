# TASK 09: RESEARCH FOLDER AUDIT

**Status:** TODO
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
| lotus_tree.py | research/lotus/ | adapters/? | If it's the engine for HolographicRouter |
| | | | |

---

## FINDINGS

(Fill in during audit)

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
