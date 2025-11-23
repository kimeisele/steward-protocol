# ARCHIVIST Census Records

This directory contains daily census records from the ARCHIVIST.

## Purpose

The ARCHIVIST conducts daily census to track Agent City's population and activity.

## Record Format

Each census creates a JSON file:
```json
{
  "date": "2025-11-23",
  "population": 42,
  "events": 1337,
  "internal_agents": 8,
  "status": "active"
}
```

## Census Routine

- **Frequency**: Daily at 6:00 UTC
- **Metrics**: Citizens, events, internal agents
- **Action**: Record stats, commit to repository

**Part of the Autarky Protocol - The Clockwork City**
