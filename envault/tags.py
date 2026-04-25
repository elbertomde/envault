"""Tag management for vault entries — group and filter variables by tag."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class TagError(Exception):
    """Raised when a tag operation fails."""


class TagManager:
    """Manages tags associated with vault files."""

    def __init__(self, tag_file: Path) -> None:
        self._path = tag_file
        self._data: Dict[str, List[str]] = self._load()

    def _load(self) -> Dict[str, List[str]]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            raise TagError(f"Failed to load tag file: {exc}") from exc

    def _save(self) -> None:
        try:
            self._path.write_text(json.dumps(self._data, indent=2))
        except OSError as exc:
            raise TagError(f"Failed to save tag file: {exc}") from exc

    def add_tag(self, vault_name: str, tag: str) -> None:
        """Add a tag to a vault entry."""
        tags = self._data.setdefault(vault_name, [])
        if tag in tags:
            raise TagError(f"Tag '{tag}' already exists on vault '{vault_name}'.")
        tags.append(tag)
        self._save()

    def remove_tag(self, vault_name: str, tag: str) -> None:
        """Remove a tag from a vault entry."""
        tags = self._data.get(vault_name, [])
        if tag not in tags:
            raise TagError(f"Tag '{tag}' not found on vault '{vault_name}'.")
        tags.remove(tag)
        if not tags:
            del self._data[vault_name]
        self._save()

    def list_tags(self, vault_name: str) -> List[str]:
        """Return all tags for a vault entry."""
        return list(self._data.get(vault_name, []))

    def find_by_tag(self, tag: str) -> List[str]:
        """Return all vault names that have the given tag."""
        return [name for name, tags in self._data.items() if tag in tags]

    def all_tags(self) -> Dict[str, List[str]]:
        """Return a copy of the full tag mapping."""
        return {k: list(v) for k, v in self._data.items()}
