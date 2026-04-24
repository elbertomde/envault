"""Vault module for managing encrypted .env files.

Handles reading, writing, and managing encrypted environment
variable files (vault files) on disk.
"""

import json
import os
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt

# Default filenames
DEFAULT_VAULT_FILE = ".env.vault"
DEFAULT_ENV_FILE = ".env"


class VaultError(Exception):
    """Raised when a vault operation fails."""
    pass


class Vault:
    """Represents an encrypted vault file containing environment variables."""

    def __init__(self, vault_path: Path):
        """
        Initialize a Vault instance.

        Args:
            vault_path: Path to the .env.vault file.
        """
        self.vault_path = Path(vault_path)

    @classmethod
    def init(cls, vault_path: Path = None) -> "Vault":
        """Create a new empty vault file.

        Args:
            vault_path: Where to create the vault. Defaults to .env.vault.

        Returns:
            A new Vault instance pointing to the created file.

        Raises:
            VaultError: If a vault already exists at the given path.
        """
        path = Path(vault_path or DEFAULT_VAULT_FILE)
        if path.exists():
            raise VaultError(f"Vault already exists at '{path}'. Use 'lock' to update it.")
        # Write an empty vault placeholder (no ciphertext yet)
        path.write_text(json.dumps({"version": 1, "ciphertext": None}), encoding="utf-8")
        return cls(path)

    def lock(self, env_path: Path, password: str) -> None:
        """Encrypt an .env file and store the ciphertext in the vault.

        Args:
            env_path: Path to the plaintext .env file to encrypt.
            password: Password used to derive the encryption key.

        Raises:
            VaultError: If the .env file does not exist.
        """
        env_file = Path(env_path)
        if not env_file.exists():
            raise VaultError(f"Environment file not found: '{env_file}'")

        plaintext = env_file.read_text(encoding="utf-8")
        ciphertext = encrypt(plaintext, password)

        payload = {"version": 1, "ciphertext": ciphertext}
        self.vault_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def unlock(self, password: str, output_path: Optional[Path] = None) -> str:
        """Decrypt the vault and return (or write) the plaintext .env content.

        Args:
            password: Password used to derive the decryption key.
            output_path: If provided, write the decrypted content to this file.

        Returns:
            The decrypted plaintext content.

        Raises:
            VaultError: If the vault file is missing, empty, or the password is wrong.
        """
        if not self.vault_path.exists():
            raise VaultError(f"Vault file not found: '{self.vault_path}'")

        try:
            payload = json.loads(self.vault_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise VaultError("Vault file is corrupted or not a valid vault.") from exc

        ciphertext = payload.get("ciphertext")
        if not ciphertext:
            raise VaultError("Vault is empty. Use 'lock' to encrypt an .env file first.")

        # Let crypto.decrypt raise ValueError on bad password / corrupted data
        try:
            plaintext = decrypt(ciphertext, password)
        except (ValueError, Exception) as exc:
            raise VaultError(f"Failed to decrypt vault: {exc}") from exc

        if output_path:
            Path(output_path).write_text(plaintext, encoding="utf-8")

        return plaintext

    def exists(self) -> bool:
        """Return True if the vault file exists on disk."""
        return self.vault_path.exists()
