# Failure Report - Blind Regex Replacement

## What Happened

Automated regex replacement broke files by replacing numbers in wrong contexts:

**Example:**
```python
# BEFORE (correct)
optimal_debt = 0.37  # Decimal number

# AFTER (broken by blind replacement)
optimal_debt = 0.PARAMPARA  # Invalid syntax
```

## Root Cause

Regex pattern `\b37\b` matched "37" in "0.37" and replaced it, breaking decimal literals.

## Action Taken

**REVERTED** last 3 commits (batch 2 & 3)

System now at working state (after batch 1 only)

## Lesson

**NEVER** use blind regex replacement on Python code.

**CORRECT approach:**
1. Use AST parsing (libcst)
2. Context-aware replacement
3. Test EACH file before commit
4. Verify imports work

## Files Actually Fixed (Batch 1 - SAFE)

- substrate/byte.py (manual verification)
- adapters/routing.py (manual verification)
- substrate/fractal.py (manual verification)  
- substrate/lotus_radix.py (manual verification)

**Status:** 4 files fixed, verified working

## Next Steps

Use Kapila remedy framework (already exists) with proper AST parsing instead of regex.

