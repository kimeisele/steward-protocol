# TASK 11: CROSS-FOLDER REDUNDANCY AUDIT

**Status:** TODO
**Estimated Time:** 3-4 hours
**Priority:** HIGH

---

## QUESTION

What files are duplicated or redundant across folders?
This is the "find the dead code" task.

---

## METHOD

For each suspected redundancy:
1. Read both files
2. Compare purpose
3. Check imports (who uses what)
4. Decide: MERGE, DELETE ONE, or KEEP BOTH

---

## SUSPECTED REDUNDANCIES

### 1. Routing Systems
| File | Purpose | Verdict |
|------|---------|---------|
| adapters/routing.py | HolographicRouter (CLI dispatch) | |
| adapters/rama_router.py | RamaPhoneticRouter (phoneme) | |
| substrate/rama_grid.py | RAMA Grid data | |

**Question:** Are routing.py and rama_router.py doing the same thing?

### 2. Sankirtan Systems
| File | Purpose | Verdict |
|------|---------|---------|
| protocols/_sankirtan.py | Interface (~100 LOC) | |
| substrate/sankirtan.py | Implementation (~1400 LOC) | |

**Question:** Is this proper Interface/Implementation separation or redundancy?

### 3. Venu/Orchestrator
| File | Purpose | Verdict |
|------|---------|---------|
| orchestrator.py (root) | VenuOrchestrator | |
| venu/ folder | ? | |

**Question:** What is in venu/ folder vs root orchestrator.py?

### 4. CLI Entry Points
| File | Purpose | Verdict |
|------|---------|---------|
| cli/entry.py | MahamantraCLIEntry | |
| cli/bridge.py | MahamantraCLIBridge | |
| commands.py (root) | ? | |
| chat.py (root) | ? | |

**Question:** How many CLI entry points do we need?

### 5. Lila Systems
| File | Purpose | Verdict |
|------|---------|---------|
| protocols/_lila.py | LilaBoundary protocol | |
| lila/ folder | ? | |

**Question:** Is lila/ folder needed if protocols/_lila.py exists?

### 6. Quarter Janaka
| File | Purpose | Verdict |
|------|---------|---------|
| dharma/janaka/ | ? | |
| karma/janaka/ | ? | |

**Question:** Why is janaka in 2 places? (Position 10 = KARMA)

### 7. Lotus Files
| File | Purpose | Verdict |
|------|---------|---------|
| _lotus.py (root) | ? | |
| _mahamantra_lotus.py (root) | ? | |
| research/lotus/ | ? | |

**Question:** Are these 3 different things or redundant?

---

## INVESTIGATION TEMPLATE

For each suspected redundancy:

```
FILES: file_a.py vs file_b.py

FILE A:
  Location:
  LOC:
  Purpose:
  Key Classes:
  Imported By:

FILE B:
  Location:
  LOC:
  Purpose:
  Key Classes:
  Imported By:

COMPARISON:
  Same Purpose: [ ] Yes [ ] No
  If No, Difference:

VERDICT:
  [ ] KEEP BOTH (different purposes)
  [ ] MERGE (combine into one)
  [ ] DELETE FILE A
  [ ] DELETE FILE B

ACTION:
```

---

## GREP COMMANDS

Find who imports what:
```bash
# Who uses routing.py?
grep -r "from.*routing import" vibe_core/mahamantra/

# Who uses rama_router.py?
grep -r "from.*rama_router import" vibe_core/mahamantra/

# Who uses _lila.py?
grep -r "from.*_lila import" vibe_core/mahamantra/
```

---

## FINDINGS

(Fill in during audit)

---

## CLEANUP ACTIONS

After audit, list files to:

**DELETE:**
-

**MERGE:**
-

**RENAME:**
-

**KEEP (confirmed essential):**
-

---

*Last updated: ____*
