"""Durable JSON/YAML storage with atomic writes and import/export support."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .models import LinksDocument

APP_DIR_NAME = "links"
DEFAULT_FILE_NAME = "links.json"


class StorageError(RuntimeError):
    """A user-facing configuration storage problem."""


class ConfigStore:
    """Read and write the Links document under the XDG config directory."""

    def __init__(self, config_home: Path | None = None) -> None:
        root = config_home or Path(
            os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        )
        self.directory = root / APP_DIR_NAME
        self.path = self.directory / DEFAULT_FILE_NAME
        self.backup_path = self.directory / f"{DEFAULT_FILE_NAME}.bak"

    def load(self) -> LinksDocument:
        if not self.path.exists():
            return LinksDocument.starter_document()

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if not isinstance(raw, dict):
                raise StorageError("The configuration root must be an object.")
            document = LinksDocument.from_dict(raw)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise StorageError(f"Could not read {self.path}: {error}") from error

        errors = document.validate()
        if errors:
            raise StorageError("; ".join(errors))
        return document

    def save(self, document: LinksDocument, *, create_backup: bool = True) -> None:
        errors = document.validate()
        if errors:
            raise StorageError("; ".join(errors))

        self.directory.mkdir(parents=True, exist_ok=True)
        if create_backup and self.path.exists():
            try:
                shutil.copy2(self.path, self.backup_path)
            except OSError as error:
                raise StorageError(
                    f"Could not create backup {self.backup_path}: {error}"
                ) from error
        payload = json.dumps(document.to_dict(), indent=2, ensure_ascii=False)
        self._atomic_write(self.path, payload + "\n")

    def load_backup(self) -> LinksDocument:
        """Load the last configuration saved before a change."""

        if not self.backup_path.exists():
            raise StorageError("No backup is available yet.")
        try:
            with self.backup_path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if not isinstance(raw, dict):
                raise StorageError("The backup root must be an object.")
            document = LinksDocument.from_dict(raw)
        except StorageError:
            raise
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise StorageError(f"Could not read {self.backup_path}: {error}") from error

        errors = document.validate()
        if errors:
            raise StorageError("; ".join(errors))
        return document

    def export_document(self, document: LinksDocument, destination: Path) -> None:
        """Export JSON or YAML based on the destination suffix."""

        suffix = destination.suffix.casefold()
        if suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import-not-found]
            except ImportError as error:
                raise StorageError(
                    "YAML export requires the optional 'PyYAML' dependency."
                ) from error
            payload = yaml.safe_dump(
                document.to_dict(), allow_unicode=True, sort_keys=False
            )
        else:
            payload = json.dumps(document.to_dict(), indent=2, ensure_ascii=False)
        self._atomic_write(destination, payload + "\n")

    def import_document(self, source: Path) -> LinksDocument:
        try:
            with source.open("r", encoding="utf-8") as handle:
                if source.suffix.casefold() in {".yaml", ".yml"}:
                    try:
                        import yaml  # type: ignore[import-not-found]
                    except ImportError as error:
                        raise StorageError(
                            "YAML import requires the optional 'PyYAML' dependency."
                        ) from error
                    raw: Any = yaml.safe_load(handle)
                else:
                    raw = json.load(handle)
            if not isinstance(raw, dict):
                raise StorageError("The imported configuration root must be an object.")
            document = LinksDocument.from_dict(raw)
        except StorageError:
            raise
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise StorageError(f"Could not import {source}: {error}") from error

        errors = document.validate()
        if errors:
            raise StorageError("; ".join(errors))
        return document

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                delete=False,
            ) as handle:
                temporary_name = handle.name
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, path)
        except OSError as error:
            if temporary_name:
                Path(temporary_name).unlink(missing_ok=True)
            raise StorageError(f"Could not write {path}: {error}") from error
