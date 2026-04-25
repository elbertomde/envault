"""Tests for envault.cli_diff module."""

import pytest
from click.testing import CliRunner

from envault.cli_diff import diff_group
from envault.vault import Vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_a(tmp_path):
    path = str(tmp_path / "a.vault")
    Vault(path).init("passA", {"ALPHA": "1", "COMMON": "x"})
    return path


@pytest.fixture
def vault_b(tmp_path):
    path = str(tmp_path / "b.vault")
    Vault(path).init("passB", {"BETA": "2", "COMMON": "x", "CHANGED": "new"})
    return path


def test_diff_vaults_success(runner, vault_a, vault_b):
    result = runner.invoke(
        diff_group,
        ["vaults", vault_a, vault_b, "--password-a", "passA", "--password-b", "passB"],
    )
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output


def test_diff_vaults_shows_removed(runner, vault_a, vault_b):
    result = runner.invoke(
        diff_group,
        ["vaults", vault_a, vault_b, "--password-a", "passA", "--password-b", "passB"],
    )
    assert "-" in result.output or "removed" in result.output.lower() or "ALPHA" in result.output


def test_diff_vaults_wrong_password_fails(runner, vault_a, vault_b):
    result = runner.invoke(
        diff_group,
        ["vaults", vault_a, vault_b, "--password-a", "wrong", "--password-b", "passB"],
    )
    assert result.exit_code != 0
    assert "Error" in result.output or "error" in result.output.lower()


def test_diff_vaults_no_differences(runner, tmp_path):
    path_a = str(tmp_path / "c.vault")
    path_b = str(tmp_path / "d.vault")
    Vault(path_a).init("pw", {"X": "1"})
    Vault(path_b).init("pw2", {"X": "1"})
    result = runner.invoke(
        diff_group,
        ["vaults", path_a, path_b, "--password-a", "pw", "--password-b", "pw2"],
    )
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_diff_vaults_show_unchanged_flag(runner, vault_a, vault_b):
    result = runner.invoke(
        diff_group,
        [
            "vaults", vault_a, vault_b,
            "--password-a", "passA",
            "--password-b", "passB",
            "--show-unchanged",
        ],
    )
    assert result.exit_code == 0
    assert "COMMON" in result.output
