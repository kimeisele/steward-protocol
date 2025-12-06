# Config Section Golden Template

Copy this folder to create a new Phoenix Config Section.

## Quick Start

```bash
# 1. Copy to phoenix sections directory
cp -r docs/templates/config_section vibe_core/phoenix/sections/my_section

# 2. Edit manifest.json
#    - Change "id" to "my_section"
#    - Change "config_file" to "config/my_section.yaml"

# 3. Edit section_main.py
#    - Rename MySectionConfig class
#    - Add your config fields
#    - Implement from_dict(), to_dict(), validate()

# 4. Create config file
cat > config/my_section.yaml << 'EOF'
# My Section Configuration
enabled: true
debug: false

nested:
  setting_a: "value"
  setting_b: 100
EOF

# 5. Test it
python -c "
from vibe_core.phoenix import get_config
config = get_config()
print(config.get_section('my_section'))
"
```

## File Structure

```
my_section/
├── __init__.py       # Package export
├── manifest.json     # Section metadata
├── section_main.py   # Config dataclass
└── README.md         # This file (optional)
```

## Required Protocol

Your config class MUST have:

```python
@dataclass
class MySectionConfig:
    section_id: str = "my_section"   # Must match manifest.json id
    source_file: str = "my_section.yaml"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MySectionConfig":
        """Create from YAML data."""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        ...

    def validate(self) -> List[str]:
        """Return list of errors (empty = valid)."""
        ...
```

## VEDA-4 Pattern

Sections follow the same pattern as everything else:

1. **SHABDA**: SectionLoader scans `vibe_core/phoenix/sections/`
2. **ARTHA**: Loads `manifest.json`, imports `section_main.py`
3. **PRATYAYA**: Calls `validate()` on loaded config
4. **KARMA**: Returns typed config instance via `from_dict()`

## See Also

- [PHOENIX_CONFIG_FRACTAL.md](../../architecture/PHOENIX_CONFIG_FRACTAL.md) - Full architecture
- [CLI Section](../../../vibe_core/phoenix/sections/cli/) - Working example
