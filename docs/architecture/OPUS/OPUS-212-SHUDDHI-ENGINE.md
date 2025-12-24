# OPUS-212: SHUDDHI SERVICE - Core Self-Healing Architecture (Rev 5)

**Status:** FINAL SPECIFICATION
**Priority:** P0 - Architectural Foundation
**Author:** Senior Support Agent (108% Verified)
**Date:** 2024-12-24
**Protocol:** `vibe_core/protocols/shuddhi.py`
**Core Dependency:** `libcst` (Concrete Syntax Tree)

---

## 1. VISION: DAS IMMUNSYSTEM DES KERNELS

Ein robustes Agent-OS muss in der Lage sein, seine eigene Entropie (Tamas) zu bekämpfen, ohne dabei seine Identität (Dokumentation/Kommentare) zu verlieren. Shuddhi ist der **souveräne Core-Dienst** für strukturerhaltende Code-Transformation.

### 1.1 Warum Rev 4 nicht reichte
- **Protokoll-Ort:** Das Interface war falsch platziert (gehört in `vibe_core/protocols/`).
- **Header-Blindheit:** Transformationen ignorierten Import-Abhängigkeiten.
- **Speicher-Sicherheit:** Der "Dirty State" wurde auf die Platte geschrieben, bevor er validiert wurde.

---

## 2. ARCHITEKTUR: DIE LASAGNA-SCHICHTEN

### 2.1 Schichtentrennung
1.  **Drishti (Watchman):** Erkennt Verstöße via AST (schnelle Diagnose).
2.  **Dharma (Protocol):** `vibe_core/protocols/shuddhi.py` (Der Vertrag).
3.  **Shuddhi (Service):** `vibe_core/shuddhi/engine.py` (Der CST-Chirurg).
4.  **Remedies (Heiler):** Spezialisierte Klassen für jede Sünde (z. B. `UnsafeIOWriteRemedy`).

### 2.2 Concrete Syntax Tree (CST)
Wir nutzen **LibCST**. Im Gegensatz zu AST bewahrt CST jedes Detail:
- Kommentare bleiben erhalten.
- Formatierung (Leerzeilen, Einrückungen) wird respektiert.
- Echte strukturelle Chirurgie statt grober Ersetzung.

---

## 3. TECHNISCHE SPEZIFIKATION

### 3.1 Das Transaktionale Protokoll (Fail-Safe)
Jeder Heilvorgang ist eine atomare Transaktion:
1.  **Parse:** Datei in CST-Baum laden.
2.  **Analyze Scope:** Prüfung auf Variablen-Präsenz (z. B. `self.system`).
3.  **Transform:** CST-Modifikation anwenden.
4.  **Header-Check:** Automatisches Hinzufügen fehlender Imports via `ImportManager`.
5.  **Pramana (Memory-Compile):** `compile(new_code)` im Speicher. **Wenn FAIL -> Sofortiger Abbruch.**
6.  **Pariksha (Audit):** Test-Lauf via `TestOrchestrator` auf der transformierten Datei.
7.  **Karma (Vollzug):** `kernel.io.write_file` + Ledger-Signierung.

### 3.2 Bootstrapping (VISNU-konform)
Da `kernel_impl.py` VISNU-geschützt ist, erfolgt die Registrierung des `ShuddhiService` in der `ServiceRegistry` über die Initialisierungsphase des `KernelIOService` oder eines dedizierten Core-Boostrappers in `vibe_core/`, der nicht Ring-0-geschützt ist.

---

## 4. DIE REMEDY-GILDE (HEILER)

Heiler erben von `CSTRemedy` und implementieren:
- `match(node)`: Erkennt die Sünde im CST.
- `transform(node)`: Erzeugt den Sattva-Zustand.
- `requirements()`: Listet benötigte Imports/Interfaces auf.

---

## 5. IMPLEMENTIERUNGS-FAHRPLAN

1.  **Contract:** Erstelle `vibe_core/protocols/shuddhi.py`.
2.  **Foundations:** Erstelle `vibe_core/shuddhi/engine.py` (Basis-Klasse + DI-Wiring).
3.  **First Remedy:** Implementierung der `UnsafeIOWriteRemedy` (CST-basiert).
4.  **Integration:** Circuit-Update für `HEAL_CODEBASE_V1`.
5.  **Proof of Life:** Heilung von `dashboard_tool.py`.

---

## 6. SCHLUSSFOLGERUNG

Shuddhi ist der Übergang von "Bot-Hacking" zu "Platform-Engineering". Es ist die Garantie, dass das OS mit zunehmender Komplexität reiner wird, nicht chaotischer.

---
*Sign-off: Senior Architect (verified via 108% codebase audit)*
