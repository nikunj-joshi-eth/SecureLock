# SecureLock desktop verification

Use fictional credentials only. These are manual checks, not claims of executed
GUI interaction tests. Run in an isolated project copy so an existing vault is
not disturbed. Keep any test vaults inside its ignored `data/` directory.

Start with `python main.py`. Check layout at 1080×720 and the 900×620 minimum,
keyboard focus/Tab order, readable dark-theme text and visible error messages.

| Check | Steps and expected result |
| --- | --- |
| First-time setup | With no `data/securelock.vault`, see setup. Try a short password, whitespace-only text and mismatched confirmation: no vault created. Matching fictional passphrase of at least 8 characters opens Dashboard. Both fields are masked and cleared after submission. |
| Existing-file protection | Restart: see login, never setup. An existing malformed file also shows login and must not be overwritten. If a file appears during setup, creation fails safely. |
| Correct login | Enter the fictional master passphrase. Dashboard opens with expected totals. |
| Three wrong passwords | Lock, submit three incorrect nonblank passwords. Remaining attempts decrease; after the third the entry/button are disabled. Enter cannot bypass the limit. Restart and use the correct passphrase. |
| Add | Open Vault, Add. All fields are required; password is masked, Show toggles it. Save a fictional record and see success only after persistence. Cancel saves nothing. |
| Search | Search a partial service name with different case. Matching rows appear in order. Clear or a blank query shows all rows; no match shows zero. No table cell contains a password. |
| Edit | Select a row, Edit. Password starts masked. Change all desired fields and save. Stable record position is retained; table strength updates. Cancel leaves the record unchanged. |
| Reveal / Hide | Select a record and click Reveal / Hide. Only then is its password readable. Click again, select another record, search or navigate away: the previous password disappears. |
| Delete | Select a row and Delete. Cancel confirmation leaves it intact; confirming removes it and reports saved success. With no selection, show a helpful prompt. |
| Generator | Test lengths 8, 16 and 128 with symbols on/off. Invalid typed values show an error. A new result is always hidden even if the previous result was shown. Show/hide works; strength appears. Nothing is copied automatically. |
| Use generated password | Click Use in Add Credential. Vault opens with a masked add form containing the generated value. Fill fictional service/username, save, then explicitly reveal to confirm it matches. |
| Dashboard | Add weak, strong and duplicate fictional passwords. Reopen Dashboard after add/edit/delete; total, strong, weak and all records participating in reuse match expected values. |
| Lock / unlock | Reveal a password, then Lock. Login replaces all session pages. Repeat from Generator. Locking via the application cleanup path closes any open credential dialog and clears its fields. Unlock requires authentication again. |
| Restart and persistence | Save changes, close the window and restart. Correct login restores changes. Inspect only the fictional vault: JSON contains version/salt/nonce/ciphertext, with no plaintext master password or credential fields. |
| Corrupted vault | Back up the fictional encrypted vault, close the app, replace the test file with invalid JSON, restart and attempt login. See a safe damaged/unsupported message; no empty vault or overwrite occurs. Restore backup. Ciphertext tampering should fail unlock too. |
| Missing/inaccessible file | Remove or deny access to the fictional vault after the login screen opens. Unlock reports a safe error without creating a replacement. Restore file/permissions afterward. |
| Failed save | In the isolated test copy, deny write/replace permission on `data/` after unlocking (use OS permissions, since Windows read-only flags may not block replacement). Attempt add/edit/delete. Expect an error, no success message, unchanged records and unchanged encrypted file; an add/edit form remains for retry. Restore permissions and retry successfully. Automated tests also inject save failures for all three operations. |

No manual checks above have been marked complete by the automated test suite.
Inactivity auto-lock, multiple simultaneous writers, high-DPI scaling and
platform-specific appearance need separate review before wider use.
