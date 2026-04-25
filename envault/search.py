"""Search for keys across vault files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import Vault, VaultError


class SearchError(Exception):
    """Raised when a search operation fails."""


@dataclass
class SearchMatch:
    key: str
    value: str
    vault_path: str


def search_vault(
    vault_path: Path,
    password: str,
    query: str,
    *,
    keys_only: bool = False,
    case_sensitive: bool = False,
) -> List[SearchMatch]:
    """Search for *query* in the keys (and optionally values) of a vault.

    Args:
        vault_path: Path to the ``.vault`` file.
        password: Password used to decrypt the vault.
        query: Substring to search for.
        keys_only: When *True* only key names are searched.
        case_sensitive: When *False* (default) the match is case-insensitive.

    Returns:
        A list of :class:`SearchMatch` objects for every matching variable.

    Raises:
        SearchError: If the vault cannot be opened or decrypted.
    """
    if not vault_path.exists():
        raise SearchError(f"Vault file not found: {vault_path}")

    try:
        vault = Vault(vault_path)
        variables = vault.unlock(password)
    except VaultError as exc:
        raise SearchError(str(exc)) from exc

    needle = query if case_sensitive else query.lower()

    matches: List[SearchMatch] = []
    for key, value in variables.items():
        haystack_key = key if case_sensitive else key.lower()
        haystack_val = value if case_sensitive else value.lower()

        hit = needle in haystack_key
        if not keys_only:
            hit = hit or needle in haystack_val

        if hit:
            matches.append(SearchMatch(key=key, value=value, vault_path=str(vault_path)))

    return matches
