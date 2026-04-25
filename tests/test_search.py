"""Tests for envault.search."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.search import SearchError, search_vault
from envault.vault import Vault


PASSWORD = "hunter2"
VARIABLES = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "supersecret",
    "DEBUG": "true",
    "API_KEY": "abc123",
}


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    v = Vault(path)
    v.init(PASSWORD)
    v.lock(PASSWORD, VARIABLES)
    return path


def test_search_finds_key_substring(vault_file: Path) -> None:
    matches = search_vault(vault_file, PASSWORD, "KEY")
    keys = {m.key for m in matches}
    assert "SECRET_KEY" in keys
    assert "API_KEY" in keys


def test_search_finds_value_substring(vault_file: Path) -> None:
    matches = search_vault(vault_file, PASSWORD, "postgres")
    assert len(matches) == 1
    assert matches[0].key == "DATABASE_URL"


def test_search_keys_only_ignores_values(vault_file: Path) -> None:
    # "abc123" is a value — should not match when keys_only=True
    matches = search_vault(vault_file, PASSWORD, "abc123", keys_only=True)
    assert matches == []


def test_search_case_insensitive_by_default(vault_file: Path) -> None:
    matches = search_vault(vault_file, PASSWORD, "database")
    assert any(m.key == "DATABASE_URL" for m in matches)


def test_search_case_sensitive_no_match(vault_file: Path) -> None:
    matches = search_vault(vault_file, PASSWORD, "database", case_sensitive=True)
    assert matches == []


def test_search_case_sensitive_match(vault_file: Path) -> None:
    matches = search_vault(vault_file, PASSWORD, "DATABASE", case_sensitive=True)
    assert any(m.key == "DATABASE_URL" for m in matches)


def test_search_no_results(vault_file: Path) -> None:
    matches = search_vault(vault_file, PASSWORD, "NONEXISTENT_QUERY_XYZ")
    assert matches == []


def test_search_wrong_password_raises(vault_file: Path) -> None:
    with pytest.raises(SearchError):
        search_vault(vault_file, "wrongpassword", "KEY")


def test_search_missing_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(SearchError, match="not found"):
        search_vault(tmp_path / "missing.vault", PASSWORD, "KEY")


def test_search_match_contains_vault_path(vault_file: Path) -> None:
    matches = search_vault(vault_file, PASSWORD, "DEBUG")
    assert len(matches) == 1
    assert str(vault_file) == matches[0].vault_path
