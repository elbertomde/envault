"""Diff support for comparing vault contents across passwords or files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from envault.vault import Vault, VaultError


class DiffError(Exception):
    """Raised when a diff operation fails."""


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: str | None = None
    new_value: str | None = None


def _load_vars(vault_path: str, password: str) -> Dict[str, str]:
    """Unlock a vault and return its key/value pairs."""
    try:
        vault = Vault(vault_path)
        return vault.unlock(password)
    except VaultError as exc:
        raise DiffError(str(exc)) from exc


def diff_vaults(
    vault_path_a: str,
    password_a: str,
    vault_path_b: str,
    password_b: str,
) -> List[DiffEntry]:
    """Compare two vault files and return a list of DiffEntry results."""
    vars_a = _load_vars(vault_path_a, password_a)
    vars_b = _load_vars(vault_path_b, password_b)
    return _compute_diff(vars_a, vars_b)


def diff_vault_passwords(
    vault_path: str,
    password_a: str,
    password_b: str,
) -> List[DiffEntry]:
    """Compare the same vault unlocked with two different passwords."""
    vars_a = _load_vars(vault_path, password_a)
    vars_b = _load_vars(vault_path, password_b)
    return _compute_diff(vars_a, vars_b)


def _compute_diff(
    vars_a: Dict[str, str],
    vars_b: Dict[str, str],
) -> List[DiffEntry]:
    """Core diff logic comparing two variable dictionaries."""
    entries: List[DiffEntry] = []
    all_keys = sorted(set(vars_a) | set(vars_b))

    for key in all_keys:
        in_a = key in vars_a
        in_b = key in vars_b

        if in_a and not in_b:
            entries.append(DiffEntry(key=key, status="removed", old_value=vars_a[key]))
        elif in_b and not in_a:
            entries.append(DiffEntry(key=key, status="added", new_value=vars_b[key]))
        elif vars_a[key] != vars_b[key]:
            entries.append(
                DiffEntry(
                    key=key,
                    status="changed",
                    old_value=vars_a[key],
                    new_value=vars_b[key],
                )
            )
        else:
            entries.append(
                DiffEntry(key=key, status="unchanged", old_value=vars_a[key])
            )

    return entries


def summarize_diff(entries: List[DiffEntry]) -> Dict[str, int]:
    """Return a count of entries grouped by status.

    Args:
        entries: A list of DiffEntry objects as returned by ``_compute_diff``.

    Returns:
        A dictionary mapping each status (``'added'``, ``'removed'``,
        ``'changed'``, ``'unchanged'``) to the number of entries with that
        status.  Statuses with a count of zero are omitted.
    """
    counts: Dict[str, int] = {}
    for entry in entries:
        counts[entry.status] = counts.get(entry.status, 0) + 1
    return counts
