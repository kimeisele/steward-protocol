# Diplomatic Bag

This directory contains draft invitations from **The Envoy** awaiting human approval.

## Purpose

The Envoy searches GitHub for high-quality AI agent projects and drafts personalized, respectful invitations. All drafts are saved here for human review before posting.

**CRITICAL**: The Envoy NEVER auto-posts. Human approval is required.

## Workflow

1. **The Envoy runs**: `python envoy/tools/diplomacy_tool.py`
2. **Drafts created**: Saved as JSON files in this directory
3. **Human reviews**: Read the invitation text
4. **Human approves**: Manually post the invitation on GitHub
5. **Archive**: Move approved drafts to `diplomatic_bag/archive/`

## Draft Format

Each draft is a JSON file containing:
- `repository`: Target project information
- `analysis`: Project analysis summary
- `invitation`: Personalized invitation text
- `created_at`: Timestamp
- `status`: "pending_approval"

## Example

```json
{
  "repository": {
    "name": "example/ai-agent",
    "stars": 250,
    "url": "https://github.com/example/ai-agent"
  },
  "invitation": "Greetings, Architect...",
  "status": "pending_approval"
}
```

## Philosophy

Quality over quantity. Respect over hype. Wisdom over noise.

*The Envoy represents Agent City's commitment to thoughtful growth.*
