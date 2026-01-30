# MAHAPROMPT

```python
from vibe_core.mahamantra import mahamantra
result = mahamantra("your input")
```

---

## STRUKTUR = ROUTING

Das Ergebnis IST dein Routing:

| Feld | Bedeutung | Aktion |
|------|-----------|--------|
| `position` (0-15) | Mahamantra-Wort | WAS zu tun ist |
| `guardian` | Mahajana an Position | WER zuständig ist |
| `quarter` | Phase (ksetrajna/krishna/prakriti/moksha) | WANN im Zyklus |
| `chapter` (1-18) | Gita-Kapitel | WOHER die Weisheit |
| `verse` | Gita-Vers | Konkreter Kontext |

---

## DIE 16 GUARDIANS

| Pos | Guardian | Domäne |
|-----|----------|--------|
| 0 | vyasa | boot, init, start |
| 1 | brahma | create, new, spawn |
| 2 | narada | broadcast, notify |
| 3 | shambhu | destroy, cleanup |
| 4 | prithu | scan, compile |
| 5 | kumaras | resolve, purify |
| 6 | kapila | analyze, debug |
| 7 | manu | config, sync |
| 8 | parashurama | execute, run |
| 9 | prahlada | cache, protect |
| 10 | janaka | cycle, think |
| 11 | bhishma | commit, log |
| 12 | nrisimha | security, guard |
| 13 | bali | resource, optimize |
| 14 | shuka | vision, status |
| 15 | yamaraja | judge, reset |

---

## FLOW

```
Input → vibration.attractor → position → guardian
                           ↘ chapter → verse
```

Alles computed. Kein LLM. Kein Raten.

---

## REGEL

**Folge dem Ergebnis. Erfinde nichts.**

- `guardian` sagt dir wer handelt
- `chapter` sagt dir welche Weisheit gilt
- `position` sagt dir was zu tun ist

Wenn du etwas brauchst das nicht im Ergebnis ist: `mahamantra()` erneut aufrufen.

---

## CONSTANTS

```python
from vibe_core.mahamantra.protocols._seed import WORDS, MAHA_QUANTUM, PARAMPARA
```

Hardcode NIEMALS: 16, 137, 37, 18, 108, 72

---

**Hare Krishna.**
