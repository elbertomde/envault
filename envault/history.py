"""History tracking for vault operations — records snapshots of variable keys over time."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


class HistoryError(Exception):
    pass


class HistoryEntry:
    def __init__(self, timestamp: str, operation: str, keys: List[str], note: str = ""):
        self.timestamp = timestamp
        self.operation = operation
        self.keys = keys
        self.note = note

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "keys": self.keys,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoryEntry":
        return cls(
            timestamp=data["timestamp"],
            operation=data["operation"],
            keys=data.get("keys", []),
            note=data.get("note", ""),
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"HistoryEntry(op={self.operation!r}, keys={self.keys})"


class VaultHistory:
    def __init__(self, history_file: Path):
        self.history_file = Path(history_file)
        self._entries: List[HistoryEntry] = self._load()

    def _load(self) -> List[HistoryEntry]:
        if not self.history_file.exists():
            return []
        try:
            data = json.loads(self.history_file.read_text())
            return [HistoryEntry.from_dict(e) for e in data]
        except (json.JSONDecodeError, KeyError) as exc:
            raise HistoryError(f"Corrupt history file: {exc}") from exc

    def _save(self) -> None:
        self.history_file.write_text(
            json.dumps([e.to_dict() for e in self._entries], indent=2)
        )

    def record(self, operation: str, keys: List[str], note: str = "") -> HistoryEntry:
        if not operation:
            raise HistoryError("Operation name must not be empty.")
        entry = HistoryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
            keys=sorted(keys),
            note=note,
        )
        self._entries.append(entry)
        self._save()
        return entry

    def list_entries(self) -> List[HistoryEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries = []
        self._save()
