"""Credential operations and encrypted integration using fictional data."""

import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from securelock_app.authentication import create_vault, save_vault, unlock_vault
from securelock_app.credentials import (add_credential, delete_credential,
                                       list_credentials, search_credentials,
                                       update_credential)
from securelock_app.crypto_utils import DecryptionError
from securelock_app.models import Vault


class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.vault = Vault()
        self.first = add_credential(self.vault, "Fictional Mail", " pretend-user ",
                                    " fictional password ")

    def test_add_preserves_fields_and_uuid(self):
        self.assertEqual(uuid.UUID(self.first.id).version, 4)
        self.assertEqual(self.first.website, "Fictional Mail")
        self.assertEqual(self.first.username, " pretend-user ")
        self.assertEqual(self.first.password, " fictional password ")
        self.assertEqual(self.vault.credentials, [self.first])

    def test_multiple_and_independent_list(self):
        second = add_credential(self.vault, self.first.website,
                                self.first.username, self.first.password)
        self.assertNotEqual(self.first.id, second.id)
        result = list_credentials(self.vault)
        self.assertEqual(result, [self.first, second])
        result.clear()
        self.assertEqual(self.vault.credentials, [self.first, second])
        self.assertEqual(list_credentials(Vault()), [])

    def test_uuid_collision_retried(self):
        new_id = uuid.uuid4()
        with patch("securelock_app.credentials.uuid.uuid4",
                   side_effect=[uuid.UUID(self.first.id), new_id]):
            record = add_credential(self.vault, "Other Fiction", "user", "fake")
        self.assertEqual(record.id, str(new_id))
        self.assertEqual(len(self.vault.credentials), 2)

    def test_search_partial_case_and_order(self):
        second = add_credential(self.vault, "FICTIONAL Calendar", "user", "fake")
        add_credential(self.vault, "Other Service", "Fictional", "Fictional")
        result = search_credentials(self.vault, "  fIcTiOnAl  ")
        self.assertEqual(result, [self.first, second])
        result.clear()
        self.assertEqual(len(self.vault.credentials), 3)
        self.assertEqual(search_credentials(self.vault, "MAIL"), [self.first])
        self.assertEqual(search_credentials(self.vault, "missing"), [])
        self.assertEqual(search_credentials(Vault(), "service"), [])

    def test_unicode_casefold(self):
        record = add_credential(self.vault, "Fictional Straße", "user", "fake")
        self.assertEqual(search_credentials(self.vault, "STRASSE"), [record])

    def test_update_preserves_id_position_and_original(self):
        second = add_credential(self.vault, "Other Fiction", "user", "fake")
        updated = update_credential(self.vault, self.first.id,
                                    "New Fiction", "new-user", "new fake password")
        self.assertEqual(updated.id, self.first.id)
        self.assertEqual((updated.website, updated.username, updated.password),
                         ("New Fiction", "new-user", "new fake password"))
        self.assertEqual(self.vault.credentials, [updated, second])
        self.assertEqual(self.first.website, "Fictional Mail")

    def test_delete_preserves_remaining_order(self):
        second = add_credential(self.vault, "Second Fiction", "user", "fake")
        third = add_credential(self.vault, "Third Fiction", "user", "fake")
        self.assertIsNone(delete_credential(self.vault, second.id))
        self.assertEqual(self.vault.credentials, [self.first, third])
        delete_credential(self.vault, self.first.id)
        delete_credential(self.vault, third.id)
        self.assertEqual(self.vault.credentials, [])

    def test_invalid_fields_leave_vault_unchanged(self):
        for invalid in ("", " \t\n", None, 42, [], b"fake"):
            for index in range(3):
                fields = ["Fictional Service", "fake-user", "fake-password"]
                fields[index] = invalid
                for operation in (lambda: add_credential(self.vault, *fields),
                                  lambda: update_credential(self.vault, self.first.id, *fields)):
                    with self.subTest(invalid=invalid, field=index):
                        before = list(self.vault.credentials)
                        with self.assertRaises(ValueError if isinstance(invalid, str) else TypeError):
                            operation()
                        self.assertEqual(self.vault.credentials, before)

    def test_invalid_queries_and_ids_leave_vault_unchanged(self):
        for invalid in ("", "  ", None, 42, []):
            for operation in (lambda: search_credentials(self.vault, invalid),
                              lambda: delete_credential(self.vault, invalid),
                              lambda: update_credential(self.vault, invalid, "fake", "user", "pass")):
                with self.assertRaises(ValueError if isinstance(invalid, str) else TypeError):
                    operation()
                self.assertEqual(self.vault.credentials, [self.first])

    def test_unknown_ids_leave_vault_unchanged(self):
        for operation in (lambda: delete_credential(self.vault, "missing"),
                          lambda: update_credential(self.vault, "missing", "fake", "user", "pass")):
            with self.assertRaises(KeyError):
                operation()
            self.assertEqual(self.vault.credentials, [self.first])

    def test_all_operations_revalidate_vault(self):
        operations = (
            lambda vault: add_credential(vault, "fake", "user", "pass"),
            list_credentials,
            lambda vault: search_credentials(vault, "fake"),
            lambda vault: update_credential(vault, self.first.id, "fake", "user", "pass"),
            lambda vault: delete_credential(vault, self.first.id),
        )
        for contents, error in (([self.first, self.first], ValueError),
                                ([self.first, "invalid"], TypeError)):
            self.vault.credentials[:] = contents
            for operation in operations:
                with self.assertRaises(error):
                    operation(self.vault)
                self.assertEqual(self.vault.credentials, contents)
        for operation in operations:
            with self.assertRaises(TypeError):
                operation(None)

    def test_encrypted_lifecycle_and_explicit_saves(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fictional.vault"
            master = "fictional master passphrase"
            session = create_vault(path, master)
            initial_bytes = path.read_bytes()
            first = add_credential(session.vault, "fictional.example", "imaginary-user",
                                   "imaginary credential password")
            second = add_credential(session.vault, "other-fiction.example", "other-user",
                                    "other fictional password")
            self.assertEqual(path.read_bytes(), initial_bytes)
            self.assertEqual(unlock_vault(path, master).vault.credentials, [])
            save_vault(path, session)
            del session
            session = unlock_vault(path, master)
            self.assertEqual(list_credentials(session.vault), [first, second])
            updated = update_credential(session.vault, first.id, "updated-fiction.example",
                                        "updated-user", "updated fictional password")
            delete_credential(session.vault, second.id)
            self.assertEqual(unlock_vault(path, master).vault.credentials, [first, second])
            save_vault(path, session)
            del session
            reopened = unlock_vault(path, master)
            self.assertEqual(list_credentials(reopened.vault), [updated])
            with self.assertRaises(DecryptionError):
                unlock_vault(path, "incorrect fictional master")
            data = path.read_bytes()
            for record in (first, second, updated):
                for value in (record.id, record.website, record.username, record.password, master):
                    self.assertNotIn(value.encode(), data)
            self.assertEqual(list(Path(directory).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
