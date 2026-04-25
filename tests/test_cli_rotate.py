"""Integration tests for the rotate CLI commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_rotate import rotate_group
from envault.vault import Vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "cli_test.vault"
    v = Vault(path)
    v.init("old-pass")
    v.set("FOO", "bar", "old-pass")
    return path


def test_rotate_success(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["run", str(vault_file)],
        input="old-pass\nnew-pass\nnew-pass\n",
    )
    assert result.exit_code == 0
    assert "rotated successfully" in result.output


def test_rotate_wrong_old_password_fails(
    runner: CliRunner, vault_file: Path
) -> None:
    result = runner.invoke(
        rotate_group,
        ["run", str(vault_file)],
        input="wrong\nnew-pass\nnew-pass\n",
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_rotate_with_audit_log(
    runner: CliRunner, vault_file: Path, tmp_path: Path
) -> None:
    log_path = tmp_path / "audit.json"
    result = runner.invoke(
        rotate_group,
        ["run", str(vault_file), "--audit-log", str(log_path)],
        input="old-pass\nnew-pass\nnew-pass\n",
    )
    assert result.exit_code == 0
    assert log_path.exists()
