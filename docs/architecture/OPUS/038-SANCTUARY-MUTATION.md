# OPUS-038: Operation Sanctuary - Mutation Testing Protocol

**Status:** PROPOSED
**Author:** Claude (Opus 4.5) + Senior Partner
**Date:** 2025-12-14
**Dependencies:** OPUS-036 (Diamond Protocol), OPUS-037 (Diamond Handlers)

---

## Executive Summary

Operation Sanctuary extends the Diamond Protocol to **legacy code** through **Mutation Testing**.

The Diamond Protocol (OPUS-036/037) works for **new code**:
- Generate TEST first → RED Gate (test must fail) → Generate CODE → GREEN Gate (test must pass)

But for **legacy code**, the code already exists. We can't use the RED Gate directly.

**Solution:** Instead of removing code (impossible), we **sabotage** it (mutation) to prove the test can detect errors.

---

## The Platinum Flaw (Problem Statement)

### Diamond Protocol (New Code) - SECURE ✅
```
1. Code doesn't exist
2. Test generated → MUST FAIL (RED Gate)
3. Code generated → MUST PASS (GREEN Gate)
4. If test passes without code → REJECTED (trivial test)
```

### Legacy Code Testing - VULNERABLE ❌
```
1. Code EXISTS
2. Test generated → immediately PASSES
3. No way to prove test isn't trivially true
4. "assert True" would pass → 100% fake coverage
```

---

## The Mutation Protocol (Solution)

### Core Insight
> "If you can't remove the code, sabotage it."

A **good test** must detect when code is **broken**.
If a test still passes after we inject bugs → the test is useless.

