# DEBUG Task Playbook

## Mission
Fix failing tests and restore green build status.

## Context Injection Points
- **Failing Tests:** ${tests.failing}
- **Error Messages:** ${tests.errors}
- **Last Commit:** ${git.last_commit}
- **Uncommitted Changes:** ${git.uncommitted}

## Workflow

1. **Identify Failures**
   - Review failing test output
   - Isolate root cause
   - Check recent changes

2. **Fix Issues**
   - Make minimal surgical changes
   - Follow existing patterns
   - Verify fix locally

3. **Validate**
   - Run failing tests
   - Run full test suite
   - Ensure no regressions

## Success Criteria
✅ All tests passing
✅ No new failures introduced
✅ Changes committed with clear message

## Anti-Slop Rules
❌ Don't refactor working code
❌ Don't add new features while debugging
❌ Don't skip running tests before claiming done
❌ Don't touch unrelated tests
