# OPUS-212: SHUDDHI SERVICE - The Surgical Self-Healing Engine (Rev 7)

**Status:** FINAL ARCHITECTURE (Sovereign Core Stack)
**Priority:** P0 - Core Immunity System
**Author:** Senior Architect (verified via holistic loop verification)
**Date:** 2024-12-24
**Protocol:** `vibe_core/protocols/shuddhi.py`
**Core Dependency:** `libcst`, `TaskService`

---

## 1. VISION: DAS ORGANISCHE IMMUNSYSTEM

Shuddhi (Sanskrit: 'Reinigung') ist die **Exekutive des Immunsystems**. Es transformiert strukturelle Sünden (Tamas) zurück in architektonische Harmonie (Sattva), ohne dabei die Identität (Kommentare/Formatierung) des Codes zu zerstören.

### 1.1 Lessons Learned (The Christmas Crisis)
- **Tool-Integrität:** Werkzeuge müssen so robust wie der Kernel sein. Fehlende Imports (wie `Optional`) in Agent-Tools legen das gesamte System lahm.
- **Kala-Puls:** Heilung ist kein einmaliges Ereignis (Sarga), sondern ein permanenter Prozess (Kala).
- **Task-Souveränität:** Heilungsaktionen müssen als erstklassige Aufgaben (Tasks) im Core-System-Ledger dokumentiert werden.

---

## 2. ARCHITEKTUR: DER HOLISTISCHE LOOP

### 2.1 Die 4 Dimensionen der Heilung
1.  **Drishti (Erkennung):** Der `LogMonitor` scannt das `system_journal.jsonl` nach Error-Mustern (z.B. `ImportError`, `NameError`).
2.  **Sankalpa (Entschluss):** Die `ShuddhiKalaBridge` (verbunden mit dem `PulseManager`) erstellt bei Erkennung automatisch einen Task im `kernel.tasks`.
3.  **Kriya (Handlung):** Der `Engineer`-Agent nutzt das `engineer.heal_violation` Tool.
4.  **Karma (Vollzug):** Die `ShuddhiEngine` transformiert den Code, schreibt ihn via `KernelIO` und schließt den Task im Ledger ab.

### 2.2 Core Stack Integration (Ring 0)
- **`TaskService` Protocol:** Definiert das OS-Level Interface für Aufgabenverwaltung.
- **`RealVibeKernel.tasks`:** Ermöglicht jedem Agenten Zugriff auf persistente, kryptografisch gesicherte Aufgaben.
- **`RealVibeKernel.shuddhi`:** Exponiert den CST-Chirurgen direkt im Kernel.

---

## 3. TECHNISCHE SPEZIFIKATION

### 3.1 Komponenten
- **`vibe_core/shuddhi/engine.py`**: Der CST-Orchestrator.
- **`vibe_core/shuddhi/log_monitor.py`**: Der Journal-Scanner.
- **`vibe_core/shuddhi/kala_bridge.py`**: Der Puls-Abonnent.
- **`vibe_core/cartridges/system/engineer/tools/shuddhi_tool.py`**: Das Agenten-Werkzeug.

---

## 4. GAD-000 CONFORMANCE
- **Radikale Transparenz:** Jede Heilung hinterlässt einen Task-Eintrag im Ledger.
- **Zero-Touch:** Das System erkennt Fehler ohne menschliche Intervention.
- **Split-Brain Heilung:** Konsolidierung aller Task-Daten in `data/vibe_agency.db`.

---

## 5. FAZIT: DIE NEUE ORDNUNG
Das Steward Protocol verfügt nun über ein autonomes Nervensystem. Es hört (Logs), fühlt (Puls) und handelt (Shuddhi). Der Kreis ist geschlossen.

**Satyam Eva Jayate.**
