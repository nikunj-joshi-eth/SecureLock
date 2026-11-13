# Contributing to SecureLock

SecureLock is a Python Programming university PBL project. Changes should be small, readable, and easy to demonstrate and explain.

## Development setup

Use Python 3.10+ with Tkinter and a virtual environment. From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m compileall -q securelock_app tests
```

Launch the **encrypted GUI** with `python main.py`. The separate `securelock.py` is an intentionally preserved, insecure plaintext prototype. Never use real secrets for testing.

## Suggested workflow

1. Open or refer to a GitHub issue describing the problem.
2. Branch from current `main` with a descriptive name (for example `fix/vault-filter`).
3. Keep changes focused; reuse existing data-model, crypto and controller functions.
4. Add unit tests for behavior changes and update documentation when necessary.
5. Run the full test suite. Test GUI interactions on a Windows desktop when changing Tkinter views.
6. Submit a pull request that explains what changed, how it was tested, and any limitations. Do not claim unperformed tests.

## Safety and compatibility rules

- Do not change vault format version 1, Scrypt parameters, salts/nonces or authenticated metadata without a separately reviewed migration plan.
- Never commit `*.vault`, `securelock_data.json`, API keys, personal credentials, screenshots showing secrets, or local configuration.
- Never log or print passwords or sessions. Use fictional data and temporary directories in tests.
- Avoid unnecessary frameworks and third-party dependencies.
- Preserve the distinction between the educational prototype and the encrypted desktop app.
- Planned team responsibilities are documented in [CONTRIBUTIONS.md](CONTRIBUTIONS.md); credit actual authorship accurately.

## Scope

Issues and pull requests should prioritize correctness, simple UI behavior, tests and accessibility over speculative security claims. This repo does not promise production-grade password management.
