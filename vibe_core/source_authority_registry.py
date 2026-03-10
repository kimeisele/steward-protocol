"""Strict loader for source-only authority registry records."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

SOURCE_AUTHORITY_REGISTRY = Path("authority-src/registry.yaml")
SOURCE_AUTHORITY_REGISTRY_KIND = "source_authority_registry"
SOURCE_AUTHORITY_REGISTRY_VERSION = 1

_ALLOWED_TOP_LEVEL_KEYS = {"kind", "version", "repo_id", "documents"}
_ALLOWED_DOCUMENT_KEYS = {
    "document_id",
    "title",
    "source_path",
    "authority",
    "domain",
    "public_abstract",
    "labels",
}


@dataclass(frozen=True, slots=True)
class SourceAuthorityDocumentRecord:
    document_id: str
    title: str
    source_path: str
    authority: str
    domain: str
    public_abstract: str = ""
    labels: dict[str, str] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "source_path": self.source_path,
            "authority": self.authority,
            "domain": self.domain,
            "public_abstract": self.public_abstract,
            "labels": dict(self.labels),
        }


@dataclass(frozen=True, slots=True)
class SourceAuthorityRegistryRecord:
    repo_id: str
    documents: tuple[SourceAuthorityDocumentRecord, ...]
    kind: str = SOURCE_AUTHORITY_REGISTRY_KIND
    version: int = SOURCE_AUTHORITY_REGISTRY_VERSION

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "version": self.version,
            "repo_id": self.repo_id,
            "documents": [record.to_payload() for record in self.documents],
        }


def load_source_authority_registry(*, workspace: Path | None = None, registry_path: Path | None = None) -> SourceAuthorityRegistryRecord:
    path = _resolve_registry_path(workspace=workspace, registry_path=registry_path)
    payload = yaml.safe_load(path.read_text()) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"invalid_source_authority_registry:{path}")
    unknown_top_level_keys = sorted(set(payload) - _ALLOWED_TOP_LEVEL_KEYS)
    if unknown_top_level_keys:
        raise ValueError(f"unsupported_source_authority_registry_keys:{','.join(unknown_top_level_keys)}")
    if str(payload.get("kind") or "") != SOURCE_AUTHORITY_REGISTRY_KIND:
        raise ValueError("invalid_source_authority_registry_kind")
    version = int(payload.get("version") or 0)
    if version != SOURCE_AUTHORITY_REGISTRY_VERSION:
        raise ValueError(f"unsupported_source_authority_registry_version:{version}")
    repo_id = str(payload.get("repo_id") or "").strip()
    if not repo_id:
        raise ValueError("missing_source_authority_repo_id")
    documents_payload = payload.get("documents") or []
    if not isinstance(documents_payload, list) or not documents_payload:
        raise ValueError("missing_source_authority_documents")
    documents = tuple(_build_document_record(item) for item in documents_payload)
    _validate_unique_documents(documents)
    return SourceAuthorityRegistryRecord(repo_id=repo_id, documents=documents)


def _resolve_registry_path(*, workspace: Path | None, registry_path: Path | None) -> Path:
    if registry_path is not None:
        resolved = Path(registry_path).resolve()
        if not resolved.exists():
            raise FileNotFoundError(resolved)
        return resolved
    search_roots = []
    if workspace is not None:
        search_roots.append(Path(workspace).resolve())
    search_roots.extend(Path(__file__).resolve().parents)
    for root in search_roots:
        candidate = root / SOURCE_AUTHORITY_REGISTRY
        if candidate.exists():
            return candidate
    raise FileNotFoundError(SOURCE_AUTHORITY_REGISTRY)


def _build_document_record(payload: object) -> SourceAuthorityDocumentRecord:
    if not isinstance(payload, dict):
        raise TypeError("invalid_source_authority_document_record")
    unknown_keys = sorted(set(payload) - _ALLOWED_DOCUMENT_KEYS)
    if unknown_keys:
        raise ValueError(f"unsupported_source_authority_document_keys:{','.join(unknown_keys)}")
    source_path = _normalize_relative_path(str(payload.get("source_path") or ""))
    labels_payload = payload.get("labels") or {}
    if not isinstance(labels_payload, dict):
        raise TypeError("invalid_source_authority_document_labels")
    document_id = str(payload.get("document_id") or "").strip()
    title = str(payload.get("title") or "").strip()
    authority = str(payload.get("authority") or "").strip()
    domain = str(payload.get("domain") or "").strip()
    if not document_id:
        raise ValueError("missing_source_authority_document_id")
    if not title:
        raise ValueError(f"missing_source_authority_title:{document_id}")
    if not authority:
        raise ValueError(f"missing_source_authority_authority:{document_id}")
    if not domain:
        raise ValueError(f"missing_source_authority_domain:{document_id}")
    return SourceAuthorityDocumentRecord(
        document_id=document_id,
        title=title,
        source_path=source_path,
        authority=authority,
        domain=domain,
        public_abstract=str(payload.get("public_abstract") or "").strip(),
        labels={str(key): str(value) for key, value in labels_payload.items()},
    )


def _normalize_relative_path(raw_path: str) -> str:
    path = Path(raw_path.strip())
    if not raw_path.strip():
        raise ValueError("missing_source_authority_source_path")
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe_source_authority_source_path:{raw_path}")
    return path.as_posix()


def _validate_unique_documents(documents: tuple[SourceAuthorityDocumentRecord, ...]) -> None:
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for record in documents:
        if record.document_id in seen_ids:
            raise ValueError(f"duplicate_source_authority_document_id:{record.document_id}")
        if record.source_path in seen_paths:
            raise ValueError(f"duplicate_source_authority_source_path:{record.source_path}")
        seen_ids.add(record.document_id)
        seen_paths.add(record.source_path)