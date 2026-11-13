"""Future Scrypt/AES-256-GCM boundary. No cryptography is implemented yet."""


class DecryptionError(ValueError):
    """Wrong key or damaged/modified encrypted data; do not return plaintext."""


def generate_salt() -> bytes:
    """Return a fresh random 16-byte salt."""
    raise NotImplementedError("Salt generation is planned for Phase 3")


def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key using Scrypt; parameters fixed by format version."""
    raise NotImplementedError("Key derivation is planned for Phase 3")


def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    """Return (fresh 12-byte nonce, ciphertext including authentication tag)."""
    raise NotImplementedError("Encryption is planned for Phase 3")


def decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Return authenticated plaintext or raise DecryptionError."""
    raise NotImplementedError("Decryption is planned for Phase 3")
