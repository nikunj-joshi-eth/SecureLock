# SecureLock v1.1.0 — proposed release notes

**Publication status:** Prepared for a future v1.1.0 GitHub release. **Not yet published.** Historical [v1.0.0](https://github.com/nikunj-joshi-eth/SecureLock/releases/tag/v1.0.0) remains unchanged.

## Highlights

The original Python PBL password manager is now presented through a redesigned **CustomTkinter desktop interface**.

- Refined dark-blue navigation, rounded controls, compact dashboard and clear screen hierarchy.
- Dashboard overview of credential counts, password-strength distribution and rule-based recommendations (not a security certification).
- Credential vault with live search, password-strength/reuse filtering, A–Z sorting, masked selection and clear edit/delete actions.
- Local password generator with an 8–128 character length control, optional symbols, masked result, strength feedback and transfer into Add Credential.
- Setup/login, credential forms and About & Credits redesigned while preserving the existing authentication and encrypted vault format.
- Academic details: Python Programming, `5.0CE202E02H`, Dr. Rosy Madan (Professor), and the four-member PBL team.

## Security and compatibility

The encrypted application is run via `python main.py`; the original `securelock.py` is a separate insecure plaintext educational prototype and **must not** be used for real credentials. Stored encrypted vaults remain compatible with version 1 (Scrypt + AES-256-GCM). No password recovery, inactivity lock, multi-writer protection or independent security audit is included.

## Testing

The professional GUI branch's final test record reports **76 passing tests, zero skipped** on Windows with Python 3.14.3 and CustomTkinter 6.0.0. [GitHub Actions succeeded for the merge commit](https://github.com/nikunj-joshi-eth/SecureLock/actions/runs/44311858715). Tests include real-widget and mock-backed checks. Full keyboard-only/125% scaling and OS-permission acceptance remains incomplete; see [GUI_MANUAL_TESTS.md](GUI_MANUAL_TESTS.md).

## Installation

Python 3.10+ is documented as the project target; release verification occurred on Python 3.14.3. Windows PowerShell:

```powershell
git clone https://github.com/nikunj-joshi-eth/SecureLock.git
cd SecureLock
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

No Windows EXE installer is included. GitHub's zip/tar source archives contain the Python source code. Use **fictional credentials only** in demonstrations.

## Links

- [Full changelog](CHANGELOG.md)
- [Screenshots](docs/screenshots/)
- [Academic project overview](PROJECT_OVERVIEW.md)
- [Security policy](SECURITY.md)
