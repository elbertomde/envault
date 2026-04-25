"""Unit tests for envault.rotate."""

import pytest
from pathlib import Path

from envault.vault import Vault
from envault.rotate import rotate_password, RotateError


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    v = Vault(path)
    v.init("old-pass")
    v.set("KEY1", "value1", "old-pass")
    v.set("KEY2", "value2", "old-pass")
    return path


def test_rotate_changes_password(vault_file: Path) -> None:
    rotate_password(vault_file, "old-pass", "new-pass")
    vault = Vault(vault_file)
    secrets = vault.unlock("new-pass")
    assert secrets["KEY1"] == "value1"
    assert secrets["KEY2"] == "value2"


def test_rotate_old_password_no_longer_works(vault_file: Path) -> None:
    rotate_password(vault_file, "old-pass", "new-pass")
    vault = Vault(vault_file)
    with pytest.raises(Exception):
        vault.unlock("old-pass")


def test_rotate_wrong_old_password_raises(vault_file: Path) -> None:
    with pytest.raises(RotateError, match="Could not unlock"):
        rotate_password(vault_file, "wrong-pass", "new-pass")


def test_rotate_empty_new_password_raises(vault_file: Path) -> None:
    with pytest.raises(RotateError, match="must not be empty"):
        rotate_password(vault_file, "old-pass", "")


def test_rotate_missing_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(RotateError, match="Vault not found"):
        rotate_password(tmp_path / "nonexistent.vault", "old", "new")


def test_rotate_records_audit(vault_file: Path, tmp_path: Path) -> None:
    from envault.audit import AuditLog

    log_path = tmp_path / "audit.json"
    audit = AuditLog(log_path)
    rotate_password(vault_file, "old-pass", "new-pass", audit_log=audit)
    entries = AuditLog(log_path).entries()
    assert len(entries) == 1
    assert entries[0]["action"] == "rotate"
