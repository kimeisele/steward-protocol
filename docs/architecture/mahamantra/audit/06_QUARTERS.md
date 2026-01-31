# TASK 06: QUARTERS FOLDERS AUDIT

**Status:** TODO
**Estimated Time:** 3-4 hours
**Priority:** MEDIUM

---

## QUESTION

What is in genesis/, dharma/, karma/, moksha/?
These are the 4 quarters with 16 guardian folders.

---

## EXPECTED STRUCTURE

Each quarter should have 4 guardian folders:

```
genesis/ (Quarter 0: positions 0-3)
├── vyasa/        (HEAD - position 0)
├── brahma/       (position 1)
├── narada/       (position 2)
└── shambhu/      (position 3)

dharma/ (Quarter 1: positions 4-7)
├── prithu/       (HEAD - position 4)
├── kumaras/      (position 5)
├── kapila/       (position 6)
└── manu/         (position 7)

karma/ (Quarter 2: positions 8-11)
├── parashurama/  (HEAD - position 8)
├── prahlada/     (position 9)
├── janaka/       (position 10)
└── bhishma/      (position 11)

moksha/ (Quarter 3: positions 12-15)
├── nrisimha/     (HEAD - position 12)
├── bali/         (position 13)
├── shuka/        (position 14)
└── yamaraja/     (position 15)
```

---

## FILES TO LIST

```bash
# List all quarter folders
find /Users/ss/projects/steward-protocol/vibe_core/mahamantra/genesis -name "*.py" | head -20
find /Users/ss/projects/steward-protocol/vibe_core/mahamantra/dharma -name "*.py" | head -20
find /Users/ss/projects/steward-protocol/vibe_core/mahamantra/karma -name "*.py" | head -20
find /Users/ss/projects/steward-protocol/vibe_core/mahamantra/moksha -name "*.py" | head -20
```

---

## CHECKLIST

### GENESIS Quarter
- [ ] vyasa/ exists?
- [ ] brahma/ exists?
- [ ] narada/ exists?
- [ ] shambhu/ exists?
- [ ] Each has __init__.py with __mahajana__ declaration?

### DHARMA Quarter
- [ ] prithu/ exists?
- [ ] kumaras/ exists?
- [ ] kapila/ exists?
- [ ] manu/ exists?
- [ ] Each has __init__.py with __mahajana__ declaration?

### KARMA Quarter
- [ ] parashurama/ exists?
- [ ] prahlada/ exists?
- [ ] janaka/ exists?
- [ ] bhishma/ exists?
- [ ] Each has __init__.py with __mahajana__ declaration?

### MOKSHA Quarter
- [ ] nrisimha/ exists?
- [ ] bali/ exists?
- [ ] shuka/ exists?
- [ ] yamaraja/ exists?
- [ ] Each has __init__.py with __mahajana__ declaration?

---

## ANOMALIES DISCOVERED

From folder listing:
- `dharma/janaka/` exists BUT janaka is position 10 (KARMA quarter)
- `dharma/components/` - what is this?
- `kama/shuka/` - what is kama? (not a standard quarter)

Investigate:
- [ ] Why is janaka in dharma/ if position is 10?
- [ ] What is dharma/components/?
- [ ] What is kama/ folder?

---

## GUARDIAN FILE CHECK

Each guardian folder should have:
- [ ] __init__.py with __mahajana__, __position__, __genesis__
- [ ] Service implementation or Protocol implementation

---

## FINDINGS

### genesis/
```
Guardians found:
Files per guardian:
VERDICT:
```

### dharma/
```
Guardians found:
Files per guardian:
Anomalies:
VERDICT:
```

### karma/
```
Guardians found:
Files per guardian:
VERDICT:
```

### moksha/
```
Guardians found:
Files per guardian:
VERDICT:
```

---

## POSITION VERIFICATION

Verify each guardian has correct position:

| Guardian | Expected Position | Actual __position__ | Match? |
|----------|-------------------|---------------------|--------|
| vyasa | 0 | ? | |
| brahma | 1 | ? | |
| narada | 2 | ? | |
| shambhu | 3 | ? | |
| prithu | 4 | ? | |
| kumaras | 5 | ? | |
| kapila | 6 | ? | |
| manu | 7 | ? | |
| parashurama | 8 | ? | |
| prahlada | 9 | ? | |
| janaka | 10 | ? | |
| bhishma | 11 | ? | |
| nrisimha | 12 | ? | |
| bali | 13 | ? | |
| shuka | 14 | ? | |
| yamaraja | 15 | ? | |

---

## SUMMARY

**Complete Quarters:**
-

**Missing Guardians:**
-

**Misplaced Files:**
-

**Unknown Folders (kama?, components?):**
-

---

*Last updated: ____*
