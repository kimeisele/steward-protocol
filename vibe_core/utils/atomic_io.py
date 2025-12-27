"""
ATOMIC I/O - Crash-Safe File Operations

DHARMA: State ist entweder ALT oder NEU, niemals KORRUPT.

Diese Utilities garantieren:
1. Atomarität: Schreibvorgang ist ganz oder gar nicht
2. Durabilität: fsync() vor rename()
3. Keine Korruption: Bei Crash bleibt alte Datei intakt

Verwendet POSIX rename() Semantik (atomic auf gleichem Filesystem).
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Union


def atomic_write_text(path: Union[str, Path], content: str, encoding: str = "utf-8") -> None:
    """
    Schreibt Text atomar in eine Datei.

    Args:
        path: Zielpfad
        content: Zu schreibender Inhalt
        encoding: Zeichenkodierung (default: utf-8)

    Raises:
        OSError: Bei Schreibfehlern

    Garantie:
        - Bei Erfolg: Neue Datei enthält content
        - Bei Fehler: Alte Datei bleibt unverändert
        - Kein Zustand dazwischen möglich
    """
    path = Path(path)

    # Stelle sicher, dass Parent-Verzeichnis existiert
    path.parent.mkdir(parents=True, exist_ok=True)

    # Erstelle temp file im gleichen Verzeichnis (wichtig für atomic rename)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp", prefix=".atomic_")

    try:
        # Schreibe Inhalt
        os.write(fd, content.encode(encoding))

        # Flush to disk (Durabilität)
        os.fsync(fd)
        os.close(fd)

        # Atomic rename (POSIX Garantie)
        os.rename(tmp_path, path)

    except Exception:
        # Cleanup bei Fehler
        try:
            os.close(fd)
        except OSError:
            pass
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def atomic_write_json(
    path: Union[str, Path], data: Dict[str, Any], indent: int = 2, ensure_ascii: bool = False
) -> None:
    """
    Schreibt JSON atomar in eine Datei.

    Args:
        path: Zielpfad
        data: Zu schreibende Daten (muss JSON-serialisierbar sein)
        indent: Einrückung (default: 2)
        ensure_ascii: ASCII-only Output (default: False, erlaubt Unicode)

    Raises:
        OSError: Bei Schreibfehlern
        TypeError: Wenn data nicht serialisierbar

    Garantie:
        - Bei Erfolg: Neue Datei enthält valides JSON
        - Bei Fehler: Alte Datei bleibt unverändert
    """
    content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)
    atomic_write_text(path, content)


def safe_read_yaml(path: Union[str, Path], default: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Liest YAML sicher mit einheitlicher Fehlerbehandlung.

    Args:
        path: Quellpfad
        default: Rückgabewert wenn Datei nicht existiert oder leer (default: {})

    Returns:
        Geladene Daten als Dict

    Raises:
        ImportError: Wenn PyYAML nicht installiert
        yaml.YAMLError: Bei Parse-Fehlern (keine Silent Failures!)

    Garantie:
        - Verwendet immer safe_load (keine Code-Execution)
        - Einheitliche UTF-8 Kodierung
        - Leere Dateien → default statt None
    """
    import yaml

    if default is None:
        default = {}

    path = Path(path)

    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data if data is not None else default


def atomic_write_yaml(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """
    Schreibt YAML atomar in eine Datei.

    Args:
        path: Zielpfad
        data: Zu schreibende Daten

    Raises:
        ImportError: Wenn PyYAML nicht installiert
        OSError: Bei Schreibfehlern
    """
    import yaml

    content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    atomic_write_text(path, content)
