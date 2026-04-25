"""Tests for envault.audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.audit import AuditError, AuditLog


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    return tmp_path / ".envault_audit.json"


def test_new_log_is_empty(log_file: Path) -> None:
    audit = AuditLog(log_file)
    assert audit.entries() == []


def test_record_creates_entry(log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("lock", user="alice", details="vault.env.enc")
    entries = audit.entries()
    assert len(entries) == 1
    assert entries[0]["action"] == "lock"
    assert entries[0]["user"] == "alice"
    assert entries[0]["details"] == "vault.env.enc"


def test_record_persists_to_disk(log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("unlock", user="bob")
    # Re-load from disk
    audit2 = AuditLog(log_file)
    assert len(audit2.entries()) == 1
    assert audit2.entries()[0]["action"] == "unlock"


def test_multiple_records(log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("lock")
    audit.record("unlock")
    audit.record("export")
    assert len(audit.entries()) == 3
    actions = [e["action"] for e in audit.entries()]
    assert actions == ["lock", "unlock", "export"]


def test_clear_removes_all_entries(log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("lock")
    audit.record("unlock")
    audit.clear()
    assert audit.entries() == []
    # Persisted as well
    audit2 = AuditLog(log_file)
    assert audit2.entries() == []


def test_entry_has_timestamp(log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("init")
    entry = audit.entries()[0]
    assert "timestamp" in entry
    assert entry["timestamp"].endswith("+00:00")


def test_corrupted_log_raises(log_file: Path) -> None:
    log_file.write_text("not valid json", encoding="utf-8")
    with pytest.raises(AuditError, match="Failed to read audit log"):
        AuditLog(log_file)


def test_user_defaults_to_env_user(log_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USER", "testuser")
    audit = AuditLog(log_file)
    audit.record("lock")
    assert audit.entries()[0]["user"] == "testuser"


def test_entries_returns_copy(log_file: Path) -> None:
    """Mutating the returned list should not affect the internal log state."""
    audit = AuditLog(log_file)
    audit.record("lock")
    entries = audit.entries()
    entries.clear()
    assert len(audit.entries()) == 1
