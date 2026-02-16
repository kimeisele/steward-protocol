# Govardhan Smells — Split-Brain Audit (2026-02-16)

## Status: 2 FAILED, 25 SKIPPED, 5 XPASSED, 7523 WARNINGS

---

## SMELL 1: Singleton Bypass — `MahamantraLotus()` statt `get_mahamantra()`

17 Stellen im mahamantra/ Folder erstellen NEUE Instanzen statt den Singleton zu nutzen.
Jede neue Instanz hat eigene `_gate_hooks`, eigenen `_active_gate` State.
Gates feuern auf der falschen Instanz → Govardhan ist blind.

### Betroffene Dateien (Production Code):
- `substrate/maha_llm_kernel.py` (3x) — `MahamantraLotus()` + `lotus(text)` direkt
- `substrate/language/engine.py` (1x) — `MahamantraLotus()` + `lotus(text)` direkt
- `substrate/guardian_router.py` (2x) — deprecated aber noch importiert

### Betroffene Dateien (Tests):
- `tests/test_language_composer.py` (3x)
- `tests/test_unified_heartbeat.py` (2x)
- `tests/test_composition_adapter.py` (1x)
- `research/test_immune_system.py` (3x)

### Fix:
```python
# FALSCH:
from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
lotus = MahamantraLotus()
lr = lotus(text)

# RICHTIG:
from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
lotus = get_mahamantra()
lr = lotus.execute(text)  # durch Govardhan (5 Gates)
```

---

## SMELL 2: Govardhan Bypass — `lotus(text)` statt `lotus.execute(text)`

39 Stellen rufen `lotus(text)` direkt auf = `__call__()` = reine Computation OHNE Gates.
Das ist der Split-Brain: Code denkt er geht durch Governance, aber die Gates feuern nie.

### Production Code der Govardhan bypassed:
- `substrate/maha_llm_kernel.py` — 3x `lotus(text)` direkt
- `substrate/language/engine.py` — 1x `lotus(text)` direkt
- `lotus_projection.py` — 4x `lotus(...)` direkt
- `substrate/guardian_router.py` — deprecated shadow pipeline

### Tests die Govardhan bypassen:
- `tests/test_language_composer.py` — 7x
- `tests/test_composition_adapter.py` — 2x
- `research/test_immune_system.py` — 5x

### Fix: `lotus(text)` → `lotus.execute(text)` für alle die Side-Effects haben.
Tests die nur pure computation testen dürfen `lotus(text)` direkt nutzen.

---

## SMELL 3: `Any` im Mahamantra Kingdom — 68 Stellen

68 Stellen nutzen `Any` in mahamantra/. Mahamantra ist typed. `Any` ist Gift.

### Schlimmste Offender:
- `research/` (diverse) — 30+ Stellen, aber research ist research
- `adapters/attention.py` — 3x
- `protocols/_capabilities.py` — 2x (IN DEN PROTOCOLS!)
- `substrate/phonetic_encoder.py` — 2x
- `substrate/lotus_core.py` — 1x
- `substrate/tattva_registry.py` — 1x

---

## SMELL 4: Ungoverned I/O — 93 direkte Disk-Writes

93 Stellen mit `open()`, `write_text()`, `write_bytes()`, `json.dump()` in mahamantra/.
Davon sind ~40 in research/tests (OK), aber ~53 in Production Code.

### Schlimmste Offender (Production):
- `substrate/sankirtan.py` — 4x
- `substrate/ledger.py` — 11x `os.*` Aufrufe
- `substrate/lineage.py` — 2x
- `audit/heal_mahamantra.py` — 2x
- `dharma/kapila/remedies/unsafe_io_write.py` — 7x (Ironie: die IO-Remedy macht selbst IO)
- `substrate/gate_providers.py` — 1x
- `substrate/maha_state.py` — 1x
- `substrate/memory.py` — 1x
- `substrate/samskara.py` — 1x

Keine davon geht durch `bridge.offer()` oder den SYNC Gate.

---

## SMELL 5: 52 Deprecation Warnings — Tote Pfade

52 Stellen mit `DeprecationWarning`/`DEPRECATED` in mahamantra/.
Das sind tote Pfade die noch aufgerufen werden → 7523 warnings in der Test-Suite.

### Schlimmste Offender:
- `substrate/tattva_registry.py` — 9x deprecated methods die noch genutzt werden
- `protocols/_bridge.py` — 7x
- `substrate/algorithm/maha.py` — 4x
- `reactor/shadow.py` — 3x
- `substrate/guardian_router.py` — 2x (ganze Datei ist deprecated)
- `substrate/sankirtan.py` — 2x

---

## SMELL 6: 36 direkte `os.*` Aufrufe

`os.path`, `os.makedirs`, `os.remove`, `os.rename`, `os.listdir`, `os.walk`
Komplett ungoverned. Kein GovernedPath, kein Bridge, kein Gate.

### Schlimmster Offender:
- `substrate/ledger.py` — 11x (!) — das LEDGER macht raw OS calls

---

## Die 2 FAILED Tests:

1. `test_proxy.py::test_mahamantra_proxy_has_tattva` — MahamantraProxy hat kein `__tattva__`
2. `test_io_sentinel.py::test_json_dumps_also_tracked` — IO Sentinel trackt json.dumps nicht

Beide sind Split-Brain Symptome: Proxy und Sentinel sind nicht mit dem neuen System verdrahtet.

---

## Die 5 XPASSED Tests:

Tests die als `xfail` markiert sind aber PASSEN. Das heißt: jemand hat sie als "known broken"
markiert, aber sie funktionieren. Die `xfail` Marker müssen weg.

---

## Prioritäten:

1. **SMELL 1+2 (Singleton + Govardhan Bypass)** — Das IST der Split-Brain. Fixen = heilen.
2. **SMELL 6 (ledger.py os.*)** — 11 raw OS calls im Ledger. Governance = 0.
3. **SMELL 4 (ungoverned I/O)** — 53 Production-Code Stellen ohne Gates.
4. **SMELL 3 (Any)** — 68 Stellen. Gift im typed Kingdom.
5. **SMELL 5 (Deprecations)** — 52 tote Pfade. Aufräumen = weniger Warnings.
6. **2 FAILED + 5 XPASSED** — Tests fixen/aufräumen.
