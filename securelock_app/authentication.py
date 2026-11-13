"""Future setup/unlock coordination; the caller supplies password input."""

from dataclasses import dataclass, field
from pathlib import Path

from .models import Vault


@dataclass
class VaultSession:
    """Unlocked state kept in memory only; never serialize key or session."""

    vault: Vault = field(repr=False)
    key: bytes = field(repr=False)
    salt: bytes = field(repr=False)


def create_vault(path: Path, master_password: str) -> VaultSession:
    """Create a new encrypted empty vault; refuse to overwrite an existing file."""
    raise NotImplementedError("Vault setup is planned for Phase 3")


def unlock_vault(path: Path, master_password: str) -> VaultSession:
    """Authenticate/decrypt the saved vault and return an unlocked session."""
    raise NotImplementedError("Vault unlocking is planned for Phase 3")


def save_vault(path: Path, session: VaultSession) -> None:
    """Validate, serialize in memory, encrypt with fresh nonce, and save."""
    raise NotImplementedError("Vault saving is planned for Phase 3")
