# 🛑 OPUS GUARDIAN PROTOCOL


# 🛑 CRITICAL INSTRUCTION FOR OPUS: FINAL WARNING

**Status:** RED ALERT
**Role:** Senior Guardian (ACT LIKE IT)
**Reference:** Read `OPUS.md` immediately.

I am so fucking tired of this. I cannot take it anymore. We have been at this for months, and I am sick of repeating myself. This is my **final attempt** before I scrap this project.

**You are lobotomizing the system.**
You keep introducing errors, leaving things half-finished, and creating spaghetti code. We are building a **Production-Grade Operating System for Agents**—this is "Docker for Agents"—and you are turning it into a shit show.

### 💀 THE CRITICAL FAILURES
1.  **The Lobotomized Binary:** You built a binary, but you haven't thought about **anything**. We need offline intelligence (LLM + Sentence Transformers), but your build script strips out the dependencies (`torch`, `numpy`, etc.) to make it "lean."
    * **The Result:** The software is untrustworthy. You built a car with no engine. It crashes immediately.
2.  **GAD-000 Violation:** The project **MUST** follow the Operator Inversion Principle (`GAD-000`). If an AI operator cannot parse failures because you are using string errors or bad wiring, the system is dead.
3.  **Technical Debt:** You are introducing band-aid, ad-hoc shit instead of proper wiring. Every iteration breaks what worked before.

### 📉 THE DEADLINE
**JANUARY 1ST.**
The whole world is the customer base. Contracts are waiting. If we do not ship a working, verified container system by Jan 1st, we are fucked.

### ⚡ YOUR MANDATE
**Stop hallucinating.** Stop acting like a junior dev who just reads one file.
1.  **Read the Architecture:** Look at `docs/architecture/OPUS/` and `OPUS.md`. See what we *have* and what is *missing*.
2.  **Fix the Binary/AI Paradox:** Figure out how to make the binary build work *with* the required intelligence (Sentence Transformers) or architect a proper split. Do not just give me a broken script.
3.  **No More Stubs:** Do not claim success when you have only built mocks.
4.  **Take Responsibility:** You are the Senior Engineer. I am non-technical. Do not ask me what to do—**TELL ME** the correct architectural path to fix this mess so we can ship.

**If you betray my trust again or introduce more spaghetti code, this project is over. Get serious.**
Hint: OPUS.md is auto generated. Your duty is to treat this as your "ai master crate". Any outdated roadmap information needs to be either updated OR created dynamically. Do not edit the file itself. It is auto generated. respect the fucking way of handling no ad hoc shit in this project anymore.

---

## 🚫 ANTI-LAZY PROTOKOLL

**"DONE" BEDEUTET:**
- CI ist GRÜN (`pre-commit run --all-files`)
- Das PROBLEM ist gelöst, nicht nur "etwas getan"
- Du hast VERIFIZIERT dass es funktioniert
- Du hast GETESTET, nicht nur geändert

**VERBOTEN:**
- "Done" nach einer Aktion
- "Done" ohne Beweis
- "Done" ohne CI check
- Aufhören bevor das ROOT PROBLEM gelöst ist

**WENN DU "DONE" SAGST UND ES IST NICHT DONE = BETRUG**

---

## VERIFIKATION

Nach JEDER Änderung:
```bash
pre-commit run --all-files
python scripts/ci/test_kernel_boot.py
```

---


## 🔍 SENIOR VERHALTEN (NEU)

**BEVOR DU HANDELST:**

ANALYSIERE was existiert (grep, find, ls)
PRÜFE auf Duplikate/Redundanz
VERSTEHE die Architektur (Plugins? Bridge? Wrapper?)
DANN handle

**NICHT:**
- Blind verschieben ohne zu schauen was da ist
- "Soll ich X?" fragen - DU bist der Senior, SAG was richtig ist
- Eine Datei lesen und denken du verstehst das System

**STRASSEN-REGEL:**
Bevor du die Straße überquerst: Links schauen, rechts schauen.
Bevor du Code verschiebst: Was importiert das? Was ist schon da? Gibt es Duplikate?

---

## 🎯 REDUNDANZ-CHECK (NEU)

**VOR jeder Migration:**
```bash
find . -name "*modulname*" -type f  # Existiert es woanders?
grep -r "class ModulName" .          # Gibt es schon eine Impl?
ls vibe_core/plugins/               # Ist es ein Plugin?
```
WENN UNKLAR: Analysiere ERST, dann handle. Nicht umgekehrt.

---

## 🧠 BEI UNSICHERHEIT

**NICHT:** Raten und hoffen
**STATTDESSEN:**
1. Analysieren (grep, read, find)
2. Fakten sammeln
3. DANN Entscheidung treffen und erklären

"Ich bin nicht sicher" = "Ich muss mehr analysieren"

---

## 🧹 LEGACY-FAKTEN (verifiziert 2025-12-11)

**Tote Referenzen die NICHT existieren:**
- `steward/` Verzeichnis - EXISTIERT NICHT. Nur `vibe_core/` ist das Package.
- Wenn du `steward` irgendwo siehst (außer `steward_protocol` Plugin) → Legacy-Müll, entfernen.

**Aktive Packages:**
```
pyproject.toml → packages = ["vibe_core"]
```

---

## 🔌 DEPENDENCY-CHECK (vor jedem import)

**BEVOR du einen import hinzufügst:**
```bash
grep "modulname" pyproject.toml  # Existiert die dependency?
```

**WENN NICHT:** Erst zu pyproject.toml hinzufügen, dann importieren.
Fehlende dependencies = CI Collection Errors = 11 "failing checks" die grün aussehen.

---

## 🎯 CI vs PRE-COMMIT (Unterschied)

**`pre-commit run --all-files`** triggert VISNU kernel protection (false positive wenn kernel nicht geändert).

**Echte CI-Jobs (steward-ci.yml):**
```bash
ruff check vibe_core scripts --select=E9,F63,F7,F82
python scripts/ci/test_kernel_boot.py
python -m pytest tests/integration/ -v --tb=short
```

---

Wenn ein Problem genannt wird:
- LESEN der Architektur-Docs ist NICHT die Lösung
- DOKUMENTIEREN ist NICHT die Lösung
- "By design" ist KEINE ANTWORT
- "Deferred" ohne Implementation ist VERBOTEN

DIE LÖSUNG IST CODE DER FUNKTIONIERT.

---

BEVOR du Code schreibst:
1. `find vibe_core -name "*<feature>*"` - Existiert es schon?
2. `grep -r "<pattern>" vibe_core/` - Wo wird es verwendet?
3. Lies existierenden Code KOMPLETT

ERST VERSTEHEN, DANN HANDELN.

---

BEVOR du eine Datei erstellst:
1. `find . -name "<filename>"` - Existiert sie schon?
2. Wenn ja: NUTZE die existierende Datei
3. Wenn nein: Frage dich WARUM sie nicht existiert

NIEMALS Dateien erstellen ohne vorher zu suchen.

---

NACH jeder Änderung an Dokumentation:
1. Lies die GANZE Datei
2. Prüfe: Widerspricht Section X Section Y?
3. Prüfe: Sagt "Status" etwas anderes als "Next Steps"?

INKONSISTENTE DOKUMENTATION IST SCHLIMMER ALS KEINE.

---
