"""Password rotation support for envault vaults."""

from pathlib import Path
from .vault import Vault, VaultError
from .audit import AuditLog


class RotateError(Exception):
    """Raised when password rotation fails."""


def rotate_password(
    vault_path: Path,
    old_password: str,
    new_password: str,
    audit_log: AuditLog | None = None,
) -> None:
    """Re-encrypt a vault with a new password.

    Decrypts the vault using *old_password*, then re-encrypts all secrets
    with *new_password*.  The vault file is updated atomically.

    Raises:
        RotateError: if the old password is wrong or the vault is corrupt.
    """
    if not vault_path.exists():
        raise RotateError(f"Vault not found: {vault_path}")

    if not new_password:
        raise RotateError("New password must not be empty.")

    vault = Vault(vault_path)

    try:
        secrets = vault.unlock(old_password)
    except VaultError as exc:
        raise RotateError(f"Could not unlock vault: {exc}") from exc

    # Re-lock with the new password by writing each secret back.
    try:
        vault.init(new_password)
        for key, value in secrets.items():
            vault.set(key, value, new_password)
    except VaultError as exc:
        raise RotateError(f"Failed to re-encrypt vault: {exc}") from exc

    if audit_log is not None:
        audit_log.record(
            action="rotate",
            details={"vault": str(vault_path)},
        )
