"""Tests for envault.export module."""

import os
import pytest

from envault.export import ExportError, export_env, import_env


SAMPLE_VARS = {"APP_ENV": "production", "SECRET_KEY": "s3cr3t", "PORT": "8080"}
PASSWORD = "test-password-123"


@pytest.fixture()
def vault_file(tmp_path):
    """Create a temporary vault file pre-loaded with SAMPLE_VARS."""
    from envault.vault import Vault

    path = str(tmp_path / "test.vault")
    vault = Vault(path)
    vault.init(PASSWORD, SAMPLE_VARS)
    return path


def test_export_env_creates_file(vault_file, tmp_path):
    dest = str(tmp_path / ".env")
    result = export_env(vault_file, PASSWORD, dest)
    assert result == dest
    assert os.path.exists(dest)


def test_export_env_contains_correct_content(vault_file, tmp_path):
    dest = str(tmp_path / ".env")
    export_env(vault_file, PASSWORD, dest)
    content = open(dest).read()
    for key, value in SAMPLE_VARS.items():
        assert f"{key}={value}" in content


def test_export_env_wrong_password_raises(vault_file, tmp_path):
    dest = str(tmp_path / ".env")
    with pytest.raises(ExportError, match="Failed to unlock vault"):
        export_env(vault_file, "wrong-password", dest)


def test_import_env_creates_vault(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    vault_path = str(tmp_path / "output.vault")
    result = import_env(str(env_file), PASSWORD, vault_path)
    assert result == vault_path
    assert os.path.exists(vault_path)


def test_import_env_roundtrip(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    vault_path = str(tmp_path / "output.vault")
    import_env(str(env_file), PASSWORD, vault_path)

    from envault.vault import Vault
    vault = Vault(vault_path)
    variables = vault.unlock(PASSWORD)
    assert variables["DB_HOST"] == "localhost"
    assert variables["DB_PORT"] == "5432"


def test_import_env_skips_comments_and_blank_lines(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nKEY=value\n")
    vault_path = str(tmp_path / "output.vault")
    import_env(str(env_file), PASSWORD, vault_path)

    from envault.vault import Vault
    variables = Vault(vault_path).unlock(PASSWORD)
    assert list(variables.keys()) == ["KEY"]


def test_import_env_invalid_line_raises(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("INVALID_LINE_WITHOUT_EQUALS\n")
    with pytest.raises(ExportError, match="Invalid .env syntax"):
        import_env(str(env_file), PASSWORD, str(tmp_path / "out.vault"))


def test_import_env_missing_file_raises(tmp_path):
    with pytest.raises(ExportError, match="Cannot read env file"):
        import_env(str(tmp_path / "nonexistent.env"), PASSWORD)
