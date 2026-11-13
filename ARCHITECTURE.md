# SecureLock architecture

## Current implementation

SecureLock is a local Python desktop application launched with `python main.py`. Its core modules, Tkinter interface and About & Credits are implemented. The original `securelock.py` is preserved unchanged as an insecure educational CLI: it stores both credentials and its master password in plaintext. It is separate from the encrypted application.

## Module boundaries

| Module | Responsibility |
| --- | --- |
| `main.py` | Desktop entry point; no startup on import |
| `securelock_app/models.py` | Validated in-memory Credential and Vault dataclasses |
| `securelock_app/authentication.py` | Create/unlock/save orchestration and memory-only session |
| `securelock_app/crypto_utils.py` | Maintained-library Scrypt and AES-256-GCM wrappers |
| `securelock_app/storage.py` | Strict bounded encrypted JSON envelope I/O and atomic writes |
| `securelock_app/credentials.py` | Validated in-memory CRUD and service search |
| `securelock_app/password_tools.py` | Secure-random generation, strength heuristic, reuse and statistics |
| `securelock_app/gui/controller.py` | Session ownership, safe errors, login attempts and save rollback |
| `securelock_app/gui/main_window.py` | Tkinter/ttk views, navigation, dialogs and secret-field cleanup |

Modules communicate through ordinary Python calls and data structures. There is no server, network dependency or database service. Storage and cryptography do not prompt or import GUI code. Credential/password operations depend on models. Authentication composes models, crypto and storage; the controller coordinates the backend for the view. Package imports do not access vaults or create windows.

## Data flow

### Setup and unlock

1. The GUI collects a masked master password; setup also requires confirmation.
2. Authentication validates input. Setup generates a fresh salt and exclusively creates an encrypted empty vault, refusing an existing destination even during publication races.
3. Unlock reads a bounded, strictly validated envelope before deriving a key.
4. Scrypt derives a 32-byte key in memory. AES-GCM authenticates and decrypts before the payload is parsed and validated into models.
5. A VaultSession retains the vault, key and salt while unlocked, never the master password. Wrong passwords or authentication failures return no session.

### Credential changes and persistence

1. The controller snapshots the list of immutable credential records.
2. Credential operations validate inputs and apply an in-memory change.
3. Authentication validates and serializes the vault only in memory, then encrypts it using a fresh nonce.
4. Storage writes encrypted bytes to a same-directory temporary file, flushes/fsyncs, and atomically replaces the destination. Initial setup publishes exclusively with a hard link.
5. Ordinary validation/save failures restore the original in-memory list; the GUI reports failure without claiming saved success.

The default file is project-relative `data/securelock.vault`. On-disk version 1 contains exactly `version`, `salt`, `nonce` and `ciphertext`. Master passwords, encryption keys and plaintext credential records are not persisted by this application. Exact format and error contracts are in [INTERFACES.md](INTERFACES.md).

### Password tools and GUI lifecycle

Generation uses `secrets`; strength and reuse analysis operate locally on unlocked data. Duplicate reports return credential IDs, not password keys. Strength counts sum to total; reused counts overlap strength classes.

The GUI provides setup/login, Dashboard, Credential Vault, Password Generator and About & Credits. Session pages redirect to login when locked. Navigation clears tracked secret StringVars and destroys old widgets/dialogs. Lock and close also drop the controller session. This is reference cleanup, not guaranteed secret memory erasure.

## Compatibility and security boundaries

Version 1 fixes Scrypt `n=2**14, r=8, p=1, length=32`, a 16-byte salt, a fresh 12-byte AES-GCM nonce per write, a full authentication tag and AAD `b"SecureLock:vault:version=1"`. Changing those choices requires an explicit new format version. Final integration does not change them.

This educational application is not independently audited. There is no recovery bypass, inactivity timer, concurrent-writer protection or rollback detection. File fsync does not ensure directory metadata durability after power loss. Setup requires hard-link support and fails closed where unavailable. Backups, filesystem permissions and endpoint security remain necessary. See INTERFACES for detailed limitations.

## Verification and project records

Automated tests use fictional data and temporary directories. See [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) for actual results and [GUI_MANUAL_TESTS.md](GUI_MANUAL_TESTS.md) for outstanding desktop checks. [PROJECT_TIMELINE.md](PROJECT_TIMELINE.md) preserves the relative development sequence; [CONTRIBUTIONS.md](CONTRIBUTIONS.md) distinguishes planned roles from individual authorship evidence. Final academic formatting awaits college requirements.
