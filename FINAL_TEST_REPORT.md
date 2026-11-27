# Release audit verification

Windows with Python 3.14, cryptography 50.0.2 and CustomTkinter 6.0.0. The full unittest suite passed **76 tests**, including real widgets, encrypted CRUD, reopening, tamper rejection and save rollback. Bytecode compilation and `pip check` passed. Full manual high-DPI and accessibility review remain pending.

## Earlier GUI verification

# Professional GUI redesign verification

Issue: #20. Branch: `feature/professional-gui`.

## Implemented

All desktop screens now use CustomTkinter, with the requested dark palette,
rounded controls, active sidebar navigation and shared components. The dashboard
uses compact metric cards, strength distribution bars, recommendations and quick
actions. Its percentage is explicitly strong / total credentials, not a security
score. The vault uses selectable credential rows, live search, strength/reuse
filters, optional A–Z sorting and a fixed selected-credential action area beside a
masked password field. Only the record list scrolls, keeping its actions visible.
The generator has a stepped 8–128 slider, numeric length, symbols toggle, masked
result, explicit Show, estimated strength and transfer into the Add form.
Add/Edit retains validation, generation, live strength and rollback-aware saving.
Setup/login and the academic About page have been rebuilt too.

The controller, backend APIs, authentication, encryption, encrypted format,
default `data/securelock.vault` path, `main.py` launcher and `securelock.py` are
unchanged. The two GUI implementation files keep layout separate from a small
set of palette/widget helpers.

## Executed validation

Windows, Python 3.14.3, CustomTkinter 6.0.0, cryptography 50.0.2:

- `python -m unittest discover -s tests -q`: **76 tests passed, zero skipped**.
- `python -m compileall -q main.py securelock_app tests`: passed.
- `python -m pip check`: passed; no broken requirements.
- `git diff --check`: passed.
- Diff checks confirm no backend/controller or `securelock.py` changes.

The original backend and security tests remain. Old ttk-specific view mocks were
adapted, and six real-widget integration tests now exercise authentication,
statistics, credits, live search/filter/sort, selection/reveal cleanup, generator
masking and transfer, form validation, injected save failure, CRUD and action
bounds at the minimum 1000×620 window. They create temporary fictional vaults.
Real-widget tests skip on systems without a Tk desktop; this Windows run executed
all of them. The sandbox could not initialize Tcl; desktop verification ran with
approved host execution instead. Tests cancel pending CTk callbacks on teardown.

The UI was actually launched and rendered at 1180×700 with fictional credentials;
setup, dashboard, vault, generator, credits and dialog were inspected from local
captures. Selected genuine app captures are in `docs/screenshots/`. This is not a
claim that a human completed every mouse/keyboard acceptance check.

## Install and launch

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

## Remaining manual checks / known limitations

Follow `GUI_MANUAL_TESTS.md`, especially 1366×768 desktop resolution, 125% display
scaling, keyboard-only navigation, long text, all dialog resize cases and native
confirmation boxes. Default window: 1180×700; minimum: 1000×620; dialog minimum:
520×560. Long pages and dialogs scroll; the vault list scrolls independently.

High-DPI and macOS/Linux visual acceptance remain unverified. No new backend
limitations were introduced or resolved: inactivity auto-lock and simultaneous
writers remain outside this redesign. Python reference cleanup does not promise
secure memory erasure. No release or merge is authorized by this change.
