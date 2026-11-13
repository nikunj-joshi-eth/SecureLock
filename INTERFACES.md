# SecureLock shared interfaces — Phase 2A

Use Python 3.10 or newer. The foundation uses the standard library only;
`cryptography` remains the planned security dependency. The original
`securelock.py` is unchanged and separate from this package.

Only the models and validation helpers are implemented. **Every feature
function below currently raises `NotImplementedError` without side effects.**
The return values and other errors below are contracts for later phases,
not working security features. Imports must not open windows, prompt, access
files, or perform cryptography.

## Shared models (implemented)

`Credential(id: str, website: str, username: str, password: str)` is a frozen
dataclass. All fields must be strings containing non-whitespace content.
Values are preserved exactly, including password spaces. Website is a service
label, not necessarily a URL. No strength policy is imposed on saved passwords.
The credential module will assign stable, nonblank unique IDs. Password is
excluded from `repr`, but remains plaintext in memory; do not log or serialize
the object to disk.

`Vault(credentials: list[Credential] = <new empty list>)` holds unlocked data.
Each instance has its own default list. IDs must be unique within the vault;
duplicate websites, usernames, and passwords are allowed. The list is mutable,
so future operations must revalidate it before changing or saving it.

| Helper signature | Output | Errors |
| --- | --- | --- |
| `validate_required_text(value: str, field_name: str) -> None` | Success without normalization; field_name is a developer-supplied label | TypeError for non-string value; ValueError for blank value |
| `validate_credential(credential: Credential) -> None` | Validates type and all four fields | TypeError for wrong model/field types; ValueError for blank fields |
| `validate_vault(vault: Vault) -> None` | Validates list, entries, and unique IDs | TypeError for wrong types; ValueError for duplicate IDs/blank fields |

Constructors invoke the relevant validator. Error messages identify fields,
never their values. Frozen records are updated by replacement, not mutation.

## Authentication (`authentication.py`, Nikunj)

`VaultSession(vault: Vault, key: bytes, salt: bytes)` carries an unlocked vault,
32-byte key, and 16-byte salt in memory. It does not retain the master password.
All fields are excluded from repr. This transport dataclass does not validate
security parameters; future authentication must validate them. Never persist
a session or its key. On lock/exit, callers discard references; reliable memory
erasure is not guaranteed in Python. No lock UI is implemented here.

| Signature | Inputs and output | Future errors |
| --- | --- | --- |
| `create_vault(path: Path, master_password: str) -> VaultSession` | Validate password (at least 8 characters, not all whitespace), create salt/key, encrypt empty Vault, save and return session | FileExistsError if path exists; TypeError/ValueError for invalid input; OSError for I/O |
| `unlock_vault(path: Path, master_password: str) -> VaultSession` | Read envelope, derive key, authenticate/decrypt, parse and validate Vault | FileNotFoundError/OSError; VaultFormatError for malformed data; DecryptionError for wrong password/tampering; TypeError/ValueError for invalid input |
| `save_vault(path: Path, session: VaultSession) -> None` | Validate vault/session, serialize only in memory, encrypt with fresh nonce and existing salt/key, save envelope | TypeError/ValueError for invalid input; OSError for I/O |

The GUI obtains passwords and handles confirmation. These functions never
prompt. Wrong passwords and tampering share `DecryptionError`; a failed unlock
must never return a session. Setup must refuse overwrite even if a file appears
while setup is in progress. Unlock accepts nonblank password strings without
reapplying setup strength rules. No separately stored password verifier is needed:
authenticated decryption verifies the derived key.

## Cryptography (`crypto_utils.py`, Nikunj)

| Signature | Inputs and output | Future errors |
| --- | --- | --- |
| `generate_salt() -> bytes` | Fresh cryptographically random 16-byte salt | OS randomness errors propagate |
| `derive_key(master_password: str, salt: bytes) -> bytes` | UTF-8 password and 16-byte salt to 32-byte Scrypt key | TypeError for wrong types; ValueError for blank password/invalid salt length |
| `encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]` | Bytes and 32-byte key to (fresh random 12-byte nonce, AES-256-GCM ciphertext including tag) | TypeError for wrong types; ValueError for invalid key length |
| `decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes` | Authenticate ciphertext using 32-byte key and 12-byte nonce, return plaintext only on success | TypeError/ValueError for invalid parameters; DecryptionError for authentication failure |

`DecryptionError` subclasses ValueError. Empty plaintext is permitted. No custom
cryptographic algorithms or fallback plaintext behavior. Before Phase 3 writes
files, document a fixed format-version-to-Scrypt-parameters mapping and the
authenticated-data policy; all writers/readers must use the same mapping.

