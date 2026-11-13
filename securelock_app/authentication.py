"""Setup, unlock and save coordination. No prompting or secret logging."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .crypto_utils import decrypt, derive_key, encrypt, generate_salt, validate_bytes
from .models import Credential, Vault, validate_required_text, validate_vault
from .storage import (EncryptedEnvelope, VaultFormatError, read_envelope,
                      strict_object, validate_path, write_envelope)


@dataclass
class VaultSession:
    """Unlocked memory only; discard references when locking."""

    vault: Vault = field(repr=False)
    key: bytes = field(repr=False)
    salt: bytes = field(repr=False)


def _envelope(session: VaultSession) -> EncryptedEnvelope:
    if not isinstance(session, VaultSession):
        raise TypeError("session must be a VaultSession")
    validate_vault(session.vault)
    validate_bytes(session.key, "key", 32)
    validate_bytes(session.salt, "salt", 16)
    plaintext = json.dumps(asdict(session.vault), ensure_ascii=True,
                           separators=(",", ":")).encode("utf-8")
    nonce, ciphertext = encrypt(plaintext, session.key)
    return EncryptedEnvelope(1, session.salt, nonce, ciphertext)


def create_vault(path: Path, master_password: str) -> VaultSession:
    """Create an encrypted empty vault with race-safe overwrite refusal."""
    validate_path(path)
    validate_required_text(master_password, "master password")
    if len(master_password) < 8:
        raise ValueError("Master password must have at least 8 characters")
    if path.exists() or path.is_symlink():
        raise FileExistsError("Vault already exists")
    salt = generate_salt()
    session = VaultSession(Vault(), derive_key(master_password, salt), salt)
    write_envelope(path, _envelope(session), overwrite=False)
    return session


def unlock_vault(path: Path, master_password: str) -> VaultSession:
    """Validate format, derive key, authenticate, then validate the payload."""
    validate_required_text(master_password, "master password")
    envelope = read_envelope(path)
    key = derive_key(master_password, envelope.salt)
    plaintext = decrypt(envelope.ciphertext, key, envelope.nonce)
    try:
        obj = json.loads(plaintext.decode("utf-8"), object_pairs_hook=strict_object)
        if not isinstance(obj, dict) or set(obj) != {"credentials"}:
            raise ValueError()
        if not isinstance(obj["credentials"], list):
            raise ValueError()
        records = []
        for record in obj["credentials"]:
            if not isinstance(record, dict) or set(record) != {"id", "website", "username", "password"}:
                raise ValueError()
            records.append(Credential(**record))
        vault = Vault(records)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise VaultFormatError("Invalid decrypted vault structure") from None
    return VaultSession(vault, key, envelope.salt)


def save_vault(path: Path, session: VaultSession) -> None:
    """Validate everything before atomically replacing encrypted data."""
    validate_path(path)
    write_envelope(path, _envelope(session))