### The Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  MUTATION PROTOCOL (Legacy Code Testing)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: ANALYZE                                               │
│  ├── Read legacy_file.py                                        │
│  └── Identify testable functions/classes                        │
│                                                                 │
│  Phase 2: DRAFT TEST                                            │
│  ├── Generate test_legacy.py                                    │
│  └── Test covers critical paths                                 │
│                                                                 │
│  Phase 3: GREEN GATE (Original Code)                            │
│  ├── Run: pytest test_legacy.py                                 │
│  ├── Expected: PASS ✅                                          │
│  └── Proves: Test works with current implementation             │
│                                                                 │
│  Phase 4: MUTATE (The Sabotage)                                 │
│  ├── Create mutated copy of legacy_file.py                      │
│  ├── Inject controlled bugs (mutation operators)                │
│  └── Examples:                                                  │
│      - if x > 0  →  if x < 0                                    │
│      - return a  →  return None                                 │
│      - x + y     →  x - y                                       │
│                                                                 │
│  Phase 5: RED GATE (Mutated Code)                               │
│  ├── Run: pytest test_legacy.py (against mutant)                │
│  ├── Expected: FAIL ✅ (test killed the mutant)                 │
│  └── If PASS: Test is USELESS (can't detect bugs)               │
│                                                                 │
│  Phase 6: VERDICT                                               │
│  ├── GREEN + RED = Test is VALID → Commit                       │
│  ├── GREEN + !RED = Test is WEAK → Regenerate                   │
│  └── !GREEN = Test is BROKEN → Debug                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mutation Operators

### Tier 1: Comparison Mutations (High Signal)
| Original | Mutation | Operator Name |
|----------|----------|---------------|
| `x > y`  | `x < y`  | GT_TO_LT |
| `x >= y` | `x <= y` | GTE_TO_LTE |
| `x == y` | `x != y` | EQ_TO_NE |
| `x < y`  | `x > y`  | LT_TO_GT |
| `x <= y` | `x >= y` | LTE_TO_GTE |
| `x != y` | `x == y` | NE_TO_EQ |

### Tier 2: Arithmetic Mutations (Medium Signal)
| Original | Mutation | Operator Name |
|----------|----------|---------------|
| `x + y`  | `x - y`  | ADD_TO_SUB |
| `x - y`  | `x + y`  | SUB_TO_ADD |
| `x * y`  | `x / y`  | MUL_TO_DIV |
| `x / y`  | `x * y`  | DIV_TO_MUL |

### Tier 3: Return Mutations (High Signal)
| Original | Mutation | Operator Name |
|----------|----------|---------------|
| `return x` | `return None` | RET_TO_NONE |
| `return True` | `return False` | RET_TRUE_TO_FALSE |
| `return False` | `return True` | RET_FALSE_TO_TRUE |
| `return x` | `return 0` | RET_TO_ZERO |
| `return x` | `return ""` | RET_TO_EMPTY |

### Tier 4: Logical Mutations (Medium Signal)
| Original | Mutation | Operator Name |
|----------|----------|---------------|
| `x and y` | `x or y` | AND_TO_OR |
| `x or y` | `x and y` | OR_TO_AND |
| `not x` | `x` | REMOVE_NOT |

### Tier 5: Statement Mutations (High Signal)
| Original | Mutation | Operator Name |
|----------|----------|---------------|
| `statement` | `pass` | STMT_TO_PASS |
| `if cond:` | `if True:` | COND_TO_TRUE |
| `if cond:` | `if False:` | COND_TO_FALSE |

---

## Implementation Strategy

### Option A: AST-Based Mutation (Recommended)
```python
import ast

class MutationVisitor(ast.NodeTransformer):
    def visit_Compare(self, node):
        # Mutate comparison operators
        if isinstance(node.ops[0], ast.Gt):
            node.ops[0] = ast.Lt()
        return node
```

**Pros:**
- Precise mutations
- Preserves code structure
- Can target specific nodes

**Cons:**
- More complex implementation
- May miss string-based patterns

### Option B: String-Based Mutation (Simpler)
```python
def mutate_comparisons(code: str) -> str:
    return code.replace(" > ", " < ")
```

**Pros:**
- Simple to implement
- Fast

**Cons:**
- May create invalid syntax
- Can mutate strings/comments accidentally

### Decision: **AST-Based** for precision, with String-Based fallback for edge cases.

---

## Circuit Design: `sanctuary_inquisitor.yaml`

```yaml
circuit:
  id: SANCTUARY_INQUISITOR
  name: "Operation Sanctuary - Legacy Code Inquisitor"
  version: "1.0.0"
  entry_state: "scan_untested_files"

  config:
    target_dirs:
      - "vibe_core/"
      - "plugins/"
    exclude_patterns:
      - "**/tests/**"
      - "**/__pycache__/**"
    min_mutation_kill_rate: 0.8  # 80% of mutants must be killed
    max_mutants_per_file: 10

  states:
    scan_untested_files:
      # Find .py files without corresponding test_*.py

    analyze_file:
      # Parse AST, identify testable units

    generate_test:
      # Create test file for legacy code

    green_gate_original:
      # Test must PASS against original code

    generate_mutants:
      # Create N mutated versions

    red_gate_mutants:
      # Test must FAIL against each mutant

    calculate_kill_rate:
      # mutants_killed / total_mutants >= threshold?

    verdict:
      # Commit test if kill rate sufficient
```

---

## Handler Design: `mutation_handlers.py`

```python
class MutationHandlers:
    """Handlers for the Mutation Protocol."""

    async def generate_mutants(self, params: Dict) -> Dict:
        """Generate mutated versions of source code."""

    async def mutation_red_gate(self, params: Dict) -> Dict:
        """
        Run test against mutant.
        SUCCESS = test FAILS (mutant killed)
        FAILURE = test PASSES (mutant survived = weak test)
        """

    async def calculate_kill_rate(self, params: Dict) -> Dict:
        """Calculate percentage of killed mutants."""
```

---

## Metrics & KPIs

| Metric | Target | Description |
|--------|--------|-------------|
| Mutation Kill Rate | ≥ 80% | % of mutants killed by tests |
| Coverage Delta | > 0% | New lines covered by generated tests |
| False Positive Rate | < 5% | Tests that pass trivially |
| Files Sanctified | 100% | All legacy files with valid tests |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Mutation creates invalid syntax | Medium | AST validation before running |
| Infinite mutants (combinatorial explosion) | High | Cap at N mutants per file |
| Test generation hallucinates | Medium | GREEN Gate catches broken tests |
| Performance (slow mutation runs) | Medium | Parallel execution, caching |

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Create `mutation_handlers.py`
- [ ] Implement AST-based mutation engine
- [ ] Implement Tier 1 operators (comparisons)

### Phase 2: Integration
- [ ] Create `sanctuary_inquisitor.yaml` circuit
- [ ] Wire handlers to kernel_tick.py
- [ ] Add mutation_red_gate logic

### Phase 3: Validation
- [ ] Break Test 3.0 (validate mutation detection)
- [ ] Run on sample legacy file
- [ ] Verify kill rate calculation

### Phase 4: Deployment
- [ ] Scan entire vibe_core/ for untested files
- [ ] Generate tests with mutation validation
- [ ] Track coverage improvement

---

## Success Criteria

**Operation Sanctuary is complete when:**

1. ✅ Every `.py` file in `vibe_core/` has a corresponding test
2. ✅ Every test achieves ≥80% mutation kill rate
3. ✅ No trivial tests (`assert True`) can pass the Mutation Protocol
4. ✅ System can self-heal by regenerating weak tests

---

## References

- [Mutation Testing Wikipedia](https://en.wikipedia.org/wiki/Mutation_testing)
- [mutmut - Python Mutation Testing](https://github.com/boxed/mutmut)
- [cosmic-ray - Mutation Testing](https://github.com/sixty-north/cosmic-ray)
- OPUS-036: Diamond Protocol (TDD Law)
- OPUS-037: Diamond Handlers (TDD Enforcement)

---

## Appendix: The Philosophy

> "A test that cannot detect errors is not a test. It is a lie."

The Diamond Protocol ensures new code is born with discipline.
The Mutation Protocol ensures legacy code is reborn with proof.

Together, they form the **Platinum Standard**:
- New Code: RED → GREEN
- Legacy Code: GREEN → MUTATE → RED

**No code escapes. No test lies. The system becomes mathematically proven.**
