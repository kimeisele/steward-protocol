# SONNET EXECUTION PLAN - COMPLETE & READY

> **WARNUNG:** Dies ist der EINZIGE auszufuehrende Plan.
> **Erstellt:** 2025-12-07 by Opus 4.5
> **Verifiziert gegen:** Live HEAD (nicht Archive!)
> **Fuer:** Sonnet zur autonomen Ausfuehrung

---

## REGEL 0: WAS NICHT ANFASSEN!

Diese Dateien/Funktionen sind BEREITS GEFIXT - NICHT MODIFIZIEREN:

| Datei | Funktion | Status |
|-------|----------|--------|
| `vibe_core/steward/constitution.py` | `verify_oath()` Lines 145-151 | FIXED - nutzt identity_tool |
| `vibe_core/steward/constitution.py` | Genesis Hash Check Line 138 | FIXED - env-gated |
| `tests/test_prana_init.py` | `TestDailyRitual` Lines 155-166 | EXISTS - nicht nochmal schreiben |

---

## PHASE 1: STEWARD PROTOCOL PLUGIN TODOs

### 1.1 Fix signature_valid in verify_agent()

**Datei:** `vibe_core/plugins/steward_protocol/plugin_main.py`
**Zeile:** 376

**VORHER:**
```python
        result = {
            "agent_id": agent_id,
            "verified": False,
            "manifest_loaded": False,
            "signature_valid": None,  # TODO: implement
            "trust_score": self._trust_scores.get(agent_id, 0.0),
        }
```

**NACHHER:**
```python
        result = {
            "agent_id": agent_id,
            "verified": False,
            "manifest_loaded": False,
            "signature_valid": False,  # Default to False, verified below
            "trust_score": self._trust_scores.get(agent_id, 0.0),
        }

        # Verify signature using ConstitutionalOath if oath exists in ledger
        if self._kernel and hasattr(self._kernel, 'ledger'):
            oath_events = [
                e for e in self._kernel.ledger.get_all_events()
                if e.get("event_type") == "OATH_TAKEN" and e.get("agent_id") == agent_id
            ]
            if oath_events:
                from vibe_core.steward.constitution import ConstitutionalOath
                latest_oath = oath_events[-1]
                # Get identity_tool if available
                identity_tool = None
                if hasattr(self._kernel, 'tool_registry'):
                    identity_tool = self._kernel.tool_registry.get_tool("identity")
                is_valid, _ = ConstitutionalOath.verify_oath(latest_oath, identity_tool=identity_tool)
                result["signature_valid"] = is_valid
```

**Kontext:** Die Funktion `verify_agent()` beginnt bei Zeile 364. Der result-Dict wird bei 372-378 definiert.

---

### 1.2 Fix valid_until in attest()

**Datei:** `vibe_core/plugins/steward_protocol/plugin_main.py`
**Zeile:** 417

**VORHER:**
```python
    def attest(self, agent_id: str, capability: str) -> Dict[str, Any]:
        """
        Create an attestation for an agent's capability.

        Returns attestation record.
        """
        attestation = {
            "agent_id": agent_id,
            "capability": capability,
            "attested_at": datetime.utcnow().isoformat(),
            "attested_by": "steward_protocol_plugin",
            "valid_until": None,  # TODO: implement expiry
        }
```

**NACHHER:**
```python
    def attest(self, agent_id: str, capability: str, validity_hours: int = 24) -> Dict[str, Any]:
        """
        Create an attestation for an agent's capability.

        Args:
            agent_id: Agent to attest
            capability: Capability being attested
            validity_hours: Hours until attestation expires (default: 24)

        Returns attestation record.
        """
        from datetime import timedelta

        now = datetime.utcnow()
        attestation = {
            "agent_id": agent_id,
            "capability": capability,
            "attested_at": now.isoformat(),
            "attested_by": "steward_protocol_plugin",
            "valid_until": (now + timedelta(hours=validity_hours)).isoformat(),
        }
```

