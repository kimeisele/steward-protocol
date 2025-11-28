"""SCRIBE Documentation Generation Tools"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name in ('CartridgeIntrospector', 'ScriptIntrospector', 'ConfigIntrospector'):
        from .introspector import CartridgeIntrospector, ScriptIntrospector, ConfigIntrospector
        return {'CartridgeIntrospector': CartridgeIntrospector,
                'ScriptIntrospector': ScriptIntrospector,
                'ConfigIntrospector': ConfigIntrospector}[name]
    elif name == 'AgentsRenderer':
        from .agents_renderer import AgentsRenderer
        return AgentsRenderer
    elif name == 'CitymapRenderer':
        from .citymap_renderer import CitymapRenderer
        return CitymapRenderer
    elif name == 'HelpRenderer':
        from .help_renderer import HelpRenderer
        return HelpRenderer
    elif name == 'ReadmeRenderer':
        from .readme_renderer import ReadmeRenderer
        return ReadmeRenderer
    elif name == 'IndexRenderer':
        from .index_renderer import IndexRenderer
        return IndexRenderer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'CartridgeIntrospector',
    'ScriptIntrospector',
    'ConfigIntrospector',
    'AgentsRenderer',
    'CitymapRenderer',
    'HelpRenderer',
    'ReadmeRenderer',
    'IndexRenderer',
]
