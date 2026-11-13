# Release notes — final integration candidate

Status: **Development Build**, prepared on `feature/final-ui-refresh`. This document does not announce a published release or a v1.0.0 tag.

## Implemented functionality

- Master-password setup, authenticated unlock and manual session lock.
- Scrypt key derivation and AES-256-GCM encrypted version-1 vaults.
- Strict bounded envelope validation and atomic encrypted saves.
- Credential add/search/edit/delete with persistence and failed-save rollback.
- Local secure-random password generation, strength estimates and reuse statistics.
- Dark Tkinter Dashboard, Credential Vault, Generator and About & Credits.

## Final UI refresh (Issue #18)

- Active sidebar navigation, consistent dark navy controls and clearer dashboard recommendations.
- Live website search, strength/reuse filters, optional A–Z display sorting, clear/reset and friendly empty states.
- Resizable Add/Edit forms with shared password generation, masking and live strength feedback.
- Updated Subject Code 5.0CE202E02H and Under the Guidance of Dr. Rosy Madan (Professor); team unchanged.
- No dependencies, crypto settings, stored ordering or version-1 format changes.

## Integration improvements

- All session pages redirect to login if invoked while locked.
- Missing-record updates/deletes report a selection problem instead of a misleading required-field error.
- Descriptive page labels adapt wrapping to the available window width.
- Ignore rules cover vaults outside the default directory, encrypted staging files and common secret-key files.
- Updated landing page, current architecture description, contribution guidance, overview and actual QA report.

The version-1 format, KDF parameters and authenticated metadata are unchanged. Existing encrypted vault compatibility is preserved. The original plaintext `securelock.py` is unchanged.

## Requirements and launch

Python 3.10+ with Tkinter and `cryptography>=46.0.0` from `requirements.txt`. Install dependencies and run `python main.py`. A writable project `data/` location and filesystem hard-link support are needed for initial setup. See README for virtual-environment instructions.

## Verification and known limitations

See [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) for actual automated results. Desktop interaction, minimum-window appearance, high-DPI behavior and screenshots remain pending; display-free tests are not manual GUI testing.

This is an educational project without an independent security audit. No recovery bypass, inactivity lock, concurrent-writer conflict handling, rollback detection or guaranteed memory erasure is provided. Strength ratings are estimates; offline guessing remains possible. Keep encrypted backups. `securelock.py` stores plaintext credentials and its master password and must only be used with fictional data.

The college report and presentation await the submission format. Merge, release publication and tagging require separate approval.
