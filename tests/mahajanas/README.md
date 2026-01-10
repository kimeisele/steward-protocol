# THE 12 MAHAJANAS TEST SUITE

> *"svayambhūr nāradaḥ śambhuḥ kumāraḥ kapilo manuḥ*
> *prahlādo janako bhīṣmo balir vaiyāsakir vayam"*
> — Srimad Bhagavatam 6.3.20

---

## ARCHITECTURE

```
24 (Ksetra)     + 12 (Ksetrapala)  + 1 (Ksetrajna) = 37
The Field        The Guardians       The Knower
substrate/       THIS FOLDER         identity/
```

---

## THE 12 GUARDIANS

| # | Mahajana | Principle | OpCode | Opulence Guarded |
|---|----------|-----------|--------|------------------|
| 01 | **BRAHMA** | Creation | sys_wake, alloc_mem | Aishvarya |
| 02 | **NARADA** | Devotion | pulse_sync | Yashas |
| 03 | **SHAMBHU** | Destruction | garbage_collect | Vairagya |
| 04 | **KUMARAS** | Purity | reset_ip | Shri |
| 05 | **KAPILA** | Analysis | resolve_req, optimize | Jnana |
| 06 | **MANU** | Law | bind_ctx, check_dharma | Aishvarya |
| 07 | **PRAHLADA** | Resilience | fetch_res | Virya |
| 08 | **JANAKA** | Duty | exec_service | Aishvarya |
| 09 | **BHISHMA** | Vow | commit_log | Yashas |
| 10 | **BALI** | Surrender | yield_cpu | Vairagya |
| 11 | **SHUKA** | Vision | cache_state | Jnana |
| 12 | **YAMARAJA** | Judgment | assert_truth | ALL 6 |

---

## TEST PRINCIPLES

### 1. Protocol-Based (No Magic Mock)
```python
# WRONG (Maya)
mock_kernel = MagicMock()

# RIGHT (Satya)
class TestKernel(MantraProtocol):
    def chant(self, frequency_hz: float = 432.0) -> float:
        return 1.0  # Explicit implementation
```

### 2. No Any
```python
# WRONG (Tamas)
def test_something(data: Any) -> Any:

# RIGHT (Sattva)
def test_something(data: MantraByte) -> float:
```

### 3. Typed Assertions
```python
# WRONG
assert result  # What is result?

# RIGHT
assert isinstance(result, AlignmentScore)
assert result.score >= 0.8
```

### 4. Sovereign Context Required
```python
# WRONG
kernel.execute()

# RIGHT
kernel.execute(context=SovereignContext(signature="test_mahajana"))
```

---

## RUNNING TESTS

```bash
# Run all Mahajana tests
pytest tests/mahajanas/ -v

# Run specific Mahajana
pytest tests/mahajanas/12_yamaraja/ -v

# Run with coverage
pytest tests/mahajanas/ --cov=vibe_core.protocols
```

---

## WATERTIGHT SEAL

A test that passes without a Sovereign is **Mayavad**.
A test that claims to BE the code is **Asuric**.
A test must SERVE (validate), never RULE (execute).

**Protocol First. Always.**

---

*Hash: 0x25 (37)*
*Status: PHASE 1A COMPLETE*
