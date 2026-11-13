# SecureLock

**Personal Digital Security Management System**

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Interface CustomTkinter](https://img.shields.io/badge/Interface-CustomTkinter-334155)
![Status Development Build](https://img.shields.io/badge/Status-Development%20Build-orange)

A Python desktop application for managing personal login credentials in a local encrypted vault, generating passwords, and reviewing password strength and reuse. Developed as a second-year B.Tech Python Programming PBL project.

**Launch the encrypted application with `python main.py`.** The preserved `securelock.py` is an insecure educational CLI prototype: it stores the master password and credentials in plaintext. Use fictional data only in that prototype; it is not connected to the desktop vault.

## Features

- First-time master-password setup and authenticated unlock.
- Scrypt key derivation and AES-256-GCM encryption through `cryptography`.
- Add, search, edit and delete credentials with immediate encrypted saves and rollback on save failure.
- Hidden passwords, explicit reveal, delete confirmation and manual vault locking.
- Password generation (8–128 characters, optional symbols) using `secrets`.
- Explainable strength estimates, duplicate detection and dashboard statistics.
- Live website search, strength/reuse filters, reset controls and optional A–Z display sorting.
- In-form password generation and live strength feedback; masked results by default.
- Dashboard recommendations derived from existing counts, without a security score.
- Dark CustomTkinter interface with About & Credits and four-member team details.

## Technologies

Python 3.10+, CustomTkinter, `cryptography`, standard-library `unittest`, dataclasses, pathlib, JSON and Git. No web service or database server is required. JSON on disk contains encrypted ciphertext and public encryption metadata, rather than plaintext credential records.

## Installation and usage

From the repository root, using Python with Tkinter installed:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

On macOS/Linux activate with `source .venv/bin/activate`. Some Linux installations require the distribution's Python Tk package. If PowerShell activation is restricted, use `.venv\Scripts\python.exe` directly for installation and launch commands.

1. Create and confirm a master password of at least eight characters. Prefer a long, unique passphrase.
2. Use Credential Vault to add fictional evaluation records; successful changes save immediately.
3. Search by service name; select a record to edit, delete or explicitly reveal its password.
4. Generate a password and optionally use it in an Add Credential form. Nothing is automatically copied to the clipboard.
5. Lock Vault when leaving the computer; unlock again with the master password.

The vault is stored at `data/securelock.vault` relative to the project location, even when launched elsewhere. Keep encrypted backups. There is no master-password recovery bypass or automatic prototype-data import. Three failed authenticated unlock attempts block login until application restart; this UI limit does not prevent offline guessing.

## Screenshots

Genuine CustomTkinter application captures at 1180×700, using only fictional data:

| View | Screenshot |
| --- | --- |
| Setup | [Setup card](docs/screenshots/setup.png) |
| Dashboard | [Password health overview](docs/screenshots/dashboard.png) |
| Credential Vault | [Vault and fixed actions](docs/screenshots/vault.png) |
| Password Generator | [Generator controls](docs/screenshots/generator.png) |

See [verification results](FINAL_TEST_REPORT.md) and the pending
[manual acceptance checklist](GUI_MANUAL_TESTS.md). Full high-DPI acceptance
remains pending.

## Project architecture

```text
main.py → CustomTkinter view → VaultController
                          ├── authentication → crypto_utils + storage
                          ├── credentials → models
                          └── password_tools → models
```

| Location | Purpose |
| --- | --- |
| `securelock_app/authentication.py` | Setup, unlock and encrypted save coordination |
| `securelock_app/crypto_utils.py` | Versioned Scrypt and AES-GCM helpers |
| `securelock_app/storage.py` | Strict envelope parsing and atomic encrypted writes |
| `securelock_app/models.py` | Validated in-memory data models |
| `securelock_app/credentials.py` | Credential CRUD and service search |
| `securelock_app/password_tools.py` | Generation, strength, reuse and statistics |
| `securelock_app/gui/` | Display-independent controller and CustomTkinter interface |
| `tests/` | Automated tests with fictional temporary data |
| `securelock.py` | Unchanged, insecure plaintext CLI prototype |

See [architecture](ARCHITECTURE.md), [interface contracts](INTERFACES.md), [development timeline](PROJECT_TIMELINE.md), [project overview](PROJECT_OVERVIEW.md) and [release notes](RELEASE_NOTES.md).

## Team and proposed responsibilities

| Member | Roll number | Planned responsibility |
| --- | --- | --- |
| Nikunj Joshi | 25/SET/BCSE/137 | Authentication, encryption coordination and integration |
| Khushi | 25/SET/BCSE/148 | Credential management and storage integration |
| Mansi | 25/SET/BCSE/131 | Password tools and security statistics |
| Sumit Kumar | 25/SET/BCSE/145 | Tkinter GUI and interaction |

These are planned roles, not verified individual authorship. See [CONTRIBUTIONS.md](CONTRIBUTIONS.md); commits and reviewed PRs provide contribution evidence.

## Testing

```powershell
python -m unittest discover -s tests -v
python -m compileall -q securelock_app tests
python -m pip check
```

Tests cover setup/reopening, wrong passwords, tampering, malformed vaults, encrypted CRUD persistence, failed-save rollback, password constraints, statistics and display-free GUI coordination. They do not establish visual usability. See [actual final test results](FINAL_TEST_REPORT.md) and the [manual desktop checklist](GUI_MANUAL_TESTS.md). `TEST_CASES.md` refers to the legacy CLI.

## Security limitations

This educational project has not been independently audited and is not a production password-manager recommendation.

- Format 1 uses Scrypt `n=2**14, r=8, p=1`, a 16-byte random salt, a 32-byte key, AES-GCM with a fresh 12-byte nonce per write and authenticated format/version metadata. These settings remain fixed for compatibility; weak master passwords can still be guessed offline.
- Unlocked secrets exist in memory. Python/Tk cannot guarantee memory erasure; malware, swap and crash dumps remain risks.
- No inactivity auto-lock, recovery bypass, breach lookup, concurrent-writer conflict handling or detection of rollback to an older valid vault is provided.
- Setup requires filesystem hard-link support and fails safely if unavailable. Atomic replacement and file fsync do not guarantee directory durability after power loss. Keep backups and appropriate OS permissions.
- Strength ratings use a small local heuristic, not a security guarantee. Reused counts include every credential participating in a duplicate group and overlap strength counts.
- The legacy `securelock.py` saves plaintext, including its master password, in `securelock_data.json`. Never use real credentials with it.

## Future enhancements

Subject to review and testing: inactivity locking, accessible layout and high-DPI improvements, encrypted backup/restore guidance, concurrent-writer protection and a separately versioned stronger KDF profile. These are proposals, not implemented features.

## Academic information

- Programme: B.Tech Computer Science and Engineering, second year
- Subject: Python Programming — Project-Based Learning
- Subject Code: 5.0CE202E02H
- Under the Guidance of: Dr. Rosy Madan (Professor)
- Build status: Development Build; final manual evaluation pending

The final academic report and presentation will be prepared only after the college submission format is available. No final release tag has been created as part of this integration.

## Project maintenance and GitHub workflow

- [Changelog](CHANGELOG.md) — implemented milestones and release history.
- [Release checklist](RELEASING.md) — manual desktop acceptance, screenshot hygiene, tagging and publication steps.
- [Security policy](SECURITY.md) — limitations and private vulnerability reporting.
- [Contribution guide](CONTRIBUTING.md) — setup, testing and pull-request expectations.
- [GitHub issue templates](.github/ISSUE_TEMPLATE/) and [pull request template](.github/pull_request_template.md) — consistent reports and reviews.
- [Windows test workflow](.github/workflows/tests.yml) — executes automated tests on supported Python versions for pushes and pull requests. Its successful execution must be verified in the **Actions** tab; file presence is not proof that CI passed.

**Repository status:** The GitHub repository is private. A published release does not automatically change visibility. There is no prebuilt Windows installer, no genuine screenshot gallery yet, and no independently validated security certification.
