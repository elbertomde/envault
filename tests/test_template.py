"""Tests for envault.template — template rendering with vault substitution."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import Vault
from envault.template import TemplateError, render_template


PASSWORD = "s3cr3t"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    vault = Vault(path)
    vault.init(PASSWORD)
    vault.lock({"APP_HOST": "localhost", "APP_PORT": "8080", "DEBUG": "true"}, PASSWORD)
    return path


@pytest.fixture()
def template_file(tmp_path: Path) -> Path:
    path = tmp_path / "config.tmpl"
    path.write_text("host={{ APP_HOST }}\nport={{ APP_PORT }}\n", encoding="utf-8")
    return path


def test_render_substitutes_placeholders(vault_file: Path, template_file: Path) -> None:
    result = render_template(template_file, vault_file, PASSWORD)
    assert "host=localhost" in result
    assert "port=8080" in result


def test_render_writes_output_file(vault_file: Path, template_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "config.out"
    render_template(template_file, vault_file, PASSWORD, output_path=out)
    assert out.exists()
    assert "localhost" in out.read_text(encoding="utf-8")


def test_render_returns_rendered_string(vault_file: Path, template_file: Path) -> None:
    result = render_template(template_file, vault_file, PASSWORD)
    assert isinstance(result, str)
    assert "{{ APP_HOST }}" not in result


def test_render_strict_raises_on_missing_key(vault_file: Path, tmp_path: Path) -> None:
    tmpl = tmp_path / "missing.tmpl"
    tmpl.write_text("value={{ UNDEFINED_KEY }}\n", encoding="utf-8")
    with pytest.raises(TemplateError, match="UNDEFINED_KEY"):
        render_template(tmpl, vault_file, PASSWORD, strict=True)


def test_render_non_strict_keeps_placeholder(vault_file: Path, tmp_path: Path) -> None:
    tmpl = tmp_path / "lenient.tmpl"
    tmpl.write_text("value={{ UNDEFINED_KEY }}\n", encoding="utf-8")
    result = render_template(tmpl, vault_file, PASSWORD, strict=False)
    assert "{{ UNDEFINED_KEY }}" in result


def test_render_wrong_password_raises(vault_file: Path, template_file: Path) -> None:
    with pytest.raises(TemplateError):
        render_template(template_file, vault_file, "wrongpassword")


def test_render_missing_template_raises(vault_file: Path, tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.tmpl"
    with pytest.raises(TemplateError, match="not found"):
        render_template(missing, vault_file, PASSWORD)


def test_render_missing_vault_raises(template_file: Path, tmp_path: Path) -> None:
    missing_vault = tmp_path / "ghost.vault"
    with pytest.raises(TemplateError):
        render_template(template_file, missing_vault, PASSWORD)


def test_render_multiple_missing_keys_reported(vault_file: Path, tmp_path: Path) -> None:
    tmpl = tmp_path / "multi.tmpl"
    tmpl.write_text("{{ FOO }} and {{ BAR }}\n", encoding="utf-8")
    with pytest.raises(TemplateError) as exc_info:
        render_template(tmpl, vault_file, PASSWORD, strict=True)
    msg = str(exc_info.value)
    assert "BAR" in msg
    assert "FOO" in msg
