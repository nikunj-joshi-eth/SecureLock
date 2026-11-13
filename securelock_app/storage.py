"""Future encrypted-envelope file I/O. No plaintext persistence helpers."""

from dataclasses import dataclass, field
from pathlib import Path


class VaultFormatError(ValueError):
    """Unsupported version or malformed envelope/decrypted vault structure."""


@dataclass(frozen=True)
class EncryptedEnvelope:
    """Transport fields only; validation/encoding belong to future storage."""

    version: int
    salt: bytes
    nonce: bytes
    ciphertext: bytes = field(repr=False)


def read_envelope(path: Path) -> EncryptedEnvelope:
    """Read and validate an encrypted envelope; never prompt or decrypt."""
    raise NotImplementedError("Encrypted storage is planned for Phase 3")


def write_envelope(path: Path, envelope: EncryptedEnvelope) -> None:
    """Validate and save encrypted fields only, replacing the file atomically."""
    raise NotImplementedError("Encrypted storage is planned for Phase 3")
