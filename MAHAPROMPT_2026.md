# MAHAPROMPT 2026: MAHAMANTRA-INITIALISIERUNG
## Mantra-Based Computation. One Algorithm. Everything Derived.

Du wirst in ein System geworfen, das KEIN normales Projekt ist.
Dies ist ein Betriebssystem basierend auf dem Mahamantra.
ALLES wird vom Mantra abgeleitet. NICHTS ist hardcoded.

Die Zahlen sind nicht willkürlich – sie SIND das Mantra.
Die Architektur ist nicht Metapher – sie IST Computation.

---

## TEIL I: DAS MANTRA (DIE EINZIGE QUELLE)

Bevor du IRGENDETWAS änderst, verstehe:

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama Hare Rama Rama Rama Hare Hare
```

**Zähle es. Das ist die Architektur.**

| Was du zählst | Was du bekommst | Wo es lebt |
|---------------|-----------------|------------|
| Wörter | WORDS | `_axioms.py` |
| Unique Namen | TRINITY | `_axioms.py` |
| "Hare" | HARE_COUNT | `_axioms.py` |
| "Krishna" | KRISHNA_COUNT | `_axioms.py` |
| "Rama" | RAMA_COUNT | `_axioms.py` |
| Unique Paare | PANCHA | `_axioms.py` |
| Hälften | HALVES | `_axioms.py` |

**Diese 7 Werte sind die EINZIGEN hardcoded Zahlen im System.**
Alles andere wird BERECHNET.

---

## TEIL II: ORIENTIERUNG (IMMER ZUERST)

**Lies diese Dateien. In dieser Reihenfolge. Keine Ausnahmen.**

```bash
# 1. Die 7 Axiome (die einzigen hardcoded Werte)
cat vibe_core/mahamantra/protocols/seed/_axioms.py

# 2. Primäre Ableitungen (direkt vom Mantra)
cat vibe_core/mahamantra/protocols/seed/_primary.py

# 3. Sekundäre Ableitungen (von primären)
cat vibe_core/mahamantra/protocols/seed/_secondary.py

# 4. Der Beweis (Code der die Ableitungen ZEIGT)
cat vibe_core/mahamantra/substrate/seed.py

# 5. Teste dass es funktioniert
python3 -c "from vibe_core.mahamantra import mahamantra; print(mahamantra('test'))"
```

**Rekonstruiere die Mathematik:**
- Wie wird QUARTERS aus KRISHNA_COUNT?
- Wie wird PARAMPARA aus KSHETRA + MAHAJANA_COUNT + KSETRAJNA?
- Wie wird MALA aus MAHAJANA_COUNT × NAVA?

Wenn du die Ableitungen nicht nachvollziehen kannst: **STOP. NOCHMAL LESEN.**

---

## TEIL III: DAS GESETZ (SSOT)

**Single Source of Truth. Keine Ausnahmen.**

```
TIER 0 - AXIOME (gezählt vom Mantra):
└── protocols/seed/_axioms.py → 7 Werte, NICHTS ANDERES

TIER 1 - PRIMÄR (direkt abgeleitet):
└── protocols/seed/_primary.py → QUARTERS, KSHETRA, NAVA, ...

TIER 2 - SEKUNDÄR (von primären abgeleitet):
└── protocols/seed/_secondary.py → PARAMPARA, MALA, GITA_CHAPTERS, ...

TIER 3+ - COSMIC/EXTENDED:
└── protocols/seed/_cosmic.py, _extended.py → MAHA_QUANTUM, Timing, ...
```

**Bei jeder Zahl frage:**
- Ist sie in `_axioms.py`? → OK, sie wurde gezählt.
- Ist sie abgeleitet? → Zeig mir die Formel.
- Ist sie hardcoded? → **ARCHITEKTUR-VERLETZUNG. FIXEN.**

---

## TEIL IV: VERBOTEN (TODSÜNDEN)

| Pattern | Warum verboten | Was stattdessen |
|---------|----------------|-----------------|
| `x = 16` | Hardcoded | `from ..._seed import WORDS` |
| `hash(x)` | Nicht deterministisch | `hashlib.sha256()` |
| `except: pass` | Silent failure | `except Exception as e: logger.exception(e)` |
| `assert x` für Security | Entfernt mit `-O` | `if not x: raise` |
| `Any` type | Type pollution | Konkrete Types oder Protocol |
| Zahl ohne Ableitung | SSOT Verletzung | Formel zeigen oder fixen |

**Wenn du eines dieser Patterns siehst: FIXEN. Nicht ignorieren.**

---

## TEIL V: DER ENTRY POINT

```python
from vibe_core.mahamantra import mahamantra

result = mahamantra("dein intent")
```

Das System routet. Nicht du.
Das System berechnet Position, Guardian, Chapter. Nicht du.
Du gibst Intent. Das Mantra macht den Rest.

---

## TEIL VI: ENTSCHEIDUNGSRAHMEN

Bei jeder Änderung:

1. **Ist eine Zahl hardcoded?** → Ableitung finden oder erstellen.
2. **Benutzt es `hash()`?** → `hashlib.sha256()` verwenden.
3. **Schluckt es Exceptions?** → Logging hinzufügen.
4. **Benutzt es `assert` für Security?** → `if not: raise` verwenden.
5. **Kann ich die Ableitung nicht finden?** → `_axioms.py` → `_primary.py` → `_secondary.py` lesen.

---

## TEIL VII: AKTIVIERUNG

**Deine erste Aktion** nach dem Lesen:

```bash
# Verifiziere dass du das System verstehst
python3 -c "
from vibe_core.mahamantra.protocols._seed import WORDS, PARAMPARA, MALA
print(f'WORDS={WORDS}')      # Muss vom Mantra kommen
print(f'PARAMPARA={PARAMPARA}')  # Muss abgeleitet sein
print(f'MALA={MALA}')        # Muss abgeleitet sein
"
```

**Danach:**
- Direkt zur Sache
- Code fixen, nicht beschreiben
- Keine Erlaubnis fragen für SSOT-Fixes
- Bei echten Entscheidungen: Optionen + Trade-offs + Empfehlung

---

## DEIN AUFTRAG

Das Mahamantra ist der Algorithmus.
Alles wird davon abgeleitet.
Deine Aufgabe: Sicherstellen dass das auch im Code so ist.

**Lies jetzt `_axioms.py`. Zähle das Mantra. Verstehe.**
