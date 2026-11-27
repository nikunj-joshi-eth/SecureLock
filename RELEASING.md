# Release checklist — SecureLock

This is a repeatable checklist for the **next GitHub release**. Do not publish a final `v1.1.0` release until the checks below have actually been completed.

## Acceptance gates

- [ ] Review final `main` and confirm no uncommitted or unmerged release-critical code.
- [ ] Run `python -m unittest discover -s tests -v` and `python -m compileall -q securelock_app tests`; record actual results.
- [ ] Verify the GitHub Actions test workflow passes, when available.
- [ ] Launch `python main.py` on Windows and complete relevant items in [GUI_MANUAL_TESTS.md](GUI_MANUAL_TESTS.md) using **fictional data only**.
- [ ] Verify master-password setup/login, credential add/edit/delete, generator, search/filters, statistics, lock/unlock, restart persistence and academic credits.
- [ ] Capture genuine masked screenshots and add to `docs/screenshots/` only after checking for exposed passwords and personal information.
- [ ] Verify the correct coordinator/subject code, documentation and known limitations.
- [ ] Review `git status`, tracked file list and changes for secrets/private vaults.
- [ ] Update [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) to distinguish executed and pending checks.
- [ ] Update [CHANGELOG.md](CHANGELOG.md) and [RELEASE_NOTES.md](RELEASE_NOTES.md) with the actual tag and date once published.

## Publish on GitHub

When the checks pass: open the repository **Releases → Draft a new release**, create tag `v1.1.0` targeting `main`, set title `SecureLock v1.1.0 — Python PBL Desktop Application`, and use a concise summary of implemented features, installation requirements and security limitations from `RELEASE_NOTES.md`. Do not mark it as an audited security product.

**Important:** A GitHub source archive is not a prebuilt Windows installer. No Windows `.exe` or installer is provided unless one is built and tested separately.

## After publication

Verify the release page exists, the tag points to the intended commit, source archives are accessible to authorized repository users, and the release notes accurately match the tagged code.

Verify repository visibility and audit reachable history and release archives for private data before publication. Review historical credits and identifiers as part of that audit.
