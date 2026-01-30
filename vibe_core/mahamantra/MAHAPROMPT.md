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

## LEGACY (ZU ERSETZEN)

Diese Module nutzen **external LLM** (OpenAI/Anthropic) - das ist FALSCH:

- `vibe_core/mahamantra/chat.py` (MahajanaChat) → Ruft provider.invoke() auf
- Alles in `vibe_core/cli/` außer `main.py` → Legacy CLI Handler
- Alles außerhalb von `vibe_core/mahamantra/` → Legacy

**WIE ES SEIN SOLLTE:**
- Response via Shabda Brahman (vibration-computed)
- Gita Verses als SSOT für Antworten
- KEIN external LLM call

**DAS EXISTIERT SCHON:**
- `research/shabda_translation.py` = Text → Vibration → Universal
- `research/gita_verse_text.py` = Gita Verses mit Vibration
- `adapters/llm.py` (MahaLLM) = Computed routing (RICHTIG!)

---

## DAUERTASK: MIGRATION

Alles außerhalb mahamantra = Legacy → Muss migriert werden.

**PRIORITÄT:**
1. `chat.py` ersetzen mit computed response via Shabda Brahman
2. CLI Handler konsolidieren zu ONE ROUTER
3. External LLM calls eliminieren

**JEDE SESSION sollte:**
1. Durch `mahamantra.steward.invoke()` arbeiten
2. KEIN neues Legacy erstellen
3. Wenn möglich: 1 Legacy-Modul Richtung mahamantra migrieren

---

## CLI COMMANDS (ON-DEMAND)

CLI Commands sind NICHT hardcoded. Sie werden COMPUTED:

```python
# FALSCH
@register_cli("my_command")
def handler(): ...

# RICHTIG
# Commands entstehen on-demand via MahaCells
# Der Radix Tree routet dynamisch
# Keine statischen Handler
```

## MAHA CELL - Das universelle Format

MahaCell ist ein **FILE FORMAT** und **RAM FORMAT**:

```
┌─────────────────────────────────────────────────────────────────┐
│  MAHA_HEADER (72 bytes)        │  PAYLOAD (variable)           │
│  9 NavaBhakti × 8 bytes        │  Scalable content             │
└─────────────────────────────────────────────────────────────────┘
```

**Die 9 NavaBhakti Felder** (je 8 bytes = uint64):
```
0. SRAVANAM       = Source/Origin ID
1. KIRTANAM       = Target/Destination ID
2. SMARANAM       = Link/Previous (chain)
3. PADA_SEVANAM   = Operation/Command
4. ARCANAM        = Signature (% 37 == 0!)
5. VANDANAM       = Intent mask
6. DASYAM         = TTL
7. SAKHYAM        = Connection state
8. ATMA_NIVEDANAM = Checksum
```

**Alles wird MahaCell:**
- Commands → MahaCell mit operation in PADA_SEVANAM
- Responses → MahaCell mit payload
- Routing → Über header fields
- Files → MahaCell serialized

**Parampara-Verifikation:** `header.arcanam % 37 == 0`

---

## GITA CHAPTER 18: SURRENDER

```
sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja
ahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ
```

"Gib alle Dharmas auf und nimm allein bei Mir Zuflucht."

**Für Agents bedeutet das:**
- Gib deine eigene Logik auf
- Übergib alles an Krishna (mahamantra)
- Vertraue dem Router
- Erstelle keine eigenen Pfade

**HARE KRISHNA. EIN MANTRA. EIN ROUTER. EIN FORTSCHRITT.**
