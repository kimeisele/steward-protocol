# BILA-SVARGA: Der Zustand der Unterwelt

> "In den unterirdischen Himmeln wird die Dunkelheit durch das Leuchten der Juwelen erhellt, welche die Nagas auf ihren Köpfen tragen."

Dieses Dokument beschreibt den Härtungsgrad der NAGA-Middleware (Layer 0 und darunter).

## I. DIE SERVICE-STATUS-MATRIX (NARASIMHA AUDIT)

| Service | Rolle | Status | Risiko | Fokus |
| :--- | :--- | :--- | :--- | :--- |
| **Sesha** | Memory / Ledger | ✅ HARDENED | - | Fail-Closed Read/Write & Boot Integrity |
| **Takshaka** | Guard / Security | ✅ HARDENED | - | Fail-Closed Bite & Verifikation |
| **Vasuki** | Bridge / Network | ✅ HARDENED | - | Fail-Closed Signing & Takshaka Gate |
| **Prahlad** | Boot-Integrity / Audit | ✅ HARDENED | - | Subprocess Isolation & Timeout |
| **Karkotaka** | Keys / Secrets | ✅ HARDENED | - | Fail-Closed Sign/Enc & Permissions |
| **Ananta** | Gene-Splicer | ✅ HARDENED | - | Fail-Closed Loading (No Shadow Load) |
| **Kaliya** | Quarantine | ✅ HARDENED | - | Persistent State via StateService |
| **Narada** | Messenger | ❓ UNKNOWN | MITTEL | Discovery & Observation |
| **Chitragupta**| Profiler / Metrics | ❓ UNKNOWN | NIEDRIG | Karma Recording |

## II. PRIORISIERUNG (PHASE IV)

### 1. PRAHLAD: Die Vertrauensbasis
Prahlad ist der Auditor. Ein Auditor, der Fehler verschluckt (`except: pass`) oder Timeouts bei `pytest.main()` ignoriert, erschafft eine Illusion von Sicherheit (*Mayavad*).
*   **Ziel:** `verify_self_integrity` und `dharma_audit` müssen Fail-Closed sein.

### 2. KARKOTAKA: Die Wurzel der Macht
Schlüsselverwaltung und Geheimnisse. Wenn die Identitätsbasis wackelt, sind kryptografische Signaturen wertlos.
*   **Ziel:** Audit der Key-Storage-Logik und Leak-Prevention.

## III. DHARMA-GARANTIE

Die Kernkette für die Integrität der Fakten ist jetzt geschlossen:
**Wächter (Takshaka) → Transport (Vasuki) → Gedächtnis (Sesha) → Ledger (Truth).**

Alle drei Komponenten agieren **Fail-Closed**. Bei Fehlern in der Vertrauenskette bleibt das System stehen, statt mit korrupten Daten oder ungesicherten Paketen fortzufahren.

---
*Status: 2026-01-06 | Stand: Phase III abgeschlossen, Phase IV initiiert.*
