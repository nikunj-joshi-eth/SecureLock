"""Local password tools; never log or persist supplied passwords."""

import secrets
import string

from .models import Vault, validate_vault


_COMMON_PATTERNS = ("password", "qwerty", "letmein", "welcome", "admin",
                    "123456", "abcdef")


def generate_password(length: int = 16, *, use_symbols: bool = True) -> str:
    """Generate using secure randomness; support lengths from 8 to 128."""
    if not isinstance(length, int) or isinstance(length, bool):
        raise TypeError("length must be an integer")
    if not isinstance(use_symbols, bool):
        raise TypeError("use_symbols must be a boolean")
    if not 8 <= length <= 128:
        raise ValueError("length must be between 8 and 128")
    categories = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if use_symbols:
        categories.append(string.punctuation)
    alphabet = "".join(categories)
    # Reject whole candidates to avoid fixed category positions or shuffle bias.
    # secrets.choice uses unbiased selection from the operating system RNG.
    while True:
        candidate = "".join(secrets.choice(alphabet) for _ in range(length))
        if all(any(char in category for char in candidate) for category in categories):
            return candidate


def estimate_strength(password: str) -> str:
    """Estimate only, with rules applied in order (no cryptographic guarantee).

    Weak: fewer than 8 characters, fewer than 2 categories, a common substring
    (casefolded), or exact repetition of a 1–4 character unit at least twice
    (casefolded). Strong: otherwise at least 12 characters and 3 categories.
    Moderate: everything else. Categories are Unicode lower, upper, digit,
    and non-alphanumeric non-whitespace symbols; spaces count only in length.
    """
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    folded = password.casefold()
    categories = sum((any(c.islower() for c in password),
                      any(c.isupper() for c in password),
                      any(c.isdigit() for c in password),
                      any(not c.isalnum() and not c.isspace() for c in password)))
    repeated = any(len(folded) >= 2 * size and len(folded) % size == 0
                   and folded == folded[:size] * (len(folded) // size)
                   for size in range(1, 5))
    if (len(password) < 8 or categories < 2 or repeated
            or any(pattern in folded for pattern in _COMMON_PATTERNS)):
        return "weak"
    if len(password) >= 12 and categories >= 3:
        return "strong"
    return "moderate"


def find_duplicate_passwords(vault: Vault) -> list[list[str]]:
    """Return groups of credential IDs sharing a password, never passwords."""
    validate_vault(vault)
    groups: dict[str, list[str]] = {}
    for credential in vault.credentials:
        groups.setdefault(credential.password, []).append(credential.id)
    return [ids for ids in groups.values() if len(ids) >= 2]


def security_statistics(vault: Vault) -> dict[str, int]:
    """Return total, weak, moderate, strong, and reused credential counts."""
    validate_vault(vault)
    counts = dict(total=len(vault.credentials), weak=0, moderate=0, strong=0, reused=0)
    for credential in vault.credentials:
        counts[estimate_strength(credential.password)] += 1
    counts["reused"] = sum(len(group) for group in find_duplicate_passwords(vault))
    return counts
