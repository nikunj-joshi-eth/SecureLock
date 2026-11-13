"""Operations on an unlocked vault; no file I/O or UI code."""

import uuid

from .models import Credential, Vault, validate_required_text, validate_vault


def add_credential(vault: Vault, website: str, username: str,
                   password: str) -> Credential:
    """Validate fields, assign a unique stable ID, append, and return record."""
    validate_vault(vault)
    credential = Credential(str(uuid.uuid4()), website, username, password)
    existing_ids = {record.id for record in vault.credentials}
    while credential.id in existing_ids:
        credential = Credential(str(uuid.uuid4()), website, username, password)
    vault.credentials.append(credential)
    return credential


def list_credentials(vault: Vault) -> list[Credential]:
    """Return a new list in insertion order; caller must hide passwords in UI."""
    validate_vault(vault)
    return list(vault.credentials)


def search_credentials(vault: Vault, query: str) -> list[Credential]:
    """Return case-insensitive website substring matches in insertion order."""
    validate_vault(vault)
    validate_required_text(query, "query")
    query = query.strip().casefold()
    return [record for record in vault.credentials
            if query in record.website.casefold()]


def update_credential(vault: Vault, credential_id: str, website: str,
                      username: str, password: str) -> Credential:
    """Replace all login fields while retaining the ID and list position."""
    validate_vault(vault)
    replacement = Credential(credential_id, website, username, password)
    for index, record in enumerate(vault.credentials):
        if record.id == credential_id:
            vault.credentials[index] = replacement
            return replacement
    raise KeyError("Credential ID not found")


def delete_credential(vault: Vault, credential_id: str) -> None:
    """Remove the matching record or raise KeyError if the ID is missing."""
    validate_vault(vault)
    validate_required_text(credential_id, "credential ID")
    for index, record in enumerate(vault.credentials):
        if record.id == credential_id:
            del vault.credentials[index]
            return
    raise KeyError("Credential ID not found")
