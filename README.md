# SecureLock — Personal Digital Security Management System

**Python PBL Project | Phase 2E Tkinter desktop application**

The `securelock_app` package now supports encrypted vault setup, unlock and save.
It uses Scrypt and AES-256-GCM through `cryptography`. See
[`INTERFACES.md`](INTERFACES.md) for contracts, version-1 format and limitations,
and [`ARCHITECTURE.md`](ARCHITECTURE.md) for the original architecture plan.
Credential add, list, search, update and delete are implemented in memory.
Local password security tools and the Tkinter desktop application are implemented.
The original `securelock.py` CLI is unchanged and still stores plaintext.

## Launch the desktop application

Install Python 3.10+ with Tkinter, then run from the project directory:

```text
python -m pip install -r requirements.txt
python main.py
```

Tkinter is included with the standard Windows Python installer. On Linux, your
distribution may require its Python Tk package. No additional GUI library is used.
The application opens a dark desktop window with Dashboard, Credential Vault
and Password Generator navigation. After unlocking, About & Credits shows the
project description, four-member team, academic details and Development Build
status. It appears below Password Generator; Lock Vault remains available.
The subject code and coordinator name are placeholders for later completion.

On first launch, create and confirm a master password of at least 8 characters.
Later launches ask you to unlock the existing vault. Three failed authenticated
unlock attempts disable sign-in until you close and restart the application.
This is a per-session UI limit, not protection against offline password guessing.
Malformed or inaccessible vaults produce safe errors; existing files are never
silently replaced during setup.

The encrypted vault is `data/securelock.vault`, relative to the project directory
even when launched from elsewhere. This directory is ignored by Git. Keep an
encrypted backup and remember your master password: there is no recovery bypass.
No prototype data is imported automatically.

Use the vault table to search services, add, edit or delete credentials. Passwords
are absent from the table; Reveal / Hide displays only the selected password.
Delete requires confirmation. Each successful change is saved immediately through
the encrypted backend. A failed save reports an error and restores the previous
in-memory records; the form remains available for retry. Dashboard counts refresh
whenever you open it after a change.

The generator supports lengths 8–128 and optional symbols. Results start hidden;
Show reveals them, and Use in Add Credential fills a masked add form. Nothing is
automatically copied to the clipboard. Lock Vault clears secret fields, closes
credential dialogs and drops the unlocked session. Navigation clears revealed
and generated passwords too. There is no inactivity timer: lock explicitly when
leaving the computer. Python cannot guarantee erasure of secrets from memory.

See [GUI_MANUAL_TESTS.md](GUI_MANUAL_TESTS.md) for the desktop verification checklist.

## Encrypted backend development

Install Python 3.10+ and run:

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q securelock_app tests
```

Call `create_vault(Path(...), master_password)`, `unlock_vault(Path(...),
master_password)` and `save_vault(Path(...), session)` from
`securelock_app.authentication`. Setup requires at least eight characters with
non-whitespace content; prefer a long, unique passphrase. The parent directory
must exist. Setup refuses existing files even during a race. Saves atomically
replace an encrypted file. Sessions and decrypted values belong in memory only.
The new GUI uses this backend; the original CLI does not.

## Credential management

Use the functions in `securelock_app.credentials` with an unlocked session's
`vault`. Records have stable UUIDs. Updates replace all three login fields while
preserving ID and insertion order. Search matches partial service names using
case-insensitive Unicode comparison; blank queries are rejected. List and search
return separate lists of immutable records. Invalid operations leave the vault
unchanged; unknown update/delete IDs raise `KeyError`.

Fictional example (the parent directory must exist):

```python
from pathlib import Path
from securelock_app.authentication import create_vault, save_vault, unlock_vault
from securelock_app.credentials import (
    add_credential, list_credentials, search_credentials,
    update_credential, delete_credential,
)

path = Path("data/fictional.vault")  # Must not already exist for setup.
session = create_vault(path, "fictional master passphrase")
record = add_credential(session.vault, "fictional.example", "fake-user", "fake-password")
matches = search_credentials(session.vault, "FICTIONAL")
record = update_credential(session.vault, record.id, "fictional.example",
                           "new-fake-user", "new-fake-password")