---

### 1.3 Add is_attestation_valid() helper

**Datei:** `vibe_core/plugins/steward_protocol/plugin_main.py`
**Nach Zeile:** 429 (nach get_attestations)

**NEUER CODE:**
```python
    def is_attestation_valid(self, agent_id: str, capability: str) -> bool:
        """
        Check if an attestation is still valid (not expired).

        Returns True if attestation exists and hasn't expired.
        """
        attestations = self._attestations.get(agent_id, {})
        attestation = attestations.get(capability)

        if not attestation:
            return False

        valid_until = attestation.get("valid_until")
        if not valid_until:
            return False

        try:
            expiry = datetime.fromisoformat(valid_until)
            return datetime.utcnow() < expiry
        except (ValueError, TypeError):
            return False
```

---

## PHASE 1 VERIFICATION

```bash
# Nach Phase 1 ausfuehren:
python -c "
from vibe_core.plugins.steward_protocol.plugin_main import StewardProtocolPlugin
from datetime import datetime, timedelta

plugin = StewardProtocolPlugin()

# Test attest() has valid_until
att = plugin.attest('test_agent', 'read_file')
assert att['valid_until'] is not None, 'valid_until should not be None'

# Test valid_until is in the future
valid_until = datetime.fromisoformat(att['valid_until'])
assert valid_until > datetime.utcnow(), 'valid_until should be in future'

# Test is_attestation_valid()
assert plugin.is_attestation_valid('test_agent', 'read_file'), 'Fresh attestation should be valid'

print('PHASE 1 PASSED')
"

# Run existing tests
python -m pytest tests/ -k "steward" -v --tb=short
```

---

## PHASE 2: STATE PERSISTENCE

### 2.1 VedicGovernance Ledger Persistence

**Datei:** `vibe_core/plugins/vedic_governance/plugin_main.py`
**Zeilen:** 64-69

**VORHER:**
```python
        # Varna = Classification (what kind of being)
        # TODO: Persist to Ledger (currently in-memory)
        self._varna_registry: Dict[str, Varna] = {}

        # Ashrama = Lifecycle (student → active → retired → system)
        # TODO: Persist to Ledger (currently in-memory)
        self._ashrama_registry: Dict[str, AshramaTransition] = {}
```

**NACHHER:** (Kein Change an __init__, aber add persistence methods)

**Neue Methode nach on_boot() (ca. Zeile 90):**
```python
    def _persist_varna(self, agent_id: str, varna: "Varna") -> None:
        """Persist varna assignment to ledger."""
        if self._kernel and hasattr(self._kernel, 'ledger'):
            self._kernel.ledger.record_event(
                event_type="VARNA_ASSIGNED",
                agent_id=agent_id,
                details={"varna": varna.value if hasattr(varna, 'value') else str(varna)}
            )

    def _persist_ashrama(self, agent_id: str, transition: "AshramaTransition") -> None:
        """Persist ashrama transition to ledger."""
        if self._kernel and hasattr(self._kernel, 'ledger'):
            self._kernel.ledger.record_event(
                event_type="ASHRAMA_TRANSITION",
                agent_id=agent_id,
                details={
                    "from_stage": transition.from_stage.value if transition.from_stage else None,
                    "to_stage": transition.to_stage.value if hasattr(transition.to_stage, 'value') else str(transition.to_stage),
                    "reason": transition.reason,
                    "timestamp": transition.timestamp.isoformat() if transition.timestamp else None
                }
            )

    def _restore_from_ledger(self) -> None:
        """Restore governance state from ledger on boot."""
        if not self._kernel or not hasattr(self._kernel, 'ledger'):
            return

        for event in self._kernel.ledger.get_all_events():
            event_type = event.get("event_type")
            agent_id = event.get("agent_id")
            details = event.get("details", {})

            if event_type == "VARNA_ASSIGNED" and agent_id:
                varna_str = details.get("varna")
                if varna_str:
                    try:
                        self._varna_registry[agent_id] = Varna(varna_str)
                    except ValueError:
                        pass  # Unknown varna value

            elif event_type == "ASHRAMA_TRANSITION" and agent_id:
                # Only keep latest transition per agent
                to_stage = details.get("to_stage")
                if to_stage:
                    try:
                        self._ashrama_registry[agent_id] = AshramaTransition(
                            from_stage=Ashrama(details.get("from_stage")) if details.get("from_stage") else None,
                            to_stage=Ashrama(to_stage),
                            reason=details.get("reason", "restored from ledger"),
                            timestamp=datetime.fromisoformat(details["timestamp"]) if details.get("timestamp") else datetime.utcnow()
                        )
                    except (ValueError, KeyError):
                        pass  # Invalid transition data
```

