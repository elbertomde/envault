"""Tests for envault.cli_export CLI commands."""

import os
import pytest
from click.testing import CliRunner

from envault.cli_export import export_group
from envault.vault import Vault


PASSWORD = "cli-test-password"
SAMPLE_VARS = {"FOO": "bar", "BAZ": "qux"}


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = Vault(path)
    vault.init(PASSWORD, SAMPLE_VARS)
    return path


def test_export_env_success(runner, vault_file, tmp_path):
    dest = str(tmp_path / "out.env")
    result = runner.invoke(export_group, ["env", vault_file, "--password", PASSWORD, "--output", dest])
    assert result.exit_code == 0
    assert "Exported to" in result.output
    assert os.path.exists(dest)


def test_export_env_wrong_password_fails(runner, vault_file, tmp_path):
    dest = str(tmp_path / "out.env")
    result = runner.invoke(export_group, ["env", vault_file, "--password", "bad", "--output", dest])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_import_env_success(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY1=val1\nKEY2=val2\n")
    vault_out = str(tmp_path / "imported.vault")
    result = runner.invoke(
        export_group,
        ["import", str(env_file), "--password", PASSWORD, "--output", vault_out],
        input=f"{PASSWORD}\n{PASSWORD}\n",
    )
    assert result.exit_code == 0
    assert "Vault created at" in result.output
    assert os.path.exists(vault_out)


def test_import_env_invalid_file_fails(runner, tmp_path):
    result = runner.invoke(
        export_group,
        ["import", str(tmp_path / "missing.env"), "--password", PASSWORD],
        input=f"{PASSWORD}\n{PASSWORD}\n",
    )
    assert result.exit_code == 1
    assert "Error" in result.output
