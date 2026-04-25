"""Tests for envault.share module."""
import json
import pytest
from pathlib import Path

from envault.crypto import encrypt
from envault.share import ShareError, export_shared, import_shared


PLAINTEXT = "API_KEY=secret123\nDB_PASS=hunter2\n"
OWNER_PASSWORD = "owner-pass"
RECIPIENT_PASSWORD = "recipient-pass"
NEW_PASSWORD = "new-local-pass"


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    path.write_text(encrypt(PLAINTEXT, OWNER_PASSWORD))
    return path


def test_export_shared_creates_file(vault_file: Path, tmp_path: Path):
    out = tmp_path / "shared.vault"
    export_shared(vault_file, OWNER_PASSWORD, RECIPIENT_PASSWORD, out)
    assert out.exists()


def test_export_shared_output_is_valid_json(vault_file: Path, tmp_path: Path):
    out = tmp_path / "shared.vault"
    export_shared(vault_file, OWNER_PASSWORD, RECIPIENT_PASSWORD, out)
    payload = json.loads(out.read_text())
    assert "data" in payload
    assert "meta" in payload


def test_export_shared_wrong_password_raises(vault_file: Path, tmp_path: Path):
    out = tmp_path / "shared.vault"
    with pytest.raises(ShareError):
        export_shared(vault_file, "wrong-password", RECIPIENT_PASSWORD, out)


def test_export_shared_missing_vault_raises(tmp_path: Path):
    with pytest.raises(ShareError):
        export_shared(tmp_path / "missing.vault", OWNER_PASSWORD, RECIPIENT_PASSWORD, tmp_path / "out.vault")


def test_import_shared_roundtrip(vault_file: Path, tmp_path: Path):
    shared = tmp_path / "shared.vault"
    export_shared(vault_file, OWNER_PASSWORD, RECIPIENT_PASSWORD, shared)

    imported = tmp_path / "imported.vault"
    import_shared(shared, RECIPIENT_PASSWORD, imported, NEW_PASSWORD)
    assert imported.exists()


def test_import_shared_plaintext_preserved(vault_file: Path, tmp_path: Path):
    from envault.crypto import decrypt

    shared = tmp_path / "shared.vault"
    export_shared(vault_file, OWNER_PASSWORD, RECIPIENT_PASSWORD, shared)

    imported = tmp_path / "imported.vault"
    import_shared(shared, RECIPIENT_PASSWORD, imported, NEW_PASSWORD)
    result = decrypt(imported.read_text(), NEW_PASSWORD)
    assert result == PLAINTEXT


def test_import_shared_wrong_recipient_password_raises(vault_file: Path, tmp_path: Path):
    shared = tmp_path / "shared.vault"
    export_shared(vault_file, OWNER_PASSWORD, RECIPIENT_PASSWORD, shared)

    with pytest.raises(ShareError):
        import_shared(shared, "bad-password", tmp_path / "out.vault", NEW_PASSWORD)


def test_import_shared_invalid_file_raises(tmp_path: Path):
    bad_file = tmp_path / "bad.vault"
    bad_file.write_text("not json at all")
    with pytest.raises(ShareError):
        import_shared(bad_file, RECIPIENT_PASSWORD, tmp_path / "out.vault", NEW_PASSWORD)
