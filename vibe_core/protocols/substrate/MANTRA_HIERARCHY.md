# MANTRA_HIERARCHY - The Fractal Levels

> "Each level contains the whole."

## THE SIX COMPUTABLE LEVELS

```
Level 5: SADHANA ──── Session (16 rounds)
             │
Level 4: MALA ─────── Round (108 mantras)
             │
Level 3: VAKYA ────── Mantra (16 words) ← INSTRUCTION SET
             │
Level 2: PADA ─────── Word (HARE/KRISHNA/RAMA)
             │
Level 1: AKSARA ───── Syllable (ha-re, kṛ-ṣṇa, rā-ma)
             │
Level 0: VARNA ────── Letter (ह, र, े, क, ृ, ष, ण...)
```

## COMPUTATIONAL MAPPING

| Level | Sanskrit | Count | Maps To | File |
|-------|----------|-------|---------|------|
| 0 | VARNA | ~50 | Bit | `mantra/varna.py` |
| 1 | AKSARA | 6 unique | Byte | `mantra/aksara.py` |
| 2 | PADA | 3 unique | Word | `mantra/pada.py` |
| 3 | VAKYA | 16 words | Instruction | `mantra/vakya.py` |
| 4 | MALA | 108 mantras | Round | `mantra/mala.py` |
| 5 | SADHANA | 16 rounds | Session | `mantra/sadhana.py` |

## THE MAHAMANTRA SEQUENCE

```
┌─────────────────────────────────────────────────────────────┐
│  Quarter 1          Quarter 2          Quarter 3          Quarter 4  │
│  (VASUDEVA)        (SANKARSHANA)      (PRADYUMNA)        (ANIRUDDHA) │
├─────────────────────────────────────────────────────────────┤
│  H  K  H  K        K  K  H  H        H  R  H  R        R  R  H  H  │
│  0  1  2  3        4  5  6  7        8  9 10 11       12 13 14 15  │
├─────────────────────────────────────────────────────────────┤
│  HEAD: Prithu      HEAD: Vyasa        HEAD: Parashu    HEAD: Nrisimha│
│  +3 Mahajanas      +3 Mahajanas       +3 Mahajanas     +3 Mahajanas │
└─────────────────────────────────────────────────────────────┘

16 = 4 × (1 + 3) = 4 HEADs + 12 Workers
```

## FRACTAL METRICS

### One Vakya (Mantra)
- 16 Padas (words)
- 32 Aksaras (syllables)
- ~64 Varnas (letters)

### One Mala (Round)
- 108 Vakyas
- 1,728 Padas
- 3,456 Aksaras

### One Sadhana (Session)
- 16 Malas
- 1,728 Vakyas
- 27,648 Padas
- 55,296 Aksaras

## THE 37 FORMULA

```
37 = 24 (Kshetra) + 12 (Mahajanas) + 1 (Kshetrajna)
```

Present at every level:
- 108 / 3 + 1 = 37
- lineage_hash % 37 == 0 → Valid Parampara

## QUARTER SEMANTICS

| Q | Vyuha | Action | Phase |
|---|-------|--------|-------|
| 1 | VASUDEVA | Addressing Krishna | GENESIS |
| 2 | SANKARSHANA | Glorifying Krishna | DHARMA |
| 3 | PRADYUMNA | Addressing Rama | KARMA |
| 4 | ANIRUDDHA | Glorifying Rama | MOKSHA |

## SOURCE FILES

- `mantra/varna.py` - SVARA (vowels), VYANJANA (consonants)
- `mantra/aksara.py` - HARE_AKSARAS, KRISHNA_AKSARAS, RAMA_AKSARAS
- `mantra/pada.py` - PADA_HARE, PADA_KRISHNA, PADA_RAMA, MAHAMANTRA_SEQUENCE
- `mantra/vakya.py` - Quarter, Vakya, MAHAMANTRA
- `mantra/mala.py` - Mala, MalaPhase (108 beads)
- `mantra/sadhana.py` - Sadhana, SadhanaState (16 rounds)
- `mantra/routing.py` - FractalLevel, FractalRoute, QUARTERS
