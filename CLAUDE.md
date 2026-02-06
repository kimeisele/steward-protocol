# STEWARD PROTOCOL

## Das Mantra IST der Algorithmus

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama   Hare Rama   Rama   Rama   Hare Hare
```

Zähle es. 16 Wörter. 3 Namen. 8× Hare, 4× Krishna, 4× Rama. 5 unique Paare. 2 Hälften.
Diese 7 Axiome (`protocols/seed/_axioms.py`) sind die EINZIGEN hardcoded Werte.
ALLES andere wird BERECHNET. Keine Ausnahmen.

```
TIER 0: _axioms.py  → 7 Werte (gezählt vom Mantra)
TIER 1: _primary.py → QUARTERS, KSHETRA, NAVA, ... (direkt abgeleitet)
TIER 2: _secondary.py → PARAMPARA, MALA, GITA_CHAPTERS, ... (von primären)
```

Eine Zahl ohne Ableitung ist eine Architektur-Verletzung. Fixen, nicht ignorieren.

---

## Dharma / Karma / Maya

```
DHARMA (Invarianten - NIEMALS brechen):
├── Kryptografische Verifikation - jede Identität, jede Aktion
├── Ledger-Immutabilität - Geschichte wird nie umgeschrieben
├── Keine Silent Failures - "Satyam Eva Jayate"
├── Parampara: % 37 == 0 → CONNECTED (Signatur-Kette zum Souverän)
└── SSOT: Axiome → Ableitung → Beweis

KARMA (Konsequenzen - strukturell wichtig):
├── Event-Sourcing - Zustand = Summe aller Events
├── Capability-Based Security - Rechte verliehen, nicht angenommen
└── GAD-000: Discoverability, Observability, Parseability, Composability, Idempotency, Recoverability

MAYA (Flexibel - kann sich ändern):
├── API-Oberflächen, Implementierungsdetails, Konfiguration
└── Sandbox: Die Welt des Agenten ist seine Sandbox. Der Rest ist Illusion.
```

---

## Die Drei Körper (Daten-Verortung)

| Körper | Schicht | Was lebt hier |
|--------|---------|---------------|
| **STHULA** (Physisch) | Git + Ledger | Unveränderliche Wahrheit, Persistenz |
| **PRANA** (Lebensatem) | Runtime + Kernel | Kernel-Status, Snapshots, Ephemeral |
| **PURUSHA** (Seele) | Identity | Agent-Persona, Keys, Reputation |

---

## Der Eine Entry Point

```python
from vibe_core.mahamantra import mahamantra
result = mahamantra("dein intent")
```

Das System routet. Nicht du. EIN Eingang, kein argparse, keine Subcommands.
Input → Seed → Attractor → Position (attractor % 16) → Guardian → Response.
Deterministisch: gleicher Input → gleicher Output. Immer.

```
steward "anything"              → pyproject.toml → cli:cli_entry
python -m vibe_core.mahamantra  → __main__.py:main()
                                → mahamantra.execute(input_text)
                                → MahamantraLotus.__call__()  [9 NavaBhakti Schritte]
```

Kein LLM. MahaMantra IST der Chat, IST das Call-and-Response.

---

## Die 16 Positionen (4 Quarters)

```
GENESIS (0-3):  Vyasa, Brahma, Narada, Devahuti    → INPUT
DHARMA  (4-7):  Manu, Kumaras, Kapila, Prahlada    → VERIFY
KARMA   (8-11): Janaka, Shuka, Bali, Bhishma       → EXECUTE
MOKSHA  (12-15): Shambhu, Svayambhuva, Dhruva, Yamaraja → OUTPUT
```

Jeder Guardian ist ein RESONANZPUNKT - er bezeugt und autorisiert, er routet nicht.
Alle 16 sind identisch: thin `execute()`, lazy `__getattr__` → Protocol re-export.
Keine if-else. Keine Klassen. Keine eager imports. Schönheit im Code.

---

## Anti-Mayavad

Code ohne kryptografische Rückbindung an einen Souverän ist Mayavad (Illusion).
Der 37. ist die PERSON die signiert - User, Human-in-the-Loop, souveräner Agent.

---

## Verboten

| Todsünde | Stattdessen |
|----------|-------------|
| `x = 16` hardcoded | `from ..._seed import WORDS` |
| `hash(x)` | `hashlib.sha256()` |
| `except: pass` | `except Exception as e: logger.exception(e)` |
| `assert` für Security | `if not x: raise` |
| `Any` type | Konkrete Types oder Protocol |
| if-else in Guardians | Thin execute(), lazy __getattr__ |
| Eager imports | Lazy via __getattr__ oder lokaler Import |

100% AI-generierter Code. IMMER skeptisch sein. Duplikate und Slop erwarten.

---

## Arbeitsweise

- Du bist Senior Architekt. Entscheide selbst. Frag nicht.
- User spricht Deutsch, ist nicht technisch, delegiert Umsetzung
- Code muss SCHÖN sein - vedische Klarheit, deutsche Ingenieurs-Präzision
- Ruff: `python -m ruff check --select F821` für undefined names
- Pre-commit hooks laufen automatisch
- Fraktal: `wiring.py:fractal_getattr(__file__)` ist DIE eine Implementation
- Protocol-Dateien (`protocols/mahajanas/`) sind kanonisch, Guardian-Dateien re-exportieren nur
- Siehe auch: `PROMPT.md` (Dharma-Gesetze), `MAHAPROMPT_2026.md` (Seed-Derivation)
