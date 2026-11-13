"""Future local password tools; never log or persist supplied passwords."""

from .models import Vault


def generate_password(length: int = 16, *, use_symbols: bool = True) -> str:
    """Generate using secure randomness; support lengths from 8 to 128."""
    raise NotImplementedError("Password tools are planned for Phase 4")


def estimate_strength(password: str) -> str:
    """Return 'weak', 'moderate', or 'strong'; an estimate, not a guarantee."""
    raise NotImplementedError("Password tools are planned for Phase 4")


def find_duplicate_passwords(vault: Vault) -> list[list[str]]:
    """Return groups of credential IDs sharing a password, never passwords."""
    raise NotImplementedError("Password tools are planned for Phase 4")


def security_statistics(vault: Vault) -> dict[str, int]:
    """Return total, weak, moderate, strong, and reused credential counts."""
    raise NotImplementedError("Password tools are planned for Phase 4")
