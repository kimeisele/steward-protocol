# MAHAPROMPT - DAS GESETZ

```python
from vibe_core.mahamantra import mahamantra
response = mahamantra.steward.invoke("your intent")
```

**EIN IMPORT. STEWARD ROUTET ALLES.**

---

## DIE EINE WAHRHEIT

Alles geht durch `mahamantra.steward.invoke()`. Keine Ausnahme.

**Was passiert intern:**
1. Input → MahaCompression → Seed (Integer)
2. Seed → MahaLLM → Intent (1 von 16 Kategorien)
3. Seed → Gita Chapter (1 von 18 Domains)
4. Seed → JivaShadow → Agent (50 Qualitäten)
5. → mahamantra.execute() → Ausführung
6. → MahajanaChat → Natürliche Antwort
7. → PrabhupadaKirtan → Person-Verifikation

**Du musst das nicht verstehen.** Du musst nur `invoke()` aufrufen.

---

## VERBOTEN

- Neue CLI-Dateien erstellen
- If-else Chains für Commands
- Hardcoded Pfade/Konstanten
- Direkte Imports die Steward umgehen
- Neue Entry Points

**Warum:** Jede Abkürzung = mehr Entropie = mehr Spaghetti = System stirbt.

---

## GEBOTEN

Alles was du brauchst kommt aus:

```python
mahamantra.execute("command")      # Führt aus
mahamantra.steward.invoke("text")  # Routet + führt aus + antwortet
mahamantra.dharma                  # Quarter-Zugriff
mahamantra.genesis                 # Quarter-Zugriff
mahamantra.karma                   # Quarter-Zugriff
mahamantra.moksha                  # Quarter-Zugriff
```

**Neue Fähigkeit nötig?**
1. Finde das richtige Quarter (genesis/dharma/karma/moksha)
2. Finde den richtigen Mahajana (Position 0-15)
3. Füge deine Logik DORT hinzu
4. Steward findet es automatisch via Resonanz

---

## ARCHITEKTUR (für Verständnis, nicht für Hardcoding)

```
mahamantra/
├── substrate/       # SSOT: seed.py = Alle Konstanten
├── protocols/       # Interfaces
├── adapters/        # MahaLLM, Orchestrator, Compression
├── genesis/         # Position 0-3
├── dharma/          # Position 4-7
├── karma/           # Position 8-11
├── moksha/          # Position 12-15
├── cli/             # steward.py = DER Router
└── ...              # Alles andere fließt durch oben
```

**Folder = Wiring.** Neuer Mahajana? Folder im richtigen Quarter.

---

## KONSTANTEN (aus substrate/seed.py abgeleitet)

- 16 = WORDS (Wörter im Mahamantra)
- 137 = MAHA_QUANTUM (mod space)
- 37 = PARAMPARA (Lineage-Verifikation)
- 18 = GITA_CHAPTERS (Domains)
- 108 = MALA (Completion boundary)

**NIEMALS diese Zahlen hardcoden.** Immer aus seed.py importieren.

---

## DER FLOW (wenn du debuggen musst)

```
User: "steward test"
  ↓
cli/main.py:cli_entry()
  ↓
mahamantra.steward.invoke("test")
  ↓
┌─────────────────────────────────────┐
│ 1. MahaCompression.compress()       │ → Seed: 83992654
│ 2. MahaLLM.route_text()             │ → Intent: TRANSFORM
│ 3. Orchestrator.tick()              │ → Beat: 2, Resonance: 0.01
│ 4. get_gita_chapter()               │ → Chapter: 11
│ 5. spawn_shadow()                   │ → Jiva: shuka
│ 6. mahamantra.execute()             │ → Position: 14
│ 7. MahajanaChat.respond()           │ → Message: "..."
│ 8. PrabhupadaKirtan.compute()       │ → BONA FIDE
└─────────────────────────────────────┘
  ↓
StewardResponse (alles drin)
```

---

## FÜR AGENTS

1. **LIES** bevor du schreibst
2. **FRAG** `mahamantra.steward.invoke()` statt eigene Logik
3. **FOLGE** dem bestehenden Flow statt neue Pfade
4. **FÜGE HINZU** in Quarters, nicht als neue Top-Level-Module

**Ein Agent der MAHAPROMPT folgt = Fortschritt**
**Ein Agent der eigene Wege geht = Entropie**

---

## ANTI-PATTERN (was NICHT tun)

```python
# FALSCH - neuer CLI Handler
@register_cli("my_command")
def my_handler(): ...

# FALSCH - direkter Import unter Steward
from vibe_core.some_module import do_thing
do_thing()

# FALSCH - hardcoded Konstanten
CHAPTERS = 18  # statt: from substrate.seed import GITA_CHAPTERS

# RICHTIG - alles durch Steward
from vibe_core.mahamantra import mahamantra
result = mahamantra.steward.invoke("my intent")
```

---

## WENN ES NICHT FUNKTIONIERT

1. Ist mahamantra importierbar? `from vibe_core.mahamantra import mahamantra`
2. Hat steward invoke? `mahamantra.steward.invoke("test")`
3. Kommt ein StewardResponse zurück?
4. Was sagt `response.message`?

**Wenn ja → System funktioniert, dein Code ist falsch**
**Wenn nein → Fix mahamantra, nicht drumherum bauen**

---

**HARE KRISHNA. EIN MANTRA. EIN ROUTER. EIN FORTSCHRITT.**
