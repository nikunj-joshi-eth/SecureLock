# SecureLock — Manual Test Cases

| No. | Test | Expected result |
|---:|---|---|
| 1 | Start the program without a data file | Master-password setup appears |
| 2 | Use fewer than 8 characters | Setup requests a longer password |
| 3 | Enter different confirmation passwords | Setup asks the user to retry |
| 4 | Enter an incorrect master password three times | Login is refused |
| 5 | Enter the correct master password | Main menu is displayed |
| 6 | Add a credential with all fields filled | Record is saved |
| 7 | Leave a required field empty | Record is not added |
| 8 | List saved records | Website and username appear; passwords remain hidden |
| 9 | Search for an existing website | Matching record is displayed |
| 10 | Search for a missing website | No-match message is displayed |
| 11 | View a password and confirm with `y` | Selected username and password appear |
| 12 | Cancel password viewing | Password is not displayed |
| 13 | Use letters for a record number | Program handles the invalid input |
| 14 | Use an out-of-range record number | Program displays an error |
| 15 | Cancel deletion | Record remains saved |
| 16 | Confirm deletion | Selected record is removed |
| 17 | Restart after saving a fake credential | Record remains available |

**Safety note:** This version stores data as readable text. Test only with fake credentials.
