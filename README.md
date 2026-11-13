# SecureLock — Personal Digital Security Management System

**Python PBL Project | Initial Command-Line Prototype**

## Project team
1. Nikunj Joshi — 25/SET/BCSE/137
2. Khushi — 25/SET/BCSE/148
3. Mansi — 25/SET/BCSE/131
4. Sumit — 25/SET/BCSE/145

## Features in this version
- Displays the project title and all four team members
- Creates a master password on the first run
- Allows up to three login attempts
- Adds credentials for a website or service
- Lists websites and usernames without automatically displaying passwords
- Searches credentials by website or service name
- Displays a selected password after confirmation
- Deletes a selected record after confirmation
- Saves records in a local JSON file
- Handles common invalid menu choices and invalid record numbers

## How to run
1. Install Python 3.
2. Extract this folder to your computer.
3. Open a terminal in this folder.
4. Run `python securelock.py`.

On Windows, `py securelock.py` may be used instead.

## Important security note
This version is an educational prototype, not a secure password manager. The master password and stored credentials are saved as readable text in `securelock_data.json`. Anyone who can open that file can read them. Use only fake sample credentials. Do not store real passwords until the project implements secure master-password verification and authenticated encryption.

## Python syllabus topics demonstrated
- Variables, strings, operators, and input/output
- Conditional statements and loops
- Lists and dictionaries
- Functions, parameters, return values, and local variables
- File handling and JSON data storage
- Exception handling and input validation

The later versions may add a Tkinter interface and suitable security libraries. NumPy, Pandas, visualization, and image processing will only be included if they serve a useful project purpose.

## Suggested manual tests
1. Run the program for the first time and set a master password of at least eight characters.
2. Try mismatched passwords during setup.
3. Try three incorrect login attempts.
4. Log in successfully.
5. Add two fake credentials.
6. List credentials and confirm that passwords are not automatically displayed.
7. Search for an existing website and for a non-existing website.
8. View a saved password, then cancel viewing another one.
9. Try letters and out-of-range numbers when selecting a record.
10. Delete a record and restart the program to check whether the change was saved.
