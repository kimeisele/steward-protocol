# OPUS-162: HARNESS Prüfstelle - Pattern Verification

> **Status**: IMPLEMENTING
> **Created**: 2025-12-20
> **Pattern**: Two-Layer Verification
> **Depends**: OPUS-160 (The Great Wiring)

---

## Preamble: Syntaktisch vs. Semantisch

Die `@HARNESS` Tags in OPUS-Dokumenten definieren erwartete Code-Patterns.
Aber "Pattern existiert" ≠ "System funktioniert".

OPUS-162 implementiert zwei Prüf-Ebenen:

1. **Syntaktisch (Pre-Commit)**: Schnell, Grep-basiert - sind die Patterns da?
2. **Semantisch (CI/Integration)**: Gründlich, Test-basiert - funktioniert der Flow?

## Two-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HARNESS Prüfstelle                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: SYNTACTIC (Pre-Commit)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Parse @HARNESS YAML from OPUS docs               │   │
│  │  • Grep for patterns in target files                │   │
│  │  • Block commit if patterns missing                 │   │
│  │  • Fast: <100ms                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Layer 2: SEMANTIC (CI/Integration Tests)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Test actual flow: event → handler → result       │   │
│  │  • Verify wiring is functional, not just present    │   │
│  │  • Run as part of test suite                        │   │
│  │  • Thorough: ~5s per test                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

### Layer 1: Syntactic (Pre-Commit Guard)

Add to `.githooks/pre-commit`:

```bash
# GUARD 8: HARNESS Pattern Verification
echo -n "  📋 HARNESS Pattern Verification... "

# Run harness_validator.py on staged OPUS docs
OPUS_DOCS=$(echo "$STAGED_FILES" | grep "docs/architecture/OPUS/.*\.md$" || true)

if [ -n "$OPUS_DOCS" ]; then
    HARNESS_OUTPUT=$(python -m vibe_core.governance.harness_validator $OPUS_DOCS 2>&1)
    HARNESS_EXIT=$?

    if [ $HARNESS_EXIT -ne 0 ]; then
        echo -e "${RED}BLOCKED${NC}"
        echo "$HARNESS_OUTPUT"
        exit 1
    fi
fi

echo -e "${GREEN}OK${NC}"
```

### Layer 2: Semantic (Integration Tests)

Located in `tests/integration/test_harness_semantic.py`:

```python
def test_genesis_flow_end_to_end():
    """SEMANTIC: New directory → MANAS → GenesisService → Compliant"""
    # Create non-compliant directory
    # Trigger MANAS perception
    # Verify GenesisService was called
    # Verify directory is now compliant
```

---

## HARNESS Tag Format

The format uses YAML inside an HTML comment:

```
<-- @ HARNESS  (note: without space between @ and HARNESS)
files:
  - path: path/to/file.py
    required: true   # File must exist
wiring:
  - pattern: "from module import Class"
    in: path/to/file.py
  - pattern: "class.*Foo"
    in: path/to/file.py
    regex: true      # Use regex matching
-- >
```

**Note**: The actual syntax uses `@HARNESS` without space.

---

## HARNESS Verification

<!-- @HARNESS
files:
  - path: vibe_core/governance/harness_validator.py
    required: true
  - path: tests/integration/test_harness_semantic.py
    required: true
wiring:
  - pattern: "def validate_harness"
    in: vibe_core/governance/harness_validator.py
-->

---

## Related Documents

- [OPUS-160: The Great Wiring](160-THE-GREAT-WIRING.md)
- [OPUS-161: Zollamt](161-ZOLLAMT.md)