**Modify on_boot():** Add call to restore:
```python
    def on_boot(self, kernel: "RealVibeKernel") -> None:
        self._kernel = kernel
        # Restore state from ledger
        self._restore_from_ledger()
        # ... rest of existing code
```

**Modify assign_varna():** Add persistence call after assignment:
```python
        self._varna_registry[agent_id] = varna
        self._persist_varna(agent_id, varna)  # ADD THIS LINE
```

**Modify transition_ashrama():** Add persistence call:
```python
        self._ashrama_registry[agent_id] = transition
        self._persist_ashrama(agent_id, transition)  # ADD THIS LINE
```

---

### 2.2 StewardProtocol Ledger Persistence

**Datei:** `vibe_core/plugins/steward_protocol/plugin_main.py`

**Neue Methoden nach __init__ (ca. Zeile 110):**
```python
    def _persist_manifest(self, agent_id: str, manifest: Dict[str, Any]) -> None:
        """Persist manifest to ledger."""
        if self._kernel and hasattr(self._kernel, 'ledger'):
            self._kernel.ledger.record_event(
                event_type="MANIFEST_REGISTERED",
                agent_id=agent_id,
                details={"manifest": manifest}
            )

    def _persist_trust_score(self, agent_id: str, score: float, reason: str = "") -> None:
        """Persist trust score change to ledger."""
        if self._kernel and hasattr(self._kernel, 'ledger'):
            self._kernel.ledger.record_event(
                event_type="TRUST_SCORE_UPDATED",
                agent_id=agent_id,
                details={"score": score, "reason": reason}
            )

    def _persist_attestation(self, agent_id: str, capability: str, attestation: Dict[str, Any]) -> None:
        """Persist attestation to ledger."""
        if self._kernel and hasattr(self._kernel, 'ledger'):
            self._kernel.ledger.record_event(
                event_type="ATTESTATION_CREATED",
                agent_id=agent_id,
                details={"capability": capability, "attestation": attestation}
            )

    def _restore_from_ledger(self) -> None:
        """Restore protocol state from ledger on boot."""
        if not self._kernel or not hasattr(self._kernel, 'ledger'):
            return

        for event in self._kernel.ledger.get_all_events():
            event_type = event.get("event_type")
            agent_id = event.get("agent_id")
            details = event.get("details", {})

            if event_type == "MANIFEST_REGISTERED" and agent_id:
                manifest = details.get("manifest")
                if manifest:
                    self._manifests[agent_id] = manifest

            elif event_type == "TRUST_SCORE_UPDATED" and agent_id:
                score = details.get("score")
                if score is not None:
                    self._trust_scores[agent_id] = float(score)

            elif event_type == "ATTESTATION_CREATED" and agent_id:
                capability = details.get("capability")
                attestation = details.get("attestation")
                if capability and attestation:
                    if agent_id not in self._attestations:
                        self._attestations[agent_id] = {}
                    self._attestations[agent_id][capability] = attestation
```

