# SecureLock desktop verification

Use fictional credentials only. These are manual checks, not claims of executed
GUI interaction tests. Run in an isolated project copy so an existing vault is
not disturbed. Keep any test vaults inside its ignored `data/` directory.

Final integration automated results are in [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md).
This checklist remains pending manual execution after the integration changes,
including descriptive-text wrapping when the window is resized.

Start with `python main.py`. Check layout at 1366×768, 1600×900 and 1920×1080
(screen resolutions; allow for the taskbar and window chrome), the 1180×700 default
and the 1000×620 minimum. At normal Windows scaling, check
active navigation highlighting, dialog resizing, keyboard focus/Tab order, readable dark-theme text and visible error messages.

| Check | Steps and expected result |
| --- | --- |
| First-time setup | With no `data/securelock.vault`, see setup. Try a short password, whitespace-only text and mismatched confirmation: no vault created. Matching fictional passphrase of at least 8 characters opens Dashboard. Both fields are masked and cleared after submission. |
| Existing-file protection | Restart: see login, never setup. An existing malformed file also shows login and must not be overwritten. If a file appears during setup, creation fails safely. |
| Correct login | Enter the fictional master passphrase. Dashboard opens with expected totals. |
| Three wrong passwords | Lock, submit three incorrect nonblank passwords. Remaining attempts decrease; after the third the entry/button are disabled. Enter cannot bypass the limit. Restart and use the correct passphrase. |
| Add | Open Vault, Add. All fields are required; password is masked, Show toggles it. Save a fictional record and see success only after persistence. Generate Password fills the field and remasks it; typing updates the strength estimate. Enter saves and Escape cancels. Cancel saves nothing. |
| Search | Type a partial service name with different case without pressing Enter. Matching rows update immediately. Test All, Weak, Moderate, Strong and Reused, including combined search. Toggle Website A–Z; disabled sorting preserves stored insertion order. Reset clears query and restores All/A–Z. Clear or a blank query shows all rows; no match shows zero. No table cell contains a password. |
| Edit | Select a row, Edit. Password starts masked. Change all desired fields and save. Stable record position is retained; table strength updates. Cancel leaves the record unchanged. |
| Reveal / Hide | Select a record and click Reveal / Hide. Only then is its password readable. Click again, select another record, search or navigate away: the previous password disappears. |
| Delete | Select a row and Delete. Cancel confirmation leaves it intact; confirming removes it and reports saved success. With no selection, show a helpful prompt. |
| Generator | Test lengths 8, 16 and 128 with symbols on/off. Slider steps keep the length within 8–128. A new result is always hidden even if the previous result was shown. Show/hide works; strength appears. Nothing is copied automatically. |
| Use generated password | Click Use in Add Credential. Vault opens with a masked add form containing the generated value. Fill fictional service/username, save, then explicitly reveal to confirm it matches. |
| Dashboard | Add weak, strong and duplicate fictional passwords. Reopen Dashboard after add/edit/delete; total, strong, weak and all records participating in reuse match expected values. Recommendations suggest replacing weak passwords and making reused passwords unique; an empty vault invites adding a credential, and no weak/reused passwords produces qualified encouragement. |
| About & Credits | After unlocking, open About & Credits below Password Generator. Check all four module labels, Development Build, academic details, Subject Code 5.0CE202E02H and the project footer. Check readability at both window sizes. Navigate back to each existing page, then lock from About: login replaces the sidebar and unlocking is required again. |
| Lock / unlock | Reveal a password, then Lock. Login replaces all session pages. Repeat from Generator. Locking via the application cleanup path closes any open credential dialog and clears its fields. Unlock requires authentication again. |
| Restart and persistence | Save changes, close the window and restart. Correct login restores changes. Inspect only the fictional vault: JSON contains version/salt/nonce/ciphertext, with no plaintext master password or credential fields. |
| Corrupted vault | Back up the fictional encrypted vault, close the app, replace the test file with invalid JSON, restart and attempt login. See a safe damaged/unsupported message; no empty vault or overwrite occurs. Restore backup. Ciphertext tampering should fail unlock too. |
| Missing/inaccessible file | Remove or deny access to the fictional vault after the login screen opens. Unlock reports a safe error without creating a replacement. Restore file/permissions afterward. |
| Failed save | In the isolated test copy, deny write/replace permission on `data/` after unlocking (use OS permissions, since Windows read-only flags may not block replacement). Attempt add/edit/delete. Expect an error, no success message, unchanged records and unchanged encrypted file; an add/edit form remains for retry. Restore permissions and retry successfully. Automated tests also inject save failures for all three operations. |

No manual checks above have been marked complete by the automated test suite.
Inactivity auto-lock, multiple simultaneous writers, high-DPI scaling and
platform-specific appearance need separate review before wider use.

## CustomTkinter redesign verification

The application was launched with a temporary fictional vault and its rendered
windows inspected at 1180×700. This is a visual inspection and automated widget
exercise, not a completed human mouse/keyboard acceptance pass.

- [ ] Check every page at 1366×768 desktop resolution and 100% / 125% scaling.
- [ ] At 1000×620, scroll vault rows; Show / Hide, Edit, Delete and Lock stay reachable.
- [ ] Navigate long Dashboard and About pages with wheel, scrollbar and keyboard focus.
- [ ] Verify setup/login feedback, three-attempt lockout, Enter and Tab order.
- [ ] Add/edit/cancel; test live strength, embedded generation and failed-save retry.
- [ ] Check live search, each strength/reuse filter, A–Z toggle and Reset filters.
- [ ] Reveal, select another row, search, navigate and lock; previous secrets clear.
- [ ] Generate at 8 and 128 characters with symbols on/off; Show and regenerate.
- [ ] Use generated password in Add Credential, save and restart the app.
- [ ] Confirm deletion cancellation and encrypted persistence with fictional data.
- [ ] Check long website/usernames and long validation text in the scrollable dialog.

Automated real-widget tests cover functional callbacks and vault action bounds at
the minimum window size. They do not establish high-DPI or cross-platform usability.
