"""Tests for envault.diff module."""

import pytest

from envault.vault import Vault
from envault.diff import DiffError, DiffEntry, diff_vaults, _compute_diff


@pytest.fixture
def vault_a(tmp_path):
    path = str(tmp_path / "a.vault")
    v = Vault(path)
    v.init("passA", {"KEY1": "value1", "SHARED": "same", "OLD": "gone"})
    return path


@pytest.fixture
def vault_b(tmp_path):
    path = str(tmp_path / "b.vault")
    v = Vault(path)
    v.init("passB", {"KEY2": "value2", "SHARED": "same", "OLD": "changed"})
    return path


def test_diff_vaults_detects_added(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    added = [e for e in entries if e.status == "added"]
    assert any(e.key == "KEY2" for e in added)


def test_diff_vaults_detects_removed(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    removed = [e for e in entries if e.status == "removed"]
    assert any(e.key == "KEY1" for e in removed)


def test_diff_vaults_detects_changed(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    changed = [e for e in entries if e.status == "changed"]
    assert any(e.key == "OLD" for e in changed)


def test_diff_vaults_detects_unchanged(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert any(e.key == "SHARED" for e in unchanged)


def test_diff_wrong_password_raises(vault_a, vault_b):
    with pytest.raises(DiffError):
        diff_vaults(vault_a, "wrong", vault_b, "passB")


def test_compute_diff_all_statuses():
    a = {"X": "1", "Y": "2", "Z": "same"}
    b = {"Y": "99", "Z": "same", "W": "new"}
    result = _compute_diff(a, b)
    statuses = {e.key: e.status for e in result}
    assert statuses["X"] == "removed"
    assert statuses["Y"] == "changed"
    assert statuses["Z"] == "unchanged"
    assert statuses["W"] == "added"


def test_compute_diff_empty_inputs():
    assert _compute_diff({}, {}) == []


def test_compute_diff_identical():
    vars_ = {"A": "1", "B": "2"}
    result = _compute_diff(vars_, vars_.copy())
    assert all(e.status == "unchanged" for e in result)


def test_diff_entry_values_populated():
    entries = _compute_diff({"K": "old"}, {"K": "new"})
    entry = entries[0]
    assert entry.old_value == "old"
    assert entry.new_value == "new"
    assert entry.status == "changed"
