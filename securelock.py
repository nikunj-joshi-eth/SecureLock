""" 
SecureLock - Personal Digital Security Management System
Python PBL Project | Initial Command-Line Version

Project Credits
1. Team member 1
2. Team member 2
3. Team member 3
4. Team member 4

IMPORTANT:
This is an educational prototype. The master password and saved credentials
are currently stored as readable text in a local JSON file. Use only fake
sample data until secure password verification and encryption are added.
"""

import json
import os
from getpass import getpass

DATA_FILE = "securelock_data.json"


def show_credits():
    """Display the project title and team members."""
    print("=" * 54)
    print("       SECURELOCK: PERSONAL DIGITAL SECURITY")
    print("                 MANAGEMENT SYSTEM")
    print("=" * 54)
    print("Project Team:")
    print("1. Team member 1")
    print("2. Team member 2")
    print("3. Team member 3")
    print("4. Team member 4")
    print("=" * 54)
    print("Educational prototype - do not store real passwords yet.\n")


def empty_data():
    """Return the default structure used by SecureLock."""
    return {"master_password": None, "credentials": []}


def load_data():
    """Load saved data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return empty_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Check that the file contains the information this program needs.
        if not isinstance(data, dict):
            raise ValueError("The saved data is not in the expected format.")

        if "master_password" not in data or "credentials" not in data:
            raise ValueError("Required information is missing from the data file.")

        if not isinstance(data["credentials"], list):
            raise ValueError("The credentials section is not valid.")

        return data

    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Could not load saved data: {error}")
        print("Please check the data file before continuing. SecureLock will close.")
        return None


def save_data(data):
    """Save application data to the local JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return True
    except OSError as error:
        print(f"Could not save the data: {error}")
        return False


def setup_master_password(data):
    """Ask the user to create a master password."""
    print("\n--- Set Up SecureLock ---")

    while True:
        password = getpass("Create a master password (at least 8 characters): ")
        confirmation = getpass("Enter it again to confirm: ")

        if len(password) < 8:
            print("The master password must contain at least 8 characters.")
        elif password != confirmation:
            print("The passwords do not match. Please try again.")
        else:
            data["master_password"] = password

            if save_data(data):
                print("Master password created successfully.")
                print("Reminder: secure password storage will be added in a later phase.")
                return True

            print("Setup could not be saved. Please check the folder permissions.")
            return False


def login(data):
    """Allow up to three attempts to enter the master password."""
    print("\n--- SecureLock Login ---")

    for attempt in range(1, 4):
        entered_password = getpass("Enter your master password: ")

        if entered_password == data["master_password"]:
            print("Login successful. Welcome to SecureLock.")
            return True

        attempts_left = 3 - attempt
        if attempts_left > 0:
            print(f"Incorrect password. Attempts left: {attempts_left}")

    print("Login failed. SecureLock will close.")
    return False


def add_credential(data):
    """Add a website, username, and password to the vault."""
    print("\n--- Add Credential ---")
    website = input("Website or service name: ").strip()
    username = input("Username or email: ").strip()
    password = getpass("Password to save: ")

    if not website or not username or not password:
        print("Website, username, and password are all required.")
        return

    credential = {
        "website": website,
        "username": username,
        "password": password
    }

    data["credentials"].append(credential)

    if save_data(data):
        print(f"Credential for '{website}' added successfully.")
    else:
        # Keep the in-memory list consistent if saving fails.
        data["credentials"].pop()
        print("Credential was not saved. Please try again.")


def list_credentials(data):
    """Show saved website names and usernames, without showing passwords."""
    print("\n--- Saved Credentials ---")

    if not data["credentials"]:
        print("Your vault is empty.")
        return

    for number, credential in enumerate(data["credentials"], start=1):
        print(f"{number}. {credential['website']}  |  {credential['username']}")


def search_credentials(data):
    """Find saved credentials by website or service name."""
    print("\n--- Search Credentials ---")
    search_text = input("Enter a website or service to search for: ").strip().lower()

    if not search_text:
        print("Please enter a search term.")
        return

    matches = []
    for credential in data["credentials"]:
        if search_text in credential["website"].lower():
            matches.append(credential)

    if not matches:
        print("No matching credentials were found.")
        return

    print("\nMatching credentials:")
    for credential in matches:
        print(f"- {credential['website']}  |  {credential['username']}")


def choose_credential(data):
    """Ask the user to select a saved record and return its list position."""
    list_credentials(data)

    if not data["credentials"]:
        return None

    try:
        number = int(input("Enter the record number: "))
    except ValueError:
        print("Please enter a whole number.")
        return None

    if number < 1 or number > len(data["credentials"]):
        print("That record number is not in the list.")
        return None

    return number - 1


def view_credential_password(data):
    """Display the password for a selected record after confirmation."""
    print("\n--- View Saved Password ---")
    position = choose_credential(data)

    if position is None:
        return

    credential = data["credentials"][position]
    confirmation = input(
        f"Show the password for '{credential['website']}'? (y/n): "
    ).strip().lower()

    if confirmation == "y":
        print(f"Username: {credential['username']}")
        print(f"Password: {credential['password']}")
    else:
        print("Password was not displayed.")


def delete_credential(data):
    """Delete a selected record after asking for confirmation."""
    print("\n--- Delete Credential ---")
    position = choose_credential(data)

    if position is None:
        return

    credential = data["credentials"][position]
    confirmation = input(
        f"Delete the record for '{credential['website']}'? (y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    removed_credential = data["credentials"].pop(position)

    if save_data(data):
        print(f"Credential for '{removed_credential['website']}' deleted.")
    else:
        # Put the record back if the file could not be updated.
        data["credentials"].insert(position, removed_credential)
        print("The record was not deleted because saving failed.")


def show_menu():
    """Display the main menu."""
    print("\n------------ Main Menu ------------")
    print("1. Add a credential")
    print("2. List saved credentials")
    print("3. Search credentials")
    print("4. View a saved password")
    print("5. Delete a credential")
    print("6. Exit SecureLock")
    print("-----------------------------------")


def run_vault_menu(data):
    """Keep showing the menu until the user chooses to exit."""
    while True:
        show_menu()
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            add_credential(data)
        elif choice == "2":
            list_credentials(data)
        elif choice == "3":
            search_credentials(data)
        elif choice == "4":
            view_credential_password(data)
        elif choice == "5":
            delete_credential(data)
        elif choice == "6":
            print("Thank you for using SecureLock. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


def main():
    """Start SecureLock and manage the login process."""
    show_credits()
    data = load_data()

    # Stop if the saved file exists but cannot be read safely.
    if data is None:
        return

    if not data["master_password"]:
        if not setup_master_password(data):
            return

    if login(data):
        run_vault_menu(data)


if __name__ == "__main__":
    main()
