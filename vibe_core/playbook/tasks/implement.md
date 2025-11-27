# IMPLEMENT Task Playbook

## Mission
Code a new feature or component following project standards.

## Context Injection Points
- **Feature Request:** ${session.backlog_item}
- **Project Phase:** ${session.phase}
- **Project Type:** ${manifest.project_type}
- **Current Branch:** ${git.branch}

## Workflow

1. **Plan**
   - Understand requirements
   - Identify affected components
   - Check existing patterns

2. **Implement**
   - Write minimal code
   - Follow project conventions
   - Add necessary tests

3. **Validate**
   - Run new tests
   - Run full test suite
   - Manual verification if needed

4. **Document**
   - Update relevant docs
   - Add code comments where needed
   - Update CHANGELOG if applicable

## Success Criteria
✅ Feature works as specified
✅ Tests pass (including new ones)
✅ Code follows project patterns
✅ Documentation updated

## Anti-Slop Rules
❌ Don't over-engineer
❌ Don't skip testing
❌ Don't ignore existing conventions
❌ Don't leave debug code
