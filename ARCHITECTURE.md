# SecureLock Architecture

## Project overview and objectives

SecureLock is a small Python desktop application for keeping personal login
credentials in a local vault. The current `securelock.py` file is a working
command-line prototype. It demonstrates the basic workflow, but currently
stores the master password and credentials as readable text. It is not safe for
real credentials.

The planned modular version will aim to:

- Protect vault contents with authenticated encryption at rest.
- Keep the master password and derived encryption key out of saved files.
- Support credential management and useful password quality tools.
- Provide a straightforward Tkinter interface backed by testable Python
  modules.
- Keep the design small enough to understand and explain in a college project.

These are design goals. They are not implemented by this document or by the
current prototype.

## Proposed modules and responsibilities

The modular application is planned under `securelock_app/`. The existing root
`securelock.py` remains the prototype and will not be overwritten as part of
this architecture setup.

| Module | Responsibility |
|---|---|
| `securelock_app/models.py` | Define the in-memory credential and vault data structures and basic validation. |
| `securelock_app/authentication.py` | Handle first-time setup and unlock flow; request a master password and coordinate key derivation and password verification without saving the password. |
| `securelock_app/crypto_utils.py` | Wrap the `cryptography` package's Scrypt key derivation and AES-256-GCM encryption/decryption. Generate a fresh random salt for a new vault and a fresh nonce for each encryption. No custom cryptographic algorithms. |
| `securelock_app/storage.py` | Read and write the serialized encrypted vault envelope. Treat malformed data and authentication/decryption failures as errors; never write plaintext credentials. |
| `securelock_app/credentials.py` | Provide credential operations such as add, list/search, update, and delete against the unlocked in-memory vault. |
| `securelock_app/password_tools.py` | Generate passwords, estimate password strength, detect duplicate passwords in the unlocked vault, and calculate security statistics. |
| `securelock_app/gui/main_window.py` | Build the Tkinter screens and translate user actions into calls to application modules. It should not contain cryptography or file-format logic. |
| `securelock.py` | For now, remain the command-line prototype. A later integration phase may turn this into the launcher for the modular application after the team has reviewed the migration plan. |

Tkinter and other standard-library modules do not need to be listed in
`requirements.txt`. The planned third-party dependency is `cryptography`.

## How modules communicate

Modules will communicate through ordinary Python functions and data structures,
not a web service, database server, or message queue. The GUI calls the
authentication and credential operations; those operations call the storage
and cryptography helpers as needed. Password tools receive the in-memory
credential data needed for a requested check and return a result for display.

The GUI should not access encrypted files directly. Storage should not prompt
the user or display GUI messages. Cryptography helpers should accept bytes and
parameters and return bytes or a clear failure; they should not know about
Tkinter widgets or credential screens. This separation keeps each module
small and makes the core logic easier to test.

## Proposed data flow

### Unlocking an existing vault

1. The GUI asks the authentication module to unlock the vault.
2. Authentication obtains the saved vault envelope through storage. The
   envelope contains a format version, Scrypt salt, AES-GCM nonce, and
   ciphertext. It contains no master password or plaintext credential fields.
3. Authentication passes the entered master password and saved salt to the
   crypto helper. Scrypt derives a 256-bit key in memory.
4. Storage/crypto decrypt and authenticate the ciphertext with AES-256-GCM.
   A wrong password or modified ciphertext fails authentication, so the
   application does not open a vault with unverified data.
5. The decrypted data is parsed into in-memory models. The derived key remains
   in memory only while unlocked and is discarded when the vault is locked or
   the application exits, as far as practical in Python.

### Creating or changing vault contents

1. The GUI sends a user action to the credential module, which validates and
   updates the in-memory vault.
2. When saving, the application serializes the vault in memory and asks the
   crypto helper to encrypt it with AES-256-GCM. A new nonce is used for each
   encryption; the vault's unique random salt is retained for deriving its
   key.
3. Storage writes the versioned envelope (salt, nonce, ciphertext and any
   required non-secret metadata) to the local data file. Plaintext credentials
   and the master password are never written to that file.

### Password tools

The password generator creates a password locally and returns it to the GUI.
Strength checks, duplicate detection and statistics operate on data already
available in the unlocked session. They do not send credentials to an external
service. Duplicate checks necessarily compare password values in memory and
must not log or save those values.

## Planned team responsibilities

- **Nikunj:** Authentication, master-password verification, Scrypt key
  derivation coordination, and integration between the security modules.
- **Khushi:** Credential management and integration with encrypted storage.
- **Mansi:** Password generator, strength checker, duplicate detection, and
  security statistics.
- **Sumit:** Tkinter GUI and frontend integration with the application modules.

All members should agree on the data format and function interfaces before
integrating their modules, and review each other's changes for compatibility.

## Development phases

1. **Architecture and repository setup:** Agree on module boundaries, planned
   data flow, dependency, and team ownership. Preserve the current prototype.
2. **Module skeletons and interfaces:** Add the package structure and define
   shared data models and function contracts without replacing the prototype.
3. **Security and storage implementation:** Implement Scrypt-based derivation,
   AES-256-GCM encryption, encrypted vault serialization, and unlock/error
   handling using the maintained `cryptography` package. Do not implement
   cryptographic primitives ourselves.
4. **Credential and password tools:** Implement credential operations and the
   password tools against the agreed in-memory model.
5. **Tkinter integration:** Build the interface and connect it to the modules.
6. **Integration, testing, and documentation:** Verify normal and failure
   paths, update the manual test cases, and explain the final limitations.
7. **Prototype transition:** Only after review, decide how the modular
   application is launched and clearly label the status of the original
   plaintext prototype.

## Proposed file structure

```text
SecureLock/
├── .gitignore
├── ARCHITECTURE.md
├── README.md
├── TEST_CASES.md
├── requirements.txt
├── securelock.py                 # Existing CLI prototype; preserved
├── securelock_app/               # Planned modular application
│   ├── __init__.py
│   ├── models.py
│   ├── authentication.py
│   ├── crypto_utils.py
│   ├── storage.py
│   ├── credentials.py
│   ├── password_tools.py
│   └── gui/
│       ├── __init__.py
│       └── main_window.py
├── data/
│   └── .gitkeep
└── tests/                         # Planned automated tests
```
