"""Strict encrypted-envelope parsing and atomic encrypted-only writes."""

import base64
import binascii
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

MAX_ENVELOPE_BYTES = 16 * 1024 * 1024


class VaultFormatError(ValueError):
    """Unsupported or malformed envelope/decrypted structure."""


@dataclass(frozen=True)
class EncryptedEnvelope:
    """Only public metadata and authenticated ciphertext cross this boundary."""

    version: int
    salt: bytes
    nonce: bytes
    ciphertext: bytes = field(repr=False)


def validate_path(path: Path) -> None:
    if not isinstance(path, Path):
        raise TypeError("path must be a Path")


def strict_object(pairs: list) -> dict:
    """Reject duplicate JSON keys instead of silently choosing one."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise VaultFormatError("Duplicate JSON field")
        result[key] = value
    return result


def validate_envelope(envelope: EncryptedEnvelope) -> None:
    if not isinstance(envelope, EncryptedEnvelope):
        raise TypeError("envelope must be an EncryptedEnvelope")
    if type(envelope.version) is not int or envelope.version != 1:
        raise VaultFormatError("Unsupported vault version")
    for name, length in (("salt", 16), ("nonce", 12)):
        value = getattr(envelope, name)
        if not isinstance(value, bytes) or len(value) != length:
            raise VaultFormatError("Invalid envelope metadata")
    if not isinstance(envelope.ciphertext, bytes) or len(envelope.ciphertext) < 16:
        raise VaultFormatError("Invalid ciphertext")


def read_envelope(path: Path) -> EncryptedEnvelope:
    """Validate bounded JSON and base64 before any expensive key derivation."""
    validate_path(path)
    with path.open("rb") as stream:
        data = stream.read(MAX_ENVELOPE_BYTES + 1)
    if len(data) > MAX_ENVELOPE_BYTES:
        raise VaultFormatError("Vault file too large")
    try:
        obj = json.loads(data.decode("utf-8"), object_pairs_hook=strict_object)
        if not isinstance(obj, dict) or set(obj) != {"version", "salt", "nonce", "ciphertext"}:
            raise VaultFormatError("Invalid envelope fields")
        binary = []
        for name in ("salt", "nonce", "ciphertext"):
            if not isinstance(obj[name], str):
                raise VaultFormatError("Invalid base64 field")
            binary.append(base64.b64decode(obj[name], validate=True))
        envelope = EncryptedEnvelope(obj["version"], *binary)
        validate_envelope(envelope)
        return envelope
    except (ValueError, UnicodeError, RecursionError, binascii.Error):
        raise VaultFormatError("Invalid vault envelope") from None


def write_envelope(path: Path, envelope: EncryptedEnvelope, *, overwrite: bool = True) -> None:
    """Stage encrypted bytes, fsync, then replace or exclusively hard-link.

    Hard-link publication fails if the destination exists, even during a race.
    Filesystems without hard-link support fail closed during setup.
    """
    validate_path(path)
    validate_envelope(envelope)
    if type(overwrite) is not bool:
        raise TypeError("overwrite must be bool")
    obj = {"version": envelope.version}
    for name in ("salt", "nonce", "ciphertext"):
        obj[name] = base64.b64encode(getattr(envelope, name)).decode("ascii")
    data = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    if len(data) > MAX_ENVELOPE_BYTES:
        raise VaultFormatError("Vault file too large")
    fd, temporary = tempfile.mkstemp(prefix=".securelock-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
