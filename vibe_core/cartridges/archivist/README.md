# The Archivist - Knowledge Base Builder

**Version:** 1.0.0
**Author:** Vibe Agency
**Status:** ARCH-050 - First Cartridge Release

## Overview

The Archivist is the first "app" (cartridge) for Vibe OS. It demonstrates how Vibe OS moves beyond a kernel to become a useful experience system.

**Core Problem:** Users have dozens of documents but no organized way to search and discover information.

**Solution:** Automatically scan a folder, extract and summarize documents, build a searchable knowledge index.

## Key Features

✅ **Offline-First:** Works completely without APIs (SmartLocalProvider)
✅ **Multi-Format:** Supports MD, TXT, and PDF documents
✅ **Smart Summarization:** Uses offline LLM for intelligent summaries
✅ **Zero Configuration:** Just point it at a folder
✅ **Indexed Output:** Generates JSON knowledge index for search/discovery

## Usage

### Command Line

```bash
# Interactive mode
./bin/vibe run --cartridge archivist

# Or direct invocation (future)
uv run apps/agency/cli.py --cartridge archivist --action build-index --folder /path/to/docs
```

### Python API

```python
from vibe_core.cartridges import get_default_cartridge_registry

registry = get_default_cartridge_registry()
archivist = registry.get_cartridge("archivist")

# Scan directory
docs = archivist.scan_directory("/path/to/documents")
print(f"Found {len(docs)} documents")

# Build knowledge index
index = archivist.build_index(
    folder_path="/path/to/documents",
    output_path="workspace/inbox/knowledge_index.json"
)

print(f"Indexed {len(index['documents'])} documents")
```

## Architecture

```
ArchivistCartridge (extends CartridgeBase)
├── scan_directory(path)      → Discover all documents
├── extract_text(file_path)   → Get document content (Sense: ReadFile)
├── summarize(text)           → Generate summary (offline LLM)
└── build_index(folder)       → Full indexing workflow

Playbook: build_knowledge_base.yaml
├── scan         → Find documents (ListDirectory sense)
├── validate     → Ensure we have documents
├── process      → Extract & summarize (ReadFile sense)
└── report       → Generate index
```

## Design Philosophy

The Archivist embodies Vibe OS principles:

1. **Single Responsibility:** Solves one problem (knowledge indexing) really well
2. **Offline-First:** Uses SmartLocalProvider—works completely offline
3. **Discoverable:** Registrable in CartridgeRegistry
4. **Composable:** Can be called by other cartridges
5. **Stateless:** Can be re-run multiple times safely

## Demonstration: The "Offline First" Story

User has 50 PDFs about the company's architecture. Without The Archivist:

```
❌ User must manually read all PDFs
❌ Requires external APIs to summarize
❌ No searchable index
❌ Knowledge is trapped in files
```

With The Archivist:

```
✅ ./bin/vibe run --cartridge archivist --folder ~/Documents/Architecture/
✅ Offline: No API calls needed
✅ 2 minutes later: Complete knowledge index in workspace/inbox/
✅ Knowledge is discoverable, searchable, indexed
```

## Future Enhancements

- **v1.1:** Add search API on top of index
- **v1.2:** Support more formats (DOCX, PPTX)
- **v1.3:** Integration with SmartSearch for intelligent queries
- **v2.0:** Real-time index updates as documents change

## Related Cartridges

- **Researcher** (planned): Query knowledge bases with AI
- **Refactorer** (planned): Refactor code based on knowledge
- **Analyst** (planned): Analyze document collections

## Testing

```bash
# Run Archivist tests
./bin/vibe test --domain cartridges

# Or directly
pytest tests/cartridges/test_archivist.py -v
```

## See Also

- [ARCH-050: Workspace Protocol & Cartridge System](../../docs/ARCH-050.md)
- [CartridgeBase](../base.py)
- [CartridgeRegistry](../registry.py)