## Storage (`storage.py`, Khushi with Nikunj)

`EncryptedEnvelope(version: int, salt: bytes, nonce: bytes, ciphertext: bytes)`
is a frozen transport dataclass without constructor validation. Ciphertext is
excluded from repr. Future storage validates version (initially integer 1),
16-byte salt, 12-byte nonce, and ciphertext with an authentication tag.
It contains no credential fields, key, or master password.

| Signature | Inputs and output | Future errors |
| --- | --- | --- |
| `read_envelope(path: Path) -> EncryptedEnvelope` | Read JSON envelope and decode binary fields from base64; no decryption | FileNotFoundError/OSError; VaultFormatError for invalid JSON, fields, base64, lengths, or unsupported version; TypeError for wrong input type |
| `write_envelope(path: Path, envelope: EncryptedEnvelope) -> None` | Validate envelope, encode bytes as base64, atomically replace encrypted file | VaultFormatError for invalid envelope; TypeError for wrong input types; OSError for I/O |

`VaultFormatError` subclasses ValueError and also covers malformed decrypted
vault structures. JSON envelope keys will be `version`, `salt`, `nonce`,
`ciphertext`; decrypted payload will be `{"credentials": [...]}` with each
record containing exactly `id`, `website`, `username`, `password`.
Authentication coordinates in-memory serialization/model construction; storage
only handles the encrypted envelope. No plaintext file helpers are provided.

## Credential management (`credentials.py`, Khushi)

| Signature | Output and behavior |
| --- | --- |
| `add_credential(vault: Vault, website: str, username: str, password: str) -> Credential` | Assign unique stable ID, append validated record, return it |
| `list_credentials(vault: Vault) -> list[Credential]` | New list of immutable records in insertion order |
| `search_credentials(vault: Vault, query: str) -> list[Credential]` | New list matching website substring using casefold, stripping query edges; insertion order; empty result for no matches |
| `update_credential(vault: Vault, credential_id: str, website: str, username: str, password: str) -> Credential` | Replace all login fields, preserving ID and position; return new record |
| `delete_credential(vault: Vault, credential_id: str) -> None` | Remove matching record |

Future errors: TypeError for wrong types, ValueError for invalid vault or blank
fields/query/ID, KeyError for missing update/delete ID. Validate before mutation;
failure leaves the vault unchanged. Operations only change memory. The caller
explicitly saves through authentication and handles any save failure. Results
contain passwords in memory; the GUI must select safe fields for display.

## Password tools (`password_tools.py`, Mansi)

| Signature | Output and behavior |
| --- | --- |
| `generate_password(length: int = 16, *, use_symbols: bool = True) -> str` | Secure random password, length 8–128 inclusive; ASCII letters/digits, plus punctuation when enabled; include upper/lower/digit and a symbol when enabled |
| `estimate_strength(password: str) -> str` | `weak`, `moderate`, or `strong`; accepts empty string as weak; no normalization |
| `find_duplicate_passwords(vault: Vault) -> list[list[str]]` | Groups of at least two credential IDs with exactly equal passwords; groups and IDs follow first occurrence order |
| `security_statistics(vault: Vault) -> dict[str, int]` | Keys `total`, `weak`, `moderate`, `strong`, `reused`; reused counts all records in duplicate groups; empty vault gives all zeros |

Future errors: TypeError for wrong types (including bool as length), ValueError
for length outside range or invalid vault. Strength thresholds must be agreed
and documented when implemented; statistics must use that same estimator.
Weak/moderate/strong counts sum to total; reused can overlap strength counts.
Tools have no network, logging, or persistence side effects. Never return
password values as duplicate-report keys.

## GUI and dependency direction

`gui.main_window.main() -> None` will launch Tkinter in Phase 5. It currently
raises NotImplementedError. Importing it does not import Tkinter or open windows.

Models depend only on the standard library. Credentials/password tools depend
on models. Storage and crypto are independent of GUI/authentication. Authentication
uses models and will coordinate storage/crypto. GUI will call authentication,
credentials, and password tools. No lower-level module imports the GUI or the
root prototype. Package initializers have no startup side effects.

## Verification

From the repository root:

```text
python -m compileall -q securelock_app tests
python -m unittest discover -s tests -v
```

Tests use fictional in-memory data only. Security algorithms, storage, and GUI
tests belong to their implementation phases; passing foundation tests does not
mean the application can safely store passwords.
