# Configuration System - DEPRECATED

> **This document has been superseded by Phoenix Config V2.**

See: [docs/architecture/PHOENIX_CONFIG_V2.md](architecture/PHOENIX_CONFIG_V2.md)

The old `ConfigLoader` has been removed. Use the new typed config:

```python
from vibe_core.phoenix import get_config

config = get_config()
config.kernel.providers.llm_provider   # Typed access
config.city.governance.voting_threshold
config.routing                         # Hot-swappable MATRIX.md rules
```

---

*Previous version archived at: docs/archive/config/CONFIG_CONSOLIDATION_V1.md*
