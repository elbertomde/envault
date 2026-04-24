"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
SAMPLE_PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/db\nAPI_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_produces_different_ciphertext_each_time():
    """Each encryption call should produce a unique ciphertext (random salt+nonce)."""
    result1 = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    result2 = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    assert result1 != result2


def test_decrypt_roundtrip():
    """Decrypting an encrypted payload should return the original plaintext."""
    ciphertext = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == SAMPLE_PLAINTEXT


def test_decrypt_wrong_password_raises():
    ciphertext = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext, "wrong-password")


def test_decrypt_corrupted_payload_raises():
    ciphertext = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    # Flip some bytes in the middle of the payload
    corrupted = ciphertext[:-4] + "AAAA"
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSWORD)


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid payload encoding"):
        decrypt("!!!not-base64!!!", PASSWORD)


def test_decrypt_too_short_payload_raises():
    import base64
    short_payload = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short_payload, PASSWORD)


def test_encrypt_empty_string():
    ciphertext = encrypt("", PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == ""


def test_encrypt_unicode_content():
    unicode_text = "SECRET=caf\u00e9\u2615"
    ciphertext = encrypt(unicode_text, PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == unicode_text