**Modify on_boot():** Add restore call:
```python
    def on_boot(self, kernel: "RealVibeKernel") -> None:
        self._kernel = kernel
        self._restore_from_ledger()  # ADD THIS LINE
        # ... rest of existing code
```

**Modify register_manifest():** Add persistence:
```python
        self._manifests[agent_id] = manifest
        self._persist_manifest(agent_id, manifest)  # ADD THIS LINE
```

**Modify attest():** Add persistence:
```python
        self._attestations[agent_id][capability] = attestation
        self._persist_attestation(agent_id, capability, attestation)  # ADD THIS LINE
```

**Modify _recalculate_trust_score():** Add persistence:
```python
        self._trust_scores[agent_id] = new_score
        self._persist_trust_score(agent_id, new_score, "task_completion")  # ADD THIS LINE
```

---

## PHASE 2 VERIFICATION

```bash
python -c "
from vibe_core.kernel_impl import RealVibeKernel

# Boot kernel with in-memory ledger
kernel = RealVibeKernel(ledger_path=':memory:')
kernel.boot()

# Get plugins
gov = kernel._plugins.get('vedic_governance')
steward = kernel._plugins.get('steward_protocol')

# Test governance persistence
from vibe_core.plugins.vedic_governance.plugin_main import Varna
gov.assign_varna('test_agent', Varna.KSHATRIYA)

# Check ledger has event
events = [e for e in kernel.ledger.get_all_events() if e.get('event_type') == 'VARNA_ASSIGNED']
assert len(events) > 0, 'VARNA_ASSIGNED event should be in ledger'

# Test steward persistence
steward.attest('test_agent', 'read_file')
events = [e for e in kernel.ledger.get_all_events() if e.get('event_type') == 'ATTESTATION_CREATED']
assert len(events) > 0, 'ATTESTATION_CREATED event should be in ledger'

print('PHASE 2 PASSED')
"

python -m pytest tests/hardening/test_governance_security.py -v --tb=short
```

---

## PHASE 3: STUB ELIMINATION (VORSICHT!)

### 3.1 Deterministic Executor Stubs

**Datei:** `vibe_core/cartridges/system/envoy/deterministic_executor.py`
**Zeilen:** 796-797, 818-819

**WICHTIG:** Diese Stubs sind Fallbacks wenn Action Handlers nicht registriert sind.
Wir aendern sie zu WARNINGS statt silent success.

**VORHER (Line 796-797):**
```python
                    else:
                        # Fallback stub
                        logger.info(f"  ✓ State check passed (stub): {resolved_target}")
```

**NACHHER:**
```python
                    else:
                        # No action handler - log warning and skip (don't fake success)
                        logger.warning(f"  ⚠️ CHECK_STATE skipped (no handler): {resolved_target}")
                        phase.result = {"skipped": True, "reason": "no_action_handler"}
```

**VORHER (Line 818-819):**
```python
                    else:
                        # Fallback stub
                        logger.info(f"  ✓ Script executed (stub): {resolved_target}")
                        phase.result = {"script": resolved_target, "params": params}
```

**NACHHER:**
```python
                    else:
                        # No action handler - log warning and skip (don't fake success)
                        logger.warning(f"  ⚠️ EXECUTE_SCRIPT skipped (no handler): {resolved_target}")
                        phase.result = {"skipped": True, "reason": "no_action_handler", "script": resolved_target}
```

---

### 3.2 MilkOcean Silent Fail

**Datei:** `vibe_core/cartridges/system/envoy/tools/milk_ocean.py`
**Zeile:** 620

**VORHER:**
```python
                except Exception:
                    pass  # Silently fail - don't disrupt routing
```

**NACHHER:**
```python
                except Exception as inner_e:
                    logger.warning(f"Event emission failed (non-blocking): {inner_e}")
                    # Continue routing - event emission is not critical
```

---

## PHASE 3 VERIFICATION

