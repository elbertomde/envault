"""Export and import utilities for envault vault files."""

import json
import os
from pathlib import Path
from typing import Optional

from envault.vault import Vault, VaultError


class ExportError(Exception):
    """Raised when export/import operations fail."""


def export_env(vault_path: str, password: str, output_path: Optional[str] = None) -> str:
    """Decrypt a vault and export its contents as a plain .env file.

    Args:
        vault_path: Path to the encrypted vault file.
        password: Password to decrypt the vault.
        output_path: Destination path for the .env file. Defaults to .env in cwd.

    Returns:
        The path where the .env file was written.

    Raises:
        ExportError: If the vault cannot be read or decrypted.
    """
    vault = Vault(vault_path)
    try:
        variables = vault.unlock(password)
    except VaultError as exc:
        raise ExportError(f"Failed to unlock vault: {exc}") from exc

    dest = output_path or os.path.join(os.getcwd(), ".env")
    lines = [f"{key}={value}\n" for key, value in variables.items()]

    with open(dest, "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    return dest


def import_env(env_path: str, password: str, vault_path: Optional[str] = None) -> str:
    """Read a plain .env file and store it as an encrypted vault.

    Args:
        env_path: Path to the plain .env file.
        password: Password used to encrypt the vault.
        vault_path: Destination path for the vault file. Defaults to <env_path>.vault.

    Returns:
        The path where the vault file was written.

    Raises:
        ExportError: If the .env file cannot be parsed or the vault cannot be written.
    """
    variables: dict[str, str] = {}

    try:
        with open(env_path, "r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ExportError(f"Invalid .env syntax on line {lineno}: {line!r}")
                key, _, value = line.partition("=")
                variables[key.strip()] = value.strip()
    except OSError as exc:
        raise ExportError(f"Cannot read env file '{env_path}': {exc}") from exc

    dest = vault_path or f"{env_path}.vault"
    vault = Vault(dest)
    vault.init(password, variables)
    return dest
