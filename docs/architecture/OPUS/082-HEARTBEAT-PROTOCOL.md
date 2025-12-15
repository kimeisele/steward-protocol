# OPUS-082: THE HEARTBEAT PROTOCOL (Cognitive Pulse)

> "The heart must beat for the mind to think, and Shiva must destroy for Brahma to create."

**Feature**: Autonomous Self-Healing & Intent Lifecycle  
**Status**: ACTIVE  
**Role**: The Carrier Wave of Intelligence  

## 1. The Trinity (Trimurti) Architecture
Das System folgt dem kosmischen Zyklus:

1.  **BRAHMA (Genesis)**: `IntentGenerator` erzeugt neue Absichten (Intents) basierend auf Beobachtungen.
2.  **VISHNU (Steward)**: `CognitiveKernel` (MANAS) hält die Intents im Buffer und priorisiert sie.
3.  **SHIVA (Dissolution)**: `ShivaLifecycleManager` prüft die Realität (`Git is Truth`). Wenn ein Intent in der Realität bereits erfüllt ist (z.B. Datei existiert), löst Shiva den Intent auf.

## 2. The Closed Loop (Der geschlossene Kreis)
1.  **Pulse**: GitHub Actions triggert `heartbeat.py`.
2.  **Wake Up**: `HeartbeatEngine` bootet `CognitiveKernel` (MANAS).
3.  **Shiva's Dance**: 
    * Shiva scannt `pending` Intents.
    * Shiva prüft: "Existiert der Test für `cognitive_kernel.py` schon?"
    * Ja? -> Intent Status: `FULFILLED_EXTERNALLY` -> Archiviert.
4.  **Brahma's Creation**: Neue Beobachtungen erzeugen neue Intents.
5.  **Execution (Karma)**: `HeartbeatEngine` führt *genehmigte* Intents via `Envoy` aus (Callback).

## 3. Verification Harness

The system is self-verifying.

```yaml
# @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/shiva.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
wiring:
  - pattern: "ShivaLifecycleManager"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "sweep_and_archive"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "set_execution_callback"
    in: scripts/heartbeat.py
```
