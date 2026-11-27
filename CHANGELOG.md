# Changelog

Notable development milestones for SecureLock. GitHub commits and merged pull requests provide the authoritative change history.

## Unreleased

- Replaced personal details in application credits with module responsibilities.
- Refreshed setup, screenshot and test documentation and clarified the historical release.

## CustomTkinter interface (unreleased)

- Complete CustomTkinter presentation redesign with rounded controls, redesigned dashboard and improved login, vault, generator and credits pages.
- Four genuine screenshots using fictional demo records added under `docs/screenshots/`.
- Expanded automated coverage: the Windows branch report records 76 passed tests; CI succeeded for merge commit `9993f17`.
- Backend/encryption format unchanged; follow the outstanding manual desktop acceptance checklist before release.

## Earlier v1.0.0 desktop release (13 November 2026)

- Polished the original Tkinter interface with a consistent dark palette, navigation and usable forms.
- Added live service-name search, password-strength and reuse filters, optional website sorting, and dashboard recommendations.
- Added password generation within credential forms and live strength feedback.
- Completed academic credits: Python Programming, subject code `5.0CE202E02H`, .
- Added test coverage and project documentation, including the architecture, project overview, development timeline and final test report.
- Original CLI plaintext prototype remains separate and explicitly marked insecure.

## Earlier development

- [PR #11](https://github.com/nikunj-joshi-eth/SecureLock/pull/11): Shared models and interfaces.
- [PR #12](https://github.com/nikunj-joshi-eth/SecureLock/pull/12): Encrypted vault authentication and storage.
- [PR #13](https://github.com/nikunj-joshi-eth/SecureLock/pull/13): Credential CRUD.
- [PR #14](https://github.com/nikunj-joshi-eth/SecureLock/pull/14): Password tools and statistics.
- [PR #15](https://github.com/nikunj-joshi-eth/SecureLock/pull/15): Tkinter GUI and vault controller.
- [PR #16](https://github.com/nikunj-joshi-eth/SecureLock/pull/16): About & Credits.
- [PR #17](https://github.com/nikunj-joshi-eth/SecureLock/pull/17): Final integration fixes and academic documentation.
- [PR #19](https://github.com/nikunj-joshi-eth/SecureLock/pull/19): GUI usability improvements and final visual polish.

- [PR #21](https://github.com/nikunj-joshi-eth/SecureLock/pull/21): CustomTkinter redesign merged.

**Release history:** [v1.0.0](https://github.com/nikunj-joshi-eth/SecureLock/releases/tag/v1.0.0) exists. Proposed `v1.1.0` is not yet published. See [RELEASING.md](RELEASING.md).
