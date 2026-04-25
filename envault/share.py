"""Team sharing support for envault vaults."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from envault.crypto import decrypt, encrypt


class ShareError(Exception):
    """Raised when a share operation fails."""


def export_shared(
    vault_path: Path,
    password: str,
    recipient_password: str,
    output_path: Path,
) -> None:
    """Re-encrypt a vault with a recipient-specific password for sharing."""
    if not vault_path.exists():
        raise ShareError(f"Vault not found: {vault_path}")

    try:
        ciphertext = vault_path.read_text()
        plaintext = decrypt(ciphertext, password)
    except Exception as exc:
        raise ShareError(f"Failed to decrypt vault: {exc}") from exc

    try:
        shared_ciphertext = encrypt(plaintext, recipient_password)
    except Exception as exc:
        raise ShareError(f"Failed to re-encrypt for recipient: {exc}") from exc

    metadata = {
        "source": str(vault_path),
        "shared": True,
    }
    payload = json.dumps({"meta": metadata, "data": shared_ciphertext})
    output_path.write_text(payload)


def import_shared(
    shared_path: Path,
    recipient_password: str,
    output_path: Path,
    new_password: str,
) -> dict:
    """Import a shared vault file, re-encrypting it with a new local password."""
    if not shared_path.exists():
        raise ShareError(f"Shared file not found: {shared_path}")

    try:
        payload = json.loads(shared_path.read_text())
        shared_ciphertext = payload["data"]
        meta = payload.get("meta", {})
    except (json.JSONDecodeError, KeyError) as exc:
        raise ShareError(f"Invalid shared file format: {exc}") from exc

    try:
        plaintext = decrypt(shared_ciphertext, recipient_password)
    except Exception as exc:
        raise ShareError(f"Failed to decrypt shared vault: {exc}") from exc

    try:
        new_ciphertext = encrypt(plaintext, new_password)
    except Exception as exc:
        raise ShareError(f"Failed to encrypt with new password: {exc}") from exc

    output_path.write_text(new_ciphertext)
    return meta
