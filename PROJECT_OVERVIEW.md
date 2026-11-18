# SecureLock project overview

## Problem statement

Users often reuse passwords or keep login details in readable notes. SecureLock demonstrates a small local desktop workflow that protects saved credentials with authenticated encryption and makes password quality easier to discuss. It is an educational implementation rather than an independently audited security product.

## Objectives

Provide master-password setup and unlock, encrypted credential persistence, practical CRUD and search, local password generation and strength/reuse statistics, and a readable CustomTkinter interface. Keep module boundaries simple enough for four second-year B.Tech students to explain and test.

## Methodology

The project progressed from a CLI prototype through architecture and shared interfaces, security/storage, credential operations, password tools, desktop integration and credits. Final integration reviews existing behavior, fixes confirmed issues, runs automated checks and documents outstanding manual verification. The relative development phases are recorded in [PROJECT_TIMELINE.md](PROJECT_TIMELINE.md); they are not dates of individual work.

## Architecture and modules

`main.py` launches the CustomTkinter view. The view calls `VaultController`, which owns the unlocked session, coordinates authentication and persistence, and restores in-memory records after failed saves. Authentication serializes validated models in memory and calls crypto/storage helpers. Credential operations and password tools operate on models without file or GUI dependencies. See [ARCHITECTURE.md](ARCHITECTURE.md) and [INTERFACES.md](INTERFACES.md).

## Implementation

Setup validates and confirms the master password, derives a 256-bit key with Scrypt and exclusively creates an encrypted empty vault. Unlock validates the bounded JSON envelope, derives the key and authenticates ciphertext before constructing records. Version 1 uses AES-256-GCM with a fresh nonce on every save and fixed authenticated format metadata. Atomic encrypted-file replacement protects ordinary save failures; no master password or key is saved.

Credential records are immutable dataclasses with stable UUIDs. Required fields reject blank content while preserving entered values, including password spaces. Live search uses case-insensitive service substrings. The controller filters a display copy by strength or reused IDs and optionally sorts websites A–Z without changing stored order. Dashboard recommendations explain the existing statistics. Add/Edit forms generate passwords through the shared helper and show live strength feedback. Password generation uses `secrets` and guarantees selected character categories. Strength is an explainable heuristic; statistics count strength classes and all records sharing passwords.

The dark CustomTkinter interface provides setup/login, Dashboard, Credential Vault, Password Generator and About & Credits. Passwords start hidden. Navigation clears tracked secrets; locking drops the session and closes dialogs. Academic details: Subject Code 5.0CE202E02H; Under the Guidance of Dr. Rosy Madan (Professor).

## Python concepts demonstrated

- Functions, arguments, return values, conditions and loops.
- Strings, lists, dictionaries, sets and Unicode comparison.
- Packages, imports and separation of responsibilities.
- Dataclasses, immutability, validation and object state.
- Exceptions and safe error translation.
- File handling, JSON, pathlib, temporary files and atomic replacement.
- CustomTkinter widgets, event callbacks and state management.
- Standard-library unit tests, mocks and temporary-directory integration tests.
- Use of a maintained external cryptography library instead of custom cryptographic algorithms.

## Results

The implemented application supports the encrypted desktop workflow and automated failure-path verification. Actual commands, environment, counts and unresolved manual checks are recorded in [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md). Automated controller tests do not prove real desktop usability. Four genuine fictional-data screenshots (setup, dashboard, vault and generator) are now in `docs/screenshots/`; the About & Credits capture remains to be added.

## Limitations and future scope

There is no independent audit, guaranteed memory erasure, password recovery, inactivity lock, multi-writer protection or rollback detection. Weak master passwords remain vulnerable to offline guessing; strength estimates are limited heuristics. Setup needs hard-link support. Future work may address usability, inactivity locking, backup guidance and a new versioned KDF profile after review.

The original `securelock.py` remains unchanged and insecure: it saves credentials and its master password in plaintext. The encrypted application is launched with `python main.py` and does not import prototype data.

## Academic deliverables

This overview supports coordinator evaluation. It is not the final formatted academic report. The coordinator's report template has been supplied. The editable report is prepared separately and still needs final genuine screenshots and an accurate manual-testing record. Planned team responsibilities are documented separately in [CONTRIBUTIONS.md](CONTRIBUTIONS.md).
