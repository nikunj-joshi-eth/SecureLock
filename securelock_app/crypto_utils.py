"""Version 1 Scrypt and AES-GCM helpers; secrets stay in memory."""

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from .models import validate_required_text

# Immutable format-v1 choices. Changing these requires a new format version.
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
AAD_V1 = b"SecureLock:vault:version=1"


class DecryptionError(ValueError):
    """Wrong password or damaged ciphertext; no plaintext is returned."""


def validate_bytes(value: bytes, name: str, length: int | None = None) -> None:
    """Check binary inputs without including their values in errors."""
    if not isinstance(value, bytes):
        raise TypeError(f"{name} must be bytes")
    if length is not None and len(value) != length:
        raise ValueError(f"Invalid {name} length")


def generate_salt() -> bytes:
    """Return a fresh cryptographically random 16-byte salt."""
    return os.urandom(16)


def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive 256 bits with format-v1 Scrypt (about 16 MiB working memory)."""
    validate_required_text(master_password, "master password")
    validate_bytes(salt, "salt", 16)
    try:
        password_bytes = master_password.encode("utf-8")
    except UnicodeError:
        raise ValueError("Master password must be valid UTF-8 text") from None
    return Scrypt(salt=salt, length=32, n=SCRYPT_N, r=SCRYPT_R,
                  p=SCRYPT_P).derive(password_bytes)


def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    """Encrypt with fresh nonce and fixed format-v1 authenticated data."""
    validate_bytes(plaintext, "plaintext")
    validate_bytes(key, "key", 32)
    nonce = os.urandom(12)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, AAD_V1)


def decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Authenticate format-v1 data before returning any plaintext."""
    validate_bytes(ciphertext, "ciphertext")
    validate_bytes(key, "key", 32)
    validate_bytes(nonce, "nonce", 12)
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, AAD_V1)
    except InvalidTag:
        raise DecryptionError("Vault authentication failed") from None
