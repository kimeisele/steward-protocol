#!/usr/bin/env python3
"""
The Archivist - ARCH-050: First Cartridge

A specialized knowledge base builder that:
1. Reads all documents (PDF, MD, TXT) in a folder
2. Extracts and summarizes content
3. Builds an indexed knowledge base
4. Enables offline-first knowledge discovery

Use Case:
  "I have 50 PDFs about our architecture. Build me a searchable knowledge base."

Demonstration:
  - Uses new "Senses" (ListDirectory, ReadFile)
  - 100% offline capability (SmartLocalProvider)
  - Generates structured knowledge artifacts
  - Foundation for future agents (Researchers, Analysts, etc.)

The Archivist is the proof that Vibe OS is not just a kernel—it's an
experience system that ships with useful apps.
"""

import json
import logging
from pathlib import Path
from typing import Any

from vibe_core.cartridges.base import CartridgeBase

logger = logging.getLogger(__name__)


class ArchivistCartridge(CartridgeBase):
    """
    The Archivist - Knowledge Base Builder for Vibe OS.

    Capabilities:
    1. scan_directory(path) → List all documents
    2. extract_text(file_path) → Get document content
    3. summarize(text, max_length=500) → Generate summary (offline LLM)
    4. build_index(folder_path) → Build complete knowledge base
    """

    name = "archivist"
    version = "1.0.0"
    description = "Knowledge base builder - reads documents and generates searchable index"
    author = "Vibe Agency"

    def __init__(self, vibe_root: Path | None = None):
        """Initialize the Archivist cartridge."""
        super().__init__(vibe_root=vibe_root)

        # Archivist-specific configuration
        self.supported_formats = [".md", ".txt", ".pdf"]
        self.max_document_size = 10 * 1024 * 1024  # 10MB

        logger.info("🗂️ The Archivist initialized - Ready to catalog knowledge")

    def scan_directory(self, folder_path: str) -> list[dict[str, Any]]:
        """
        Scan a directory and list all supported documents.

        Args:
            folder_path: Path to scan

        Returns:
            List of document metadata dicts
        """
        folder = Path(folder_path)

        if not folder.exists():
            logger.error(f"❌ Folder not found: {folder_path}")
            return []

        if not folder.is_dir():
            logger.error(f"❌ Not a directory: {folder_path}")
            return []

        documents = []

        for file_path in folder.rglob("*"):
            if not file_path.is_file():
                continue

            # Check supported format
            if file_path.suffix.lower() not in self.supported_formats:
                continue

            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_document_size:
                logger.warning(f"⚠️ Skipping oversized file: {file_path} ({file_size} bytes)")
                continue

            documents.append(
                {
                    "path": str(file_path),
                    "name": file_path.name,
                    "format": file_path.suffix.lower(),
                    "size_bytes": file_size,
                }
            )

        logger.info(f"📊 Found {len(documents)} documents in {folder_path}")
        return sorted(documents, key=lambda x: x["path"])

    def extract_text(self, file_path: str) -> str | None:
        """
        Extract text from a document.

        Currently supports: TXT, MD
        PDF support can be added with pypdf library.

        Args:
            file_path: Path to document

        Returns:
            Text content or None if extraction fails
        """
        file = Path(file_path)

        if not file.exists():
            logger.error(f"❌ File not found: {file_path}")
            return None

        try:
            # TXT and MD files
            if file.suffix.lower() in [".txt", ".md"]:
                with open(file, encoding="utf-8") as f:
                    return f.read()

            # PDF support (requires pypdf)
            if file.suffix.lower() == ".pdf":
                try:
                    import PyPDF2

                    text = []
                    with open(file, "rb") as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text.append(page.extract_text())
                    return "\n".join(text)
                except ImportError:
                    logger.warning("⚠️ PyPDF2 not installed. PDF extraction unavailable.")
                    return None

        except Exception as e:
            logger.error(f"❌ Failed to extract text from {file_path}: {e}")
            return None

        return None

    def summarize(self, text: str, max_length: int = 500) -> str:
        """
        Generate a summary of text using the offline LLM provider.

        Args:
            text: Text to summarize
            max_length: Maximum summary length

        Returns:
            Summary string
        """
        if not self.llm_provider:
            logger.warning("⚠️ LLM provider not available. Returning first 500 chars.")
            return text[:500]

        try:
            # Use offline LLM (SmartLocalProvider)
            summary = self.llm_provider.generate(
                prompt=f"Summarize the following text in {max_length} characters or less:\n\n{text[:2000]}",
                max_tokens=int(max_length / 4),
            )

            return summary.strip() if summary else text[:max_length]

        except Exception as e:
            logger.warning(f"⚠️ Summarization failed: {e}. Using text truncation.")
            return text[:max_length]

    def build_index(self, folder_path: str, output_path: str | None = None) -> dict[str, Any]:
        """
        Build a complete knowledge index from all documents in a folder.

        Args:
            folder_path: Path to documents
            output_path: Where to save the index (optional)

        Returns:
            Index structure with all documents and summaries
        """
        # Scan directory
        documents = self.scan_directory(folder_path)

        if not documents:
            logger.warning(f"⚠️ No documents found in {folder_path}")
            return {"status": "empty", "documents": [], "folder": folder_path}

        # Extract and summarize each document
        index = {
            "folder": str(folder_path),
            "total_documents": len(documents),
            "documents": [],
        }

        logger.info(f"📖 Building knowledge index from {len(documents)} documents...")

        for doc in documents:
            logger.info(f"📄 Processing: {doc['name']}")

            # Extract text
            text = self.extract_text(doc["path"])
            if not text:
                logger.warning(f"⚠️ Could not extract text from {doc['name']}")
                continue

            # Generate summary
            summary = self.summarize(text)

            # Create document entry
            doc_entry = {
                "name": doc["name"],
                "path": doc["path"],
                "format": doc["format"],
                "size_bytes": doc["size_bytes"],
                "text_length": len(text),
                "summary": summary,
                "preview": text[:200],  # First 200 chars
            }

            index["documents"].append(doc_entry)

        # Save index if requested
        if output_path:
            try:
                with open(output_path, "w") as f:
                    json.dump(index, f, indent=2)
                logger.info(f"💾 Index saved to {output_path}")
                index["saved_to"] = str(output_path)
            except Exception as e:
                logger.error(f"❌ Failed to save index: {e}")

        self.execution_count += 1
        logger.info(f"✅ Knowledge index built: {len(index['documents'])} documents indexed")

        return index

    def report_status(self) -> dict[str, Any]:
        """Report Archivist status."""
        status = super().report_status()
        status.update(
            {
                "supported_formats": self.supported_formats,
                "max_document_size_mb": self.max_document_size / (1024 * 1024),
            }
        )
        return status


__all__ = ["ArchivistCartridge"]
