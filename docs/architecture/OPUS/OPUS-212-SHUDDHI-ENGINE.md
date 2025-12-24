# OPUS-212: SHUDDHI SERVICE - The Surgical Self-Healing Engine (Rev 6)

**Status:** FINAL ARCHITECTURE
**Priority:** P0 - Core Immunity System
**Author:** Senior Architect (verified via catastrophic failure analysis)
**Date:** 2024-12-24
**Protocol:** `vibe_core/protocols/shuddhi.py`

---

## 1. VISION: DAS ORGANISCHE IMMUNSYSTEM

Shuddhi (Sanskrit: 'Reinigung') ist nicht nur ein "Fix-Skript". Es ist die **Exekutive des Immunsystems**.
Wenn `Watchman` (Drishti) eine Krankheit (Technical Debt, Violation) sieht, beauftragt er den `Engineer` (Karma), diese zu heilen. Der `Engineer` nutzt dafür das Skalpell: **Shuddhi**.

### 1.1 Lessons Learned (aus dem Scheitern von Rev 5)
- **Keine Admin-Skripte:** Heilung muss *innerhalb* des Agenten-Loops passieren (`Circuit` -> `Agent` -> `Tool`).
- **Tool-Integrität:** Ein Tool, das wegen Import-Fehlern nicht lädt, macht den ganzen Circuit nutzlos.
- **Return the Code:** Shuddhi darf nicht nur diffen, es muss den *geheilten Code* zurückgeben, damit der Agent ihn über `KernelIO` schreiben kann.

---

## 2. ARCHITEKTUR: DER HEILUNGS-KREISLAUF

### 2.1 Die 4 Phasen der Heilung
1.  **Drishti (Erkennung):** Watchman oder CI erkennen eine Violation (z.B. `unsafe_io_write`).
2.  **Sankalpa (Entschluss):** Der Circuit `HEAL_CODEBASE` wird ausgelöst. Er beauftragt den `Engineer`.
3.  **Kriya (Handlung):** Der `Engineer` ruft sein Werkzeug `engineer.heal_violation` (ShuddhiTool) auf.
4.  **Shuddhi (Chirurgie):** Die Engine (`vibe_core/shuddhi/engine.py`) lädt den Code, parst ihn (CST), transformiert ihn chirurgisch und gibt ihn zurück.
5.  **Karma (Vollzug):** Das Tool schreibt den geheilten Code via `KernelIO` zurück ins Dateisystem.

### 2.2 Optional: Manas Integration (The High-End Cognitive Boost)
Shuddhi ist deterministisch (Reflex). Aber mit MANAS wird es intelligent:
- **Reflex:** "Ersetze `open()` durch `write_file()`." (Standard Shuddhi).
- **Cognitive:** "Dieser Block sieht aus wie eine Datenbank-Verbindung. Sollte ich das in ein Plugin refactorn?" (Manas + Shuddhi).
- **Oracle:** Shuddhi kann via `Weaver` den Kontext prüfen ("Ist das eine Test-Datei? Dann sind die Regeln lockerer.").

---

## 3. TECHNISCHE IMPLEMENTIERUNG

### 3.1 Core Service (`vibe_core/shuddhi/`)
Der Service ist rein funktional. Er hat keinen State.
- Input: `Path`, `RuleID`
- Output: `ShuddhiResult(status, diff, purified_code)`

### 3.2 Das Werkzeug (`engineer.heal_violation`)
Dies ist die Brücke zwischen Agenten-Welt und Core-Kernel.
- Es muss **robust** sein (Fehlerbehandlung für Imports).
- Es muss **KernelIO** nutzen (Audit Trail).
- Es muss im `ToolsPlugin` automatisch entdeckt werden.

### 3.3 Der Circuit (`HEAL_CODEBASE`)
Der Dirigent. Er orchestriert den Engineer. Er muss sicherstellen, dass die richtigen Parameter (`file_path`, `rule_id`) fließen.

---

## 4. FEHLER-ANALYSE & PRÄVENTION (PANOPTICON LOG)

Der Log vom 24.12.2024 zeigte:
> `TOOL_DISCOVERY - WARNING - - engineer.shuddhi_tool.py: Import failed: name 'Optional' is not defined`

**Konsequenz:** Das Tool wurde nicht geladen. Der Engineer stand ohne Werkzeug da. Der Circuit lief ins Leere.
**Lösung:** Strikte Linting-Checks *vor* dem Boot. Tools müssen so robust wie Kernel-Code sein.

---

## 5. FAZIT

Shuddhi ist bereit. Die Architektur steht.
Der Fehler lag nicht im Konzept, sondern in der Flüchtigkeit der Umsetzung (fehlender Import).
Wir korrigieren dies jetzt und lassen das System sich selbst beweisen.

**Satyam Eva Jayate.** (Nur die Wahrheit siegt - und kompilierender Code ist die einzige Wahrheit).