save_vault(path, session)  # Changes are saved only when explicitly requested.
del session
session = unlock_vault(path, "fictional master passphrase")
records = list_credentials(session.vault)  # Contains plaintext passwords in memory.
delete_credential(session.vault, record.id)
save_vault(path, session)
del session
```

Credential operations do no file I/O. Discard session and record references on
lock/exit; Python cannot guarantee secret memory erasure. Direct backend callers
must save explicitly; the GUI saves after each credential change.

## Password security tools

Use `securelock_app.password_tools` with an unlocked vault:

- `generate_password(length=16, use_symbols=True)` returns an 8–128 character
  password using `secrets`, with uppercase, lowercase, digits and optionally
  punctuation. Required categories occur in every result, with no fixed positions.
- `estimate_strength(password)` returns `weak`, `moderate` or `strong`.
- `find_duplicate_passwords(vault)` returns groups of credential IDs in first
  occurrence order, comparing passwords exactly (including case and Unicode).
- `security_statistics(vault)` returns `total`, `weak`, `moderate`, `strong` and
  `reused`. Reused counts every record participating in a duplicate group.

The strength rules apply in order: **weak** for fewer than 8 characters, fewer
than two categories, a common substring, or an entire string made by repeating
a 1–4 character unit at least twice; otherwise **strong** for at least 12
characters and three categories; otherwise **moderate**. Empty strings are weak.
Categories are Unicode lowercase, uppercase, digits and non-alphanumeric,
non-whitespace symbols. Spaces count only toward length. Common substrings are
`password`, `qwerty`, `letmein`, `welcome`, `admin`, `123456` and `abcdef`.
Pattern checks use casefolded text; passwords are never modified.

This explainable heuristic is an estimate, not a cryptographic guarantee. Its
small pattern list is incomplete and can flag useful passphrases too. There is
no external breach lookup. Tools only use memory: they do not modify vaults,
log, print, save passwords or contact services. Callers must also keep returned
passwords out of logs and plaintext files. See INTERFACES.md for exact contracts.

## Encrypted format and limitations

Version 1 saves exactly version, base64 salt, nonce and ciphertext. It derives a
32-byte key with Scrypt (`n=2**14, r=8, p=1`), uses a random 16-byte per-vault salt
and a fresh random 12-byte AES-GCM nonce each save, and authenticates fixed
format/version metadata. Invalid formats are rejected before key derivation;
wrong passwords and modified ciphertext fail without returning a session.
No master password, key or plaintext vault data is written by the backend.

This educational implementation is not independently audited. Weak master
passwords remain vulnerable to offline guessing. Python cannot guarantee memory
erasure, and malware, swap or crash dumps can expose unlocked secrets. There is
no password-reset bypass, rollback protection or concurrent-save conflict
handling. Keep encrypted backups. Setup requires filesystem hard-link support;
unsupported filesystems fail safely. See INTERFACES.md for full details.

## Project team
1. Nikunj Joshi — 25/SET/BCSE/137
2. Khushi — 25/SET/BCSE/148
3. Mansi — 25/SET/BCSE/131
4. Sumit Kumar — 25/SET/BCSE/145

## Original CLI prototype features
- Displays the project title and all four team members
- Creates a master password on the first run
- Allows up to three login attempts
- Adds credentials for a website or service
- Lists websites and usernames without automatically displaying passwords
- Searches credentials by website or service name
- Displays a selected password after confirmation
- Deletes a selected record after confirmation
- Saves records in a local JSON file
- Handles common invalid menu choices and invalid record numbers

## How to run the insecure original prototype
1. Install Python 3.
2. Extract this folder to your computer.
3. Open a terminal in this folder.
4. Run `python securelock.py`.

On Windows, `py securelock.py` may be used instead.

## Important security note
This version is an educational prototype, not a secure password manager. The master password and stored credentials are saved as readable text in `securelock_data.json`. Anyone who can open that file can read them. Use only fake sample credentials. Use fictional credentials in this prototype even though the separate backend now implements encryption.

## Python syllabus topics demonstrated
- Variables, strings, operators, and input/output
- Conditional statements and loops
- Lists and dictionaries
- Functions, parameters, return values, and local variables
- File handling and JSON data storage
- Exception handling and input validation

The modular backend uses `cryptography`; the desktop GUI uses Tkinter/ttk. Install
the dependency with `python -m pip install -r requirements.txt` when
working on that version. NumPy, Pandas, visualization, and image processing
will only be included if they serve a useful project purpose.

## Suggested manual tests
1. Run the program for the first time and set a master password of at least eight characters.
2. Try mismatched passwords during setup.
3. Try three incorrect login attempts.
4. Log in successfully.
5. Add two fake credentials.
6. List credentials and confirm that passwords are not automatically displayed.
7. Search for an existing website and for a non-existing website.
8. View a saved password, then cancel viewing another one.
9. Try letters and out-of-range numbers when selecting a record.
10. Delete a record and restart the program to check whether the change was saved.
