"""In-memory models only. Never write these plaintext values to disk."""

from dataclasses import dataclass, field


def validate_required_text(value: str, field_name: str) -> None:
    """Require a string with non-whitespace content without modifying it."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} is required")


@dataclass(frozen=True)
class Credential:
    """One login; stable ID is assigned by the credential module.

    Passwords are preserved exactly and excluded from repr, not encrypted.
    Website is a service label, so it need not be a URL.
    """

    id: str
    website: str
    username: str
    password: str = field(repr=False)

    def __post_init__(self) -> None:
        validate_credential(self)


def validate_credential(credential: Credential) -> None:
    """Raise TypeError for wrong types or ValueError for blank fields."""
    if not isinstance(credential, Credential):
        raise TypeError("credential must be a Credential")
    for name in ("id", "website", "username", "password"):
        validate_required_text(getattr(credential, name), name)


@dataclass
class Vault:
    """Unlocked credentials; each vault owns its own list, with unique IDs."""

    credentials: list[Credential] = field(default_factory=list)

    def __post_init__(self) -> None:
        validate_vault(self)


def validate_vault(vault: Vault) -> None:
    """Validate again before operations, since the list is mutable."""
    if not isinstance(vault, Vault):
        raise TypeError("vault must be a Vault")
    if not isinstance(vault.credentials, list):
        raise TypeError("credentials must be a list")
    seen = set()
    for credential in vault.credentials:
        validate_credential(credential)
        if credential.id in seen:
            raise ValueError("credential IDs must be unique")
        seen.add(credential.id)
