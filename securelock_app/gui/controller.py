"""Display-independent GUI coordination; security stays in the backend."""

from pathlib import Path

from .. import authentication, credentials, password_tools
from ..crypto_utils import DecryptionError
from ..storage import VaultFormatError


class AppError(Exception):
    """Safe display message without secret values."""


class VaultController:
    """Own the unlocked session and save each change with rollback on failure."""

    def __init__(self, path: Path):
        self.path = path
        self.session = None
        self.failed_attempts = 0

    def vault_exists(self):
        try:
            self.path.lstat()  # Access errors must not look like first-time setup.
        except FileNotFoundError:
            return False
        except OSError:
            raise AppError("Cannot access the vault location. Check permissions.") from None
        return True

    def setup(self, password, confirmation):
        if password != confirmation:
            raise AppError("Master passwords do not match.")
        if len(password) < 8 or not password.strip():
            raise AppError("Use at least 8 characters, with non-space content.")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            session = authentication.create_vault(self.path, password)
        except FileExistsError:
            raise AppError("A vault already exists. Restart to sign in; it was not overwritten.") from None
        except (OSError, ValueError):
            raise AppError("Cannot create the vault. Check the location and permissions.") from None
        self.session = session
        self.failed_attempts = 0

    def login(self, password):
        if self.failed_attempts >= 3:
            raise AppError("Sign-in limit reached. Close and restart SecureLock to try again.")
        try:
            session = authentication.unlock_vault(self.path, password)
        except DecryptionError:
            self.failed_attempts += 1
            remaining = 3 - self.failed_attempts
            if not remaining:
                raise AppError("Sign-in limit reached. Close and restart SecureLock to try again.") from None
            raise AppError(f"Cannot unlock: incorrect password or damaged vault. {remaining} attempts left.") from None
        except VaultFormatError:
            raise AppError("The vault is damaged or unsupported. Restore a usable encrypted backup.") from None
        except FileNotFoundError:
            raise AppError("The vault is missing. Restore it before signing in.") from None
        except OSError:
            raise AppError("Cannot read the vault. Check file permissions and try again.") from None
        except ValueError:
            raise AppError("Enter a nonblank master password using valid text.") from None
        self.session = session
        self.failed_attempts = 0

    def lock(self):
        # Reference removal is not reliable memory erasure in Python.
        self.session = None
        self.failed_attempts = 0

    def _vault(self):
        if self.session is None:
            raise AppError("Unlock the vault first.")
        return self.session.vault

    def records(self, query=""):
        vault = self._vault()
        return (credentials.search_credentials(vault, query) if query.strip()
                else credentials.list_credentials(vault))

    def statistics(self):
        return password_tools.security_statistics(self._vault())

    def _change(self, operation, *args):
        vault = self._vault()
        previous = list(vault.credentials)  # Records are frozen.
        try:
            result = operation(vault, *args)
        except (ValueError, TypeError, KeyError):
            vault.credentials[:] = previous
            raise AppError("Enter a service, username and password with non-space content.") from None
        try:
            if not self.vault_exists():
                raise OSError()
            authentication.save_vault(self.path, self.session)
        except (OSError, ValueError, AppError):
            vault.credentials[:] = previous
            raise AppError("Save failed. The change was undone. Check the vault file and permissions, then retry.") from None
        return result

    def add(self, website, username, password):
        return self._change(credentials.add_credential, website, username, password)

    def update(self, credential_id, website, username, password):
        return self._change(credentials.update_credential, credential_id, website, username, password)

    def delete(self, credential_id):
        self._change(credentials.delete_credential, credential_id)
