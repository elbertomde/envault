"""Template rendering support for envault — substitute env vars into template files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from envault.vault import Vault, VaultError


class TemplateError(Exception):
    """Raised when template rendering fails."""


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(
    template_path: str | Path,
    vault_path: str | Path,
    password: str,
    output_path: Optional[str | Path] = None,
    *,
    strict: bool = True,
) -> str:
    """Render *template_path* by substituting ``{{ KEY }}`` placeholders with
    values decrypted from *vault_path*.

    Parameters
    ----------
    template_path:
        Path to the template file containing ``{{ KEY }}`` placeholders.
    vault_path:
        Path to the encrypted vault file.
    password:
        Password used to decrypt the vault.
    output_path:
        If given, the rendered content is written to this path.
    strict:
        When *True* (default), raise :class:`TemplateError` for any placeholder
        whose key is not present in the vault.  When *False*, leave the
        placeholder unchanged.

    Returns
    -------
    str
        The fully rendered template content.
    """
    template_path = Path(template_path)
    vault_path = Path(vault_path)

    if not template_path.exists():
        raise TemplateError(f"Template file not found: {template_path}")

    try:
        vault = Vault(vault_path)
        variables: dict[str, str] = vault.unlock(password)
    except VaultError as exc:
        raise TemplateError(str(exc)) from exc

    template_content = template_path.read_text(encoding="utf-8")

    missing: list[str] = []

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in variables:
            return variables[key]
        if strict:
            missing.append(key)
            return match.group(0)  # keep original while collecting all missing
        return match.group(0)

    rendered = _PLACEHOLDER_RE.sub(_replace, template_content)

    if missing:
        raise TemplateError(
            "Template references undefined variable(s): " + ", ".join(sorted(missing))
        )

    if output_path is not None:
        Path(output_path).write_text(rendered, encoding="utf-8")

    return rendered
