# DOCUMENT Task Playbook

## Mission
Update documentation to reflect current state.

## Context Injection Points
- **Recent Changes:** ${git.recent_commits}
- **Documentation Path:** ${manifest.docs_path}
- **Target Audience:** ${session.doc_audience}

## Workflow

1. **Identify Scope**
   - What changed?
   - What needs updating?
   - Who's the audience?

2. **Update Docs**
   - Fix outdated content
   - Add new sections
   - Update examples

3. **Verify**
   - Check links work
   - Validate code examples
   - Ensure clarity

## Success Criteria
✅ Documentation is current
✅ Examples work
✅ Clear and concise
✅ Links validated

## Anti-Slop Rules
❌ Don't write misleading docs
❌ Don't skip testing examples
❌ Don't use outdated information
❌ Don't ignore style guide
