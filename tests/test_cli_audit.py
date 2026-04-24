"""Tests for envault.cli_audit."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.audit import AuditLog
from envault.cli_audit import audit_group


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    return tmp_path / ".envault_audit.json"


def test_list_empty(runner: CliRunner, log_file: Path) -> None:
    result = runner.invoke(audit_group, ["list", "--log", str(log_file)])
    assert result.exit_code == 0
    assert "No audit entries found" in result.output


def test_list_shows_entries(runner: CliRunner, log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("lock", user="alice", details="vault.env.enc")
    result = runner.invoke(audit_group, ["list", "--log", str(log_file)])
    assert result.exit_code == 0
    assert "alice" in result.output
    assert "lock" in result.output
    assert "vault.env.enc" in result.output


def test_list_entry_without_details(runner: CliRunner, log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("unlock", user="bob")
    result = runner.invoke(audit_group, ["list", "--log", str(log_file)])
    assert result.exit_code == 0
    assert "unlock" in result.output
    assert " — " not in result.output


def test_clear_with_confirmation(runner: CliRunner, log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("export", user="carol")
    result = runner.invoke(audit_group, ["clear", "--log", str(log_file)], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    audit2 = AuditLog(log_file)
    assert audit2.entries() == []


def test_clear_aborted(runner: CliRunner, log_file: Path) -> None:
    audit = AuditLog(log_file)
    audit.record("lock", user="dave")
    result = runner.invoke(audit_group, ["clear", "--log", str(log_file)], input="n\n")
    assert result.exit_code != 0
    audit2 = AuditLog(log_file)
    assert len(audit2.entries()) == 1