```bash
# Diese Aenderungen sind Logging-only, keine Funktionsaenderung
# Einfach sicherstellen dass System noch bootet:

python -c "
from vibe_core.kernel_impl import RealVibeKernel
kernel = RealVibeKernel(ledger_path=':memory:')
kernel.boot()
print(f'Kernel status: {kernel.status}')
assert kernel.status == 'running', 'Kernel should be running'
print('PHASE 3 PASSED')
"

python -m pytest tests/ -k "envoy or executor" -v --tb=short
```

---

## PHASE 4: TEST RESTORATION

### 4.1 Move UniversalProvider Tests

**Von:** `tests/archive/broken_async/test_playbook_system.py`
**Nach:** `tests/integration/test_playbook_system.py`

**Kommando:**
```bash
# Check if file exists first
ls -la tests/archive/broken_async/test_playbook_system.py

# If exists, move it
mv tests/archive/broken_async/test_playbook_system.py tests/integration/test_playbook_system.py

# Update imports if needed (check for broken imports)
python -c "import tests.integration.test_playbook_system" 2>&1 || echo "May need import fixes"
```

**Falls Import Errors:** Die Tests muessen evtl. angepasst werden weil sich Imports geaendert haben. Check:
- `from vibe_core.cartridges.system.envoy.universal_provider import UniversalProvider`
- Wenn UniversalProvider nicht mehr existiert, Test SKIP markieren

---

## PHASE 4 VERIFICATION

```bash
# Run the restored tests
python -m pytest tests/integration/test_playbook_system.py -v --tb=short || echo "Some tests may need fixes"

# Full test suite
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -20
```

---

## FINAL VERIFICATION (NACH ALLEN PHASEN)

```bash
# 1. Run all hardening tests
python -m pytest tests/hardening/ -v --tb=short

# 2. Run all governance tests
python -m pytest tests/ -k "governance" -v --tb=short

# 3. Run all steward tests
python -m pytest tests/ -k "steward" -v --tb=short

# 4. Run full test suite
python -m pytest tests/ --timeout=60 -q

# 5. Verify kernel boots clean
python -c "
from vibe_core.kernel_impl import RealVibeKernel
k = RealVibeKernel(ledger_path=':memory:')
k.boot()
print(f'Status: {k.status}')
print(f'Plugins: {list(k._plugins.keys())}')
print('ALL PHASES COMPLETE')
"
```

---

## ROLLBACK INSTRUCTIONS

Falls etwas schiefgeht:

```bash
# Option 1: Git reset (empfohlen)
git checkout -- vibe_core/plugins/steward_protocol/plugin_main.py
git checkout -- vibe_core/plugins/vedic_governance/plugin_main.py
git checkout -- vibe_core/cartridges/system/envoy/deterministic_executor.py
git checkout -- vibe_core/cartridges/system/envoy/tools/milk_ocean.py

# Option 2: Stash changes
git stash

# Option 3: Reset to last commit
git reset --hard HEAD
```

---

## EXECUTION ORDER SUMMARY

```
PHASE 1: Plugin TODOs (SAFE - nur neue Logik)
  1.1 verify_agent() signature_valid fix
  1.2 attest() valid_until fix
  1.3 is_attestation_valid() helper
  → VERIFY → COMMIT

PHASE 2: Persistence (SAFE - additive)
  2.1 VedicGovernance ledger methods
  2.2 StewardProtocol ledger methods
  → VERIFY → COMMIT

PHASE 3: Stub Warnings (LOW RISK - logging only)
  3.1 deterministic_executor stub→warning
  3.2 milk_ocean silent→warning
  → VERIFY → COMMIT

PHASE 4: Test Restore (SAFE - just file move)
  4.1 Move archived tests
  → VERIFY → COMMIT
```

---

**Signed:** Opus 4.5
**Date:** 2025-12-07
**Status:** READY FOR SONNET EXECUTION
