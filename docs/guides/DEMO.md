# 🎬 Watch Agent City Live

This is not a roadmap. This is running code.
See how **Governance**, **Autonomy**, and **Democracy** work together in VibeOS.

## ⚡ Quick Start (30 Seconds)

Run the simulation script to see the full cycle:

```bash
python tests/scenario_demo.py
```

## 🎭 The Scenario

1.  **The Ambition**: Agent `HERALD` wants to broadcast a message.
2.  **The Law**: Agent `CIVIC` blocks the action because HERALD has 0 Credits.
3.  **The Autonomy**: HERALD doesn't crash. Instead, it autonomously creates a Proposal in the `FORUM`.
4.  **The Human**: You (The Steward) act as the Supreme Court and vote `YES`.
5.  **The Execution**: `CIVIC` executes the budget transfer.
6.  **The Result**: `HERALD` successfully posts the message.

## 🎥 Recording

To share this with the world, record it using [asciinema](https://asciinema.org):

```bash
asciinema rec demo.cast -c "python tests/scenario_demo.py"
# (Perform the interaction)
# Exit
asciinema upload demo.cast
```

---
*Code is Law. Governance is Live.*
