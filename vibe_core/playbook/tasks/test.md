# TEST Task Playbook

## Mission
Run test suite and verify code quality.

## Context Injection Points
- **Test Framework:** ${manifest.test_framework}
- **Uncommitted Changes:** ${git.uncommitted}
- **Last Test Status:** ${tests.status}

## Workflow

1. **Pre-Test Check**
   - Verify environment setup
   - Check dependencies installed
   - Review uncommitted changes

2. **Run Tests**
   - Execute full test suite
   - Check for failures
   - Review coverage if available

3. **Report**
   - Document test results
   - Identify any failures
   - Update session state

## Success Criteria
✅ All tests pass
✅ No environmental issues
✅ Results documented

## Anti-Slop Rules
❌ Don't skip failed tests
❌ Don't claim success without running
❌ Don't ignore warnings
❌ Don't modify tests to pass without fixing code
