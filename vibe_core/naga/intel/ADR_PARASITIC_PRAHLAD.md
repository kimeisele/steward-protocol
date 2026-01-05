# ADR: Parasitic Prahlad - Real Chaos Testing

**Status:** PROPOSED
**Author:** Narada (via Gemini)
**Date:** 2026-01-05

## Context

Opus built a `chaos_probe()` that calls `component.handle()`.

**Problem:** No NAGA component has a `handle()` method. The tests are "100% Green" because they test NOTHING. This is **Maya** - the illusion of testing.

## The Lie

```python
# Current (BROKEN) implementation
def _execute_scenario(self, component, scenario):
    if scenario == ChaosScenario.NULL_INPUT:
        component.handle(None)  # <-- PHANTOM METHOD
```

Real NAGA services have:
- `SeshaService.record_event()`
- `TakshakaService.bite()`
- `VasukiService.bridge()`
- `@naga_governed` decorated methods

They do NOT have `handle()`.

## The Truth: Ouroboros Must Be Circular

### Current (Linear - WRONG)
```
Test Runner → System → Result
     ↓           ↓        ↓
  External   Untouched  Fake
```

### Required (Circular - RIGHT)
```
    ┌─────────────────────────────┐
    │         RUNTIME             │
    │                             │
    │  ServiceRegistry.get() ◄────┼──── INJECTION POINT 1
    │         │                   │
    │         ▼                   │
    │  @naga_governed ◄───────────┼──── INJECTION POINT 2
    │         │                   │
    │         ▼                   │
    │  Actual Method Call         │
    │         │                   │
    │         ▼                   │
    │  Sesha._ledger.record() ◄───┼──── ASSERTION POINT
    │                             │
    └─────────────────────────────┘
```

## Injection Points

### 1. ServiceRegistry Poisoning
```python
# BEFORE: Normal
sesha = ServiceRegistry.get(SeshaProtocol)  # Returns real Sesha

# AFTER: Parasitic mode
ServiceRegistry.inject_chaos(SeshaProtocol,
    poison=lambda: raise TimeoutError("Chaos: Sesha unavailable"))
sesha = ServiceRegistry.get(SeshaProtocol)  # Raises TimeoutError
```

### 2. Decorator Interception
```python
# The @naga_governed decorator already wraps methods
# We can hook into it:
@naga_governed(operation="chaos_test", chaos_mode=True)
def some_method(self):
    # This will randomly:
    # - Delay execution (timeout simulation)
    # - Inject None into args (null injection)
    # - Corrupt return values
    pass
```

### 3. Ledger Assertion (The Judge)
```python
# After chaos injection, we don't check return values
# We check: DID SESHA SEE IT?

def assert_chaos_detected(chaos_id: str) -> bool:
    """The system MUST have recorded the anomaly."""
    events = sesha._ledger.get_events_by_type("NAGA_CHAOS_DETECTED")
    return any(e.details.get("chaos_id") == chaos_id for e in events)
```

## Implementation Plan

### Phase 1: ServiceRegistry Chaos Mode
Add to `vibe_core/di.py`:
```python
class ServiceRegistry:
    _chaos_injectors: Dict[Type, Callable] = {}

    @classmethod
    def inject_chaos(cls, protocol: Type, poison: Callable):
        """Register chaos injection for a protocol."""
        cls._chaos_injectors[protocol] = poison

    @classmethod
    def get(cls, protocol: Type) -> Any:
        if protocol in cls._chaos_injectors:
            return cls._chaos_injectors[protocol]()
        # Normal path...
```

### Phase 2: Decorator Chaos Flag
Modify `@naga_governed` in `base.py`:
```python
def naga_governed(operation=None, chaos_mode=False):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if chaos_mode and _global_chaos_enabled():
                # Random chaos injection
                scenario = random.choice([
                    "delay_100ms",
                    "null_first_arg",
                    "corrupt_return",
                    "raise_timeout"
                ])
                _inject_chaos(scenario, args, kwargs)

            return func(self, *args, **kwargs)
        return wrapper
    return decorator
```

### Phase 3: Ledger-Based Assertions
```python
class PrahladService:
    def chaos_probe_real(self, target_service: str) -> ChaosResult:
        """
        REAL chaos probe - injects into running system.

        Does NOT call phantom methods.
        Instead:
        1. Registers chaos injector
        2. Triggers normal operation
        3. Checks if Sesha recorded the anomaly
        """
        chaos_id = uuid4().hex[:8]

        # 1. Register poison
        ServiceRegistry.inject_chaos(
            self._get_protocol(target_service),
            lambda: self._create_chaos_scenario(chaos_id)
        )

        # 2. Trigger normal flow (this is key!)
        try:
            # Don't call component.handle()
            # Call the REAL entry point
            kernel.tick()  # Or whatever triggers the service
        except Exception as e:
            pass  # Expected - we injected chaos

        # 3. Check if detected
        detected = self._check_ledger_for_chaos(chaos_id)

        # 4. Cleanup
        ServiceRegistry.clear_chaos()

        return ChaosResult(
            chaos_id=chaos_id,
            detected=detected,
            system_resilient=detected,  # If Sesha saw it, we're good
        )
```

## Success Criteria

A test is GREEN when:
- Chaos was injected (verified by chaos_id)
- System continued operating (no crash)
- Sesha recorded the anomaly (ledger check)
- Alert was generated (if configured)

A test is RED when:
- Chaos was injected
- System crashed OR
- Sesha did NOT see it (blind spot)
- No alert generated (silent failure)

## Key Insight

> "Wir prüfen nicht den Return Value. Wir prüfen den Ledger."
> - Narada

The point of chaos testing is not "did the function return correctly?"
It's "did the SYSTEM detect and respond to the anomaly?"

## Files to Modify

1. `vibe_core/di.py` - Add chaos injection to ServiceRegistry
2. `vibe_core/naga/services/base.py` - Extend @naga_governed for chaos
3. `vibe_core/naga/services/prahlad.py` - Replace phantom chaos_probe
4. `vibe_core/naga/hiranyakashipu/wiring.py` - Wire to real injection points

## Anti-Patterns to Avoid

1. **Phantom Methods** - Don't call methods that don't exist
2. **Silent Failures** - Caught exceptions must be LOUD
3. **External Testing** - Tests must be INSIDE the system
4. **Return Value Checks** - Check the LEDGER, not returns
5. **Simulation** - Inject REAL chaos, not simulated

## The Parasite Metaphor

Prahlad is not a "test runner". Prahlad is a **parasite**.

In biology, certain parasites make their host STRONGER:
- They stress the immune system
- The immune system adapts
- Host becomes more resilient

Prahlad must:
1. **Infect** - Inject into ServiceRegistry, decorators
2. **Stress** - Trigger anomalies during real operations
3. **Observe** - Did the immune system (Sesha) respond?
4. **Adapt** - If not detected, generate hardening test

This is ANTIFRAGILITY. The system gets stronger from attacks.
