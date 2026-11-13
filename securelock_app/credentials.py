"""Future operations on an unlocked vault; no file I/O or UI code."""

from .models import Credential, Vault


def add_credential(vault: Vault, website: str, username: str,
                   password: str) -> Credential:
    """Validate fields, assign a unique stable ID, append, and return record."""
    raise NotImplementedError("Credential management is planned for Phase 4")


def list_credentials(vault: Vault) -> list[Credential]:
    """Return a new list in insertion order; caller must hide passwords in UI."""
    raise NotImplementedError("Credential management is planned for Phase 4")


def search_credentials(vault: Vault, query: str) -> list[Credential]:
    """Return case-insensitive website substring matches in insertion order."""
    raise NotImplementedError("Credential management is planned for Phase 4")


def update_credential(vault: Vault, credential_id: str, website: str,
                      username: str, password: str) -> Credential:
    """Replace all login fields while retaining the ID and list position."""
    raise NotImplementedError("Credential management is planned for Phase 4")


def delete_credential(vault: Vault, credential_id: str) -> None:
    """Remove the matching record or raise KeyError if the ID is missing."""
    raise NotImplementedError("Credential management is planned for Phase 4")
