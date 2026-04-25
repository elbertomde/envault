"""Tests for envault/history.py"""

import json
import pytest
from pathlib import Path

from envault.history import VaultHistory, HistoryError


@pytest.fixture
def history_file(tmp_path):
    return tmp_path / "history.json"


def test_new_history_is_empty(history_file):
    h = VaultHistory(history_file)
    assert h.list_entries() == []


def test_record_creates_entry(history_file):
    h = VaultHistory(history_file)
    entry = h.record("lock", ["DB_URL", "SECRET"])
    assert entry.operation == "lock"
    assert set(entry.keys) == {"DB_URL", "SECRET"}


def test_record_persists_to_disk(history_file):
    h = VaultHistory(history_file)
    h.record("unlock", ["API_KEY"], note="manual unlock")

    h2 = VaultHistory(history_file)
    entries = h2.list_entries()
    assert len(entries) == 1
    assert entries[0].operation == "unlock"
    assert entries[0].note == "manual unlock"


def test_record_keys_are_sorted(history_file):
    h = VaultHistory(history_file)
    entry = h.record("lock", ["Z_VAR", "A_VAR", "M_VAR"])
    assert entry.keys == ["A_VAR", "M_VAR", "Z_VAR"]


def test_multiple_records_accumulate(history_file):
    h = VaultHistory(history_file)
    h.record("lock", ["FOO"])
    h.record("rotate", ["FOO"])
    h.record("unlock", ["FOO"])
    assert len(h.list_entries()) == 3


def test_record_empty_operation_raises(history_file):
    h = VaultHistory(history_file)
    with pytest.raises(HistoryError, match="Operation name"):
        h.record("", ["KEY"])


def test_clear_removes_all_entries(history_file):
    h = VaultHistory(history_file)
    h.record("lock", ["A"])
    h.record("unlock", ["A"])
    h.clear()
    assert h.list_entries() == []


def test_clear_persists(history_file):
    h = VaultHistory(history_file)
    h.record("lock", ["A"])
    h.clear()
    h2 = VaultHistory(history_file)
    assert h2.list_entries() == []


def test_corrupt_history_file_raises(history_file):
    history_file.write_text("not valid json")
    with pytest.raises(HistoryError, match="Corrupt history file"):
        VaultHistory(history_file)


def test_entry_has_timestamp(history_file):
    h = VaultHistory(history_file)
    entry = h.record("lock", ["KEY"])
    assert entry.timestamp
    assert "T" in entry.timestamp  # ISO format


def test_record_no_note_defaults_empty(history_file):
    h = VaultHistory(history_file)
    entry = h.record("lock", ["KEY"])
    assert entry.note == ""
