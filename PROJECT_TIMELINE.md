# SecureLock — Development Timeline and Evidence

**Project:** Personal Digital Security Management System (Python PBL)  
**Team:** Nikunj Joshi (137), Khushi (148), Mansi (131), Sumit Kumar (145)

This document records the project's planned 10-working-day sequence and current implementation checkpoints. **Working days are relative phases, not claims about when the work happened.** GitHub commits and pull requests are the source of truth for dates and actual changes. Proposed module ownership is not proof of individual authorship.

| Phase | Proposed window | Deliverable | GitHub evidence | Status |
| --- | --- | --- | --- | --- |
| 1. Architecture | Days 1–2 | Requirements, README, architecture | [Issue #1](https://github.com/nikunj-joshi-eth/SecureLock/issues/1) | Implemented |
| 2A. Shared foundation | Days 1–2 | Models, interfaces, tests | [PR #11](https://github.com/nikunj-joshi-eth/SecureLock/pull/11) | Merged |
| 2B. Authentication | Days 3–5 | Scrypt/AES-GCM encrypted vault | [PR #12](https://github.com/nikunj-joshi-eth/SecureLock/pull/12) | Merged |
| 2C. Credential management | Days 3–5 | Add/search/edit/delete | [PR #13](https://github.com/nikunj-joshi-eth/SecureLock/pull/13) | Merged |
| 2D. Password tools | Days 3–5 | Generator, strength/reuse statistics | [PR #14](https://github.com/nikunj-joshi-eth/SecureLock/pull/14) | Merged |
| 2E. Desktop interface | Days 6–7 | Tkinter GUI and integration controller | [PR #15](https://github.com/nikunj-joshi-eth/SecureLock/pull/15) | Merged |
| 2F. Credits | Days 6–7 | About & Credits with placeholders | [PR #16](https://github.com/nikunj-joshi-eth/SecureLock/pull/16) | Merged |
| 3. Integration | Days 6–7 | End-to-end integration and issues | [Issue #6](https://github.com/nikunj-joshi-eth/SecureLock/issues/6) | Verification pending |
| 4. Quality assurance | Days 8–9 | Automated/manual tests, fixes, documentation | [Issue #7](https://github.com/nikunj-joshi-eth/SecureLock/issues/7), [Issue #8](https://github.com/nikunj-joshi-eth/SecureLock/issues/8) | Final review pending |
| 5. Submission and release | Day 10 | Report, PPT, release notes, final tagged version | [Issue #9](https://github.com/nikunj-joshi-eth/SecureLock/issues/9), [Issue #10](https://github.com/nikunj-joshi-eth/SecureLock/issues/10) | Pending |

## Proposed module ownership

- **Nikunj Joshi (137):** Authentication, encryption coordination, integration
- **Khushi (148):** Credential management and storage integration
- **Mansi (131):** Password generator, strength/reuse detection, security statistics
- **Sumit Kumar (145):** Tkinter desktop GUI and interaction

Record actual contributions through individual GitHub commits and reviewed PRs; do not equate planned ownership with completed authorship.

## Final verification record

- User reported the initial desktop application worked and looked good after GUI smoke testing; a recorded final verification pass after credits integration is still needed.
- Automated tests exist in the repository; record the final local test command, actual passing count, environment, and outcome in the final QA report.
- Test with **fictional credentials only**. The original `securelock.py` is a separate **insecure plaintext prototype**; use `python main.py` for the encrypted application.
- Coordinator and subject code placeholders in About & Credits remain unfilled intentionally.
- Do not label version 1.0 final or close the final release issue until the end-to-end checks and submission artifacts have actually been completed.

## Useful commands

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q securelock_app tests
python main.py
```
