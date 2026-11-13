# SecureLock — Personal Digital Security Management System

**Python PBL Project | Phase 2B encrypted backend**

The `securelock_app` package now supports encrypted vault setup, unlock and save.
It uses Scrypt and AES-256-GCM through `cryptography`. See
[`INTERFACES.md`](INTERFACES.md) for contracts, version-1 format and limitations,
and [`ARCHITECTURE.md`](ARCHITECTURE.md) for the original architecture plan.
Credential CRUD, password tools and Tkinter integration are still pending.
The original `securelock.py` CLI is unchanged and still stores plaintext.

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
This backend is separate from the prototype; running the CLI does not use it.

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
4. Sumit — 25/SET/BCSE/145

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

The modular backend uses `cryptography`; Tkinter integration is pending. Install
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
