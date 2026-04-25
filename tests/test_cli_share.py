"""Tests for envault CLI share commands."""
import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_share import share_group
from envault.crypto import encrypt


PLAINTEXT = "KEY=value\nSECRET=topsecret\n"
OWNER_PASS = "owner"
RECIPIENT_PASS = "recipient"
NEW_PASS = "newpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "env.vault"
    path.write_text(encrypt(PLAINTEXT, OWNER_PASS))
    return path


def test_export_shared_success(runner: CliRunner, vault_file: Path, tmp_path: Path):
    out = tmp_path / "shared.vault"
    result = runner.invoke(
        share_group,
        ["export", str(vault_file), str(out),
         "--password", OWNER_PASS,
         "--recipient-password", RECIPIENT_PASS],
    )
    assert result.exit_code == 0
    assert out.exists()
    assert "exported" in result.output


def test_export_shared_wrong_password_fails(runner: CliRunner, vault_file: Path, tmp_path: Path):
    out = tmp_path / "shared.vault"
    result = runner.invoke(
        share_group,
        ["export", str(vault_file), str(out),
         "--password", "wrongpass",
         "--recipient-password", RECIPIENT_PASS],
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_import_shared_success(runner: CliRunner, vault_file: Path, tmp_path: Path):
    shared = tmp_path / "shared.vault"
    runner.invoke(
        share_group,
        ["export", str(vault_file), str(shared),
         "--password", OWNER_PASS,
         "--recipient-password", RECIPIENT_PASS],
    )

    imported = tmp_path / "imported.vault"
    result = runner.invoke(
        share_group,
        ["import", str(shared), str(imported),
         "--recipient-password", RECIPIENT_PASS,
         "--new-password", NEW_PASS],
    )
    assert result.exit_code == 0
    assert imported.exists()
    assert "imported" in result.output


def test_import_shared_wrong_recipient_password_fails(runner: CliRunner, vault_file: Path, tmp_path: Path):
    shared = tmp_path / "shared.vault"
    runner.invoke(
        share_group,
        ["export", str(vault_file), str(shared),
         "--password", OWNER_PASS,
         "--recipient-password", RECIPIENT_PASS],
    )

    imported = tmp_path / "imported.vault"
    result = runner.invoke(
        share_group,
        ["import", str(shared), str(imported),
         "--recipient-password", "badpass",
         "--new-password", NEW_PASS],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
