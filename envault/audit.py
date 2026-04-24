"""Audit log for tracking vault operations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_LOG_FILENAME = ".envault_audit.json"


class AuditError(Exception):
    """Raised when an audit log operation fails."""


class AuditLog:
    """Manages a simple JSON-based audit log for vault operations."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self._entries: List[dict] = self._load()

    def _load(self) -> List[dict]:
        if not self.log_path.exists():
            return []
        try:
            with self.log_path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            raise AuditError(f"Failed to read audit log: {exc}") from exc

    def _save(self) -> None:
        try:
            with self.log_path.open("w", encoding="utf-8") as fh:
                json.dump(self._entries, fh, indent=2)
        except OSError as exc:
            raise AuditError(f"Failed to write audit log: {exc}") from exc

    def record(self, action: str, user: Optional[str] = None, details: Optional[str] = None) -> None:
        """Append a new entry to the audit log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "user": user or os.environ.get("USER", "unknown"),
            "details": details or "",
        }
        self._entries.append(entry)
        self._save()

    def entries(self) -> List[dict]:
        """Return all audit log entries."""
        return list(self._entries)

    def clear(self) -> None:
        """Remove all audit log entries."""
        self._entries = []
        self._save()
